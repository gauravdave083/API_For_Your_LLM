from django.contrib import admin
from .models import EmbeddingModel, ChunkEmbedding, VectorStore


@admin.register(EmbeddingModel)
class EmbeddingModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'dimension', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(ChunkEmbedding)
class ChunkEmbeddingAdmin(admin.ModelAdmin):
    list_display = ['chunk', 'embedding_model', 'vector_id', 'created_at']
    list_filter = ['embedding_model', 'created_at']
    search_fields = ['chunk__chunk_text', 'vector_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(VectorStore)
class VectorStoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'embedding_model', 'total_vectors', 'is_active', 'updated_at']
    list_filter = ['is_active', 'embedding_model', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at', 'total_vectors']