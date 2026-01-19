# Prompt Manager - Architecture Walkthrough

*A comprehensive guide to understanding the codebase*

---

## Overview

Prompt Manager is a voice-enabled AI chat application built with Flask (Python) and vanilla JavaScript. It supports multiple LLM providers (OpenAI, Anthropic, Ollama) and features a sophisticated hands-free conversation mode.

**Key Capabilities:**
- Multi-provider LLM support (OpenAI, Claude, local Ollama models)
- Voice-first interaction with wake word detection ("Hey Amber")
- Template system with hierarchical linkages
- Prompt library with search and categorization
- Conversation persistence and context management
- Secure API key storage (encrypted with Fernet)

---

## Directory Structure

```
prompt-manager/
├── src/prompt_manager/           # Main application package
│   ├── business/                 # Business logic layer (14 modules)
│   ├── domain/                   # Pure domain models (7 modules)
│   ├── web/                      # Flask web layer
│   │   ├── routes/               # HTTP route handlers
│   │   └── services/             # Service layer
│   ├── templates/                # Jinja2 HTML templates (17 files)
│   ├── static/                   # CSS, JS, images
│   │   └── js/modules/           # Voice feature modules (13 files)
│   └── data/                     # Static data files
│
├── routes/                       # Legacy route handlers
├── tests/                        # Test suite
│   ├── js/                       # JavaScript tests (Jest)
│   └── *.py                      # Python tests (pytest)
│
├── settings/                     # User settings
│   └── user_settings.json        # Runtime configuration
│
├── prompt_manager_app.py         # Main entry point
└── api_server.py                 # Standalone API server
```

---

## Architecture Layers

The application follows a **Clean Architecture** pattern with clear separation:

```
┌─────────────────────────────────────────────────────┐
│                    Presentation                      │
│   (routes/, templates/, static/js/)                  │
├─────────────────────────────────────────────────────┤
│                   Application                        │
│   (web/services/, business/)                         │
├─────────────────────────────────────────────────────┤
│                     Domain                           │
│   (domain/ - pure Python, no dependencies)           │
├─────────────────────────────────────────────────────┤
│                  Infrastructure                      │
│   (storage.py, key_loader.py, providers)             │
└─────────────────────────────────────────────────────┘
```

### Layer Responsibilities

1. **Presentation Layer** - HTTP handling, HTML rendering, user interface
2. **Application Layer** - Request orchestration, business flow coordination
3. **Domain Layer** - Core business logic, pure functions, no framework dependencies
4. **Infrastructure Layer** - External services, persistence, API clients

---

## Backend Components

### Entry Points

| File | Port | Purpose |
|------|------|---------|
| `prompt_manager_app.py` | 8000 | Full web application |
| `api_server.py` | 5002 | REST API only |

### Business Logic (`src/prompt_manager/business/`)

| Module | Responsibility |
|--------|----------------|
| `llm_provider.py` | Abstract base for LLM providers |
| `llm_provider_manager.py` | Provider registration & switching |
| `ollama_provider.py` | Local Ollama model support |
| `chat_service.py` | Chat conversation orchestration |
| `conversation_manager.py` | Conversation persistence |
| `token_manager.py` | Token counting & context trimming |
| `key_loader.py` | Encrypted API key storage |
| `search_service.py` | Full-text search |
| `user_settings_manager.py` | User preferences |

### Domain Models (`src/prompt_manager/domain/`)

Pure Python classes with **zero framework dependencies**:

| Module | Key Classes | Purpose |
|--------|-------------|---------|
| `conversation.py` | `ConversationBuilder`, `ContextWindowManager` | Message ordering, context limits |
| `linkage_manager.py` | `LinkageManager`, `ComboBoxState` | Hierarchical template dependencies |
| `model_catalog.py` | `ModelCatalog` | Available LLM model definitions |
| `ollama_model.py` | `OllamaModel` | Local model representation |

### Key Design Patterns

**Provider Pattern** - Supports multiple LLM backends:
```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str: ...

class OpenAIProvider(LLMProvider): ...
class OllamaProvider(LLMProvider): ...
```

**Repository Pattern** - Data persistence:
```python
class StorageManager:
    def save_prompt(self, prompt: Prompt) -> None: ...
    def load_prompts(self) -> List[Prompt]: ...
```

---

## Frontend Components

### HTML Templates (`src/prompt_manager/templates/`)

| Template | Purpose |
|----------|---------|
| `chat_dashboard.html` | Main chat interface (32KB) |
| `settings.html` | API keys & configuration |
| `prompts_library.html` | Prompt management |
| `template_builder.html` | Template creation |

### JavaScript Modules (`src/prompt_manager/static/js/modules/`)

The voice system is organized into **13 focused modules**:

#### State Management
- `conversation_mode.js` - State machine (IDLE → WAKE_LISTENING → LISTENING → SENDING → PLAYING)
- `config.js` - Runtime configuration loader

#### Voice Input
- `voice_interaction.js` - Main orchestrator (speech recognition, synthesis)
- `silence_detector.js` - Pure logic for detecting speech pauses
- `silence_checking_service.js` - Interval-based silence polling
- `wake_word_detector.js` - Wake/sleep word detection ("Hey Amber", "Sleep Amber")

#### Command Processing
- `transcript_processor.js` - Routes transcripts to appropriate handlers
- `command_detector.js` - Ember command system ("Ember, repeat that")
- `voice_command_detector.js` - Pause/resume commands

#### UI Feedback
- `conversation_state_indicator.js` - Visual state display
- `notifications.js` - Toast notifications
- `error_handler.js` - Error display

#### Configuration
- `voice_settings.js` - Voice settings panel

### State Machine

The conversation mode follows a clear state machine:

```
                    ┌──────────────┐
                    │    IDLE      │
                    └──────┬───────┘
                           │ activate()
                    ┌──────▼───────┐
        ┌───────────│WAKE_LISTENING│◄────────────┐
        │           └──────┬───────┘              │
        │                  │ wake word            │ sleep word
        │           ┌──────▼───────┐              │
        │     ┌─────│  LISTENING   │──────────────┘
        │     │     └──────┬───────┘
        │     │            │ silence timeout / send
        │     │     ┌──────▼───────┐
        │     │     │   SENDING    │
        │     │     └──────┬───────┘
        │     │            │ response received
        │     │     ┌──────▼───────┐
        │     └─────│   PLAYING    │
        │           └──────────────┘
        │                  │ playback complete
        │                  └─────────────────────►
        │
        │ deactivate()
        └──────────────────────────────────────────►
```

---

## Data Flow

### Chat Message Flow

```
User speaks
    │
    ▼
voice_interaction.js (Web Speech API)
    │
    ▼
transcript_processor.js (classify transcript)
    │
    ▼
conversation_mode.js (state transition)
    │
    ▼
chat_dashboard.js (send to backend)
    │
    ▼
/api/chat/send (Flask route)
    │
    ▼
chat_service.py (orchestration)
    │
    ▼
llm_provider.py (generate response)
    │
    ▼
Response flows back up
```

### Silence Detection Flow

```
Speech ends
    │
    ▼
silence_detector.onSpeechEnd()
    │
    ▼
silence_checking_service polls every 100ms
    │
    ▼
silence_detector.isSilent() returns true after 8 seconds
    │
    ▼
Auto-send triggered
```

---

## Configuration

### User Settings (`settings/user_settings.json`)

```json
{
  "default_provider": "ollama",
  "default_model": "gemma3:4b",
  "temperature": 1.0,
  "max_tokens": 3000,
  "hands_free": {
    "wake_words": ["hey amber", "hi amber", "amber"],
    "sleep_words": ["sleep amber", "goodbye amber"],
    "silence_timeout_seconds": 8
  }
}
```

### Environment Variables

- `OPENAI_API_KEY` - OpenAI API credential
- Flask runs on port 8000 by default

---

## Testing

### Python Tests (pytest)

```bash
pytest tests/                    # Run all tests
pytest tests/test_api.py         # Run specific file
pytest -v                        # Verbose output
```

**Key test files:**
- `test_chat_service.py` - Chat orchestration
- `test_llm_provider.py` - Provider abstraction
- `test_conversation.py` - Domain models
- `test_token_manager.py` - Token counting

### JavaScript Tests (Jest)

```bash
npm test                         # Run all JS tests
npm test -- --watch             # Watch mode
npm test -- silence_detector    # Run specific tests
```

**Key test files:**
- `silence_detector.test.js` - Silence detection logic
- `wake_word_detector.test.js` - Wake/sleep word matching
- `conversation_mode_state_machine.test.js` - State transitions
- `transcript_processor.test.js` - Transcript routing

### Test Coverage

- **Python**: 50+ test files covering routes, services, domain
- **JavaScript**: 14 test files with 200+ tests
- **Integration**: Full workflow tests for voice features

---

## Key Files Reference

### Most Important Files to Understand

1. **`voice_interaction.js`** (600 lines) - Heart of voice features
2. **`conversation_mode.js`** - State machine for conversation flow
3. **`chat_service.py`** - Backend chat orchestration
4. **`dashboard.py`** - Main API routes
5. **`chat_dashboard.html`** - Main UI template

### Files Changed in Hands-Free Implementation

- `voice_interaction.js` - Speech recognition handlers
- `silence_detector.js` - Pure domain logic
- `silence_checking_service.js` - Polling service
- `wake_word_detector.js` - Wake/sleep detection
- `transcript_processor.js` - Transcript routing
- `config.js` - Runtime configuration
- `conversation_mode.js` - State machine

---

## Development Workflow

### Running the Application

```bash
# Start the web application
python prompt_manager_app.py

# Or start API server only
python api_server.py

# Run tests
pytest tests/
npm test
```

### Adding a New Feature

1. **Domain first** - Create pure domain models in `domain/`
2. **Business logic** - Add orchestration in `business/`
3. **API routes** - Expose via `routes/` or `web/routes/`
4. **Frontend** - Update templates and JS modules
5. **Tests** - Add tests at each layer

### Code Quality Principles

From `.cursorrules`:
- **RED-GREEN-REFACTOR** - Write failing test first
- **Pure domain models** - No framework dependencies
- **Explicit dependencies** - Constructor injection
- **Small, focused functions** - Single responsibility
- **Comprehensive tests** - Test behavior, not implementation

---

## Future Enhancements

Planned features (from memory cards):
- Knowledge base / memory system for AI continuity
- Semantic search for prompts
- Multi-user support with per-user settings
- Enhanced voice command vocabulary
- Real-time collaboration features

---

*Document generated: January 2026*
*Version: 0.9.0-beta*
