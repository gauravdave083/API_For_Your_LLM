import streamlit as st
import requests
import json
from datetime import datetime
import os

# Basic page configuration
st.set_page_config(
    page_title="AI Chat",
    page_icon="💬",
    layout="centered"
)

# Simple, clean styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
    }
    
    .message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    
    .user-message {
        background-color: #e3f2fd;
        text-align: right;
    }
    
    .bot-message {
        background-color: #f5f5f5;
        text-align: left;
    }
    
    .input-area {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 1rem;
        border-top: 1px solid #ddd;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

def main():
    st.title("💬 AI Chat")
    
    # Display messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**AI:** {message['content']}")
    
    # Input
    user_input = st.text_input("Type your message:", key="input")
    
    if st.button("Send") and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Simple echo response (replace with actual API call)
        st.session_state.messages.append({"role": "assistant", "content": f"You said: {user_input}"})
        
        st.rerun()

if __name__ == "__main__":
    main()