# RAG Chat Assistant

A complete Retrieval Augmented Generation (RAG) application built with Django backend and Streamlit frontend, using open-source LLM models.

## 🏗️ Architecture

Based on the RAG workflow diagram, this application implements:

1. **Document Upload & Processing**
2. **Text Chunking & Embedding Generation**
3. **Vector Storage & Similarity Search**
4. **LLM Response Generation with Context**

## 🚀 Features

- **📤 Document Upload**: Support for TXT, PDF, DOCX formats
- **🔍 Semantic Search**: FAISS-based vector similarity search
- **🤖 Local LLM**: GPT4All/Ollama integration
- **💬 Chat Interface**: Interactive Streamlit UI
- **📊 Context Visualization**: See source documents for responses
- **⚙️ REST API**: Complete Django REST API backend

## 🛠️ Technology Stack

- **Backend**: Django + Django REST Framework
- **Frontend**: Streamlit
- **Vector Database**: FAISS
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **LLM**: GPT4All (open-source) / Ollama
- **Database**: SQLite (default) / PostgreSQL
- **Async Processing**: Celery + Redis

## 📋 Prerequisites

- Python 3.8+
- Node.js (optional, for development)
- Redis server (for background tasks)
- 8GB+ RAM (for LLM models)

## 🔧 Installation

### 1. Clone and Setup

```bash
git clone <repository-url>
cd API_For_Your_LLM
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Backend Setup

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Optional
python manage.py runserver
```

### 3. Start Redis (for background tasks)

```bash
# Install Redis first if not installed
redis-server
```

### 4. Start Celery Worker (in new terminal)

```bash
cd backend
celery -A rag_backend worker --loglevel=info
```

### 5. Frontend Setup

```bash
# In new terminal
cd frontend
streamlit run streamlit_app.py
```

## 🎯 Usage

1. **Start Backend**: Django server on http://localhost:8000
2. **Start Frontend**: Streamlit app on http://localhost:8501
3. **Upload Documents**: Use sidebar to upload PDF/DOCX/TXT files
4. **Chat**: Ask questions about your documents
5. **View Context**: See which document chunks informed responses

## 📁 Project Structure

```
API_For_Your_LLM/
├── backend/
│   ├── rag_backend/          # Django project settings
│   ├── documents/            # Document processing app
│   ├── embeddings/           # Vector embeddings app
│   ├── chat/                # Chat and LLM app
│   ├── manage.py
│   └── db.sqlite3
├── frontend/
│   └── streamlit_app.py     # Streamlit interface
├── requirements.txt
├── README.md
└── docker-compose.yml      # Optional Docker setup
```

## 🔗 API Endpoints

### Documents
- `POST /api/documents/documents/` - Upload document
- `GET /api/documents/documents/` - List documents
- `GET /api/documents/documents/{id}/chunks/` - Get document chunks

### Embeddings
- `POST /api/embeddings/embeddings/search/` - Similarity search
- `GET /api/embeddings/stores/` - List vector stores
- `POST /api/embeddings/stores/{id}/rebuild/` - Rebuild vector store

### Chat
- `POST /api/chat/chat/send_message/` - Send chat message
- `GET /api/chat/chat/llm_status/` - Check LLM status
- `GET /api/chat/sessions/` - List chat sessions

## ⚙️ Configuration

### LLM Models

#### GPT4All (Default)
- Models automatically downloaded on first use
- Stored in `backend/models/` directory
- Recommended: `mistral-7b-openorca.Q4_0.gguf`

#### Ollama (Alternative)
1. Install Ollama: https://ollama.ai/
2. Download model: `ollama pull llama2`
3. Update `backend/rag_backend/settings.py`:
   ```python
   LLM_MODEL_TYPE = 'ollama'
   OLLAMA_MODEL_NAME = 'llama2'
   ```

### Environment Variables

Create `.env` file in backend directory:

```env
SECRET_KEY=your-secret-key
DEBUG=True
LLM_MODEL_TYPE=gpt4all
CHUNK_SIZE=500
CHUNK_OVERLAP=100
```

## 🐳 Docker Setup (Optional)

```yaml
# docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - redis
    volumes:
      - ./backend:/app
  
  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    depends_on:
      - backend
```

## 🧪 Testing

```bash
cd backend
python manage.py test
```

## 📊 Performance Tips

1. **Memory**: LLM models require 4-8GB RAM
2. **Storage**: Vector indexes can be large with many documents
3. **GPU**: Use `faiss-gpu` for better performance with large datasets
4. **Chunking**: Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP` for your use case

## 🔍 Troubleshooting

### Common Issues

1. **LLM Model Not Loading**
   - Check available disk space (models are 2-4GB)
   - Verify internet connection for model download

2. **Vector Search Errors**
   - Ensure documents are processed before querying
   - Check if embeddings were generated successfully

3. **API Connection Issues**
   - Verify Django server is running on port 8000
   - Check CORS settings in Django configuration

### Debug Mode

Enable debug logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Sentence Transformers for embeddings
- FAISS for vector similarity search
- GPT4All for open-source LLM
- Django and Streamlit communities

---

**Made with ❤️ for the open-source AI community**

This repository demonstrates how to securely control access to an AI/LLM model by wrapping it with a simple Python API.
Instead of exposing the model directly, we use an API layer to manage the usage of LLM.

🚀 Features

✅ REST API built with Python & FastAPI (lightweight & fast).
🔒 Secure access with API keys.
📜 Request/response logging for monitoring usage.
⚡ Supports any AI model (OpenAI, HuggingFace, or custom LLMs).
🔌 Easily extendable for rate limiting, user roles, or advanced monitoring.
