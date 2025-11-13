from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
import logging

from .models import ChatSession, ChatMessage, RAGContext
from .serializers import (
    ChatSessionSerializer,
    ChatMessageSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer,
    LLMStatusSerializer
)
from .services import RAGService

logger = logging.getLogger(__name__)


class ChatSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing chat sessions"""
    queryset = ChatSession.objects.all()
    serializer_class = ChatSessionSerializer
    
    def get_queryset(self):
        """Filter by user if authenticated"""
        queryset = super().get_queryset()
        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        return queryset
    
    def perform_create(self, serializer):
        """Set user when creating session"""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for a chat session"""
        try:
            session = self.get_object()
            messages = ChatMessage.objects.filter(session=session)
            serializer = ChatMessageSerializer(messages, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving messages for session {pk}: {str(e)}")
            return Response(
                {'error': 'Failed to retrieve messages'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ChatViewSet(viewsets.ViewSet):
    """ViewSet for chat functionality"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rag_service = RAGService()
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Send a message and get AI response"""
        try:
            # Validate request
            request_serializer = ChatRequestSerializer(data=request.data)
            request_serializer.is_valid(raise_exception=True)
            
            message_text = request_serializer.validated_data['message']
            session_id = request_serializer.validated_data.get('session_id')
            use_rag = request_serializer.validated_data['use_rag']
            max_context_chunks = request_serializer.validated_data['max_context_chunks']
            
            with transaction.atomic():
                # Get or create session
                if session_id:
                    try:
                        session = ChatSession.objects.get(id=session_id)
                    except ChatSession.DoesNotExist:
                        session = ChatSession.objects.create(
                            user=request.user if request.user.is_authenticated else None,
                            title=message_text[:50] + "..." if len(message_text) > 50 else message_text
                        )
                else:
                    session = ChatSession.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        title=message_text[:50] + "..." if len(message_text) > 50 else message_text
                    )
                
                # Create user message
                user_message = ChatMessage.objects.create(
                    session=session,
                    message_type='user',
                    content=message_text,
                    metadata=request_serializer.validated_data
                )
                
                # Generate AI response
                if use_rag:
                    response_data = self.rag_service.generate_rag_response(
                        message_text,
                        context_chunks=None  # Let service fetch relevant chunks
                    )
                else:
                    response_data = self.rag_service.generate_rag_response(
                        message_text,
                        context_chunks=[]  # No context
                    )
                
                # Create assistant message
                assistant_message = ChatMessage.objects.create(
                    session=session,
                    message_type='assistant',
                    content=response_data['response'],
                    metadata={
                        'generation_time_ms': response_data['generation_time_ms'],
                        'llm_service': response_data['llm_service'],
                        'context_used': response_data['context_used'],
                        'use_rag': use_rag
                    }
                )
                
                # Store RAG context if used
                if response_data.get('context_chunks'):
                    for rank, chunk in enumerate(response_data['context_chunks']):
                        RAGContext.objects.create(
                            message=assistant_message,
                            chunk_id=chunk['chunk_id'],
                            chunk_text=chunk['chunk_text'],
                            document_title=chunk['document_title'],
                            similarity_score=chunk['similarity_score'],
                            rank=rank
                        )
                
                # Update session timestamp
                session.save()
                
                # Prepare response
                response_data = {
                    'session_id': session.id,
                    'user_message': ChatMessageSerializer(user_message).data,
                    'assistant_message': ChatMessageSerializer(assistant_message).data,
                    'response_metadata': {
                        'generation_time_ms': response_data['generation_time_ms'],
                        'llm_service': response_data['llm_service'],
                        'context_chunks_count': len(response_data.get('context_chunks', [])),
                        'context_used': response_data['context_used']
                    }
                }
                
                response_serializer = ChatResponseSerializer(response_data)
                return Response(response_serializer.data)
                
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            return Response(
                {'error': f'Failed to process message: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def llm_status(self, request):
        """Get LLM service status"""
        try:
            status_data = self.rag_service.get_llm_status()
            serializer = LLMStatusSerializer(status_data)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting LLM status: {str(e)}")
            return Response(
                {'error': 'Failed to get LLM status'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for reading messages"""
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    
    def get_queryset(self):
        """Filter by session and user permissions"""
        queryset = super().get_queryset()
        session_id = self.request.query_params.get('session_id')
        
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        # Filter by user if authenticated
        if self.request.user.is_authenticated:
            queryset = queryset.filter(session__user=self.request.user)
        
        return queryset