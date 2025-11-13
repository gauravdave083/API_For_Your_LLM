import os
import pickle
import logging
from typing import List, Dict, Tuple, Any
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from django.conf import settings
from django.core.cache import cache

from .models import EmbeddingModel, ChunkEmbedding, VectorStore
from documents.models import DocumentChunk

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing embeddings"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or getattr(settings, 'EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2')
        self.model = None
        self.embedding_model_obj = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            # Check cache first
            cache_key = f"embedding_model_{self.model_name}"
            self.model = cache.get(cache_key)
            
            if self.model is None:
                logger.info(f"Loading embedding model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                # Cache for 1 hour
                cache.set(cache_key, self.model, 3600)
            
            # Get or create embedding model record
            self.embedding_model_obj, created = EmbeddingModel.objects.get_or_create(
                name=self.model_name,
                defaults={
                    'model_path': self.model_name,
                    'dimension': self.model.get_sentence_embedding_dimension(),
                    'is_active': True
                }
            )
            
            if created:
                logger.info(f"Created new embedding model record: {self.model_name}")
                
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        try:
            if not texts:
                return np.array([])
            
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def generate_embedding_for_chunk(self, chunk: DocumentChunk) -> ChunkEmbedding:
        """Generate and store embedding for a single chunk"""
        try:
            # Generate embedding
            embedding_vector = self.generate_embeddings([chunk.chunk_text])[0]
            
            # Create or update chunk embedding
            chunk_embedding, created = ChunkEmbedding.objects.get_or_create(
                chunk=chunk,
                embedding_model=self.embedding_model_obj,
                defaults={
                    'vector_id': f"chunk_{chunk.id}",
                    'embedding_vector': embedding_vector.tolist()
                }
            )
            
            if not created:
                # Update existing embedding
                chunk_embedding.embedding_vector = embedding_vector.tolist()
                chunk_embedding.save()
            
            return chunk_embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding for chunk {chunk.id}: {str(e)}")
            raise
    
    def generate_embeddings_for_document(self, document_id: int) -> int:
        """Generate embeddings for all chunks of a document"""
        try:
            chunks = DocumentChunk.objects.filter(document_id=document_id)
            embeddings_created = 0
            
            for chunk in chunks:
                self.generate_embedding_for_chunk(chunk)
                embeddings_created += 1
            
            logger.info(f"Generated {embeddings_created} embeddings for document {document_id}")
            return embeddings_created
            
        except Exception as e:
            logger.error(f"Error generating embeddings for document {document_id}: {str(e)}")
            raise


class VectorStoreService:
    """Service for managing FAISS vector store"""
    
    def __init__(self, store_name: str = "default", embedding_service: EmbeddingService = None):
        self.store_name = store_name
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store_obj = None
        self.index = None
        self.id_mapping = {}  # Maps FAISS index positions to chunk IDs
        self.store_path = os.path.join(getattr(settings, 'VECTOR_DB_PATH', 'vector_store'), store_name)
        
        # Ensure directory exists
        os.makedirs(self.store_path, exist_ok=True)
        
        self._load_or_create_store()
    
    def _load_or_create_store(self):
        """Load existing vector store or create new one"""
        try:
            # Get or create vector store record
            self.vector_store_obj, created = VectorStore.objects.get_or_create(
                name=self.store_name,
                defaults={
                    'embedding_model': self.embedding_service.embedding_model_obj,
                    'index_path': self.store_path,
                    'total_vectors': 0,
                    'is_active': True
                }
            )
            
            if created or not os.path.exists(os.path.join(self.store_path, 'index.faiss')):
                logger.info(f"Creating new vector store: {self.store_name}")
                self._create_new_index()
            else:
                logger.info(f"Loading existing vector store: {self.store_name}")
                self._load_existing_index()
                
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            raise
    
    def _create_new_index(self):
        """Create a new FAISS index"""
        try:
            dimension = self.embedding_service.embedding_model_obj.dimension
            # Using IndexFlatIP for inner product similarity (cosine similarity)
            self.index = faiss.IndexFlatIP(dimension)
            self.id_mapping = {}
            self._save_index()
            
        except Exception as e:
            logger.error(f"Error creating new index: {str(e)}")
            raise
    
    def _load_existing_index(self):
        """Load existing FAISS index"""
        try:
            index_path = os.path.join(self.store_path, 'index.faiss')
            mapping_path = os.path.join(self.store_path, 'id_mapping.pkl')
            
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
                
                if os.path.exists(mapping_path):
                    with open(mapping_path, 'rb') as f:
                        self.id_mapping = pickle.load(f)
                else:
                    # Rebuild mapping from database
                    self._rebuild_id_mapping()
            else:
                self._create_new_index()
                
        except Exception as e:
            logger.error(f"Error loading existing index: {str(e)}")
            self._create_new_index()
    
    def _save_index(self):
        """Save FAISS index and ID mapping"""
        try:
            index_path = os.path.join(self.store_path, 'index.faiss')
            mapping_path = os.path.join(self.store_path, 'id_mapping.pkl')
            
            faiss.write_index(self.index, index_path)
            
            with open(mapping_path, 'wb') as f:
                pickle.dump(self.id_mapping, f)
            
            # Update database record
            self.vector_store_obj.total_vectors = self.index.ntotal
            self.vector_store_obj.save()
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise
    
    def _rebuild_id_mapping(self):
        """Rebuild ID mapping from database"""
        try:
            embeddings = ChunkEmbedding.objects.filter(
                embedding_model=self.embedding_service.embedding_model_obj
            ).order_by('id')
            
            self.id_mapping = {}
            for idx, embedding in enumerate(embeddings):
                if idx < self.index.ntotal:
                    self.id_mapping[idx] = embedding.chunk.id
            
            logger.info(f"Rebuilt ID mapping with {len(self.id_mapping)} entries")
            
        except Exception as e:
            logger.error(f"Error rebuilding ID mapping: {str(e)}")
            raise
    
    def add_embeddings(self, embeddings: List[ChunkEmbedding]):
        """Add embeddings to the vector store"""
        try:
            if not embeddings:
                return
            
            vectors = np.array([emb.vector_array for emb in embeddings])
            
            # Normalize vectors for cosine similarity
            faiss.normalize_L2(vectors)
            
            # Add to index
            start_idx = self.index.ntotal
            self.index.add(vectors)
            
            # Update ID mapping
            for i, embedding in enumerate(embeddings):
                self.id_mapping[start_idx + i] = embedding.chunk.id
            
            self._save_index()
            logger.info(f"Added {len(embeddings)} embeddings to vector store")
            
        except Exception as e:
            logger.error(f"Error adding embeddings: {str(e)}")
            raise
    
    def search_similar(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks"""
        try:
            if self.index.ntotal == 0:
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embeddings([query_text])[0]
            query_vector = np.array([query_embedding])
            
            # Normalize for cosine similarity
            faiss.normalize_L2(query_vector)
            
            # Search
            k = min(k, self.index.ntotal)
            distances, indices = self.index.search(query_vector, k)
            
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx in self.id_mapping:
                    chunk_id = self.id_mapping[idx]
                    try:
                        chunk = DocumentChunk.objects.select_related('document').get(id=chunk_id)
                        results.append({
                            'chunk_id': chunk_id,
                            'chunk_text': chunk.chunk_text,
                            'document_title': chunk.document.title,
                            'document_id': chunk.document.id,
                            'similarity_score': float(distance),
                            'chunk_index': chunk.chunk_index,
                            'metadata': chunk.metadata
                        })
                    except DocumentChunk.DoesNotExist:
                        logger.warning(f"Chunk {chunk_id} not found in database")
                        continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}")
            raise
    
    def rebuild_index(self):
        """Rebuild the entire vector store from database"""
        try:
            logger.info("Rebuilding vector store index...")
            
            # Get all embeddings
            embeddings = ChunkEmbedding.objects.filter(
                embedding_model=self.embedding_service.embedding_model_obj
            ).select_related('chunk')
            
            if not embeddings.exists():
                logger.info("No embeddings found, creating empty index")
                self._create_new_index()
                return
            
            # Create new index
            dimension = self.embedding_service.embedding_model_obj.dimension
            self.index = faiss.IndexFlatIP(dimension)
            self.id_mapping = {}
            
            # Add all embeddings
            vectors = []
            for idx, embedding in enumerate(embeddings):
                vectors.append(embedding.vector_array)
                self.id_mapping[idx] = embedding.chunk.id
            
            if vectors:
                vectors_array = np.array(vectors)
                faiss.normalize_L2(vectors_array)
                self.index.add(vectors_array)
            
            self._save_index()
            logger.info(f"Rebuilt index with {len(vectors)} vectors")
            
        except Exception as e:
            logger.error(f"Error rebuilding index: {str(e)}")
            raise