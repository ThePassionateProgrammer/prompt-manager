# 🔧 Refactoring Plan - Prompt Manager V1.0

## 📊 Current State Analysis

### **Code Statistics:**
```
Routes:
- dashboard.py: 412 lines, 21 functions
- linkage.py: 789 lines
- static.py: 27 lines

Business Logic:
- conversation_manager.py: 191 lines ✅ CLEAN
- llm_provider_manager.py: 53 lines ✅ CLEAN (100% tested)
- llm_provider.py: 101 lines ✅ CLEAN
- key_loader.py: 214 lines ✅ CLEAN
- custom_combo_box_integration.py: 82 lines
- prompt_builder.py: 157 lines
- prompt_validator.py: 123 lines
- search_service.py: 109 lines

Tests: 6,781 lines across 52 test files
```

### **Health Indicators:**
✅ **Good Coverage**: 45 tests passing for new features  
✅ **Clean Architecture**: Business logic separated from routes  
✅ **TDD Followed**: Tests written first (recent features)  
⚠️ **Large Route File**: dashboard.py has 412 lines, 21 functions  
⚠️ **Magic Numbers**: Token estimation, context limits hardcoded  
⚠️ **Incomplete TODO**: System prompt not persisted to database  

---

## 🎯 Refactoring Priorities

### **Priority 1: Extract Business Logic from Routes** ⭐⭐⭐

#### **Problem:**
`routes/dashboard.py` has 412 lines with mixed concerns:
- Route handlers (HTTP layer)
- Business logic (token calculation, message building)
- Configuration (default prompts, context limits)

#### **Solution:**
Create dedicated managers:

```python
# src/prompt_manager/business/chat_manager.py
class ChatManager:
    """Handles chat message preparation and context management."""
    
    def build_messages(self, message, history, system_prompt)
    def estimate_tokens(self, text)
    def calculate_token_usage(self, messages, model)
    def auto_trim_messages(self, messages, model)
```

```python
# src/prompt_manager/business/model_config.py
class ModelConfig:
    """Configuration for LLM models."""
    
    MODELS = {...}
    CONTEXT_LIMITS = {...}
    DEFAULT_SYSTEM_PROMPT = "..."
    
    def get_model_info(self, model_id)
    def get_context_limit(self, model_id)
```

#### **Benefits:**
- ✅ Routes become thin HTTP handlers
- ✅ Business logic is testable
- ✅ Configuration centralized
- ✅ Easier to maintain

#### **Files to Change:**
- Create: `src/prompt_manager/business/chat_manager.py`
- Create: `src/prompt_manager/business/model_config.py`
- Modify: `routes/dashboard.py` (reduce to ~150 lines)
- Add: `tests/test_chat_manager.py`
- Add: `tests/test_model_config.py`

---

### **Priority 2: Persist System Prompts Properly** ⭐⭐⭐

#### **Problem:**
System prompts currently only exist in memory:
```python
# TODO: Save to user settings/database
```

#### **Solution:**
Create SettingsManager:

```python
# src/prompt_manager/business/settings_manager.py
class SettingsManager:
    """Manages user settings and preferences."""
    
    def __init__(self, settings_file='settings/user_settings.json'):
        self.settings_file = Path(settings_file)
        
    def get_system_prompt(self) -> str
    def save_system_prompt(self, prompt: str) -> bool
    def get_default_model(self) -> str
    def save_default_model(self, model: str) -> bool
    def get_all_settings(self) -> Dict
```

#### **Benefits:**
- ✅ Settings persist across sessions
- ✅ User preferences remembered
- ✅ Easy to add new settings
- ✅ Testable

#### **Files to Change:**
- Create: `src/prompt_manager/business/settings_manager.py`
- Create: `tests/test_settings_manager.py`
- Modify: `routes/dashboard.py` (use SettingsManager)

---

### **Priority 3: Consolidate Token Utilities** ⭐⭐

#### **Problem:**
Token estimation logic scattered in multiple places:
- `estimate_tokens()` function in dashboard.py
- `calculate_token_usage()` function in dashboard.py
- Magic number: "4 characters per token"

#### **Solution:**
Create TokenManager:

```python
# src/prompt_manager/business/token_manager.py
class TokenManager:
    """Handles token estimation and context management."""
    
    CHARS_PER_TOKEN = 4
    
    def estimate_tokens(self, text: str) -> int
    def calculate_message_tokens(self, messages: List) -> int
    def get_context_limit(self, model: str) -> int
    def calculate_usage_percentage(self, tokens: int, model: str) -> float
    def should_trim(self, tokens: int, model: str, threshold: float = 0.9) -> bool
    def trim_messages(self, messages: List, keep_count: int = 5) -> Tuple[List, int]
```

#### **Benefits:**
- ✅ Centralized token logic
- ✅ Easy to improve estimation
- ✅ Consistent across app
- ✅ Highly testable

#### **Files to Change:**
- Create: `src/prompt_manager/business/token_manager.py`
- Create: `tests/test_token_manager.py`
- Modify: `routes/dashboard.py` (use TokenManager)

---

### **Priority 4: Clean Up Test Suite** ⭐⭐

#### **Problem:**
- 52 test files (6,781 lines)
- Many obsolete tests from old features
- Some tests skipped indefinitely
- Potential overlap/redundancy

#### **Solution:**

1. **Remove Obsolete Tests:**
   - Tests for deleted features
   - Tests that require Selenium
   - Tests for old template builder implementation

2. **Consolidate Related Tests:**
   - Combine similar test files
   - Group by feature, not file structure
   - Reduce total test file count

3. **Fix Skipped Tests:**
   - Either implement proper fixtures or delete
   - No permanently skipped tests in V1.0

#### **Benefits:**
- ✅ Faster test runs
- ✅ Clearer test organization
- ✅ Easier to maintain
- ✅ Better documentation

---

### **Priority 5: Improve Error Handling** ⭐

#### **Problem:**
Generic error handling in routes:
```python
except Exception as e:
    return jsonify({'error': str(e)}), 500
```

#### **Solution:**
Create custom exceptions and error handler:

```python
# src/prompt_manager/exceptions.py
class PromptManagerError(Exception):
    """Base exception."""

class ProviderNotFoundError(PromptManagerError):
    """Provider not found."""

class InvalidMessageError(PromptManagerError):
    """Invalid message format."""

class ContextLimitError(PromptManagerError):
    """Context limit exceeded."""

# routes/dashboard.py
@dashboard_bp.errorhandler(ProviderNotFoundError)
def handle_provider_not_found(e):
    return jsonify({'error': str(e)}), 404
```

#### **Benefits:**
- ✅ Specific error types
- ✅ Better error messages
- ✅ Consistent HTTP status codes
- ✅ Easier debugging

---

### **Priority 6: Code Style & Consistency** ⭐

#### **Problem:**
- Inconsistent docstring styles
- Mix of single/double quotes
- Variable naming inconsistencies

#### **Solution:**
Run automated tools:

```bash
# Format code
black src/ routes/ tests/

# Check style
flake8 src/ routes/

# Type checking
mypy src/
```

#### **Benefits:**
- ✅ Consistent style
- ✅ Easier to read
- ✅ Professional appearance
- ✅ Fewer bugs

---

## 📋 Refactoring Roadmap

### **Phase 1: Extract Business Logic** (2-3 hours)
1. Create ChatManager
2. Create ModelConfig  
3. Create TokenManager
4. Create SettingsManager
5. Write tests for each (test-first!)
6. Update dashboard.py to use managers
7. Verify all existing tests still pass

### **Phase 2: Clean Up Tests** (1-2 hours)
1. Identify obsolete test files
2. Delete or consolidate
3. Fix skipped tests
4. Run full suite
5. Verify >90% coverage

### **Phase 3: Error Handling** (1 hour)
1. Create exception hierarchy
2. Add error handlers
3. Update routes to use specific exceptions
4. Test error scenarios

### **Phase 4: Code Style** (30 mins)
1. Run black
2. Fix flake8 warnings
3. Update docstrings
4. Final cleanup

### **Phase 5: Documentation** (30 mins)
1. Update README
2. Add API documentation
3. Update TESTING_GUIDE
4. Create V1.0 release notes

---

## 🎬 Refactoring Order (Recommended)

1. **ChatManager** (highest impact, most used)
2. **TokenManager** (used by ChatManager)
3. **ModelConfig** (used by both)
4. **SettingsManager** (user-facing improvement)
5. **Clean up tests** (reduces noise)
6. **Error handling** (polish)
7. **Code style** (final touches)

---

## 🔍 Specific Code Smells Found

### **routes/dashboard.py:**
- ❌ Line 142-157: Token calculation mixed with routes
- ❌ Line 130-138: Model config hardcoded
- ❌ Line 182-197: Message building logic in route
- ❌ Line 318: TODO comment (incomplete feature)

### **Opportunity for Improvement:**
- 📦 Extract 4 business logic classes
- 🧪 Add 40-50 new tests for extracted code
- 📉 Reduce dashboard.py from 412 → ~150 lines
- 🎯 Achieve 100% coverage for all managers

---

## ✅ What's Already Good

### **Don't Refactor:**
1. ✅ `LLMProviderManager` - Already perfect (100% tested)
2. ✅ `ConversationManager` - Clean, tested, single responsibility
3. ✅ `SecureKeyManager` - Robust, well-designed
4. ✅ UI Templates - Functional, modern, user-tested
5. ✅ Recent tests - Well-structured, comprehensive

### **Strengths to Maintain:**
- Test-first approach
- Business logic separation
- Clean interfaces
- Comprehensive testing
- User-focused design

---

## 🤔 Questions for You

### **Before I Start Refactoring:**

1. **Test Cleanup Strategy:**
   - Should I delete all tests for deleted features?
   - Or mark them clearly as "obsolete" first?

2. **Backward Compatibility:**
   - Keep old API endpoints for compatibility?
   - Or can I make breaking changes since it's pre-V1.0?

3. **Configuration:**
   - Store settings in JSON file?
   - Or use a proper database (SQLite)?

4. **Scope:**
   - Do ALL refactoring before V1.0 release?
   - Or prioritize must-haves and defer nice-to-haves?

5. **Code Style:**
   - Should I run `black` formatter (opinionated auto-format)?
   - Or manual cleanup to preserve your style?

---

## 🎯 My Recommendation

### **For V1.0 Release:**

**Must-Have Refactoring:**
1. ✅ Extract ChatManager (critical for maintainability)
2. ✅ Extract TokenManager (DRY principle)
3. ✅ Create ModelConfig (centralize configuration)
4. ✅ Persist SettingsManager (fix TODO)
5. ✅ Delete obsolete tests (reduce noise)

**Nice-to-Have (Post-V1.0):**
6. ⏭️ Custom exceptions (can add later)
7. ⏭️ Code style automation (non-breaking)
8. ⏭️ Advanced test consolidation

### **Estimated Time:**
- **Must-Have**: 3-4 hours
- **Nice-to-Have**: 1-2 hours
- **Total**: 4-6 hours

### **Expected Results:**
- Dashboard.py: 412 → ~150 lines (-63%)
- New business classes: 4
- New tests: ~50
- Total test coverage: >95%
- All existing functionality preserved
- Cleaner, more maintainable code

---

**Should I proceed with the refactoring plan? Any changes to the priorities?** 

I'll wait for your input before starting! 🚀
