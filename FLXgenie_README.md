# 🧠 FLXgenie - Your Intelligent AI Assistant

FLXgenie is a modern, Google Gemini-inspired AI assistant interface built with Streamlit. It provides a sleek, user-friendly frontend for interacting with your AI models through a FastAPI backend.

## ✨ Features

### 🎨 **Beautiful Interface**
- Google Gemini-inspired design
- Modern, responsive UI with custom CSS styling
- Dark/light theme compatibility
- Gradient backgrounds and smooth animations

### 💬 **Advanced Chat System**
- Multi-session chat management
- Real-time conversation history
- Message timestamps
- Export chat history to JSON
- Quick prompt suggestions

### ⚙️ **Powerful Configuration**
- Multiple AI model support (Mistral, Llama2, CodeLlama, TinyLlama)
- Adjustable temperature and token limits
- API key management
- Session persistence

### 📊 **Analytics & Insights**
- Conversation analytics
- Message statistics
- Response time tracking
- Usage metrics

### 🚀 **Quick Actions**
- Pre-defined prompt templates
- One-click chat clearing
- Export functionality
- Session switching

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- FastAPI backend running
- Required Python packages (see requirements.txt)

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API key:**
   Create a `.env` file with your API key:
   ```
   API_KEY=your_api_key_here
   ```

3. **Launch FLXgenie:**
   ```bash
   # Option 1: Use the launch script (recommended)
   ./launch_flxgenie.sh
   
   # Option 2: Manual start
   # Terminal 1: Start API backend
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   
   # Terminal 2: Start frontend
   streamlit run flxgenie_frontend.py --server.port 8501
   ```

4. **Access the application:**
   - Frontend: http://localhost:8501
   - API Documentation: http://localhost:8000/docs

## 🎯 Usage Guide

### Getting Started
1. **Configure API Key**: Enter your API key in the sidebar
2. **Select Model**: Choose your preferred AI model
3. **Adjust Settings**: Set temperature and token limits
4. **Start Chatting**: Type your message and click Send!

### Advanced Features

#### **Multi-Session Management**
- Create new chat sessions for different topics
- Switch between sessions seamlessly
- Maintain separate conversation histories

#### **Model Configuration**
- **Temperature**: Controls creativity (0.0 = focused, 1.0 = creative)
- **Max Tokens**: Limits response length
- **Model Selection**: Choose from available models

#### **Quick Prompts**
Use pre-defined prompts for common tasks:
- Code explanation and debugging
- Creative writing assistance
- Technical explanations
- Business strategy help

#### **Export & Analytics**
- Download chat history as JSON
- View conversation statistics
- Track usage patterns

## 🔧 Configuration Options

### Sidebar Settings
- **API Configuration**: Secure API key input
- **Chat Sessions**: Create, switch, and manage conversations
- **Model Settings**: Fine-tune AI behavior
- **Statistics**: View usage metrics
- **Quick Actions**: Fast access to common tasks

### Environment Variables
```bash
API_KEY=your_api_key_here          # Required: Your API access key
STREAMLIT_SERVER_PORT=8501         # Optional: Frontend port
FASTAPI_SERVER_PORT=8000          # Optional: Backend port
```

## 🎨 UI Components

### **Chat Interface**
- **User Messages**: Right-aligned with blue accent
- **AI Responses**: Left-aligned with red accent
- **Timestamps**: Display message timing
- **Loading States**: Visual feedback during processing

### **Sidebar Navigation**
- **Branding**: FLXgenie logo and tagline
- **Configuration**: All settings in one place
- **Quick Access**: Instant actions and prompts
- **Statistics**: Real-time usage data

### **Feature Cards**
- **Fast Responses**: Highlighting speed
- **Smart AI**: Emphasizing intelligence
- **Multi-Session**: Showcasing flexibility
- **Customizable**: Promoting personalization

## 🚀 API Integration

FLXgenie integrates seamlessly with your FastAPI backend:

```python
# API Endpoint: POST /generate
# Headers: X-API-Key
# Parameters: prompt (string)
# Response: {"response": "AI generated text"}
```

### Error Handling
- Connection timeouts
- Invalid API keys
- Server errors
- User-friendly error messages

## 📱 Responsive Design

FLXgenie works perfectly on:
- **Desktop**: Full-featured experience
- **Tablet**: Optimized layout
- **Mobile**: Touch-friendly interface

## 🔒 Security Features

- **API Key Protection**: Secure input handling
- **Session Isolation**: Separate user contexts
- **Data Privacy**: Local session storage
- **Secure Communication**: HTTPS support

## 🎭 Customization

### **Styling**
- Custom CSS for modern appearance
- Gradient backgrounds
- Smooth transitions
- Brand colors and fonts

### **Functionality**
- Modular component design
- Easy feature additions
- Configurable behavior
- Extensible architecture

## 📈 Performance

- **Fast Loading**: Optimized Streamlit components
- **Efficient Updates**: Smart state management
- **Memory Usage**: Minimal resource consumption
- **Scalability**: Handles multiple sessions

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Check if FastAPI backend is running
   - Verify API key configuration
   - Test endpoint: http://localhost:8000/docs

2. **Streamlit Won't Start**
   - Install required dependencies
   - Check port availability (8501)
   - Update Streamlit version

3. **No AI Response**
   - Verify API key validity
   - Check model availability
   - Review server logs

### Debug Mode
Enable debug logging by setting:
```bash
export STREAMLIT_LOGGER_LEVEL=debug
```

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Streamlit**: For the amazing web framework
- **FastAPI**: For the robust backend foundation
- **Google Gemini**: For design inspiration
- **Open Source Community**: For continuous support

---

**Built with ❤️ by the FLXgenie Team**

*Transform your AI interactions with FLXgenie - where intelligence meets elegance.*