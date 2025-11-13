from django.contrib import admin
from .models import ChatSession, ChatMessage, RAGContext


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'user']
    search_fields = ['title']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'message_type', 'content_preview', 'created_at']
    list_filter = ['message_type', 'created_at', 'session']
    search_fields = ['content']
    readonly_fields = ['created_at']
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = "Content"


@admin.register(RAGContext)
class RAGContextAdmin(admin.ModelAdmin):
    list_display = ['message', 'document_title', 'similarity_score', 'rank']
    list_filter = ['document_title', 'rank']
    search_fields = ['chunk_text', 'document_title']