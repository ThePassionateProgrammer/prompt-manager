# Episodes 8A & 8B: Production Plan
**Real-World Refactoring on a Real Codebase**

---

## Episode 8A: "Legacy Code Techniques on Fresh Code"
**Duration:** 8-10 minutes  
**Theme:** Safe refactoring → Understanding → Pinning tests → Dependency injection → Coverage

**Based on:** Feathers' "Working Effectively with Legacy Code" + Fowler's "Refactoring" + Bernstein's "Beyond Legacy Code"

---

## Episode 8B: "Domain Models: What We Have & Why They Matter"
**Duration:** 8-10 minutes  
**Theme:** Review existing domain layer, explain DDD principles, show the value

---

## 🎬 EPISODE 8A: Production Plan

### Hook (30 sec)
**[SCREEN: Show the 78-line endpoint]**

> "This is a real production codebase. 10 features, 408 tests, users love it. But it has 78-line functions, global state, and tests that need 5 mocks. Most developers would say 'it works, don't touch it.' Today we'll apply legacy code techniques to make it maintainable. This isn't a toy project - this is real refactoring."

---

### Act 1: System Overview (2 min)

**[SCREEN: Project structure]**

**Conversation:**

**David:** "Claude, walk me through the system. High level - what are the main components?"

**Claude:** "Let me show you..."

**[I'll guide a tour showing:]**
```
Routes (5 blueprints)
  ├─ dashboard.py - Chat, settings, providers (410 lines)
  ├─ linkage.py - Template builder (1,324 lines!)
  ├─ prompts_api.py - API endpoints
  ├─ prompts_library.py - CRUD page
  └─ static.py - JS assets

Business Layer
  ├─ llm_provider_manager.py - Provider management
  ├─ conversation_manager.py - Chat persistence
  ├─ token_manager.py - Token calculation
  └─ key_loader.py - Encrypted key storage

Domain (exists but underutilized)
  └─ linkage_manager.py - Template linkages

Templates
  ├─ chat_dashboard.html (1,700 lines!)
  └─ prompts_library.html
```

**Key insights:**
- Routes are getting large (410 lines, 1,324 lines)
- Business logic mixed with HTTP
- Domain layer exists but incomplete
- Template complexity suggests JS extraction needed

---

### Act 2: The Problem Deep Dive (2 min)

**[SCREEN: routes/dashboard.py, lines 135-213]**

**David:** "Show me the worst offender."

**Claude:** "The chat endpoint. 78 lines. Let me trace through it..."

**[I walk through, identifying:]**
- Lines 140-145: HTTP parsing
- Lines 150-155: Validation
- Lines 160-175: Message array building (domain logic!)
- Lines 176-192: Token calculation and trimming (domain logic!)
- Lines 193-205: LLM call (infrastructure)
- Lines 206-213: Response formatting

**David:** "Six different concerns. How do we even start?"

**Claude:** "With safe refactorings - extract methods to see the structure clearly."

---

### Act 3: Safe Refactoring - Extract Method (3 min)

**[SCREEN: Live refactoring]**

**We extract together:**

**Refactoring 1: Extract Message Building**
```python
# Before: Inline
messages = []
messages.append({'role': 'system', 'content': system_prompt})
messages.extend(history)
messages.append({'role': 'user', 'content': message})

# After: Extracted
def _build_message_array(message, history, system_prompt):
    """Build message array for LLM."""
    messages = []
    if system_prompt:
        messages.append({'role': 'system', 'content': system_prompt})
    messages.extend(history)
    messages.append({'role': 'user', 'content': message})
    return messages
```

**Run tests:** `pytest tests/test_chat_routes.py -v`  
**Status:** ✅ Still green

**David:** "Good. Now what?"

**Refactoring 2: Extract Token Management**
```python
def _auto_trim_if_needed(messages, model, token_manager):
    """Trim messages if approaching context limit."""
    prompt_tokens = token_manager.calculate_message_tokens(messages)
    if token_manager.should_trim(prompt_tokens, model, threshold=0.9):
        return token_manager.trim_messages(messages, keep_count=5)
    return messages, 0
```

**Run tests:** ✅ Still green

**David:** "The function is getting clearer. What does this reveal?"

**Claude:** "These extracted methods show us the domain concepts: MessageBuilder, TokenManager. These want to be their own classes."

---

### Act 4: Pinning Tests & Dependency Injection (2 min)

**[SCREEN: Show the global state problem]**

**David:** "How do we test these extracted methods? They still use global managers."

**Claude:** "We need to inject dependencies. But first, let's pin the behavior with a characterization test."

**[Show writing a pinning test:]**
```python
def test_send_message_current_behavior(client, mocker):
    """Pin current behavior before refactoring."""
    # Mock the globals
    mock_provider = mocker.patch('routes.dashboard.provider_manager')
    mock_provider.get_provider.return_value = Mock(generate=Mock(return_value="Response"))
    
    response = client.post('/api/chat/send', json={'message': 'Test'})
    
    assert response.status_code == 200
    assert 'response' in response.json
    # This test locks in current behavior
```

**David:** "Now we can refactor safely. The test tells us if we break something."

**Claude:** "Exactly. Now let's inject those dependencies..."

**[Show dependency injection:]**
```python
# Before: Global
provider = provider_manager.get_provider(provider_name)

# After: Injected
def send_message():
    provider_manager = current_app.config['PROVIDER_MANAGER']
    provider = provider_manager.get_provider(provider_name)
```

**Run tests:** ✅ Still green, but now testable!

---

### Act 5: What We Learned (1 min)

**[SCREEN: Before/after comparison]**

**David:** "What did we accomplish?"

**Claude:** 
- "Clarified 78 lines into logical chunks"
- "Identified hidden domain concepts"
- "Pinned behavior with tests"
- "Injected dependencies for testability"
- "Ready for domain extraction in Episode 8B"

**David:** "And we didn't break anything because..."

**Claude:** "Tests stayed green the whole time. That's the legacy code technique - small steps, always green."

**Outro:** "In Episode 8B, we'll extract the domain model."

---

## 🎬 EPISODE 8B: Production Plan

### Hook (30 sec)
> "In 8A, we used safe refactoring to understand the code. Now we'll extract domain models. But first, let's see what domain models we already have..."

---

### Act 1: What Domain Models Exist (2 min)

**[SCREEN: Show src/prompt_manager/domain/]**

**David:** "We already have domain models?"

**Claude:** "Yes! linkage_manager.py - 182 lines of pure domain logic."

**[Walk through linkage_manager.py]**
- No framework dependencies ✓
- Pure business rules ✓
- Self-validating ✓
- "This is what a domain model looks like"

**David:** "What else do we have scattered around?"

**[Show business/ directory]**
- token_manager.py - "Actually domain logic!"
- prompt_validator.py - "Domain logic!"
- conversation_manager.py - "Mixed - some domain, some infrastructure"

**Claude:** "We have domain logic, just not all in domain/"

---

### Act 2: Extract Prompt Domain Model (3 min)

**[SCREEN: Live extraction]**

**Start with tests:**
```python
# tests/unit/domain/test_prompt.py
def test_prompt_requires_name():
    with pytest.raises(ValueError, match="Name is required"):
        Prompt(name="", text="Text", category="general")
```

**Run:** ❌ RED (module doesn't exist)

**Write minimal code:**
```python
# src/prompt_manager/domain/prompt.py
from dataclasses import dataclass

@dataclass
class Prompt:
    name: str
    text: str
    category: str
    
    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Name is required")
```

**Run:** ✅ GREEN

**Refactor - add full features:**
```python
@dataclass
class Prompt:
    name: str
    text: str
    category: str
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Name is required")
        if not self.text.strip():
            raise ValueError("Text is required")
    
    def matches_query(self, query: str) -> bool:
        """Domain logic: search matching."""
        q = query.lower()
        return q in self.name.lower() or q in self.text.lower()
```

**Run tests:** ✅ GREEN

**Commit!**

---

### Act 3: Using the Domain Model (2 min)

**[SCREEN: Refactor route to use Prompt]**

**Before:**
```python
# routes/prompts_api.py
prompts = manager.list_prompts()
prompts_data = [p.to_dict() for p in prompts]
```

**After:**
```python
# routes/prompts_api.py
prompts = manager.list_prompts()  # Returns Prompt objects
prompts_data = [p.__dict__ for p in prompts]  # Dataclass magic!
```

**Show:** Tests still pass, code is cleaner

---

### Act 4: Domain-Driven Design Principles (2 min)

**[SCREEN: Architecture diagram]**

**David:** "Why bother with domain models?"

**Claude:** "Three reasons..."

**1. Testability**
```python
# Without domain model - need mocks
def test_prompt_validation(mock_storage, mock_validator):
    # Setup mocks...
    manager.add_prompt(...)

# With domain model - no mocks!
def test_prompt_validation():
    with pytest.raises(ValueError):
        Prompt(name="", text="Text")
```

**2. Portability**
- No Flask dependency
- Can use in CLI, API, GUI, anywhere
- Pure Python

**3. Clarity**
- Business rules in one place
- Easy to understand
- Easy to change

**David:** "And DDD says domain is the heart..."

**Claude:** "Everything else serves the domain. Routes serve it, storage serves it, UI serves it. The domain is your competitive advantage."

---

### Act 5: What We Have Now (1 min)

**[SCREEN: After walkthrough]**

**New structure:**
```
domain/
  ├─ prompt.py (NEW - pure domain)
  ├─ message.py (could extract)
  └─ linkage_manager.py (already good)

business/
  ├─ token_manager.py (could move to domain)
  └─ conversation_manager.py (could split)

routes/
  └─ dashboard.py (now using domain models)
```

**Metrics:**
- Domain layer established ✓
- Tests easier to write ✓
- Code more maintainable ✓

**David:** "V1.0 refactoring complete?"

**Claude:** "Yes. Clean architecture, domain-driven, test-supported. This is production code."

---

## 🎥 RECORDING WORKFLOW

### Setup (5 min)
1. Open terminal (large font - 18pt)
2. Open VS Code (large font - 16pt)
3. Position windows side-by-side or use tabs
4. Start screen recorder (QuickTime or OBS)
5. Open SuperWhisper

### Recording Session 1: Overview & Safe Refactoring (1 hour)
**For Episode 8A**

1. **I give system overview** (you ask questions)
2. **We identify problem areas** (conversation)
3. **We do 2-3 safe refactorings** (extract methods)
4. **We pin behavior with tests** (characterization tests)
5. **We inject dependencies** (make testable)
6. **We reflect** (what did we learn?)

**Stop recording. You have Episode 8A raw footage.**

---

### Recording Session 2: Domain Extraction (1 hour)
**For Episode 8B**

1. **Review existing domain models** (linkage_manager)
2. **Extract Prompt domain model** (test-first)
3. **Show before/after route complexity**
4. **Explain DDD principles** (why domain matters)
5. **Walk through final structure**
6. **Reflect** (what V1.0 means now)

**Stop recording. You have Episode 8B raw footage.**

---

## 📋 CONVERSATION OUTLINE - Episode 8A

**Use this as a script, but stay flexible:**

### Opening (David on camera, then screen)
"We're going to refactor a real codebase using legacy code techniques. Claude, show me what we're working with."

### System Tour (Screen recording conversation)

**David:** "Give me the 30,000-foot view. What's the architecture?"

**Claude:** [Shows file structure, explains layers]

**David:** "What's our biggest problem area?"

**Claude:** "routes/dashboard.py - the chat endpoint mixes concerns. Let me show you..."

**David:** "78 lines? Walk me through it."

**Claude:** [Traces through, identifying responsibilities]

**David:** "If this were legacy code, where would you start?"

**Claude:** "Safe refactorings to understand it. Extract methods to reveal structure."

### Safe Refactoring Demo (Live coding)

**David:** "Show me."

**Claude:** "Let me extract the message building logic..."

[Extract method, run tests, show green]

**David:** "What did that reveal?"

**Claude:** "Message building is a domain concept. It wants to be its own class."

**David:** "Keep going."

[Extract token management, run tests, green]

**David:** "Now what?"

**Claude:** "Now we can see the structure. But we still can't test it easily because of global state."

### Pinning & Dependency Injection

**David:** "How do we fix that?"

**Claude:** "First, pin the behavior with a characterization test..."

[Write pinning test]

**David:** "This locks in current behavior?"

**Claude:** "Yes. Now we can inject dependencies safely..."

[Show dependency injection]

**David:** "Run the pinning test."

[Run test - green]

**Claude:** "Still works. But now we can mock the dependencies for unit testing."

### Reflection

**David:** "What did we accomplish?"

**Claude:** 
- Understood the code through safe refactoring
- Revealed hidden domain concepts
- Pinned behavior with tests
- Injected dependencies for testability
- Ready for domain extraction

**David:** "And we didn't break anything?"

**Claude:** "Tests green the whole time. That's the discipline."

---

## 📋 CONVERSATION OUTLINE - Episode 8B

### Opening
**David:** "We prepared the code. Now let's extract domain models. But first, what do we already have?"

### Review Existing Domain

**Claude:** "We already have domain models! linkage_manager.py - look at this..."

[Show linkage_manager.py]
- No framework dependencies
- Pure business logic
- Self-validating

**David:** "This is good domain code. What else?"

**Claude:** "token_manager.py is actually domain logic, just in the wrong directory..."

### Extract Prompt Domain Model

**David:** "Let's extract Prompt. Show me the process."

**Claude:** "Test first..."

[Write test, RED, write code, GREEN, refactor]

**David:** "Why is this better than what we had?"

**Claude:** [Show comparison]
- Before: PromptManager mixes domain, storage, validation
- After: Prompt is pure domain, testable without mocks

### DDD Principles

**David:** "Why does Domain-Driven Design matter?"

**Claude:** "The domain is your competitive advantage. Everything else—databases, frameworks, UIs—those are commodities. Your business rules are unique. Protect them. Keep them pure."

**David:** "And pure means?"

**Claude:** "No dependencies. Can run without Flask, without databases, without anything external. Just Python and your rules."

### Final Architecture

**[SCREEN: Show the clean architecture]**

**David:** "What does V1.0 look like now?"

**Claude:** 
- Domain layer with business rules
- Services orchestrating domain objects  
- Routes handling HTTP only
- 95% test coverage
- Easy to extend, easy to test

**David:** "This is production code."

**Claude:** "This is V1.0."

---

## 🎯 WHAT MAKES THIS VALUABLE

### Not Toy Project
- 2,549 lines of real code
- 408 real tests
- 10 working features
- Real complexity

### Not Trivial Refactoring
- 78-line function to tackle
- Global state to untangle
- Mixed concerns to separate
- Real problems

### Proven Techniques
- Feathers' characterization tests
- Fowler's extract method
- Bernstein's pinning approach
- DDD principles
- Applied to real code

### Viewers Learn
- How to approach messy code (even fresh code)
- Safe refactoring techniques
- When to pin, when to inject
- How to test the untestable
- Domain-driven design in practice

---

## 📝 PROCEDURE FILE WE'LL CREATE

After both episodes, we'll document:

**LEGACY_CODE_REFACTORING_PROCEDURE.md**
1. Understand first (safe refactorings reveal structure)
2. Pin behavior (characterization tests)
3. Inject dependencies (make testable)
4. Add fine-grained tests (safety net)
5. Extract domain (complex refactoring now safe)
6. Verify (tests protect you)

**This becomes our reusable process.**

---

## 🎬 PRODUCTION SIMPLIFICATION

### What You Record
**Session 1 (Today):** 1 hour - Overview + safe refactoring + pinning  
**Session 2 (Tomorrow):** 1 hour - Domain extraction + DDD + final walkthrough

### What I Do
- Respond to your questions
- Guide the refactoring
- Explain the principles
- Show the techniques

### Post-Production
- You edit to 8-10 min each
- Add TTS for some of my responses (optional)
- Add on-camera reactions/commentary
- Add B-roll (code, diagrams, metrics)

**Total filming: 2 hours**  
**Total editing: 4-5 hours**  
**Two professional episodes teaching real techniques**

---

## 🚀 READY TO START?

**When you say "Let's start the walkthrough," I'll:**

1. Give you the high-level system overview
2. Identify the problem areas
3. Propose safe refactorings
4. Walk through the techniques
5. Extract domain models
6. Reflect on what we learned

**You just:**
- Record screen
- Ask questions
- Guide the conversation
- We learn together on camera

**Sound good?** 🎯

