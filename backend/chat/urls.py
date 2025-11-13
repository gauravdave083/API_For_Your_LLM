from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatSessionViewSet, ChatViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet)
router.register(r'chat', ChatViewSet, basename='chat')
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]