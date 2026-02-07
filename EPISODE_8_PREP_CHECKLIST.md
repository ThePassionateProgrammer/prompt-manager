# Episode 8 Preparation Checklist

**Goal:** Capture "before footage" showing current codebase state before refactoring

---

## 📹 Before Footage Required (Record BEFORE refactoring)

### **1. Terminal Commands** (Record these executions)

```bash
# A. Project structure
tree -L 3 -I '__pycache__|*.pyc|venv'

# B. Test coverage report
pytest --cov=src --cov=routes --cov-report=term-missing

# C. Line counts
find src routes -name "*.py" | xargs wc -l | tail -1

# D. Test count
pytest --collect-only | grep "tests"

# E. Cyclomatic complexity (optional, if you have radon)
pip install radon
radon cc src/prompt_manager -a
radon cc routes -a
```

---

### **2. Code Walkthrough** (Screen recording with commentary)

#### **A. routes/dashboard.py**
**What to show:**
- Scroll from line 1 to end
- **Pause and highlight:** Lines 14-42 (global state initialization)
  - Commentary: "These three global managers make testing impossible"
- **Pause and highlight:** Lines 135-213 (send_message endpoint)
  - Commentary: "78 lines in one function—HTTP, validation, business logic, storage, all mixed"
- **Pause and count responsibilities:**
  - HTTP parsing
  - Validation
  - Token calculation
  - Message building
  - Trimming logic
  - LLM calls
  - Storage
  - Error handling

#### **B. src/prompt_manager/prompt_manager.py**
**What to show:**
- Show the entire PromptManager class
- **Highlight:** Mixed concerns
  - `__init__` takes storage file (storage concern)
  - `add_prompt` has validation (domain concern)
  - `add_prompt` calls `self.storage.save()` (infrastructure concern)
- Commentary: "Three different responsibilities in one class"

#### **C. src/prompt_manager/business/token_manager.py**
**What to show:**
- Scroll through the entire file
- Commentary: "This is actually pretty good—pure logic, minimal dependencies. This is closer to our target."

#### **D. tests/test_chat_routes.py** (or similar)
**What to show:**
- Find a test with lots of mocking
- **Highlight:** The mocking setup
  - Count the mocks (should be 4-5)
- Commentary: "15 lines of mocking for a 3-line test. This is a code smell."

---

### **3. Running Application** (Screen recording)

**What to show:**
1. Start the server
2. Navigate to http://localhost:8000/dashboard
3. Send a chat message (show it works)
4. Open Prompts Library (show it works)
5. Open Template Builder (show it works)
6. Open Settings (show it works)

**Commentary:** "Everything works perfectly. Users love it. But maintaining and extending this code? That's where the pain is."

---

### **4. Specific Code Examples** (Close-up recordings)

#### **Example 1: Global State**
```python
# routes/dashboard.py lines 14-17
provider_manager = LLMProviderManager()
conversation_manager = ConversationManager()
token_manager = TokenManager()
```
**Commentary:** "Global instances. Can't test routes without these. Can't mock these easily."

#### **Example 2: Mixed Concerns**
```python
# routes/dashboard.py send_message function
@dashboard_bp.route('/api/chat/send', methods=['POST'])
def send_message():
    data = request.get_json()              # HTTP
    message = data.get('message')
    if not message:                         # Validation
        return jsonify({'error': ...})
    provider = provider_manager.get(...)    # Infrastructure
    messages = []                           # Business logic
    messages.append({'role': 'system'...})
    # ... 70 more lines ...
```

---

### **5. Create a Dependency Diagram** (Draw on screen or use tool)

**Current (Messy):**
```
┌─────────────────────────┐
│       Routes            │
│  (Everything mixed)     │
│   - HTTP                │
│   - Validation          │
│   - Business Logic      │
│   - Storage             │
│   - Infrastructure      │
└─────────────────────────┘
         ↓  ↓  ↓
    Too many dependencies
```

**Target (Clean):**
```
Routes (thin)
    ↓
Services (orchestration)
    ↓
Domain (pure logic) ← The heart
    ↓
Repositories + Infrastructure
```

---

## 📊 Metrics to Capture

Run these and **screenshot the results:**

### **Before Refactoring:**
- Lines in `routes/dashboard.py` send_message: **78**
- Global dependencies: **3**
- Test coverage: **~85%**
- Average mocks per test: **~4**
- Cyclomatic complexity: **~12**
- Total tests: **142**

### **Record these numbers:**
```bash
# Test coverage
pytest --cov=src --cov=routes --cov-report=term-missing | tail -20

# Lines in send_message
sed -n '135,213p' routes/dashboard.py | wc -l
```

---

## 🎬 Interview Clips (Optional but Powerful)

### **Question 1:** "Why refactor working code?"
**Your Answer:** "Working code is step one. Production code requires clean architecture, comprehensive tests, and room to grow. This is what separates hobbyists from professionals."

### **Question 2:** "What's the biggest pain point right now?"
**Your Answer:** "Adding a new feature requires touching multiple files. Testing requires mocking everything. Changing storage or LLM providers would be a nightmare."

### **Question 3:** "What will refactoring enable?"
**Your Answer:** "Easy testing, easy extensions, easy maintenance. We'll be able to add V2.0 features without breaking V1.0. That's the goal."

---

## 📝 Before You Start Recording

### **Checklist:**
- [ ] Server is running and all features work
- [ ] You know which files to show
- [ ] You've identified the specific line ranges
- [ ] You have your commentary ready
- [ ] You understand the problems you're showing
- [ ] You're ready to articulate WHY these are problems

---

## 🎯 What Makes This Footage Valuable

### **Don't Just Show Code—Show the Pain:**
1. **The 78-line endpoint** - "This is unmaintainable"
2. **The global state** - "This is untestable"
3. **The mixed concerns** - "This violates every SOLID principle"
4. **The mocking nightmare** - "Tests should be simple"
5. **The working app** - "But it works! So why change it?"

### **Create Contrast:**
Show that it works, THEN show why it's still not done.

---

## ⏱️ Time Estimate

- Terminal commands: **5 minutes**
- Code walkthroughs: **15 minutes**
- Running app: **5 minutes**
- Close-up examples: **10 minutes**
- Interview clips: **5 minutes**
- **Total: ~40 minutes of raw footage**

You'll edit this down to ~5-8 minutes of "before" footage in the final episode.

---

## 🚨 Critical: DO NOT START REFACTORING YET

**Capture all this footage FIRST.**

Once you start refactoring, you can't go back to show the "before" state. This footage is essential for:
1. Teaching (showing the problems)
2. Contrast (before/after comparison)
3. Motivation (why refactoring matters)
4. Credibility (you're not making up problems)

---

## ✅ Ready to Record?

Once you have all this footage, come back and we'll:
1. Review the footage
2. Plan the refactoring approach
3. Start the TDD cycles
4. Extract domain layer
5. Build service layer
6. Implement repositories
7. Refactor routes
8. Capture "after" footage
9. Edit the episode

**Good luck with the recordings!** 🎬

