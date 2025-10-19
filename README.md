# Prompt Manager V1.0

A production-ready prompt management system with AI chat capabilities, template building, and domain-driven architecture.

[![Tests](https://img.shields.io/badge/tests-447%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage->90%25-brightgreen)](#)
[![Python](https://img.shields.io/badge/python-3.11-blue)](#)
[![Architecture](https://img.shields.io/badge/architecture-clean-blue)](#)

**V1.0 Highlights:**
- 🏗️ Clean Architecture (Routes → Business → Domain)
- 🎯 Domain-Driven Design with pure domain models
- ✅ 447 comprehensive tests (all passing)
- 🔒 Encrypted API key storage
- 🚀 Production-ready code quality

## 🌟 Features

### **AI Chat Interface**
- **Multi-Model Support**: GPT-4, GPT-4 Turbo, GPT-3.5, GPT-3.5-16K
- **Chat History**: Full conversation context maintained automatically
- **Token Tracking**: Real-time context usage with visual indicators
- **Auto-Trimming**: Intelligent message trimming to prevent context overflow
- **Conversation Persistence**: Save and reload conversations
- **Customizable System Prompts**: Define AI behavior and personality

### **Secure API Key Management**
- **Encrypted Storage**: API keys encrypted at rest using Fernet encryption
- **Multiple Providers**: Support for OpenAI, Claude, Gemini (extensible)
- **Test Connections**: Verify API keys before use
- **Local Storage**: Keys never leave your machine

### **Prompt Management**
- **GUID-based identification**: Unique IDs for reliable prompt tracking
- **JSON persistence**: Structured storage in JSON format
- **Search functionality**: Find prompts by name, content, or category
- **Category organization**: Organize prompts hierarchically
- **Template Builder**: Create dynamic prompt templates with variables

### **Template Builder**
- **Interactive UI**: Build complex prompt templates visually
- **Custom Combo Boxes**: Cascading dependencies between variables
- **Save & Load**: Persist templates for reuse
- **Linkage System**: Dynamic template variable resolution

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd prompt-manager
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

**Start the web server:**
```bash
python prompt_manager_app.py
```

The application will:
- Automatically find an available port (default: 8000)
- Open your browser to the web interface
- Display available features and URLs

**Access the application:**
- **Chat Interface**: http://localhost:8000/chat
- **Settings**: http://localhost:8000/settings
- **Template Builder**: http://localhost:8000/template-builder
- **Dashboard**: http://localhost:8000/dashboard

### First-Time Setup

1. Navigate to **Settings** (http://localhost:8000/settings)
2. Add your OpenAI API key
3. (Optional) Customize your system prompt
4. Test your connection
5. Start chatting at http://localhost:8000/chat

## 💬 Usage Guide

### Chat Interface

The chat interface provides a full-featured AI conversation experience:

**Basic Chat:**
1. Type your message in the input box
2. Press Enter or click Send
3. View AI response with context awareness

**Advanced Features:**
- **Model Selection**: Choose between GPT-4, GPT-3.5, and variants
- **Temperature Control**: Adjust creativity (0.0 = focused, 1.0 = creative)
- **Max Tokens**: Control response length
- **Token Tracking**: Visual bar shows context usage
- **Auto-Trim**: Automatically manages long conversations
- **Collapsible Controls**: Hide/show settings panel

**Token Management:**
- Green bar (0-50%): Plenty of context available
- Orange bar (50-80%): Moderate usage
- Red bar (80-100%): Approaching limit, auto-trim enabled

### Settings Management

**API Keys:**
- Add keys for OpenAI, Claude, Gemini
- Test connection before saving
- Keys encrypted with Fernet encryption
- Stored locally at `~/.prompt_manager/keys.enc`

**System Prompts:**
- Define AI personality and behavior
- Applies to all conversations
- Reset to default anytime
- Examples: "You are a coding expert", "You are a creative writer"

### Template Builder

Build dynamic prompt templates with variables:

1. **Create Template**: Define slots with `{{variable_name}}`
2. **Add Dropdowns**: Create custom combo boxes for each variable
3. **Define Options**: Add choices for each dropdown
4. **Set Dependencies**: Create cascading relationships
5. **Save Template**: Persist for reuse
6. **Generate Prompts**: Fill in variables to create final prompt

**Example Template:**
```
You are a {{role}} helping with {{task}} for a {{audience}} audience.
Use a {{tone}} tone and {{format}} format.
```

### Programmatic Usage

Use the business logic directly in your Python code:

```python
from src.prompt_manager.business.llm_provider_manager import LLMProviderManager
from src.prompt_manager.business.llm_provider import OpenAIProvider
from src.prompt_manager.business.conversation_manager import ConversationManager

# Set up LLM provider
provider_manager = LLMProviderManager()
provider_manager.add_provider('openai', OpenAIProvider(api_key='your-key'))
provider_manager.set_default_provider('openai')

# Generate response
response = provider_manager.generate(
    prompt="Hello, how are you?",
    model="gpt-3.5-turbo",
    temperature=0.7
)

# Manage conversations
conv_manager = ConversationManager()
conversation = {
    'messages': [
        {'role': 'user', 'content': 'Hello'},
        {'role': 'assistant', 'content': 'Hi there!'}
    ],
    'model': 'gpt-3.5-turbo'
}
saved = conv_manager.save_conversation(conversation)
```

## 📁 Data Storage

The application stores data locally in structured formats:

### **API Keys**
- Location: `~/.prompt_manager/keys.enc`
- Format: Encrypted binary (Fernet)
- Contains: Provider names and encrypted API keys

### **Conversations**
- Location: `conversations/conversations.json`
- Format: JSON
- Contains: Full conversation history with metadata

### **Templates**
- Location: `templates/templates.json`
- Format: JSON
- Contains: Saved prompt templates and linkages

### **Settings**
- Location: `settings/user_settings.json` (planned)
- Format: JSON
- Contains: User preferences, default models, system prompts

## 🧪 Testing

The project uses pytest with comprehensive test coverage:

**Run all tests:**
```bash
python -m pytest tests/ -v
```

**Run specific test suites:**
```bash
# Business logic tests
python -m pytest tests/test_llm_provider_manager.py -v
python -m pytest tests/test_conversation_storage.py -v
python -m pytest tests/test_chat_context_management.py -v

# Integration tests
python -m pytest tests/test_chat_routes.py -v
python -m pytest tests/test_api.py -v
```

**Test coverage:**
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

See `TESTING_GUIDE.md` for detailed testing documentation.

## 🏗️ Architecture

**V1.0 features a clean, three-layer architecture:**

```
┌─────────────────────────────────────┐
│     Routes (HTTP Layer)             │
│   • Thin orchestration              │
│   • No business logic               │
└──────────────┬──────────────────────┘
               │ uses
               ▼
┌─────────────────────────────────────┐
│  Business Layer (Services)          │
│   • LLMProviderManager              │
│   • ConversationManager             │
│   • TokenManager                    │
└──────────────┬──────────────────────┘
               │ uses
               ▼
┌─────────────────────────────────────┐
│   Domain Layer (Pure Logic)         │
│   • ConversationBuilder             │
│   • ContextWindowManager            │
│   • LinkageManager                  │
│   ✅ Zero dependencies               │
└─────────────────────────────────────┘
```

### **Project Structure**
```
prompt-manager/
├── prompt_manager_app.py          # Main application entry point
├── routes/
│   ├── dashboard.py               # Chat & settings routes
│   ├── linkage.py                 # Template builder routes
│   └── static.py                  # Static file serving
├── src/prompt_manager/
│   ├── domain/                    # Pure business logic (NEW in V1.0)
│   │   ├── conversation.py        # ConversationBuilder & ContextWindowManager
│   │   └── linkage_manager.py    # Template linkage rules
│   ├── business/                  # Business services
│   │   ├── llm_provider_manager.py
│   │   ├── llm_provider.py
│   │   ├── conversation_manager.py
│   │   ├── token_manager.py
│   │   ├── key_loader.py
│   │   └── ...
│   ├── templates/                 # Jinja2 HTML templates
│   │   ├── chat_dashboard.html
│   │   ├── settings.html
│   │   └── ...
│   ├── static/                    # CSS, JS, images
│   ├── prompt_manager.py          # Core prompt management
│   └── template_service.py        # Template persistence
└── tests/                         # Comprehensive test suite
    ├── test_llm_provider_manager.py
    ├── test_conversation_storage.py
    ├── test_chat_context_management.py
    └── ...
```

### **Clean Architecture Principles**
- **Domain Layer**: Pure business logic, zero dependencies (NEW in V1.0)
- **Business Layer**: Services orchestrating domain and infrastructure
- **Routes**: Thin HTTP handlers, dependency injection pattern
- **Templates**: Presentation only, no logic
- **Tests**: 447 tests covering all layers, 16 pure domain tests

### **Domain Models (Pure Business Logic)**
- **ConversationBuilder**: Message array construction rules
- **ContextWindowManager**: Token trimming and context limits
- **LinkageManager**: Template variable linkage system

✅ **No Flask dependencies** - Portable to CLI, desktop, or mobile apps!

## 🚀 Roadmap

### **Version 1.0** ✅ COMPLETE
- ✅ Multi-model chat interface
- ✅ Token tracking and auto-trimming
- ✅ Conversation persistence
- ✅ Secure API key storage (encrypted)
- ✅ System prompt customization
- ✅ Template builder with linkages
- ✅ Clean architecture refactoring
- ✅ Domain-driven design
- ✅ 447 comprehensive tests
- ✅ Dependency injection pattern

### **Version 2.0** (Planned)
- 🔮 Claude and Gemini integration
- 🔮 Conversation history UI
- 🔮 Export conversations (Markdown, PDF)
- 🔮 Prompt library integration
- 🔮 Usage analytics and cost tracking
- 🔮 Multi-user support

## 📝 Documentation

### **V1.0 Documentation**
- **V1_FINAL_REPORT.md**: Complete V1.0 metrics and achievements
- **V1_COMPLETION_PLAN.md**: Refactoring strategy and execution
- **EPISODE_8A_NARRATION_SCRIPT.md**: Safe refactoring guide
- **EPISODE_9_DOMAIN_MODELS_SCRIPT.md**: Domain extraction guide
- **.cursorrules**: AI collaboration partnership charter

### **Technical Documentation**
- **TESTING_GUIDE.md**: Comprehensive testing documentation
- **ARCHITECTURE.md**: System design and patterns (coming soon)
- **CHAT_IMPLEMENTATION.md**: Chat feature technical details

### **Video Series**
- 📹 **Episode 8A**: Safe Refactoring (Extract Method, Dependency Injection)
- 📹 **Episode 9**: Domain Models (What they are & why they matter)

## 🤝 Contributing

This is a learning project built with AI pair programming. Contributions welcome!

## 📄 License

MIT License - See LICENSE file for details 