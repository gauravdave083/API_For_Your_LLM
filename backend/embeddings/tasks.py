try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Create a dummy decorator for when Celery is not available
    def shared_task(func):
        return func

import logging
from .services import EmbeddingService, VectorStoreService

logger = logging.getLogger(__name__)


@shared_task
def generate_embeddings_for_document(document_id: int):
    """Celery task to generate embeddings for a document"""
    try:
        logger.info(f"Starting embedding generation for document {document_id}")
        
        # Generate embeddings
        embedding_service = EmbeddingService()
        embeddings_created = embedding_service.generate_embeddings_for_document(document_id)
        
        # Add to vector store
        vector_store = VectorStoreService()
        
        # Get the embeddings we just created
        from .models import ChunkEmbedding
        from documents.models import DocumentChunk
        
        chunks = DocumentChunk.objects.filter(document_id=document_id)
        embeddings = ChunkEmbedding.objects.filter(
            chunk__in=chunks,
            embedding_model=embedding_service.embedding_model_obj
        )
        
        vector_store.add_embeddings(list(embeddings))
        
        logger.info(f"Successfully generated and stored {embeddings_created} embeddings for document {document_id}")
        return {
            'document_id': document_id,
            'embeddings_created': embeddings_created,
            'status': 'completed'
        }
        
    except Exception as e:
        logger.error(f"Error generating embeddings for document {document_id}: {str(e)}")
        raise


@shared_task
def rebuild_vector_store():
    """Celery task to rebuild the vector store"""
    try:
        logger.info("Starting vector store rebuild")
        
        vector_store = VectorStoreService()
        vector_store.rebuild_index()
        
        logger.info("Vector store rebuild completed successfully")
        return {'status': 'completed'}
        
    except Exception as e:
        logger.error(f"Error rebuilding vector store: {str(e)}")
        raise