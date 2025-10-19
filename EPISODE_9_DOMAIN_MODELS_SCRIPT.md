# Episode 9: Domain Models - What Good Code Looks Like
**Target: 6-8 minutes final footage**

---

## CONCEPT: Show, Don't Build

**Instead of:** Building a domain model from scratch (complex, time-consuming)  
**We'll do:** Walk through existing domain code + explain principles + show where to apply them

**Value:** Viewers learn to **recognize** good domain code and **identify** where it's needed

---

## 🎬 STRUCTURE

### **Act 1: What is a Domain Model?** (On Camera - 1 min)
**[Your footage from yesterday]**

### **Act 2: Example of Good Domain Code** (Screen Walkthrough - 2 min)
**[You narrate over screen recording of code]**

### **Act 3: Example of Domain Logic in Wrong Place** (Screen Walkthrough - 2 min)
**[You narrate, pointing out the problem]**

### **Act 4: The Fix (Simple)** (Quick Screen Recording - 1 min)
**[Optional: Show one simple extraction]**

### **Act 5: Why This Matters** (On Camera - 1 min)
**[Your footage + maybe B-roll of architecture diagram]**

---

## 📋 ACT 1: WHAT IS A DOMAIN MODEL? (On Camera)

**Your Script (what you probably already said):**

> "A domain model is your business logic with zero dependencies. No Flask. No databases. No frameworks. Just Python and your rules.
>
> Why? Your business rules are your competitive advantage. Frameworks change. Databases get replaced. But your core logic—that's unique to you.
>
> Let me show you what this looks like in our codebase."

---

## 📋 ACT 2: GOOD DOMAIN CODE WALKTHROUGH (Screen Recording)

**Screen:** Open `src/prompt_manager/domain/linkage_manager.py`

### **Narration Script:**

**[Showing top of file - imports]**
> "This is a domain model. Look at the imports—just Python. No Flask, no SQLAlchemy, nothing external. This is pure domain logic."

**[Scroll to class definition ~line 15]**
> "We have domain objects: LinkageRule, ComboBoxState. These represent our business concepts."

**[Scroll to a method, ~line 50]**
> "Here's a business rule: when to create linkages. Pure logic—takes input, applies rules, returns output."

**[Scroll to another method, ~line 80]**
> "Another rule: how to clear subsequent selections. No databases involved. No HTTP. Just the rule."

**[Show the tests - open `tests/test_linkage_domain.py`]**
> "And look at the tests—no mocks needed. Create the object, call the method, verify the result. That's the power of pure domain logic."

**Key Points to Make:**
- ✅ No external dependencies
- ✅ Pure functions/methods
- ✅ Easy to test (no mocks)
- ✅ Portable (use anywhere)

---

## 📋 ACT 3: DOMAIN LOGIC IN WRONG PLACE (Screen Recording)

**Screen:** Open `routes/dashboard.py`, show the ORIGINAL (before refactoring) version

**[If you want, we can revert to show the original 78-line function]**

### **Narration Script:**

**[Showing the send_chat_message function BEFORE refactoring]**
> "Now look at this route. It's mixing HTTP, domain logic, and infrastructure."

**[Scroll to message building code, lines 185-201]**
> "This block—building the message array—that's domain logic. It's a business rule: 'messages need system prompt first, then history, then user message.' But it's buried in a route."

**[Scroll to token trimming, lines 203-208]**
> "This too—context window management. That's a business rule: 'trim at 90%, keep last 5 messages.' But it's tied to Flask and the route."

**[Pause on the function]**
> "Can we test this message building logic without Flask? No. Can we use it in a CLI tool? No. Can we explain the business rule to a non-programmer? Not easily."

**Key Points to Make:**
- ❌ Domain logic mixed with HTTP
- ❌ Can't test in isolation
- ❌ Can't reuse elsewhere
- ❌ Hard to understand the business rules

---

## 📋 ACT 4: THE FIX (Optional - Simple Version)

**Two options here:**

### **OPTION A: Just Show The After**

**Screen:** Show `routes/dashboard.py` AFTER refactoring

**Narration:**
> "After refactoring, we extracted those business rules into functions. `_build_message_array`—pure domain logic. `_auto_trim_if_needed`—another pure function. Now the route just orchestrates. It doesn't contain business logic."

**[Show the extracted functions]**
> "These functions could move to a domain directory. They're ready. Zero Flask dependencies."

---

### **OPTION B: Do One Simple Live Extraction**

**If you want to show the process (adds ~2 minutes):**

**Screen:** Start with BEFORE code

**You say:** "Let's extract the message building."

**Claude does:** Extract `_build_message_array` (like we did in Episode 8A)

**You say:** "Now it's testable. Now it's reusable. Now it's clear."

**Run tests:** Show green

**You say:** "That's how you move domain logic from routes to domain."

---

## 📋 ACT 5: WHY THIS MATTERS (On Camera + Maybe Diagram)

**Your Script:**

> "Why go through this trouble? Three reasons:
>
> **Testability:** Test business rules without mocking frameworks.
>
> **Portability:** Use your logic in web apps, CLIs, desktop apps—anywhere.
>
> **Clarity:** When someone asks 'what does your app do?' you point to the domain layer. That's your unique value.
>
> Eric Evans wrote the book on this—Domain-Driven Design. The domain is the center. Everything else serves it.
>
> In our next episodes, we'll extract more domain models and build a proper domain layer. But now you know what to look for."

---

## 📊 OPTIONAL: B-ROLL / DIAGRAMS

**If you want visual aids:**

### **Diagram 1: Before**
```
┌─────────────────────────────────────┐
│         Routes (HTTP Layer)         │
│  ┌─────────────────────────────┐   │
│  │ Business Logic Mixed In 😢  │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### **Diagram 2: After**
```
┌─────────────────────────────────────┐
│         Routes (HTTP Layer)         │
│      (Just orchestration)           │
└──────────────┬──────────────────────┘
               │ calls
               ▼
┌─────────────────────────────────────┐
│      Domain Layer (Pure Logic)      │
│  ✅ No dependencies                 │
│  ✅ Easy to test                    │
│  ✅ Portable                        │
└─────────────────────────────────────┘
```

---

## 🎬 PRODUCTION WORKFLOW

### **What You Need to Record:**

1. ✅ **On-camera intro** (you did this)
2. ✅ **On-camera "why it matters"** (you did this)
3. **Screen recording: Good domain code walkthrough** (5 min)
   - Open `linkage_manager.py`
   - Scroll through, pause on key parts
   - Record your narration following the script
4. **Screen recording: Bad example walkthrough** (3 min)
   - Show original messy function
   - Point out the problems
5. **Optional: Screen recording: Show the fix** (2 min)
   - Show refactored code OR do one live extraction

**Total recording time: ~10-15 minutes**  
**Final edit: 6-8 minutes**

---

## 📝 SIMPLIFIED NARRATION SCRIPT (For Screen Recordings)

### **Part 1: Good Domain Code (linkage_manager.py)**

1. "This is a domain model."
2. "Look at the imports—just Python."
3. "Domain objects: LinkageRule, ComboBoxState."
4. "Business rules as methods—pure logic."
5. "Tests need no mocks."

### **Part 2: Bad Example (dashboard.py original)**

1. "This route mixes concerns."
2. "Message building—that's domain logic in the wrong place."
3. "Token trimming—another business rule buried here."
4. "Can't test without Flask. Can't reuse elsewhere."

### **Part 3: The Fix (dashboard.py refactored)**

1. "We extracted the business rules."
2. "Pure functions, no Flask dependencies."
3. "Now testable. Now portable. Now clear."

---

## 🎯 WHAT MAKES THIS VALUABLE

**Not toy examples:** Real production code with 400 tests  
**Not theory:** Show actual code, explain actual benefits  
**Not overwhelming:** One concept: domain models vs routes  
**Actionable:** Viewers can identify domain logic in their code

---

## 💡 ALTERNATE ENDING (Teaser for Next Episode)

**Instead of promising "we'll extract models next time," show the current state:**

> "We've identified domain logic that needs extraction. In the next episode, we'll build the proper domain layer, move these functions, and create a clean architecture. But for now—look for domain logic hiding in your routes. That's your starting point."

---

## ✅ MY RECOMMENDATION

**SIMPLEST VERSION** (Easiest to shoot, still valuable):

1. On-camera intro (from yesterday)
2. Screen walkthrough: Good domain code (`linkage_manager.py`) - 3 min
3. Screen walkthrough: Domain logic in wrong place (original `dashboard.py`) - 2 min
4. On-camera wrap-up: Why it matters (from yesterday)

**Total: ~6 minutes**

**No live coding. No complex extractions. Just show, explain, inspire.**

---

**Does this approach work for you?** Want me to adjust anything?


