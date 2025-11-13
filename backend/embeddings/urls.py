from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmbeddingModelViewSet, VectorStoreViewSet, EmbeddingViewSet

router = DefaultRouter()
router.register(r'models', EmbeddingModelViewSet)
router.register(r'stores', VectorStoreViewSet)
router.register(r'embeddings', EmbeddingViewSet)

urlpatterns = [
    path('', include(router.urls)),
]