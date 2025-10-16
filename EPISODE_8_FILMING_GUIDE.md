# Episode 8: Detailed Step-by-Step Filming Guide

**Goal:** Capture "before footage" showing current codebase state  
**Time needed:** ~1 hour total  
**Equipment:** Screen recorder (QuickTime, OBS, or similar)

---

## 🎬 FILMING SEQUENCE (Do in this exact order)

### **PART 1: Terminal Commands** (10 minutes)

Open Terminal, navigate to project directory, and record these commands ONE AT A TIME:

#### **Recording 1-A: Project Structure**
```bash
# Start recording
tree -L 3 -I '__pycache__|*.pyc|venv|.git'

# If tree isn't installed:
brew install tree

# Then run again
tree -L 3 -I '__pycache__|*.pyc|venv|.git'
```

**What to say while recording:**
> "This is our current file structure. Notice how routes, business logic, and templates are separated, but we'll see the separation isn't as clean as it appears."

**Stop recording. Save as:** `01-project-structure.mov`

---

#### **Recording 1-B: Test Coverage**
```bash
# Start new recording
source venv/bin/activate
pytest --cov=src --cov=routes --cov-report=term-missing
```

**What to say:**
> "We have 142 tests with about 85% coverage. That's good, but let's look at WHAT we're testing and HOW complex the tests are."

**Stop recording. Save as:** `02-test-coverage.mov`

---

#### **Recording 1-C: Metrics**
```bash
# Start new recording

# Line counts
echo "=== Line Counts ==="
find src routes -name "*.py" -not -path "*/test*" | xargs wc -l | tail -1

# Count files
echo "=== File Counts ==="
find src routes -name "*.py" -not -path "*/test*" | wc -l

# Test count
echo "=== Test Count ==="
pytest --collect-only | grep "test session starts"

# Show specific file sizes
echo "=== Largest Files ==="
find src routes -name "*.py" | xargs wc -l | sort -rn | head -10
```

**What to say:**
> "These are our baseline metrics. Pay attention to the file sizes - some of our route handlers are getting quite large."

**Stop recording. Save as:** `03-metrics.mov`

---

###  **PART 2: The Working Application** (10 minutes)

Make sure server is running: http://localhost:8000

#### **Recording 2-A: Dashboard Tour**
**Start screen recording of browser**

1. Navigate to http://localhost:8000/dashboard
2. Show the interface (don't interact yet)
3. Click "Show Controls" if collapsed
4. Scroll through the controls panel

**What to say:**
> "Here's our V1.0 application. It has 10 features, all working. Users love it. But as developers, we need to look beyond 'does it work' to 'can we maintain it.'"

**Stop recording. Save as:** `04-dashboard-working.mov`

---

#### **Recording 2-B: Features Demo**
**Start new recording**

1. Type a message in chat (e.g., "Hello, test message")
2. Click Send
3. Show the response appears
4. Click "History" button
5. Show empty or existing history
6. Close history modal
7. Click "Prompts Library" button (📚 in nav)
8. Show prompts table
9. Click "Back to Dashboard"
10. Click "Template Builder" in nav (if visible)
11. Show it loads
12. Navigate back to dashboard

**What to say:**
> "Everything works. Chat works. History works. Prompts library works. Template builder works. This is what most developers call 'done.' But we're not done."

**Stop recording. Save as:** `05-features-working.mov`

---

### **PART 3: The Problem Code** (20 minutes)

#### **Recording 3-A: Routes with Global State**
**Open `routes/dashboard.py` in your editor**  
**Start screen recording**

1. Scroll to top of file
2. **Pause at lines 14-18** (the global managers)
3. **Highlight these lines with your cursor**

```python
# Initialize managers
provider_manager = LLMProviderManager()
conversation_manager = ConversationManager()
token_manager = TokenManager()
```

**What to say:**
> "Here's our first problem: global state. These three managers are created once when the module loads. That means every test needs to deal with them. We can't mock them easily. We can't test routes in isolation. This is a testing nightmare."

**Stop recording. Save as:** `06-global-state-problem.mov`

---

#### **Recording 3-B: The 78-Line Endpoint**
**Still in `routes/dashboard.py`**  
**Start new recording**

1. Scroll to line 135 (or search for `def send_message()`)
2. **Pause at the function signature**
3. **Slowly scroll through the entire function** (lines 135-213)
4. **Pause at line 213** (end of function)
5. Go back to top of function

**What to say:**
> "This is our chat endpoint. It's 78 lines long. Let me scroll through it so you can see everything it does... [scroll slowly]... It handles HTTP requests, validates input, calculates tokens, builds message arrays, calls the LLM, formats responses, and handles errors. That's at least 6 different responsibilities in one function."

**Stop recording. Save as:** `07-long-endpoint-problem.mov`

---

#### **Recording 3-C: Responsibility Identification**
**Still in the send_message function**  
**Start new recording**

Scroll through again, but this time **pause and point out each responsibility:**

1. Lines ~140-145: "HTTP parsing"
2. Lines ~150-155: "Validation"
3. Lines ~160-180: "Business logic - message building"
4. Lines ~180-195: "Business logic - token calculation and trimming"
5. Lines ~195-205: "Infrastructure - LLM calls"
6. Lines ~205-213: "Response formatting"

**What to say:**
> "Let me show you the different responsibilities. Here's HTTP parsing... here's validation... here's business logic for building messages... here's more business logic for tokens... here's the infrastructure call to the LLM... and here's response formatting. Six different concerns, all tangled together."

**Stop recording. Save as:** `08-responsibilities-identified.mov`

---

#### **Recording 3-D: The Test for This Endpoint**
**Open `tests/test_chat_routes.py` (or similar)**  
**Start new recording**

1. Find a test for `send_message` or similar chat endpoint
2. Scroll through the test
3. **Highlight all the mock setup**

**What to say:**
> "Now let's look at the test for this endpoint. Look at all this mocking setup... [point to mocks]... We need to mock the provider manager, the conversation manager, the token manager, the actual provider... That's 4-5 mocks just to test one endpoint. The test is harder to read than the production code!"

**Stop recording. Save as:** `09-test-complexity.mov`

---

#### **Recording 3-E: Mixed Concerns in PromptManager**
**Open `src/prompt_manager/prompt_manager.py`**  
**Start new recording**

1. Show the `__init__` method - takes `storage_file`
2. Show the `add_prompt` method - has validation AND storage calls
3. Highlight both

**What to say:**
> "Here's another example of mixed concerns. The PromptManager takes a storage file in its constructor - that's an infrastructure concern. Then in add_prompt, it validates the data - that's a domain concern - and then calls self.storage.save - back to infrastructure. Three different layers mixed into one class."

**Stop recording. Save as:** `10-mixed-concerns-prompt-manager.mov`

---

### **PART 4: Architecture Diagrams** (10 minutes)

#### **Recording 4-A: Draw Current Architecture**
**Use a whiteboard, paper, or drawing app (Excalidraw, draw.io)**  
**Start recording**

Draw this diagram while explaining:

```
┌─────────────────────────────────────┐
│           Routes                    │
│  ┌──────────────────────────────┐   │
│  │  HTTP Handling               │   │
│  │  Validation                  │   │
│  │  Business Logic              │   │
│  │  Token Calculation           │   │
│  │  LLM Calls                   │   │
│  │  Storage                     │   │
│  │  Response Formatting         │   │
│  │                              │   │
│  │  ALL MIXED TOGETHER          │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

**What to say:**
> "This is our current architecture. Everything is in the routes. HTTP, validation, business rules, infrastructure - all tangled together. This is why testing is hard. This is why changes ripple through multiple files. This is why adding a new LLM provider is scary."

**Stop recording. Save as:** `11-current-architecture.mov`

---

#### **Recording 4-B: Draw Target Architecture**
**Continue or start new recording**

Draw this diagram:

```
┌──────────────────┐
│   Routes (thin)  │  ← Just HTTP concerns
└────────┬─────────┘
         ↓
┌──────────────────┐
│    Services      │  ← Orchestration
└────────┬─────────┘
         ↓
┌──────────────────┐
│  DOMAIN LAYER    │  ← Pure business logic
│                  │     No dependencies!
│  - Prompt        │
│  - Message       │
│  - Conversation  │
└────────┬─────────┘
         ↓
    ┌────┴────┐
    ↓         ↓
┌──────┐  ┌──────┐
│ Repos│  │ Infra│
└──────┘  └──────┘
```

**What to say:**
> "This is where we're going. Thin routes that just handle HTTP. Services that orchestrate. A domain layer with pure business logic - no Flask, no databases, no external APIs. Just Python. And repositories and infrastructure that can be swapped out. This is clean architecture."

**Stop recording. Save as:** `12-target-architecture.mov`

---

### **PART 5: The "Why Refactor?" Interview** (5 minutes)

#### **Recording 5-A: Self-Interview**
**Record yourself answering these questions**

**Q1: "The code works. Why touch it?"**
> "Working code is just step one. Production code needs to be maintainable, testable, and extensible. Right now, adding a new LLM provider would require changing routes, services, and tests. That's fragile. We need to make change easy before we make changes."

**Q2: "What's the biggest pain point?"**
> "Testing. To test one endpoint, I need 5 mocks. That's a code smell. It means too much is coupled together. When tests are hard, you write fewer tests. When you have fewer tests, you're afraid to refactor. It's a vicious cycle."

**Q3: "What will refactoring enable?"**
> "Easy testing - most tests won't need mocks. Easy extensions - want to add Claude? Just implement one interface. Easy maintenance - business rules in one place. And most importantly, confidence. Confidence to add features without breaking existing code."

**Stop recording. Save as:** `13-why-refactor-interview.mov`

---

## 📊 METRICS TO SCREENSHOT

Take screenshots of these (don't need video):

1. Test coverage report (pytest --cov output)
2. routes/dashboard.py showing line count in editor
3. The send_message function (lines 135-213)
4. Test file showing multiple mocks
5. Git log showing recent commits

Save as: `metrics-01.png`, `metrics-02.png`, etc.

---

## ✅ CHECKLIST - Did You Capture Everything?

Before you finish, verify you have:

- [ ] `01-project-structure.mov` - Terminal tree command
- [ ] `02-test-coverage.mov` - Pytest coverage report
- [ ] `03-metrics.mov` - Line counts and file stats
- [ ] `04-dashboard-working.mov` - Application UI overview
- [ ] `05-features-working.mov` - Features demo
- [ ] `06-global-state-problem.mov` - Global managers highlighted
- [ ] `07-long-endpoint-problem.mov` - 78-line function scroll
- [ ] `08-responsibilities-identified.mov` - Function breakdown
- [ ] `09-test-complexity.mov` - Test with multiple mocks
- [ ] `10-mixed-concerns-prompt-manager.mov` - PromptManager class
- [ ] `11-current-architecture.mov` - Current architecture diagram
- [ ] `12-target-architecture.mov` - Clean architecture diagram
- [ ] `13-why-refactor-interview.mov` - Interview answers
- [ ] Screenshots of metrics and code

---

## 🎥 FILMING TIPS

### **Screen Recording Settings:**
- **Resolution:** 1920x1080 or your screen's native resolution
- **Frame rate:** 30fps is fine
- **Audio:** Record your voice clearly
- **Cursor:** Make sure it's visible
- **Font size:** Increase terminal and editor font size (18-20pt)

### **What to Emphasize:**
1. **Pause when showing code** - Give viewers time to read
2. **Scroll slowly** - Don't rush through long files
3. **Highlight with cursor** - Circle or underline key sections
4. **Repeat key points** - "6 different responsibilities" should be said multiple times

### **Common Mistakes to Avoid:**
- ❌ Scrolling too fast
- ❌ Not pausing on important code
- ❌ Forgetting to speak while recording
- ❌ Window/tab switching too quickly
- ❌ Small font sizes

### **If You Make a Mistake:**
- Just stop recording
- Start a new recording
- You'll edit later - it's OK to have multiple takes

---

## 📝 AFTER FILMING

### **Review Your Footage:**
1. Watch each clip
2. Make sure audio is clear
3. Make sure code is readable
4. Re-record anything that's not clear

### **Organize Files:**
```
before-footage/
├── terminal/
│   ├── 01-project-structure.mov
│   ├── 02-test-coverage.mov
│   └── 03-metrics.mov
├── application/
│   ├── 04-dashboard-working.mov
│   └── 05-features-working.mov
├── code/
│   ├── 06-global-state-problem.mov
│   ├── 07-long-endpoint-problem.mov
│   ├── 08-responsibilities-identified.mov
│   ├── 09-test-complexity.mov
│   └── 10-mixed-concerns-prompt-manager.mov
├── architecture/
│   ├── 11-current-architecture.mov
│   └── 12-target-architecture.mov
├── interview/
│   └── 13-why-refactor-interview.mov
└── screenshots/
    ├── metrics-01.png
    ├── metrics-02.png
    └── ...
```

---

## 🚀 NEXT STEPS

Once you have all this footage:

1. ✅ Review and confirm quality
2. ✅ Tell me you're done filming
3. ✅ We'll start the refactoring
4. ✅ Capture "after" footage
5. ✅ Edit the episode

---

## ⏱️ TIME ESTIMATES

- Terminal commands: 10 minutes
- Working application: 10 minutes
- Problem code: 20 minutes
- Architecture diagrams: 10 minutes
- Interview: 5 minutes
- Screenshots: 5 minutes
- **Total: ~60 minutes**

---

## 💡 REMEMBER

- **Take your time** - Quality over speed
- **Speak clearly** - Your voice teaches
- **Pause on code** - Let viewers read
- **Show the pain** - Make the problems obvious
- **Stay positive** - We're making it better!

**You've got this, David! This footage will make the episode compelling and educational.** 🎬

