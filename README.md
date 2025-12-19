# Prompt Manager

An educational AI collaboration playground with chat interface, prompt library, and local LLM support. Built test-first using domain-driven design principles.

## Vision

Prompt Manager is designed to help you:
- **Learn to prompt effectively** through experimentation and prompt reuse
- **Chat with local AI models** (currently Gemma3 via Ollama)
- **Manage and share prompts** with an organized library
- **Explore different AI interfaces** as we build new interaction patterns

This is both a learning tool for AI collaboration and a useful chat client, with an emphasis on clean architecture and extensibility.

## Features

### Current (v1.0 - In Development)
- **Chat Interface**: Real-time streaming chat with Ember (Gemma3:4b)
- **Conversation Persistence**: Save and resume chat sessions
- **Prompt Library**: Organize, search, and reuse prompts
- **Local LLM Support**: Run entirely offline with Ollama
- **Domain-Driven Design**: Clean, testable, extensible architecture
- **Test Coverage**: Comprehensive test suite (26+ tests and growing)

### Legacy Features (Available in Advanced Mode)
- Template Builder with cascading dependencies
- Prompt Builder with reusable components
- Category organization
- Search functionality

## Prerequisites

- **Python 3.11+**
- **Ollama** (for local LLM support)
- **Git** (for cloning the repository)

### Installing Ollama

Ollama is required to run local AI models:

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or download from https://ollama.com/download
```

After installing Ollama, pull the Gemma3 model:

```bash
ollama pull gemma3:4b
```

Verify it's working:

```bash
ollama list  # Should show gemma3:4b
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ThePassionateProgrammer/prompt-manager.git
cd prompt-manager
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Ollama Python client
- pytest (testing framework)
- Other utilities

### 4. Verify Installation

Run the test suite to ensure everything is working:

```bash
./venv/bin/python -m pytest tests/ -v
```

You should see all tests passing:
```
==================== 42 passed in 0.17s ====================
```

## Running the Application

### Current Development Status

**Phases 1 & 2 Complete (42 tests passing)**:
- ✅ Domain models (ChatMessage, Conversation)
- ✅ Ollama integration with streaming support
- ⏳ Web interface coming in Phase 5+

To test the current implementation:

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Ensure Ollama is running
ollama list  # Should show gemma3:4b

# Run all tests to see domain models and Ollama provider in action
./venv/bin/python -m pytest tests/ -v

# Run specific domain tests
./venv/bin/python -m pytest tests/test_conversation.py -v

# Run Ollama integration tests (uses mocks, no server needed)
./venv/bin/python -m pytest tests/test_ollama_provider.py -v
```

### Option 1: Chat Interface (Coming in Phase 5+)

```bash
# Activate virtual environment
source venv/bin/activate

# Start the unified server (not yet implemented)
python -m src.prompt_manager.app

# Open browser to http://localhost:8000/chat
```

### Option 2: Legacy Web Interface

```bash
# Activate virtual environment
source venv/bin/activate

# Start the legacy server
python enhanced_simple_server.py

# Open browser to http://localhost:8000
```

### Option 3: CLI (Prompt Library Only)

```bash
# Activate virtual environment
source venv/bin/activate

# List all prompts
python prompt_manager.py list

# Add a prompt
python prompt_manager.py add "My Prompt" --text "Your prompt text here"

# Search prompts
python prompt_manager.py search "keyword"
```

## Development

### Running Tests

```bash
# Run all tests
./venv/bin/python -m pytest tests/ -v

# Run specific test file
./venv/bin/python -m pytest tests/test_chat_message.py -v

# Run with coverage
./venv/bin/python -m pytest tests/ --cov=src/prompt_manager --cov-report=html
```

### Project Structure

```
prompt-manager/
├── src/prompt_manager/
│   ├── domain/                   # Pure domain models (NEW)
│   │   ├── chat_message.py       # Message entity
│   │   └── conversation.py       # Conversation aggregate
│   ├── business/                 # Business logic services
│   │   ├── llm_provider.py       # LLM abstraction (OpenAI, Ollama)
│   │   ├── chat_service.py       # Chat orchestration (COMING)
│   │   ├── conversation_storage.py  # Persistence (COMING)
│   │   └── [other services]
│   ├── prompt.py                 # Prompt entity (legacy)
│   ├── prompt_manager.py         # Prompt CRUD (legacy)
│   └── storage.py                # JSON persistence
├── tests/
│   ├── test_chat_message.py     # Domain tests (NEW)
│   ├── test_conversation.py     # Domain tests (NEW)
│   └── [other tests]
├── requirements.txt              # Python dependencies
├── CLAUDE.md                     # Development partnership charter
└── README.md
```

### Architecture Principles

We follow **Clean Architecture** and **Domain-Driven Design**:

1. **Domain Layer** (pure business logic, zero dependencies)
   - ChatMessage, Conversation entities
   - Business rules and validation
   - Framework-agnostic

2. **Business Layer** (application services)
   - Orchestrates domain objects
   - Handles persistence
   - LLM provider abstraction

3. **Presentation Layer** (Flask web/API)
   - Routes and controllers
   - JSON serialization
   - User interface

4. **Test-First Development**
   - Write tests before implementation
   - High test coverage (currently 26 tests)
   - Fast feedback loop

## Configuration

### Ollama Settings

By default, the app connects to Ollama at `http://localhost:11434` and uses the `gemma3:4b` model (Ember).

To use a different model:

```python
# In your code or configuration
chat_service = ChatService(
    llm_provider=OllamaProvider(
        base_url="http://localhost:11434",
        default_model="gemma3:12b"  # or any other model
    )
)
```

### Storage

Data is stored in JSON files in the project directory:
- `prompts.json` - Prompt library
- `conversations.json` - Chat conversations (COMING)
- `templates.json` - Template definitions (legacy)

These files are git-ignored and safe to delete for a fresh start.

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

## Roadmap

### Phase 1: Domain Models ✅
- [x] ChatMessage entity
- [x] Conversation aggregate root
- [x] Comprehensive test coverage (26 tests)

### Phase 2: Ollama Integration ✅
- [x] OllamaProvider implementation
- [x] Streaming response support
- [x] Health checks and error handling
- [x] Complete test coverage (16 tests)

### Phase 3: Persistence
- [ ] ConversationStorage
- [ ] Save/load conversations
- [ ] Conversation listing

### Phase 4: Chat Service
- [ ] ChatService orchestration
- [ ] Message handling
- [ ] LLM integration

### Phase 5+: Web Interface
- [ ] Streaming chat UI
- [ ] Conversation management
- [ ] Prompt library integration
- [ ] Advanced features exploration

### Future Vision
- Enhanced context management
- Multiple interface experiments
- RAG-style knowledge integration
- Prompt sharing and collaboration

## License

This project is open source and available for educational use.

## Acknowledgments

Built with test-first, domain-driven principles as a collaboration between:
- **David** - Vision, architecture, domain expertise
- **Claude Sonnet 4.5** - Implementation, testing, documentation

*Generated with [Claude Code](https://claude.com/claude-code)*
