from django.db import models
from documents.models import DocumentChunk
import numpy as np


class EmbeddingModel(models.Model):
    """Model for storing embedding model information"""
    name = models.CharField(max_length=255, unique=True)
    model_path = models.CharField(max_length=500)
    dimension = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class ChunkEmbedding(models.Model):
    """Model for storing embeddings of document chunks"""
    chunk = models.OneToOneField(
        DocumentChunk, 
        on_delete=models.CASCADE, 
        related_name='embedding'
    )
    embedding_model = models.ForeignKey(
        EmbeddingModel, 
        on_delete=models.CASCADE,
        related_name='embeddings'
    )
    vector_id = models.CharField(max_length=255, unique=True)  # FAISS index ID
    embedding_vector = models.JSONField()  # Store as JSON array
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Embedding for {self.chunk}"

    @property
    def vector_array(self):
        """Get embedding as numpy array"""
        return np.array(self.embedding_vector)

    @vector_array.setter
    def vector_array(self, value):
        """Set embedding from numpy array"""
        self.embedding_vector = value.tolist()

    class Meta:
        ordering = ['-created_at']
        unique_together = ['chunk', 'embedding_model']


class VectorStore(models.Model):
    """Model for storing vector database metadata"""
    name = models.CharField(max_length=255, unique=True)
    embedding_model = models.ForeignKey(
        EmbeddingModel, 
        on_delete=models.CASCADE,
        related_name='vector_stores'
    )
    index_path = models.CharField(max_length=500)
    total_vectors = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-updated_at']