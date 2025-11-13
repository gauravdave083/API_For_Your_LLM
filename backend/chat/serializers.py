from rest_framework import serializers
from .models import ChatSession, ChatMessage, RAGContext


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for ChatSession"""
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_active', 'message_count']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class RAGContextSerializer(serializers.ModelSerializer):
    """Serializer for RAGContext"""
    
    class Meta:
        model = RAGContext
        fields = ['chunk_id', 'chunk_text', 'document_title', 'similarity_score', 'rank']


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage"""
    rag_context = RAGContextSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'message_type', 'content', 'metadata', 'created_at', 'rag_context']
        read_only_fields = ['created_at']


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat request"""
    message = serializers.CharField(max_length=2000, help_text="User message")
    session_id = serializers.UUIDField(required=False, help_text="Chat session ID (optional)")
    use_rag = serializers.BooleanField(default=True, help_text="Whether to use RAG")
    max_context_chunks = serializers.IntegerField(default=5, min_value=1, max_value=10)


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response"""
    session_id = serializers.UUIDField()
    user_message = ChatMessageSerializer()
    assistant_message = ChatMessageSerializer()
    response_metadata = serializers.DictField()


class LLMStatusSerializer(serializers.Serializer):
    """Serializer for LLM status"""
    service_type = serializers.CharField()
    is_available = serializers.BooleanField()
    model_type = serializers.CharField()