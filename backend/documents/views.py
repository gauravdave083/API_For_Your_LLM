from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
from django.db.models import Count, Q
import logging

from .models import Document, DocumentChunk
from .serializers import (
    DocumentSerializer, 
    DocumentChunkSerializer,
    DocumentUploadResponseSerializer
)
from .services import DocumentProcessor

logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing documents"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        """Upload and process a document"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            with transaction.atomic():
                # Save document
                document = serializer.save()
                
                # Process document and create chunks
                processor = DocumentProcessor()
                chunks_data = processor.process_document(document)
                
                # Save chunks to database
                chunks_created = 0
                for chunk_data in chunks_data:
                    DocumentChunk.objects.create(
                        document=document,
                        chunk_text=chunk_data['text'],
                        chunk_index=chunk_data['index'],
                        metadata=chunk_data['metadata']
                    )
                    chunks_created += 1
                
                # Mark document as processed
                document.processed = True
                document.save()
                
                # Trigger embedding generation (async task)
                try:
                    from embeddings.tasks import generate_embeddings_for_document
                    generate_embeddings_for_document.delay(document.id)
                except ImportError:
                    # Fallback if Celery not available
                    pass
                
                response_data = {
                    'message': 'Document uploaded and processed successfully',
                    'document_id': document.id,
                    'chunks_created': chunks_created,
                    'processing_status': 'completed'
                }
                
                response_serializer = DocumentUploadResponseSerializer(response_data)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error uploading document: {str(e)}")
            return Response(
                {'error': f'Failed to process document: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def chunks(self, request, pk=None):
        """Get chunks for a specific document"""
        try:
            document = self.get_object()
            chunks = DocumentChunk.objects.filter(document=document)
            serializer = DocumentChunkSerializer(chunks, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving chunks for document {pk}: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve document chunks'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess a document"""
        try:
            document = self.get_object()
            
            with transaction.atomic():
                # Delete existing chunks
                DocumentChunk.objects.filter(document=document).delete()
                
                # Reprocess document
                processor = DocumentProcessor()
                chunks_data = processor.process_document(document)
                
                # Create new chunks
                chunks_created = 0
                for chunk_data in chunks_data:
                    DocumentChunk.objects.create(
                        document=document,
                        chunk_text=chunk_data['text'],
                        chunk_index=chunk_data['index'],
                        metadata=chunk_data['metadata']
                    )
                    chunks_created += 1
                
                document.processed = True
                document.save()
                
                # Regenerate embeddings
                try:
                    from embeddings.tasks import generate_embeddings_for_document
                    generate_embeddings_for_document.delay(document.id)
                except ImportError:
                    # Fallback if Celery not available
                    pass
                
                return Response({
                    'message': 'Document reprocessed successfully',
                    'chunks_created': chunks_created
                })
                
        except Exception as e:
            logger.error(f"Error reprocessing document {pk}: {str(e)}")
            return Response(
                {'error': 'Failed to reprocess document'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def processing_status(self, request):
        """Get overall document processing status"""
        try:
            total = Document.objects.count()
            processed = Document.objects.filter(processed=True).count()
            unprocessed = Document.objects.filter(processed=False).count()
            total_chunks = DocumentChunk.objects.count()
            
            stats = {
                'total_documents': total,
                'processed_documents': processed,
                'unprocessed_documents': unprocessed,
                'total_chunks': total_chunks
            }
            return Response(stats)
        except Exception as e:
            logger.error(f"Error getting processing status: {e}")
            return Response(
                {'error': 'Failed to get processing status'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DocumentChunkViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for reading document chunks"""
    queryset = DocumentChunk.objects.all()
    serializer_class = DocumentChunkSerializer
    
    def get_queryset(self):
        """Filter chunks by document if specified"""
        queryset = super().get_queryset()
        document_id = self.request.query_params.get('document_id')
        if document_id:
            queryset = queryset.filter(document_id=document_id)
        return queryset