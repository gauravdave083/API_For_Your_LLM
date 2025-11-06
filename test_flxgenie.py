#!/usr/bin/env python3
"""
FLXgenie Demo Script
This script demonstrates how to test the FLXgenie frontend and backend.
"""

import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_backend():
    """Test the FastAPI backend"""
    print("🔧 Testing API Backend...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API Backend is running successfully!")
            return True
        else:
            print(f"❌ API Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API Backend connection failed: {e}")
        return False

def test_frontend():
    """Test the Streamlit frontend"""
    print("🎨 Testing Streamlit Frontend...")
    
    try:
        # Test frontend endpoint
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit Frontend is running successfully!")
            return True
        else:
            print(f"❌ Frontend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend connection failed: {e}")
        return False

def test_api_functionality():
    """Test API functionality with a sample request"""
    print("🧠 Testing AI Generation...")
    
    api_key = os.getenv("API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("⚠️  Please configure a valid API_KEY in the .env file")
        return False
    
    try:
        headers = {"X-API-Key": api_key}
        params = {"prompt": "Hello, how are you?"}
        
        response = requests.post(
            "http://localhost:8000/generate",
            headers=headers,
            params=params,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ AI Generation successful!")
            print(f"🤖 Response: {data.get('response', 'No response')[:100]}...")
            return True
        else:
            print(f"❌ API request failed with status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return False

def main():
    """Main demo function"""
    print("🧠 FLXgenie System Test")
    print("=" * 40)
    
    # Test backend
    backend_ok = test_api_backend()
    time.sleep(1)
    
    # Test frontend
    frontend_ok = test_frontend()
    time.sleep(1)
    
    # Test API functionality (only if backend is running)
    api_ok = False
    if backend_ok:
        api_ok = test_api_functionality()
    
    # Summary
    print("\n📊 Test Summary")
    print("-" * 20)
    print(f"Backend API: {'✅ Pass' if backend_ok else '❌ Fail'}")
    print(f"Frontend UI: {'✅ Pass' if frontend_ok else '❌ Fail'}")
    print(f"AI Function: {'✅ Pass' if api_ok else '❌ Fail'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 FLXgenie is ready to use!")
        print("📱 Access the frontend at: http://localhost:8501")
        print("📚 API docs available at: http://localhost:8000/docs")
    else:
        print("\n⚠️  Some components need attention:")
        if not backend_ok:
            print("   - Start the API backend: uvicorn main:app --reload")
        if not frontend_ok:
            print("   - Start the frontend: streamlit run flxgenie_frontend.py")

if __name__ == "__main__":
    main()