# Prompt Studio - Program Statistics

## Current Status

**Test Suite**: 603 passing, 133 skipped | **Branch**: main | **Commits**: 233

Prompt Studio is a multi-provider LLM chat application with prompt management,
voice interaction, and local model browsing. Built with Flask, domain-driven
design, and test-first methodology.

---

## Architecture

| Layer | Files | Lines | Purpose |
|-------|------:|------:|---------|
| Domain | 9 | 1,394 | Pure business logic, zero dependencies |
| Business | 19 | 2,669 | Services, providers, orchestration |
| Routes | 6 | 2,148 | Flask blueprints, thin HTTP layer |
| Templates | 18 | 9,153 | Jinja2 HTML pages |
| JavaScript | 7 | 3,451 | Client-side UI logic |
| CSS | 4 | 729 | Studio Vibe dark theme |
| Tests | 59 | 11,493 | Unit + integration tests |
| App entry | 1 | 157 | Flask app factory |

**Total production code**: ~17,544 lines across 64 files
**Total test code**: 11,493 lines across 59 files

---

## LLM Providers

| Provider | Type | Models | Status |
|----------|------|--------|--------|
| Ollama | Local | 17 catalog models | Full support + model browser |
| OpenAI | Cloud API | 4 models (GPT-4, GPT-3.5) | Full support |
| Anthropic | Cloud API | 5 models (Claude 4, 3.5) | Full support |
| Google | Cloud API | 4 models (Gemini 2.x) | Full support |

---

## Domain Models

| Model | File | Purpose |
|-------|------|---------|
| ChatMessage | chat_message.py | Message entity with role/content/timestamp |
| ChatSession | chat_session.py | Session aggregate for chat interactions |
| Conversation | conversation.py | Conversation aggregate with auto-titling |
| ConversationBuilder | conversation.py | Builds LLM message arrays |
| ContextWindowManager | conversation.py | Token limit management |
| ConversationMode | conversation_mode.py | Chat mode state (creative, precise, etc.) |
| LinkageManager | linkage_manager.py | Template linkage persistence |
| ModelCatalog | model_catalog.py | Provider model catalogs with enrichment |
| OllamaModel | ollama_model.py | Local model with name:tag parsing |
| VoiceInteractionManager | voice_interaction.py | Voice input/output state |

---

## Business Services

| Service | Purpose |
|---------|---------|
| AnthropicProvider | Claude API integration |
| ChatService | Chat orchestration |
| ConversationManager | Conversation CRUD |
| ConversationStorage | JSON file persistence |
| CustomComboBoxIntegration | Template combo box logic |
| FeatureFlags | Feature toggle management |
| GoogleProvider | Gemini API integration |
| KeyLoader | Secure API key loading |
| LLMProvider / OpenAIProvider | OpenAI API integration |
| LLMProviderManager | Multi-provider management |
| OllamaDiscovery | Local model list/pull/delete |
| OllamaProvider | Ollama API integration + streaming |
| PromptBuilder | Prompt template assembly |
| PromptValidator | Input validation |
| ProviderFactory | Provider instantiation |
| SearchService | Prompt search and filtering |
| TokenManager | Context window token tracking |
| UserSettingsManager | User preferences persistence |

---

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Chat | / | Main chat interface with SSE streaming |
| Chat Dashboard | /chat | Multi-provider chat dashboard |
| Model Browser | /models | Ollama model catalog with filtering |
| Settings | /settings | API keys, system prompt, provider config |
| Prompts Library | /prompts | Prompt template management |
| Template Builder | /builder | Custom combo box template builder |
| Setup | /setup | First-run configuration |

---

## Key Features

- **Multi-provider chat** with OpenAI, Anthropic, Google, and Ollama
- **SSE streaming** for real-time response rendering
- **Model browser** with category/size filtering and install status
- **Secure API key management** with keychain integration
- **Voice interaction** (speech-to-text and text-to-speech)
- **Conversation history** with auto-titling
- **Prompt template system** with linkage persistence
- **Studio Vibe dark theme** across all pages
- **Context window management** with automatic trimming
