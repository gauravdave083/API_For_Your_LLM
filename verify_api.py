#!/usr/bin/env python3
"""
Verification script to test RAG API endpoints
"""

import requests
import json

def test_api_connection():
    """Test basic API connectivity"""
    print("🧪 Testing API Connection")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:8000/api/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is accessible")
            return True
        else:
            print(f"❌ Backend API returned status {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Cannot connect to backend API: {e}")
        return False

def test_document_endpoints():
    """Test document-related endpoints"""
    print("\n📄 Testing Document Endpoints")
    print("=" * 40)
    
    try:
        # Test document list endpoint
        response = requests.get("http://localhost:8000/api/documents/", timeout=5)
        if response.status_code == 200:
            print("✅ Document list endpoint working")
            print(f"   Found {len(response.json())} documents")
        else:
            print(f"❌ Document list endpoint failed: {response.status_code}")
        
        # Test document processing status
        response = requests.get("http://localhost:8000/api/documents/documents/processing_status/", timeout=5)
        if response.status_code == 200:
            print("✅ Document processing status endpoint working")
            status = response.json()
            print(f"   Total documents: {status.get('total_documents', 0)}")
        else:
            print(f"❌ Processing status endpoint failed: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Document endpoints error: {e}")

def test_chat_endpoints():
    """Test chat-related endpoints"""
    print("\n💬 Testing Chat Endpoints")
    print("=" * 40)
    
    try:
        # Test chat session list
        response = requests.get("http://localhost:8000/api/chat/sessions/", timeout=5)
        if response.status_code == 200:
            print("✅ Chat sessions endpoint working")
            print(f"   Found {len(response.json())} chat sessions")
        else:
            print(f"❌ Chat sessions endpoint failed: {response.status_code}")
            
        # Test creating a new chat session
        response = requests.post("http://localhost:8000/api/chat/sessions/", 
                               json={"name": "Test Session"}, 
                               timeout=5)
        if response.status_code == 201:
            print("✅ Chat session creation working")
            session_id = response.json()["id"]
            print(f"   Created session with ID: {session_id}")
            return session_id
        else:
            print(f"❌ Chat session creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"❌ Chat endpoints error: {e}")
    
    return None

def test_embeddings_endpoints():
    """Test embedding-related endpoints"""
    print("\n🧮 Testing Embeddings Endpoints")
    print("=" * 40)
    
    try:
        # Test embedding models list
        response = requests.get("http://localhost:8000/api/embeddings/models/", timeout=5)
        if response.status_code == 200:
            print("✅ Embedding models endpoint working")
            models = response.json()
            print(f"   Found {len(models)} embedding models")
        else:
            print(f"❌ Embedding models endpoint failed: {response.status_code}")
            
        # Test vector store status
        response = requests.get("http://localhost:8000/api/embeddings/stores/vector_store_status/", timeout=5)
        if response.status_code == 200:
            print("✅ Vector store status endpoint working")
            status = response.json()
            print(f"   Total embeddings: {status.get('total_embeddings', 0)}")
            print(f"   Vector stores: {status.get('vector_stores', 0)}")
        else:
            print(f"❌ Vector store status endpoint failed: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Embeddings endpoints error: {e}")

def main():
    """Run all API tests"""
    print("🚀 RAG API Verification")
    print("=" * 50)
    
    # Test basic connectivity
    if not test_api_connection():
        print("\n❌ Cannot proceed with tests - backend API not accessible")
        print("💡 Make sure Django server is running: python manage.py runserver")
        return
    
    # Test all endpoints
    test_document_endpoints()
    test_chat_endpoints()
    test_embeddings_endpoints()
    
    print("\n" + "=" * 50)
    print("🎉 API verification completed!")
    print("\n💡 Next steps:")
    print("   1. Upload a document via the Streamlit interface")
    print("   2. Test chat functionality with the uploaded document")
    print("   3. Check vector embeddings and similarity search")
    
    print(f"\n🌐 Access the application:")
    print(f"   • Frontend: http://localhost:8501")
    print(f"   • Backend API: http://localhost:8000/api/")
    print(f"   • Django Admin: http://localhost:8000/admin/")

if __name__ == "__main__":
    main()