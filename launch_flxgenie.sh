#!/bin/bash

# FLXgenie Launch Script
# This script starts both the API backend and Streamlit frontend

echo "🚀 Starting FLXgenie..."
echo "=========================="

# Check if required packages are installed
echo "📦 Checking dependencies..."
python -c "import streamlit, fastapi, ollama, requests, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔐 Creating environment file..."
    echo "API_KEY=your_api_key_here" > .env
    echo "⚠️  Please update the API_KEY in .env file"
fi

echo "🎯 Starting services..."

# Start FastAPI backend in background
echo "🔧 Starting API backend..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Wait for API to start
sleep 3

# Check if API is running
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ API backend started successfully on http://localhost:8000"
else
    echo "❌ Failed to start API backend"
    kill $API_PID 2>/dev/null
    exit 1
fi

# Start Streamlit frontend
echo "🎨 Starting FLXgenie frontend..."
streamlit run flxgenie_frontend.py --server.port 8501 --server.address 0.0.0.0

# Cleanup when script exits
trap "echo '🛑 Shutting down services...'; kill $API_PID 2>/dev/null; exit" INT TERM EXIT