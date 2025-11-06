import streamlit as st
import requests
import json
import time
from datetime import datetime
import os
from typing import List, Dict
import base64
from io import BytesIO
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="FLXgenie - Your AI Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Google Gemini-like interface
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        max-width: 80%;
    }
    
    .user-message {
        background-color: #f0f2f6;
        margin-left: auto;
        border-left: 4px solid #1f77b4;
    }
    
    .assistant-message {
        background-color: #e8f4fd;
        margin-right: auto;
        border-left: 4px solid #ff6b6b;
    }
    
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #ddd;
        border-radius: 10px;
        background-color: #fafafa;
    }
    
    .sidebar-content {
        padding: 1rem;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .stats-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    
    .stTextInput input {
        border-radius: 20px;
        border: 2px solid #e0e0e0;
        padding: 0.5rem 1rem;
    }
    
    .stButton button {
        border-radius: 20px;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}
if "current_session" not in st.session_state:
    st.session_state.current_session = "default"
if "model_settings" not in st.session_state:
    st.session_state.model_settings = {
        "temperature": 0.7,
        "max_tokens": 1000,
        "model": "mistral"
    }

class FLXGenieAPI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def generate_response(self, prompt: str, api_key: str) -> Dict:
        """Generate response from the API"""
        try:
            headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
            data = {"prompt": prompt}
            
            response = requests.post(
                f"{self.base_url}/generate",
                headers=headers,
                params=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"API Error: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection Error: {str(e)}"}

def sidebar_content():
    """Sidebar with navigation and settings"""
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        # Logo and title
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h1 style="color: #667eea; font-size: 2rem;">🧠 FLXgenie</h1>
            <p style="color: #666; font-size: 0.9rem;">Your Intelligent AI Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # API Configuration
        st.subheader("🔐 API Configuration")
        api_key = st.text_input(
            "API Key",
            type="password",
            value=st.session_state.api_key,
            help="Enter your API key to access the service"
        )
        if api_key:
            st.session_state.api_key = api_key
            st.success("✅ API Key configured")
        
        st.divider()
        
        # Chat Sessions Management
        st.subheader("💬 Chat Sessions")
        
        # New session
        if st.button("➕ New Chat Session"):
            session_id = f"session_{len(st.session_state.chat_sessions) + 1}"
            st.session_state.chat_sessions[session_id] = []
            st.session_state.current_session = session_id
            st.session_state.messages = []
            st.rerun()
        
        # Session selector
        if st.session_state.chat_sessions:
            selected_session = st.selectbox(
                "Select Session",
                list(st.session_state.chat_sessions.keys()),
                index=list(st.session_state.chat_sessions.keys()).index(st.session_state.current_session) if st.session_state.current_session in st.session_state.chat_sessions else 0
            )
            if selected_session != st.session_state.current_session:
                st.session_state.current_session = selected_session
                st.session_state.messages = st.session_state.chat_sessions[selected_session]
                st.rerun()
        
        st.divider()
        
        # Model Settings
        st.subheader("⚙️ Model Settings")
        
        model_options = ["mistral", "llama2", "codellama", "tinyllama"]
        selected_model = st.selectbox(
            "Model",
            model_options,
            index=model_options.index(st.session_state.model_settings["model"]) if st.session_state.model_settings["model"] in model_options else 0
        )
        st.session_state.model_settings["model"] = selected_model
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.model_settings["temperature"],
            step=0.1,
            help="Controls randomness in responses"
        )
        st.session_state.model_settings["temperature"] = temperature
        
        max_tokens = st.slider(
            "Max Tokens",
            min_value=100,
            max_value=2000,
            value=st.session_state.model_settings["max_tokens"],
            step=100,
            help="Maximum length of response"
        )
        st.session_state.model_settings["max_tokens"] = max_tokens
        
        st.divider()
        
        # Statistics
        st.subheader("📊 Statistics")
        total_messages = sum(len(session) for session in st.session_state.chat_sessions.values())
        
        st.markdown(f"""
        <div class="stats-card">
            <strong>Total Messages:</strong> {total_messages}<br>
            <strong>Active Sessions:</strong> {len(st.session_state.chat_sessions)}<br>
            <strong>Current Model:</strong> {st.session_state.model_settings['model']}
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Quick Actions
        st.subheader("🚀 Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                if st.session_state.current_session in st.session_state.chat_sessions:
                    st.session_state.chat_sessions[st.session_state.current_session] = []
                st.rerun()
        
        with col2:
            if st.button("📥 Export Chat"):
                export_chat_history()
        
        # Predefined prompts
        st.subheader("💡 Quick Prompts")
        quick_prompts = [
            "Explain quantum computing in simple terms",
            "Write a Python function to sort a list",
            "What are the latest trends in AI?",
            "Help me debug this code error",
            "Create a marketing strategy for a startup"
        ]
        
        for prompt in quick_prompts:
            if st.button(f"💭 {prompt[:30]}...", key=f"quick_{prompt}"):
                st.session_state.user_input = prompt
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def export_chat_history():
    """Export chat history to JSON"""
    if st.session_state.messages:
        chat_data = {
            "session": st.session_state.current_session,
            "timestamp": datetime.now().isoformat(),
            "messages": st.session_state.messages,
            "model_settings": st.session_state.model_settings
        }
        
        json_str = json.dumps(chat_data, indent=2)
        b64 = base64.b64encode(json_str.encode()).decode()
        
        st.download_button(
            label="📥 Download Chat History",
            data=json_str,
            file_name=f"flxgenie_chat_{st.session_state.current_session}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def display_message(message: Dict, key: str):
    """Display a chat message with proper styling"""
    role = message["role"]
    content = message["content"]
    timestamp = message.get("timestamp", "")
    
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 You</strong> <small style="color: #666;">{timestamp}</small><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🧠 FLXgenie</strong> <small style="color: #666;">{timestamp}</small><br>
            {content}
        </div>
        """, unsafe_allow_html=True)

def main_interface():
    """Main chat interface"""
    # Header
    st.markdown("""
    <div class="main-header">
        <h1 style="color: #667eea;">🧠 FLXgenie</h1>
        <p style="color: #666; font-size: 1.1rem;">Your Intelligent AI Assistant - Powered by Advanced Language Models</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🚀 Fast Responses</h4>
            <p>Lightning-fast AI responses</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🧠 Smart AI</h4>
            <p>Advanced language understanding</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>💬 Multi-Session</h4>
            <p>Manage multiple conversations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <h4>⚙️ Customizable</h4>
            <p>Flexible model settings</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat history
        if st.session_state.messages:
            for i, message in enumerate(st.session_state.messages):
                display_message(message, f"msg_{i}")
        else:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; color: #666;">
                <h3>👋 Welcome to FLXgenie!</h3>
                <p>Start a conversation by typing your message below.</p>
                <p>💡 <strong>Tip:</strong> Use the sidebar for quick prompts and settings.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Input section
    st.divider()
    
    # Initialize the API client
    api_client = FLXGenieAPI()
    
    # Chat input form
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Type your message here... (e.g., 'Explain machine learning' or 'Write a Python script')",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.form_submit_button("🚀 Send", use_container_width=True)
    
    # Handle user input
    if submit_button and user_input:
        if not st.session_state.api_key:
            st.error("⚠️ Please configure your API key in the sidebar first!")
            return
        
        # Add user message
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        }
        st.session_state.messages.append(user_message)
        
        # Update session storage
        if st.session_state.current_session not in st.session_state.chat_sessions:
            st.session_state.chat_sessions[st.session_state.current_session] = []
        st.session_state.chat_sessions[st.session_state.current_session] = st.session_state.messages
        
        # Show loading spinner
        with st.spinner("🤔 FLXgenie is thinking..."):
            # Get AI response
            response = api_client.generate_response(user_input, st.session_state.api_key)
            
            if response["success"]:
                ai_content = response["data"]["response"]
                ai_message = {
                    "role": "assistant",
                    "content": ai_content,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.messages.append(ai_message)
                st.session_state.chat_sessions[st.session_state.current_session] = st.session_state.messages
                
                # Show success message
                st.success("✅ Response generated successfully!")
            else:
                error_message = {
                    "role": "assistant",
                    "content": f"❌ Error: {response['error']}",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.messages.append(error_message)
                st.error(f"Failed to get response: {response['error']}")
        
        st.rerun()
    
    # Additional features section
    st.divider()
    
    # Advanced features
    with st.expander("🔧 Advanced Features"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Analytics")
            if st.session_state.messages:
                df_messages = pd.DataFrame([
                    {
                        "Role": msg["role"].title(),
                        "Length": len(msg["content"]),
                        "Time": msg.get("timestamp", "")
                    }
                    for msg in st.session_state.messages
                ])
                st.dataframe(df_messages, use_container_width=True)
            else:
                st.info("No messages to analyze yet.")
        
        with col2:
            st.subheader("🎯 Conversation Insights")
            if st.session_state.messages:
                total_messages = len(st.session_state.messages)
                user_messages = len([m for m in st.session_state.messages if m["role"] == "user"])
                avg_length = sum(len(m["content"]) for m in st.session_state.messages) / total_messages
                
                st.metric("Total Messages", total_messages)
                st.metric("User Messages", user_messages)
                st.metric("Avg Message Length", f"{avg_length:.0f} chars")
            else:
                st.info("Start chatting to see insights!")

def main():
    """Main application entry point"""
    sidebar_content()
    main_interface()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🧠 <strong>FLXgenie</strong> - Your Intelligent AI Assistant | Built with ❤️ using Streamlit</p>
        <p><small>Powered by Advanced Language Models • Secure • Fast • Reliable</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()