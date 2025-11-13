import streamlit as st
import requests
import json
import time
from typing import List, Dict, Any, Optional
import uuid

# Configuration
API_BASE_URL = "http://localhost:8000/api"

class RAGChatInterface:
    """Streamlit interface for RAG Chat application"""
    
    def __init__(self):
        self.api_base = API_BASE_URL
        self.setup_page_config()
        self.initialize_session_state()
    
    def setup_page_config(self):
        """Configure Streamlit page"""
        st.set_page_config(
            page_title="RAG Chat Assistant",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'chat_session_id' not in st.session_state:
            st.session_state.chat_session_id = None
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'documents' not in st.session_state:
            st.session_state.documents = []
        if 'llm_status' not in st.session_state:
            st.session_state.llm_status = None
    
    def check_api_connection(self) -> bool:
        """Check if Django API is accessible"""
        try:
            response = requests.get(f"{self.api_base}/chat/llm_status/", timeout=5)
            if response.status_code == 200:
                st.session_state.llm_status = response.json()
                return True
            return False
        except requests.RequestException:
            return False
    
    def upload_document(self, uploaded_file) -> bool:
        """Upload document to the backend"""
        try:
            files = {"file": uploaded_file}
            data = {"title": uploaded_file.name}
            
            response = requests.post(
                f"{self.api_base}/documents/documents/",
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                st.success(f"✅ Document uploaded successfully! Created {result['chunks_created']} chunks.")
                self.refresh_documents()
                return True
            else:
                st.error(f"❌ Upload failed: {response.text}")
                return False
                
        except requests.RequestException as e:
            st.error(f"❌ Upload error: {str(e)}")
            return False
    
    def refresh_documents(self):
        """Refresh the list of uploaded documents"""
        try:
            response = requests.get(f"{self.api_base}/documents/documents/")
            if response.status_code == 200:
                st.session_state.documents = response.json()
        except requests.RequestException:
            pass
    
    def send_message(self, message: str, use_rag: bool = True) -> Optional[Dict[str, Any]]:
        """Send message to chat API"""
        try:
            data = {
                "message": message,
                "use_rag": use_rag,
                "max_context_chunks": 5
            }
            
            if st.session_state.chat_session_id:
                data["session_id"] = st.session_state.chat_session_id
            
            response = requests.post(
                f"{self.api_base}/chat/chat/send_message/",
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.chat_session_id = result['session_id']
                return result
            else:
                st.error(f"❌ Chat error: {response.text}")
                return None
                
        except requests.RequestException as e:
            st.error(f"❌ Connection error: {str(e)}")
            return None
    
    def render_sidebar(self):
        """Render the sidebar with controls and status"""
        with st.sidebar:
            st.title("🤖 RAG Chat Assistant")
            
            # API Status
            st.subheader("🔌 API Status")
            if self.check_api_connection():
                st.success("✅ Connected to backend")
                if st.session_state.llm_status:
                    llm_status = st.session_state.llm_status
                    st.info(f"🧠 LLM: {llm_status.get('service_type', 'Unknown')}")
                    if llm_status.get('is_available'):
                        st.success("🟢 LLM Available")
                    else:
                        st.error("🔴 LLM Unavailable")
            else:
                st.error("❌ Backend disconnected")
                st.info("Make sure Django server is running on http://localhost:8000")
            
            st.divider()
            
            # Document Upload
            st.subheader("📄 Document Management")
            uploaded_file = st.file_uploader(
                "Upload Document",
                type=['txt', 'pdf', 'docx', 'doc'],
                help="Upload documents to enable RAG functionality"
            )
            
            if uploaded_file is not None:
                if st.button("Upload Document"):
                    with st.spinner("Uploading and processing..."):
                        self.upload_document(uploaded_file)
            
            # Document List
            if st.button("🔄 Refresh Documents"):
                self.refresh_documents()
            
            if st.session_state.documents:
                st.write(f"📚 **Documents ({len(st.session_state.documents)}):**")
                for doc in st.session_state.documents[:5]:  # Show first 5
                    with st.expander(f"📄 {doc['title'][:30]}..."):
                        st.write(f"**Type:** {doc.get('file_type', 'Unknown')}")
                        st.write(f"**Size:** {doc.get('file_size', 0):,} bytes")
                        st.write(f"**Uploaded:** {doc.get('upload_date', 'Unknown')[:10]}")
                        st.write(f"**Processed:** {'✅' if doc.get('processed') else '❌'}")
            else:
                st.info("No documents uploaded yet")
            
            st.divider()
            
            # Chat Settings
            st.subheader("⚙️ Chat Settings")
            use_rag = st.checkbox("Enable RAG", value=True, help="Use document context for responses")
            
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.session_state.chat_session_id = None
                st.rerun()
    
    def render_chat_interface(self):
        """Render the main chat interface"""
        st.title("💬 Chat with Your Documents")
        
        # Chat messages container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    
                    # Show context if available
                    if message["role"] == "assistant" and message.get("context"):
                        with st.expander("📚 Source Context"):
                            for i, context in enumerate(message["context"], 1):
                                st.write(f"**Source {i}: {context['document_title']}**")
                                st.write(f"Similarity: {context['similarity_score']:.3f}")
                                st.write(f"Content: {context['chunk_text'][:200]}...")
                                if i < len(message["context"]):
                                    st.divider()
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your documents..."):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.write(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    use_rag = st.sidebar.checkbox("Enable RAG", value=True)
                    response_data = self.send_message(prompt, use_rag)
                    
                    if response_data:
                        assistant_message = response_data['assistant_message']
                        response_content = assistant_message['content']
                        
                        st.write(response_content)
                        
                        # Show metadata
                        metadata = response_data.get('response_metadata', {})
                        st.caption(f"⏱️ Generated in {metadata.get('generation_time_ms', 0):.0f}ms using {metadata.get('llm_service', 'Unknown')}")
                        
                        # Prepare context for storage
                        context_data = []
                        if assistant_message.get('rag_context'):
                            context_data = [
                                {
                                    'document_title': ctx['document_title'],
                                    'similarity_score': ctx['similarity_score'],
                                    'chunk_text': ctx['chunk_text']
                                }
                                for ctx in assistant_message['rag_context']
                            ]
                            
                            # Show context
                            with st.expander("📚 Source Context"):
                                for i, context in enumerate(context_data, 1):
                                    st.write(f"**Source {i}: {context['document_title']}**")
                                    st.write(f"Similarity: {context['similarity_score']:.3f}")
                                    st.write(f"Content: {context['chunk_text'][:200]}...")
                                    if i < len(context_data):
                                        st.divider()
                        
                        # Add assistant message to chat
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response_content,
                            "context": context_data,
                            "metadata": metadata
                        })
                    else:
                        st.error("Failed to generate response")
    
    def render_info_tab(self):
        """Render information and instructions"""
        st.title("ℹ️ About RAG Chat Assistant")
        
        st.markdown("""
        ## Welcome to the RAG Chat Assistant!
        
        This application demonstrates **Retrieval Augmented Generation (RAG)** - a technique that enhances 
        AI responses by providing relevant context from your uploaded documents.
        
        ### 🔄 How it works:
        
        1. **📄 Upload Documents**: Upload your documents (PDF, DOCX, TXT)
        2. **✂️ Text Chunking**: Documents are split into smaller, manageable chunks
        3. **🔢 Embedding Generation**: Each chunk is converted to vector embeddings
        4. **💾 Vector Storage**: Embeddings are stored in FAISS vector database
        5. **🔍 Similarity Search**: When you ask a question, relevant chunks are found
        6. **🤖 LLM Response**: The AI uses relevant context to generate informed responses
        
        ### 🚀 Features:
        
        - **📤 Document Upload**: Support for TXT, PDF, DOCX formats
        - **🔍 Semantic Search**: Find relevant content using vector similarity
        - **🤖 Local LLM**: Uses open-source models (GPT4All/Ollama)
        - **💬 Chat Interface**: Natural conversation with document context
        - **📊 Context Visualization**: See which documents informed the response
        - **⚙️ Configurable**: Toggle RAG on/off, adjust context chunks
        
        ### 🛠️ Technology Stack:
        
        - **Frontend**: Streamlit
        - **Backend**: Django REST Framework
        - **Vector DB**: FAISS
        - **Embeddings**: Sentence Transformers
        - **LLM**: GPT4All / Ollama (open-source)
        
        ### 📝 Usage Tips:
        
        1. Upload relevant documents first for better responses
        2. Ask specific questions about your document content
        3. Enable RAG for context-aware responses
        4. Check the source context to verify information
        5. Use clear, specific questions for best results
        
        ### 🔧 Setup Requirements:
        
        1. Django backend running on http://localhost:8000
        2. GPT4All model downloaded or Ollama service running
        3. Required Python packages installed
        
        ---
        
        **Need help?** Check the API status in the sidebar and ensure your backend is running.
        """)
    
    def run(self):
        """Main application runner"""
        # Render sidebar
        self.render_sidebar()
        
        # Main content tabs
        tab1, tab2 = st.tabs(["💬 Chat", "ℹ️ Info"])
        
        with tab1:
            self.render_chat_interface()
        
        with tab2:
            self.render_info_tab()


def main():
    """Main function to run the Streamlit app"""
    app = RAGChatInterface()
    app.run()


if __name__ == "__main__":
    main()