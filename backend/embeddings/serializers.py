from rest_framework import serializers
from .models import EmbeddingModel, ChunkEmbedding, VectorStore


class EmbeddingModelSerializer(serializers.ModelSerializer):
    """Serializer for EmbeddingModel"""
    
    class Meta:
        model = EmbeddingModel
        fields = ['id', 'name', 'model_path', 'dimension', 'created_at', 'is_active']
        read_only_fields = ['created_at']


class ChunkEmbeddingSerializer(serializers.ModelSerializer):
    """Serializer for ChunkEmbedding"""
    chunk_text = serializers.CharField(source='chunk.chunk_text', read_only=True)
    document_title = serializers.CharField(source='chunk.document.title', read_only=True)
    
    class Meta:
        model = ChunkEmbedding
        fields = [
            'id', 'chunk', 'chunk_text', 'document_title', 'embedding_model', 
            'vector_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class VectorStoreSerializer(serializers.ModelSerializer):
    """Serializer for VectorStore"""
    embedding_model_name = serializers.CharField(source='embedding_model.name', read_only=True)
    
    class Meta:
        model = VectorStore
        fields = [
            'id', 'name', 'embedding_model', 'embedding_model_name', 
            'index_path', 'total_vectors', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at', 'total_vectors']


class SimilaritySearchRequestSerializer(serializers.Serializer):
    """Serializer for similarity search request"""
    query = serializers.CharField(max_length=2000, help_text="Query text to search for")
    k = serializers.IntegerField(default=5, min_value=1, max_value=20, help_text="Number of results to return")
    store_name = serializers.CharField(default="default", max_length=255, help_text="Vector store name")


class SimilaritySearchResultSerializer(serializers.Serializer):
    """Serializer for similarity search results"""
    chunk_id = serializers.IntegerField()
    chunk_text = serializers.CharField()
    document_title = serializers.CharField()
    document_id = serializers.IntegerField()
    similarity_score = serializers.FloatField()
    chunk_index = serializers.IntegerField()
    metadata = serializers.DictField()


class SimilaritySearchResponseSerializer(serializers.Serializer):
    """Serializer for similarity search response"""
    query = serializers.CharField()
    results = SimilaritySearchResultSerializer(many=True)
    total_results = serializers.IntegerField()
    search_time_ms = serializers.FloatField()