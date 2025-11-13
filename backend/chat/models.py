from django.db import models
from django.contrib.auth.models import User
import uuid


class ChatSession(models.Model):
    """Model for storing chat sessions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Chat: {self.title}"

    class Meta:
        ordering = ['-updated_at']


class ChatMessage(models.Model):
    """Model for storing chat messages"""
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

    class Meta:
        ordering = ['created_at']


class RAGContext(models.Model):
    """Model for storing RAG context used in responses"""
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='rag_context')
    chunk_id = models.PositiveIntegerField()  # Reference to DocumentChunk
    chunk_text = models.TextField()
    document_title = models.CharField(max_length=255)
    similarity_score = models.FloatField()
    rank = models.PositiveIntegerField()  # Order in which chunks were used

    def __str__(self):
        return f"Context for {self.message.id}: {self.document_title}"

    class Meta:
        ordering = ['rank']
        unique_together = ['message', 'rank']