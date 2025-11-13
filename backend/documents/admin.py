from django.contrib import admin
from .models import Document, DocumentChunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_type', 'file_size', 'processed', 'upload_date']
    list_filter = ['processed', 'file_type', 'upload_date']
    search_fields = ['title', 'content']
    readonly_fields = ['upload_date', 'file_size', 'file_type']


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['document', 'chunk_index', 'created_at']
    list_filter = ['document', 'created_at']
    search_fields = ['chunk_text', 'document__title']
    readonly_fields = ['created_at']