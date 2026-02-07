# 🎬 Quick Reference Card for Filming

**Copy this to a second screen or print it out**

---

## ✅ READY TO RECORD

**Server:** http://localhost:8000 ✅  
**Bugs:** All fixed ✅  
**Tests:** 408 passing ✅

---

## 📝 FILMING SEQUENCE (60 min total)

### **1. Terminal Commands** (10 min)

```bash
# Recording 1-A: Structure
tree -L 3 -I '__pycache__|*.pyc|venv|.git'

# Recording 1-B: Coverage  
source venv/bin/activate
pytest --cov=src --cov=routes --cov-report=term-missing

# Recording 1-C: Metrics
find src routes -name "*.py" -not -path "*/test*" | xargs wc -l | tail -1
```

**Key numbers to mention:**
- 408 tests passing
- 57% coverage
- 2,549 total lines of code

---

### **2. Working Application** (10 min)

**Navigate to:** http://localhost:8000/dashboard

**Demo:**
1. Type and send a message
2. Open History
3. Open Prompts Library (📚 button)
4. Go to Template Builder
5. Back to dashboard

**Say:** "Everything works. Users love it. But can we maintain it?"

---

### **3. Problem Code** (20 min)

#### **File A: routes/dashboard.py**

**Lines 14-18:** Global managers
```python
provider_manager = LLMProviderManager()
conversation_manager = ConversationManager()
token_manager = TokenManager()
```
**Say:** "Global state makes testing impossible"

**Lines 135-213:** 78-line endpoint
**Say:** "Six different responsibilities in one function"

#### **File B: tests/test_chat_routes.py**

**Find:** Any test with multiple mocks
**Say:** "4-5 mocks just to test one endpoint"

#### **File C: src/prompt_manager/prompt_manager.py**

**Show:** PromptManager class
**Say:** "Validation, business logic, and storage all mixed together"

---

### **4. Architecture Diagrams** (10 min)

**Current:**
```
Routes
  ├─ HTTP
  ├─ Validation
  ├─ Business Logic
  ├─ Storage
  └─ Everything mixed!
```

**Target:**
```
Routes (thin)
  ↓
Services
  ↓
Domain (pure)
  ↓
Repos + Infra
```

---

### **5. Interview** (5 min)

**Q1:** "Why refactor working code?"  
**A:** "Working is step one. Production code needs maintainability, testability, extensibility."

**Q2:** "What's the pain?"  
**A:** "Testing requires 5 mocks. That's a code smell."

**Q3:** "What will this enable?"  
**A:** "Easy testing, easy extensions, confidence to add features."

---

## 💡 FILMING TIPS

✅ **Pause on code** - Let viewers read  
✅ **Scroll slowly** - Don't rush  
✅ **Speak clearly** - You're teaching  
✅ **Large fonts** - 18-20pt  
✅ **Highlight with cursor** - Circle key sections  

❌ **Don't rush** - Quality over speed  
❌ **Don't mumble** - Enunciate  
❌ **Don't go silent** - Narrate what you're doing  

---

## 📊 KEY METRICS TO MENTION

- **408 tests passing**
- **57% coverage**
- **2,549 lines of code**
- **78 lines in one endpoint** (routes/dashboard.py send_message)
- **4-5 mocks per test** (on average)
- **6 different responsibilities** in send_message

---

## 🎯 KEY MESSAGES

1. **"Working code is just step one"**
2. **"Production code requires refactoring"**
3. **"Testing is hard because too much is coupled"**
4. **"We'll separate concerns to make change easy"**
5. **"Domain layer = pure business logic"**

---

## ⏱️ TIME CHECK

- Terminal: ~10 min  
- App demo: ~10 min  
- Problem code: ~20 min  
- Diagrams: ~10 min  
- Interview: ~5 min  
- **Buffer: 5 min**
- **Total: 60 min**

---

## 🆘 IF YOU GET STUCK

**Problem:** Command fails  
**Solution:** Skip it, note it, ask Claude later

**Problem:** Can't find file/line  
**Solution:** Use the filming guide for exact paths

**Problem:** Forgot what to say  
**Solution:** Read from the guide - it's OK!

---

## ✅ FINAL CHECKLIST

Before you start:
- [ ] Screen recorder ready
- [ ] Audio tested
- [ ] Font size increased (18-20pt)
- [ ] Server running (http://localhost:8000)
- [ ] Terminal in project directory
- [ ] Water nearby
- [ ] Phone on silent

---

## 🎬 YOU'VE GOT THIS!

**Remember:** You're teaching the journey from "working" to "production-ready"

**Show the pain** → **Show the solution** → **Show the results**

**Go make great footage!** 🚀

