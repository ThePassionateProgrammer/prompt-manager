# Episode 8: Refactoring to V1.0 - Comprehensive Plan

**Title:** "The Great Refactoring: From Working Code to Production Code"  
**Focus:** Test-first refactoring with domain-driven design principles  
**Approach:** Patterns-based teaching with before/after comparisons  
**Duration:** 15-20 minutes (split into 2 parts if needed)

---

## Executive Summary

**Central Theme:** *"Working code is step one. Production code requires refactoring."*

We'll transform our feature-complete but tech-debt-laden V1.0 into a clean, domain-driven architecture using:
- **Domain Layer** extraction (business rules separated from everything)
- **Test-First Development** (RED → GREEN → REFACTOR)
- **Single Responsibility Principle**
- **Separation of Concerns**
- **Hidden class extraction**

---

## Before Footage Checklist

### **1. Current Codebase State (5-10 minutes)**

Record these screens in order:

#### A. **Project Structure Overview**
```bash
# Terminal recording
tree -L 3 -I '__pycache__|*.pyc|venv'
```
**Show:** Current file organization, note how routes contain business logic

#### B. **Test Coverage Report**
```bash
# Terminal recording
pytest --cov=src --cov=routes --cov-report=term-missing
```
**Show:** Current coverage (~85%), identify gaps

#### C. **Key Problem Areas** (Screen recordings with commentary)

**File 1: `routes/dashboard.py`**
- Scroll through the file (line 1 to end)
- **Highlight:** Lines 14-42 (provider initialization - global state)
- **Highlight:** Lines 135-213 (send_message - 78 lines of business logic)
- **Commentary:** "Notice how HTTP handling and business logic are mixed"

**File 2: `src/prompt_manager/business/llm_provider_manager.py`**
- Show the entire file
- **Commentary:** "This is a manager, but it has no real domain logic"

**File 3: `src/prompt_manager/business/token_manager.py`**
- Show the entire file
- **Commentary:** "Good! This is closer to what we want—pure logic, no dependencies"

**File 4: `src/prompt_manager/prompt_manager.py`**
- Show the PromptManager class
- **Commentary:** "Mixed concerns: validation, storage, and business rules together"

#### D. **Running Application** (Screen recording)
- Start the server
- Show the dashboard working
- Send a chat message (show it works)
- Open Prompts Library (show it works)
- Open Template Builder (show it works)
- **Commentary:** "Everything works, but let's look at what it takes to maintain this..."

#### E. **Dependency Diagram** (Draw or show)
```
Current (BAD):
Routes → Business Logic → Storage
  ↓         ↓              ↓
  └─────────┴──────────────┘
         Everything mixed

Goal (GOOD):
Routes → Services → Domain ← Repositories
                      ↑
                   Pure Logic
```

### **2. Specific Code Examples (Close-ups)**

#### A. **Global State Problem**
```python
# routes/dashboard.py - Record this section
provider_manager = LLMProviderManager()  # Line 15
conversation_manager = ConversationManager()  # Line 16
token_manager = TokenManager()  # Line 17
```
**Commentary:** "Global instances make testing impossible"

#### B. **Business Logic in Routes Problem**
```python
# routes/dashboard.py - Record lines 135-213
@dashboard_bp.route('/api/chat/send', methods=['POST'])
def send_message():
    # ... 78 lines of business logic here ...
```
**Commentary:** "This route handler is doing way too much"

#### C. **Mixed Concerns Problem**
```python
# src/prompt_manager/prompt_manager.py - Record the PromptManager class
class PromptManager:
    def __init__(self, storage_file='prompts.json'):  # Storage concern
        self.storage = PromptStorage(storage_file)
    
    def add_prompt(self, name, text, category, **kwargs):
        # Validation (domain concern)
        if not name or not text:
            raise ValueError("Name and text required")
        
        # Business logic (domain concern)
        prompt = Prompt(...)
        
        # Storage (infrastructure concern)
        self.storage.save(prompt)
```
**Commentary:** "Three different concerns in one class"

### **3. Test Examples (Before Refactoring)**

Record running these specific tests:

```bash
# Show test that's hard to write due to global state
pytest tests/test_chat_routes.py::TestChatRoutes::test_send_message -v

# Show test with lots of mocking due to tight coupling
pytest tests/test_llm_provider_manager.py -v
```

**Commentary:** "Notice how many mocks we need? That's a code smell."

### **4. Metrics to Capture**

Run and record output:

```bash
# Line counts
find src routes -name "*.py" | xargs wc -l | tail -1

# Test count
pytest --collect-only | grep "test session starts"

# Cyclomatic complexity (if you have radon installed)
radon cc src/prompt_manager -a
radon cc routes -a
```

---

## Refactoring Phases - Detailed Plan

### **Phase 1: Extract Domain Layer (TDD Cycle 1-3)**

**Goal:** Pure business logic with zero dependencies

#### **Test 1: Extract Prompt Domain Model**
```python
# tests/unit/domain/test_prompt.py (NEW FILE - write this test FIRST)

def test_prompt_validates_name_required():
    """Prompt requires a name."""
    with pytest.raises(ValueError, match="Name is required"):
        Prompt(name="", text="Some text", category="general")

def test_prompt_validates_text_required():
    """Prompt requires text."""
    with pytest.raises(ValueError, match="Text is required"):
        Prompt(name="Test", text="", category="general")

def test_prompt_creates_with_valid_data():
    """Prompt creates successfully with valid data."""
    prompt = Prompt(
        name="Test Prompt",
        text="Test text",
        category="general",
        description="A test"
    )
    assert prompt.name == "Test Prompt"
    assert prompt.text == "Test text"
    assert prompt.category == "general"
    assert prompt.description == "A test"
    assert prompt.id is not None  # Auto-generated
    assert prompt.created_at is not None
```

**Production Code:**
```python
# src/prompt_manager/domain/prompt.py (NEW FILE)

from dataclasses import dataclass, field
from datetime import datetime
import uuid

@dataclass
class Prompt:
    """Domain model representing a prompt.
    
    Pure business logic, no dependencies on storage or UI.
    """
    name: str
    text: str
    category: str
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    tags: list = field(default_factory=list)
    
    def __post_init__(self):
        """Validate on creation."""
        if not self.name or not self.name.strip():
            raise ValueError("Name is required")
        if not self.text or not self.text.strip():
            raise ValueError("Text is required")
        if not self.category or not self.category.strip():
            raise ValueError("Category is required")
    
    def update(self, **kwargs):
        """Update prompt fields and reset modified_at."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.modified_at = datetime.now()
    
    def matches_query(self, query: str) -> bool:
        """Check if prompt matches search query."""
        query = query.lower()
        return (
            query in self.name.lower() or
            query in self.text.lower() or
            query in self.category.lower() or
            query in self.description.lower()
        )
```

#### **Test 2: Extract Message Domain Model**
```python
# tests/unit/domain/test_message.py (NEW FILE)

def test_message_requires_role():
    """Message requires a role."""
    with pytest.raises(ValueError):
        Message(role="", content="test")

def test_message_requires_content():
    """Message requires content."""
    with pytest.raises(ValueError):
        Message(role="user", content="")

def test_message_to_dict():
    """Message converts to API format."""
    msg = Message(role="user", content="Hello")
    assert msg.to_dict() == {"role": "user", "content": "Hello"}
```

**Production Code:**
```python
# src/prompt_manager/domain/message.py (NEW FILE)

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class MessageRole(Enum):
    """Valid message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class Message:
    """Domain model for a chat message."""
    role: str
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if not self.role or self.role not in [r.value for r in MessageRole]:
            raise ValueError(f"Role must be one of: {[r.value for r in MessageRole]}")
        if not self.content or not self.content.strip():
            raise ValueError("Content is required")
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self):
        """Convert to API format."""
        return {
            "role": self.role,
            "content": self.content
        }
```

#### **Test 3: Extract Conversation Domain Model**
```python
# tests/unit/domain/test_conversation.py (NEW FILE)

def test_conversation_starts_empty():
    """New conversation has no messages."""
    conv = Conversation()
    assert len(conv.messages) == 0

def test_conversation_add_message():
    """Can add messages to conversation."""
    conv = Conversation()
    msg = Message(role="user", content="Hello")
    conv.add_message(msg)
    assert len(conv.messages) == 1

def test_conversation_token_count():
    """Conversation calculates token count."""
    conv = Conversation()
    conv.add_message(Message(role="user", content="Hello world"))
    assert conv.estimated_tokens > 0
```

**Production Code:**
```python
# src/prompt_manager/domain/conversation.py (NEW FILE)

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import uuid

from .message import Message

@dataclass
class Conversation:
    """Domain model for a conversation."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    messages: List[Message] = field(default_factory=list)
    model: str = "gpt-3.5-turbo"
    system_prompt: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, message: Message):
        """Add a message to the conversation."""
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    @property
    def estimated_tokens(self) -> int:
        """Estimate total tokens in conversation."""
        # Simple estimation: 4 chars per token
        total_chars = sum(len(msg.content) for msg in self.messages)
        return total_chars // 4
    
    @property
    def message_count(self) -> int:
        """Count non-system messages."""
        return len([m for m in self.messages if m.role != "system"])
    
    def auto_generate_title(self) -> str:
        """Generate a title from the first user message."""
        for msg in self.messages:
            if msg.role == "user":
                title = msg.content[:50]
                if len(msg.content) > 50:
                    title += "..."
                return title
        return "Untitled Conversation"
```

---

### **Phase 2: Extract Service Layer (TDD Cycle 4-6)**

**Goal:** Orchestrate domain objects, handle use cases

#### **Test 4: ChatService**
```python
# tests/unit/services/test_chat_service.py (NEW FILE)

def test_chat_service_builds_message_array():
    """ChatService builds proper message array with system prompt."""
    service = ChatService(token_calculator=MockTokenCalculator())
    
    result = service.prepare_messages(
        user_message="Hello",
        history=[],
        system_prompt="You are helpful"
    )
    
    assert len(result) == 2
    assert result[0].role == "system"
    assert result[1].role == "user"

def test_chat_service_trims_when_needed():
    """ChatService auto-trims long conversations."""
    service = ChatService(token_calculator=MockTokenCalculator(over_limit=True))
    
    long_history = [Message("user", f"Msg {i}") for i in range(20)]
    
    result = service.prepare_messages(
        user_message="New message",
        history=long_history,
        system_prompt="System"
    )
    
    assert len(result) < len(long_history)
```

**Production Code:**
```python
# src/prompt_manager/services/chat_service.py (NEW FILE)

from typing import List
from ..domain.message import Message
from ..domain.conversation import Conversation

class ChatService:
    """Service for managing chat interactions.
    
    Orchestrates domain logic, no HTTP or storage concerns.
    """
    
    def __init__(self, token_calculator, trim_threshold=0.9, keep_count=5):
        self.token_calculator = token_calculator
        self.trim_threshold = trim_threshold
        self.keep_count = keep_count
    
    def prepare_messages(
        self,
        user_message: str,
        history: List[Message],
        system_prompt: str,
        model: str = "gpt-3.5-turbo"
    ) -> List[Message]:
        """Prepare messages for LLM, including trimming if needed."""
        
        # Build message array
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        
        # Add history
        messages.extend(history)
        
        # Add new user message
        messages.append(Message(role="user", content=user_message))
        
        # Trim if needed
        if self._should_trim(messages, model):
            messages = self._trim_messages(messages)
        
        return messages
    
    def _should_trim(self, messages: List[Message], model: str) -> bool:
        """Determine if messages should be trimmed."""
        tokens = self.token_calculator.calculate(messages)
        limit = self.token_calculator.get_limit(model)
        return (tokens / limit) >= self.trim_threshold
    
    def _trim_messages(self, messages: List[Message]) -> List[Message]:
        """Trim old messages, keeping system prompt and recent messages."""
        system = [m for m in messages if m.role == "system"]
        others = [m for m in messages if m.role != "system"]
        
        # Keep only last N messages
        trimmed = others[-self.keep_count:]
        
        return system + trimmed
```

#### **Test 5: PromptService**
```python
# tests/unit/services/test_prompt_service.py (NEW FILE)

def test_prompt_service_creates_prompt():
    """PromptService creates a valid prompt."""
    repo = InMemoryPromptRepository()
    service = PromptService(repository=repo)
    
    prompt = service.create_prompt(
        name="Test",
        text="Text",
        category="general"
    )
    
    assert prompt.id is not None
    assert repo.get(prompt.id) == prompt

def test_prompt_service_search_by_category():
    """PromptService searches by category."""
    repo = InMemoryPromptRepository()
    service = PromptService(repository=repo)
    
    service.create_prompt("P1", "Text1", "cat1")
    service.create_prompt("P2", "Text2", "cat2")
    service.create_prompt("P3", "Text3", "cat1")
    
    results = service.search(category="cat1")
    assert len(results) == 2
```

---

### **Phase 3: Extract Repository Layer (TDD Cycle 7-9)**

**Goal:** Abstract storage, swap implementations easily

#### **Test 7: Repository Interface**
```python
# tests/unit/repositories/test_prompt_repository.py (NEW FILE)

def test_json_repository_saves_and_loads():
    """JsonPromptRepository persists to file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        repo = JsonPromptRepository(f.name)
        
        prompt = Prompt(name="Test", text="Text", category="cat")
        repo.save(prompt)
        
        loaded = repo.get(prompt.id)
        assert loaded.name == "Test"
```

---

### **Phase 4: Refactor Routes (TDD Cycle 10-12)**

**Goal:** Thin controllers, delegate to services

#### **Test 10: Chat Routes Use ChatService**
```python
# tests/integration/test_chat_integration.py (NEW FILE)

def test_chat_endpoint_delegates_to_service(client, mock_chat_service):
    """Chat endpoint uses ChatService, not inline logic."""
    
    response = client.post('/api/chat/send', json={
        'message': 'Hello',
        'model': 'gpt-3.5-turbo'
    })
    
    assert response.status_code == 200
    mock_chat_service.prepare_messages.assert_called_once()
```

**Production Code:**
```python
# routes/dashboard.py (REFACTORED)

@dashboard_bp.route('/api/chat/send', methods=['POST'])
def send_message():
    """Send a chat message - thin controller."""
    try:
        # Extract request data
        data = request.get_json()
        message = data.get('message')
        model = data.get('model', 'gpt-3.5-turbo')
        history = data.get('history', [])
        system_prompt = data.get('system_prompt', '')
        
        # Get services from app context
        chat_service = current_app.config['CHAT_SERVICE']
        llm_service = current_app.config['LLM_SERVICE']
        
        # Prepare messages (business logic in service)
        messages = chat_service.prepare_messages(
            user_message=message,
            history=[Message(**m) for m in history],
            system_prompt=system_prompt,
            model=model
        )
        
        # Generate response (infrastructure service)
        response = llm_service.generate(messages, model=model)
        
        # Return response
        return JsonResponse.success({
            'response': response,
            'token_usage': chat_service.calculate_usage(messages, response)
        })
        
    except ValueError as e:
        return JsonResponse.error(str(e), code='VALIDATION_ERROR', status=400)
    except Exception as e:
        return JsonResponse.error(str(e), code='SERVER_ERROR', status=500)
```

---

## Target Architecture

### **Directory Structure (After Refactoring)**

```
src/prompt_manager/
├── domain/                  # Pure business logic (NEW)
│   ├── __init__.py
│   ├── prompt.py           # Prompt entity
│   ├── message.py          # Message value object
│   ├── conversation.py     # Conversation aggregate
│   └── template.py         # Template entity
│
├── services/                # Use case orchestration (NEW)
│   ├── __init__.py
│   ├── chat_service.py     # Chat use cases
│   ├── prompt_service.py   # Prompt CRUD use cases
│   └── template_service.py # Template use cases
│
├── repositories/            # Storage abstraction (NEW)
│   ├── __init__.py
│   ├── interfaces.py       # Repository interfaces
│   ├── prompt_repository.py
│   ├── conversation_repository.py
│   └── json_storage.py     # JSON implementation
│
├── infrastructure/          # External concerns (REFACTORED)
│   ├── __init__.py
│   ├── llm_provider.py     # LLM interface
│   ├── token_calculator.py # Token calculation
│   └── key_manager.py      # Key storage
│
├── utils/                   # Shared utilities (NEW)
│   ├── __init__.py
│   ├── responses.py        # JSON response helpers
│   └── errors.py           # Custom exceptions
│
└── config.py                # Configuration (NEW)

routes/
├── dashboard.py             # THIN - delegates to services
├── prompts.py              # THIN - delegates to services
└── templates.py            # THIN - delegates to services

tests/
├── unit/
│   ├── domain/             # Domain model tests (NEW)
│   ├── services/           # Service tests (NEW)
│   └── repositories/       # Repository tests (NEW)
├── integration/            # Full workflow tests (NEW)
│   ├── test_chat_workflow.py
│   └── test_prompt_workflow.py
└── fixtures/               # Shared test data
```

---

## Success Metrics

### **Before:**
- Business logic in routes: **60+ lines per endpoint**
- Global state: **3 global managers**
- Test coverage: **~85%**
- Mocks per test: **3-5 mocks average**
- Cyclomatic complexity: **8-12 per function**

### **After (Target):**
- Business logic in routes: **< 10 lines per endpoint**
- Global state: **0 (dependency injection)**
- Test coverage: **95%+**
- Mocks per test: **1-2 mocks average**
- Cyclomatic complexity: **< 5 per function**

---

## Before Footage Summary

### **Must Record:**
1. ✅ Full project tree structure
2. ✅ Test coverage report (before)
3. ✅ `routes/dashboard.py` - lines 135-213 (the 78-line endpoint)
4. ✅ Global state initialization (lines 14-42)
5. ✅ Mixed concerns in `PromptManager`
6. ✅ Working application (all features)
7. ✅ Current test running (show mocking complexity)
8. ✅ Metrics (line counts, test counts, complexity)

### **Optional but Valuable:**
- Dependency diagram (draw it)
- Quick interview: "Why refactor working code?"
- Show git log of rapid feature development

---

## Episode Flow Recommendation

1. **Hook:** "It works. But can you maintain it? Can you extend it? Can you test it?"
2. **Problem:** Show the pain points in current code
3. **Solution:** Introduce domain-driven refactoring
4. **Patterns:** Teach 3-4 key patterns with before/after
5. **Results:** Show metrics improvement
6. **Takeaways:** Lessons for professional development

**This sets up a compelling narrative: Working → Maintainable → Professional**

