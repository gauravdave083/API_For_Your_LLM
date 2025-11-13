@echo off
echo 🚀 Setting up RAG Chat Assistant...

REM Check Python version
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo 📥 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo 📁 Creating directories...
mkdir backend\models 2>nul
mkdir backend\vector_store 2>nul
mkdir backend\media 2>nul
mkdir backend\staticfiles 2>nul

echo 🔧 Setting up Django backend...
cd backend

REM Apply migrations
python manage.py makemigrations
python manage.py migrate

echo 👤 Create admin user? (y/n)
set /p create_admin=
if /i "%create_admin%"=="y" (
    python manage.py createsuperuser
)

cd ..

echo ✅ Setup complete!
echo.
echo 🎯 To start the application:
echo 1. Start Redis: redis-server
echo 2. Start Django: cd backend ^&^& python manage.py runserver
echo 3. Start Celery: cd backend ^&^& celery -A rag_backend worker --loglevel=info
echo 4. Start Streamlit: cd frontend ^&^& streamlit run streamlit_app.py
echo.
echo 🌐 Access the app at:
echo - Frontend: http://localhost:8501
echo - Backend API: http://localhost:8000
echo - Admin Panel: http://localhost:8000/admin

pause