from rest_framework import serializers
from .models import Document, DocumentChunk


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file', 'content', 'upload_date', 
            'processed', 'file_type', 'file_size'
        ]
        read_only_fields = ['upload_date', 'processed', 'file_type', 'file_size']

    def validate_file(self, value):
        """Validate uploaded file"""
        if not value:
            raise serializers.ValidationError("No file provided")
        
        # Check file size (max 50MB)
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 50MB")
        
        # Check file type
        allowed_extensions = ['.txt', '.pdf', '.docx', '.doc']
        file_extension = value.name.lower().split('.')[-1]
        if f'.{file_extension}' not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type .{file_extension} not supported. "
                f"Allowed types: {', '.join(allowed_extensions)}"
            )
        
        return value


class DocumentChunkSerializer(serializers.ModelSerializer):
    """Serializer for DocumentChunk model"""
    
    class Meta:
        model = DocumentChunk
        fields = ['id', 'chunk_text', 'chunk_index', 'metadata', 'created_at']
        read_only_fields = ['created_at']


class DocumentUploadResponseSerializer(serializers.Serializer):
    """Serializer for document upload response"""
    message = serializers.CharField()
    document_id = serializers.IntegerField()
    chunks_created = serializers.IntegerField()
    processing_status = serializers.CharField()