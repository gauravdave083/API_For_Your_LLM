import streamlit as st
import requests
import json
from datetime import datetime
import os
from typing import List, Dict

# Page configuration
st.set_page_config(
    page_title="ChatGPT",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ChatGPT-like CSS styling
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    
    /* Dark theme styling */
    .stApp {
        background-color: #212121;
        color: white;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #171717;
        width: 260px;
    }
    
    .sidebar-content {
        background-color: #171717;
        padding: 0;
        height: 100vh;
    }
    
    /* Main content area */
    .main-content {
        background-color: #212121;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }
    
    /* Header styling */
    .chat-header {
        background-color: #212121;
        padding: 12px 16px;
        border-bottom: 1px solid #424242;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Chat messages styling */
    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 20px;
        background-color: #212121;
    }
    
    .message-container {
        max-width: 768px;
        margin: 0 auto;
        padding: 24px 0;
    }
    
    .user-message {
        background-color: #2f2f2f;
        color: white;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        margin-left: 50px;
        position: relative;
    }
    
    .assistant-message {
        background-color: transparent;
        color: white;
        padding: 12px 0;
        margin: 8px 0;
        border-radius: 8px;
    }
    
    /* Input area styling */
    .input-container {
        background-color: #212121;
        padding: 20px;
        border-top: 1px solid #424242;
    }
    
    .input-wrapper {
        max-width: 768px;
        margin: 0 auto;
        position: relative;
    }
    
    /* Custom buttons */
    .sidebar-button {
        background-color: transparent;
        border: 1px solid #424242;
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        margin: 4px 0;
        width: 100%;
        text-align: left;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .sidebar-button:hover {
        background-color: #2f2f2f;
    }
    
    .chat-item {
        background-color: transparent;
        color: #b3b3b3;
        padding: 8px 12px;
        border-radius: 8px;
        margin: 2px 0;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .chat-item:hover {
        background-color: #2f2f2f;
    }
    
    .chat-item.active {
        background-color: #2f2f2f;
        color: white;
    }
    
    /* Hide streamlit input styling */
    .stTextInput > div > div > input {
        background-color: #2f2f2f;
        border: 1px solid #424242;
        border-radius: 12px;
        color: white;
        padding: 12px 16px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #10a37f;
        box-shadow: 0 0 0 1px #10a37f;
    }
    
    /* Welcome message styling */
    .welcome-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 60vh;
        text-align: center;
    }
    
    .welcome-title {
        font-size: 32px;
        font-weight: 600;
        margin-bottom: 8px;
        color: white;
    }
    
    .welcome-subtitle {
        font-size: 16px;
        color: #b3b3b3;
        margin-bottom: 32px;
    }
    
    /* Action buttons styling */
    .action-buttons {
        display: flex;
        gap: 8px;
        margin-top: 8px;
    }
    
    .action-btn {
        background: transparent;
        border: 1px solid #424242;
        color: #b3b3b3;
        padding: 6px 12px;
        border-radius: 16px;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .action-btn:hover {
        background-color: #2f2f2f;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        "Greeting exchange": [],
        "Multitasking LLM name ideas": [],
        "Test API timeout": [],
        "Hackathon name ideas": [],
        "Best GPT-OSS project": []
    }
if "current_session" not in st.session_state:
    st.session_state.current_session = "Greeting exchange"
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

class ChatGPTAPI:
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

def render_sidebar():
    """Render the sidebar with ChatGPT-like styling"""
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        
        # New chat button
        if st.button("🖊️ New chat", key="new_chat", help="Start a new conversation"):
            new_chat_name = f"New chat {len(st.session_state.chat_sessions) + 1}"
            st.session_state.chat_sessions[new_chat_name] = []
            st.session_state.current_session = new_chat_name
            st.session_state.messages = []
            st.rerun()
        
        # Search chats
        st.text_input("🔍 Search chats", placeholder="Search chats", key="search_chats")
        
        # Navigation sections
        st.markdown("### Library")
        if st.button("📚 Library", key="library"):
            st.info("Library feature")
        
        if st.button("📁 Projects", key="projects"):
            st.info("Projects feature")
        
        st.markdown("### GPTs")
        if st.button("🔍 Explore", key="explore"):
            st.info("Explore GPTs")
        
        # Custom GPTs (sample)
        st.markdown('<div style="padding: 8px 0; color: #b3b3b3; font-size: 14px;">🟠 GMAT Tutor</div>', unsafe_allow_html=True)
        st.markdown('<div style="padding: 8px 0; color: #b3b3b3; font-size: 14px;">📄 Research Paper Generator</div>', unsafe_allow_html=True)
        
        st.markdown("### Chats")
        
        # Chat sessions
        for chat_name in st.session_state.chat_sessions.keys():
            is_active = chat_name == st.session_state.current_session
            button_class = "chat-item active" if is_active else "chat-item"
            
            if st.button(chat_name, key=f"chat_{chat_name}"):
                st.session_state.current_session = chat_name
                st.session_state.messages = st.session_state.chat_sessions[chat_name]
                st.rerun()
        
        # User profile at bottom
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown('<div style="color: #b3b3b3; font-size: 14px;">👤 Gaurav Dave</div>', unsafe_allow_html=True)
        with col2:
            if st.button("⬆️", key="upgrade", help="Upgrade"):
                st.info("Upgrade to Plus")
        
        st.markdown('</div>', unsafe_allow_html=True)

def render_main_content():
    """Render the main chat content area"""
    # Get current messages
    current_messages = st.session_state.chat_sessions.get(st.session_state.current_session, [])
    
    # Header with model selector and buttons
    st.markdown("""
    <div class="chat-header">
        <div style="display: flex; align-items: center;">
            <span style="font-weight: 600; margin-right: 8px;">ChatGPT</span>
            <select style="background: transparent; border: none; color: white;">
                <option>4o</option>
                <option>o1-preview</option>
                <option>o1-mini</option>
            </select>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
            <button style="background: #6366f1; color: white; border: none; padding: 6px 12px; border-radius: 6px; font-size: 14px;">
                ✨ Get Plus
            </button>
            <span style="color: #ef4444; font-size: 14px;">🧠 Memory full</span>
            <button style="background: transparent; border: none; color: #b3b3b3;">📤 Share</button>
            <button style="background: transparent; border: none; color: #b3b3b3;">⋯</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat messages area
    if current_messages:
        st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
        for message in current_messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message-container">
                    <div class="user-message">
                        {message["content"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-container">
                    <div class="assistant-message">
                        <strong>ChatGPT</strong><br>
                        {message["content"]}
                        <div class="action-buttons">
                            <button class="action-btn">📋</button>
                            <button class="action-btn">👍</button>
                            <button class="action-btn">👎</button>
                            <button class="action-btn">↻</button>
                            <button class="action-btn">⋯</button>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Welcome screen
        if st.session_state.current_session == "Greeting exchange":
            st.markdown("""
            <div class="welcome-container">
                <div class="welcome-title">Hi</div>
                <div style="margin: 20px 0;">
                    <div style="color: white; font-size: 18px;">Hey Gaurav! 👋</div>
                    <div style="color: white; font-size: 18px; margin-top: 8px;">How are you doing today?</div>
                    <div class="action-buttons" style="margin-top: 16px;">
                        <button class="action-btn">📋</button>
                        <button class="action-btn">👍</button>
                        <button class="action-btn">👎</button>
                        <button class="action-btn">↻</button>
                        <button class="action-btn">⋯</button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="welcome-container">
                <div class="welcome-title">What can I help with?</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Memory warning
    st.markdown("""
    <div style="background-color: #2d2d2d; padding: 12px; margin: 20px; border-radius: 8px; text-align: center;">
        <strong>ChatGPT's out of space for saved memories</strong><br>
        <span style="color: #b3b3b3;">New memories won't be added until you make space. </span>
        <a href="#" style="color: #10a37f;">Learn more</a>
        <button style="background: white; color: black; border: none; padding: 6px 16px; border-radius: 6px; margin-left: 12px;">Manage</button>
        <button style="background: transparent; border: none; color: #b3b3b3; margin-left: 8px;">✕</button>
    </div>
    """, unsafe_allow_html=True)

def render_input_area():
    """Render the input area at the bottom"""
    # API Key input (hidden but functional)
    if not st.session_state.api_key:
        with st.expander("⚙️ API Configuration"):
            api_key = st.text_input("Enter your API Key", type="password", key="api_key_input")
            if api_key:
                st.session_state.api_key = api_key
                st.success("API Key configured!")
                st.rerun()
    
    # Initialize API client
    api_client = ChatGPTAPI()
    
    # Input form
    with st.form("chat_input_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([1, 8, 1])
        
        with col1:
            st.markdown("")  # Empty space
        
        with col2:
            user_input = st.text_input(
                "",
                placeholder="Ask anything",
                label_visibility="collapsed",
                key="message_input"
            )
        
        with col3:
            col_a, col_b = st.columns([1, 1])
            with col_a:
                if st.form_submit_button("🎤", help="Voice input"):
                    st.info("Voice input not implemented")
            with col_b:
                send_button = st.form_submit_button("📎", help="Attach files")
    
    # Handle message submission
    if user_input and st.session_state.api_key:
        # Add user message
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": timestamp
        }
        
        # Update current session
        if st.session_state.current_session not in st.session_state.chat_sessions:
            st.session_state.chat_sessions[st.session_state.current_session] = []
        
        st.session_state.chat_sessions[st.session_state.current_session].append(user_message)
        
        # Get AI response
        with st.spinner("ChatGPT is thinking..."):
            response = api_client.generate_response(user_input, st.session_state.api_key)
            
            if response["success"]:
                ai_content = response["data"]["response"]
                ai_message = {
                    "role": "assistant",
                    "content": ai_content,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.chat_sessions[st.session_state.current_session].append(ai_message)
            else:
                error_message = {
                    "role": "assistant",
                    "content": f"Error: {response['error']}",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
                st.session_state.chat_sessions[st.session_state.current_session].append(error_message)
        
        st.rerun()
    
    # Footer disclaimer
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 12px; padding: 12px;">
        ChatGPT can make mistakes. Check important info.
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application"""
    render_sidebar()
    
    # Main content area
    with st.container():
        render_main_content()
        render_input_area()

if __name__ == "__main__":
    main()