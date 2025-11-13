from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import time
import logging

from .models import EmbeddingModel, ChunkEmbedding, VectorStore
from .serializers import (
    EmbeddingModelSerializer,
    ChunkEmbeddingSerializer, 
    VectorStoreSerializer,
    SimilaritySearchRequestSerializer,
    SimilaritySearchResponseSerializer
)
from .services import EmbeddingService, VectorStoreService

logger = logging.getLogger(__name__)


class EmbeddingModelViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for managing embedding models"""
    queryset = EmbeddingModel.objects.all()
    serializer_class = EmbeddingModelSerializer


class VectorStoreViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for managing vector stores"""
    queryset = VectorStore.objects.all()
    serializer_class = VectorStoreSerializer
    
    @action(detail=False, methods=['get'])
    def vector_store_status(self, request):
        """Get vector store status"""
        try:
            from django.conf import settings
            import os
            
            stats = {
                'total_embeddings': ChunkEmbedding.objects.count(),
                'vector_stores': VectorStore.objects.count(),
                'embedding_models': EmbeddingModel.objects.count(),
                'vector_db_path': settings.VECTOR_DB_PATH,
                'vector_db_exists': os.path.exists(settings.VECTOR_DB_PATH)
            }
            return Response(stats)
        except Exception as e:
            logger.error(f"Error getting vector store status: {e}")
            return Response(
                {'error': 'Failed to get vector store status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def rebuild(self, request, pk=None):
        """Rebuild a vector store"""
        try:
            vector_store_obj = self.get_object()
            
            # Trigger rebuild task
            from .tasks import rebuild_vector_store
            task = rebuild_vector_store.delay()
            
            return Response({
                'message': 'Vector store rebuild started',
                'task_id': task.id,
                'status': 'processing'
            })
            
        except Exception as e:
            logger.error(f"Error rebuilding vector store {pk}: {str(e)}")
            return Response(
                {'error': 'Failed to rebuild vector store'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class EmbeddingViewSet(viewsets.ModelViewSet):
    """ViewSet for managing embeddings and search"""
    queryset = ChunkEmbedding.objects.all()
    serializer_class = ChunkEmbeddingSerializer
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Search for similar chunks using vector similarity"""
        try:
            # Validate request
            search_serializer = SimilaritySearchRequestSerializer(data=request.data)
            search_serializer.is_valid(raise_exception=True)
            
            query = search_serializer.validated_data['query']
            k = search_serializer.validated_data['k']
            store_name = search_serializer.validated_data['store_name']
            
            # Perform search
            start_time = time.time()
            
            vector_store = VectorStoreService(store_name=store_name)
            results = vector_store.search_similar(query, k)
            
            search_time_ms = (time.time() - start_time) * 1000
            
            # Prepare response
            response_data = {
                'query': query,
                'results': results,
                'total_results': len(results),
                'search_time_ms': search_time_ms
            }
            
            response_serializer = SimilaritySearchResponseSerializer(response_data)
            return Response(response_serializer.data)
            
        except Exception as e:
            logger.error(f"Error performing similarity search: {str(e)}")
            return Response(
                {'error': f'Search failed: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def generate_for_document(self, request):
        """Generate embeddings for a specific document"""
        try:
            document_id = request.data.get('document_id')
            if not document_id:
                return Response(
                    {'error': 'document_id is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Trigger embedding generation task
            from .tasks import generate_embeddings_for_document
            task = generate_embeddings_for_document.delay(document_id)
            
            return Response({
                'message': 'Embedding generation started',
                'document_id': document_id,
                'task_id': task.id,
                'status': 'processing'
            })
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return Response(
                {'error': 'Failed to generate embeddings'}, 
                status=status.HTTP_400_BAD_REQUEST
            )