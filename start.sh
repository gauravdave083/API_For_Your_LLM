#!/bin/bash

# Quick start script for RAG Chat Assistant
echo "🚀 Quick Start - RAG Chat Assistant"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Test setup
echo "🧪 Testing setup..."
python test_setup.py

# Run migrations
echo "🗄️ Setting up database..."
cd backend
python manage.py makemigrations documents
python manage.py makemigrations embeddings  
python manage.py makemigrations chat
python manage.py migrate

# Create necessary directories
mkdir -p models vector_store media staticfiles

echo "✅ Setup complete!"
echo ""
echo "🎯 To start the application:"
echo "Terminal 1: cd backend && python manage.py runserver"
echo "Terminal 2: cd frontend && streamlit run streamlit_app.py"
echo ""
echo "🌐 URLs:"
echo "- Frontend: http://localhost:8501"
echo "- Backend: http://localhost:8000"
echo "- API Docs: http://localhost:8000/api/"