#!/bin/bash

# RAG Chat Assistant Setup Script

echo "🚀 Setting up RAG Chat Assistant..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
echo "🐍 Python version: $python_version"

if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "❌ Error: Python 3.8 or higher is required"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/models
mkdir -p backend/vector_store
mkdir -p backend/media
mkdir -p backend/staticfiles

# Backend setup
echo "🔧 Setting up Django backend..."
cd backend

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
echo "👤 Create admin user? (y/n)"
read create_admin
if [ "$create_admin" = "y" ]; then
    python manage.py createsuperuser
fi

cd ..

echo "✅ Setup complete!"
echo ""
echo "🎯 To start the application:"
echo "1. Start Redis: redis-server"
echo "2. Start Django: cd backend && python manage.py runserver"
echo "3. Start Celery: cd backend && celery -A rag_backend worker --loglevel=info"
echo "4. Start Streamlit: cd frontend && streamlit run streamlit_app.py"
echo ""
echo "🌐 Access the app at:"
echo "- Frontend: http://localhost:8501"
echo "- Backend API: http://localhost:8000"
echo "- Admin Panel: http://localhost:8000/admin"