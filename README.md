# Prompt Manager V1.0

A production-ready prompt management system with AI chat capabilities, template building, and domain-driven architecture. Built as an educational AI collaboration playground with chat interface, prompt library, and local LLM support using test-first development and domain-driven design principles.

## Vision

Prompt Manager is designed to help you:
- **Learn to prompt effectively** through experimentation and prompt reuse
- **Chat with AI models** (OpenAI, Anthropic, Google, and local models via Ollama)
- **Manage and share prompts** with an organized library
- **Explore different AI interfaces** as we build new interaction patterns

[![Tests](https://img.shields.io/badge/tests-447%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage->90%25-brightgreen)](#)
[![Python](https://img.shields.io/badge/python-3.11-blue)](#)
[![Architecture](https://img.shields.io/badge/architecture-clean-blue)](#)

**V1.0 Highlights:**
- Clean Architecture (Routes -> Business -> Domain)
- Domain-Driven Design with pure domain models
- 447 comprehensive tests (all passing)
- Encrypted API key storage
- Production-ready code quality
- Multi-LLM provider support (OpenAI, Anthropic, Google, Ollama)
- Real-time SSE streaming chat
- Conversation persistence

## Features

### **AI Chat Interface**
- **Multi-Provider Support**: OpenAI, Anthropic (Claude), Google (Gemini), and Ollama (local)
- **Chat History**: Full conversation context maintained automatically
- **Token Tracking**: Real-time context usage with visual indicators
- **Auto-Trimming**: Intelligent message trimming to prevent context overflow
- **Conversation Persistence**: Save and reload conversations
- **Customizable System Prompts**: Define AI behavior and personality
- **Real-time SSE Streaming**: Stream responses as they arrive from the LLM

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

## Prerequisites

- **Python 3.11+**
- **Ollama** (optional, for local LLM support)
- **Git** (for cloning the repository)

### Installing Ollama (Optional)

Ollama enables running AI models locally without API keys:

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com/download
```

After installing Ollama, pull a model:

```bash
ollama pull gemma3:4b
ollama list  # Verify it's available
```

## Quick Start

### Easy Installation (Recommended)

```bash
git clone <repository-url>
cd prompt-manager
./setup.sh
```

The setup script automatically:
- Creates a Python virtual environment
- Installs all dependencies
- Checks for Ollama (optional, for local AI models)

### Manual Installation

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

```bash
source venv/bin/activate
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
2. Add your API key for one of the supported providers:
   - **OpenAI**: ChatGPT models
   - **Anthropic**: Claude models
   - **Google**: Gemini models
3. Or use **Ollama** for local models (no API key needed)
4. (Optional) Customize your system prompt
5. Start chatting at http://localhost:8000/chat

### Local AI with Ollama (Optional)

Run AI models locally without API keys:

1. **Install Ollama**: https://ollama.ai
2. **Start Ollama**: `ollama serve`
3. **Download a model**: `ollama pull gemma3:4b` (lightweight, ~3GB)
4. The app automatically detects Ollama and shows local models

## Usage Guide

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

## Data Storage

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

## Testing

The project uses pytest with comprehensive test coverage:

**Run all tests:**
```bash
# Run all tests
./venv/bin/python -m pytest tests/ -v

# Run specific test file
./venv/bin/python -m pytest tests/test_chat_message.py -v

# Run with coverage
./venv/bin/python -m pytest tests/ --cov=src/prompt_manager --cov-report=html
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

## Architecture

**V1.0 features a clean, three-layer architecture:**

```
+-------------------------------------+
|     Routes (HTTP Layer)             |
|   - Thin orchestration              |
|   - No business logic               |
+----------------+--------------------+
                 | uses
                 v
+-------------------------------------+
|  Business Layer (Services)          |
|   - LLMProviderManager              |
|   - ConversationManager             |
|   - TokenManager                    |
+----------------+--------------------+
                 | uses
                 v
+-------------------------------------+
|   Domain Layer (Pure Logic)         |
|   - ConversationBuilder             |
|   - ContextWindowManager            |
|   - LinkageManager                  |
|   - Conversation (aggregate root)   |
|   - ChatMessage (entity)            |
|   Zero dependencies                 |
+-------------------------------------+
```

### **Project Structure**
```
prompt-manager/
├── prompt_manager_app.py          # Main application entry point
├── enhanced_simple_server.py      # Alternative server with chat routes
├── routes/
│   ├── dashboard.py               # Chat & settings routes
│   ├── linkage.py                 # Template builder routes
│   └── static.py                  # Static file serving
├── src/prompt_manager/
│   ├── domain/                    # Pure business logic
│   │   ├── chat_message.py        # Message entity
│   │   ├── conversation.py        # Conversation aggregate + builders
│   │   └── linkage_manager.py     # Template linkage rules
│   ├── business/                  # Business services
│   │   ├── llm_provider_manager.py
│   │   ├── llm_provider.py        # LLM abstraction (OpenAI, Ollama)
│   │   ├── chat_service.py        # Chat orchestration
│   │   ├── conversation_manager.py
│   │   ├── conversation_storage.py
│   │   ├── token_manager.py
│   │   ├── key_loader.py
│   │   └── ...
│   ├── templates/                 # Jinja2 HTML templates
│   │   ├── chat_dashboard.html
│   │   ├── chat.html
│   │   ├── settings.html
│   │   └── ...
│   ├── static/                    # CSS, JS, images
│   ├── prompt_manager.py          # Core prompt management
│   └── template_service.py        # Template persistence
└── tests/                         # Comprehensive test suite
    ├── test_llm_provider_manager.py
    ├── test_conversation_storage.py
    ├── test_chat_context_management.py
    ├── test_ollama_provider.py
    └── ...
```

### **Clean Architecture Principles**
- **Domain Layer**: Pure business logic, zero dependencies
- **Business Layer**: Services orchestrating domain and infrastructure
- **Routes**: Thin HTTP handlers, dependency injection pattern
- **Templates**: Presentation only, no logic
- **Tests**: 447 tests covering all layers

### **Domain Models (Pure Business Logic)**
- **ConversationBuilder**: Message array construction rules
- **ContextWindowManager**: Token trimming and context limits
- **LinkageManager**: Template variable linkage system
- **Conversation**: Aggregate root for chat conversations
- **ChatMessage**: Message entity

No Flask dependencies - Portable to CLI, desktop, or mobile apps!

## Roadmap

### **Version 1.0** - COMPLETE
- Multi-model chat interface
- Token tracking and auto-trimming
- Conversation persistence
- Secure API key storage (encrypted)
- System prompt customization
- Template builder with linkages
- Clean architecture refactoring
- Domain-driven design
- 447 comprehensive tests
- Dependency injection pattern
- Ollama integration with streaming support

### **Version 2.0** (Planned)
- Claude and Gemini integration
- Conversation history UI
- Export conversations (Markdown, PDF)
- Prompt library integration
- Usage analytics and cost tracking
- Multi-user support
- Enhanced context management
- RAG-style knowledge integration

## Documentation

### **V1.0 Documentation**
- **V1_FINAL_REPORT.md**: Complete V1.0 metrics and achievements
- **V1_COMPLETION_PLAN.md**: Refactoring strategy and execution
- **TESTING_GUIDE.md**: Comprehensive testing documentation
- **CLAUDE.md**: Development partnership charter

## Contributing

This project is built as an educational collaboration between David (human) and Claude (AI). We document our learnings and design decisions in:

- `CLAUDE.md` - Partnership charter and principles
- `knowledge-base/` - ADRs, spike reports, technical notes
- Git commit messages - Detailed context for each change

Feel free to:
- Report issues
- Suggest features
- Learn from the code
- Fork for your own experiments

## License

MIT License - See LICENSE file for details

## Acknowledgments

Built with test-first, domain-driven principles as a collaboration between:
- **David** - Vision, architecture, domain expertise
- **Claude** - Implementation, testing, documentation

*Generated with [Claude Code](https://claude.com/claude-code)*
