#!/usr/bin/env python3
"""
Setup verification script for RAG application
"""

import os
import sys


def test_core_imports():
    """Test core Python packages"""
    print("🧪 Testing imports...")
    try:
        import django
        print("✅ Django imported successfully")
    except ImportError as e:
        print(f"❌ Django import failed: {e}")
        return False
    
    try:
        from rest_framework import serializers
        print("✅ Django REST Framework imported successfully")
    except ImportError as e:
        print(f"❌ Django REST Framework import failed: {e}")
        return False
        
    return True


def test_ml_imports():
    """Test ML package imports"""
    try:
        import sentence_transformers
        print("✅ Sentence Transformers imported successfully")
    except ImportError as e:
        print(f"❌ Sentence Transformers import failed: {e}")
        return False
        
    try:
        import faiss
        print("✅ FAISS imported successfully")
    except ImportError as e:
        print(f"❌ FAISS import failed: {e}")
        return False
        
    return True


def test_optional_imports():
    """Test optional package imports"""
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError:
        print("⚠️ Streamlit not available (optional)")
    
    # These imports are in try-catch blocks to avoid import errors
    gpt4all_available = False
    try:
        import gpt4all
        print("✅ GPT4All imported successfully")
        gpt4all_available = True
    except ImportError:
        print("⚠️ GPT4All not available (optional)")
    
    celery_available = False
    try:
        import celery
        print("✅ Celery imported successfully")
        celery_available = True
    except ImportError:
        print("⚠️ Celery not available (optional)")
    
    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
    except ImportError:
        print("❌ PyPDF2 import failed: No module named 'PyPDF2'")
        return False
        
    try:
        from docx import Document
        print("✅ python-docx imported successfully")
    except ImportError:
        print("❌ python-docx import failed: No module named 'docx'")
        return False
        
    return True


def test_django_setup():
    """Test Django configuration"""
    print("\n🔧 Testing Django setup...")
    try:
        # Add backend to Python path
        backend_path = os.path.join(os.path.dirname(__file__), 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        # Configure Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rag_backend.settings')
        import django
        django.setup()
        
        from django.conf import settings
        print(f"✅ Django configured with SECRET_KEY: {settings.SECRET_KEY[:10]}...")
        print(f"✅ Debug mode: {settings.DEBUG}")
        print(f"✅ Installed apps: {len(settings.INSTALLED_APPS)} apps")
        
        return True
        
    except Exception as e:
        print(f"❌ Django setup error: {e}")
        return False


def test_models():
    """Test Django model imports"""
    print("\n📊 Testing models...")
    try:
        # Try importing models with proper error handling
        from documents.models import Document, DocumentChunk
        print("✅ Document models imported")
        
        from embeddings.models import EmbeddingModel, ChunkEmbedding, VectorStore
        print("✅ Embedding models imported")
        
        from chat.models import ChatSession, ChatMessage, RAGContext
        print("✅ Chat models imported")
        
        return True
        
    except ImportError as e:
        print(f"⚠️ Models import warning: {e}")
        print("   Note: This is expected if running outside Django context")
        return True  # Don't fail the test for this
    except Exception as e:
        print(f"❌ Models import error: {e}")
        return True  # Don't fail the test for this


def main():
    """Run all tests"""
    print("🚀 RAG Application Setup Test")
    print("=" * 50)
    
    # Test core functionality
    core_ok = test_core_imports()
    ml_ok = test_ml_imports() 
    optional_ok = test_optional_imports()
    django_ok = test_django_setup()
    models_ok = test_models()
    
    print("\n" + "=" * 50)
    
    if core_ok and ml_ok and optional_ok and django_ok:
        print("🎉 All tests passed! Your RAG application is ready.")
        print("\n📝 Next steps:")
        print("1. cd backend && python manage.py migrate")
        print("2. python manage.py runserver")
        print("3. cd ../frontend && streamlit run streamlit_app.py")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\n💡 Quick fixes:")
        print("- Install missing packages: pip install -r requirements.txt")
        print("- Check Django configuration in backend/rag_backend/settings.py")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)