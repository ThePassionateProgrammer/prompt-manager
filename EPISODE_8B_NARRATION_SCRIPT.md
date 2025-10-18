# Episode 8B: Domain-Driven Design - Narration Script
**Target: 5-7 minutes final footage**

---

## OPENING (On Camera - 30 seconds)

**You say:**
> "In Episode 8A, we extracted functions and revealed domain concepts. Today we'll take those concepts and build a proper domain layer. This is Domain-Driven Design - putting your business rules at the center of your architecture. Let's see what we already have and what we can improve."

---

## ACT 1: WHAT IS A DOMAIN MODEL? (On Camera - 1 minute)

**You say:**
> "A domain model is your business logic with zero dependencies. No Flask, no databases, no frameworks. Just Python and your rules.
>
> Why? Because your business rules are your competitive advantage. Frameworks come and go. Databases change. But your core logic - that's unique to you. Protect it. Keep it pure.
>
> Let me show you one we already have."

---

## ACT 2: EXISTING DOMAIN MODEL (Screen Recording - 1.5 minutes)

**Show:** `src/prompt_manager/domain/linkage_manager.py`

**You say (voiceover):**
> "This is a domain model. 182 lines of pure business logic about template linkages."

**Scroll through, pausing at:**

- **Top of file (imports):** "Just Python. No Flask, no SQLAlchemy, nothing external."
- **Class definition:** "Domain objects - LinkageRule, ComboBoxState, LinkageManager"
- **Methods (scroll through a few):** "Business rules. When to create linkages, when to clear them, how to restore state."
- **Line 50-60 (pick a method):** "Look at this method - pure logic. Takes input, applies rules, returns output. Completely testable."

**You say:**
> "This is what domain models look like. But we have business logic scattered in our routes. Let's fix that."

---

## ACT 3: EXTRACT MESSAGE DOMAIN MODEL (Screen Recording - 2.5 minutes)

**You say (on camera or voiceover):**
> "Remember those functions we extracted in Episode 8A? _build_message_array and _auto_trim_if_needed? They're domain logic hiding in a route file. Let's extract them properly."

### **Step 1: Write the Test First**

**Claude creates:** `tests/unit/domain/test_conversation.py`

**NARRATION CUES:**

**When you see the test file:**
> "Test-first. We define what we want before we build it."

**Point out the test:**
```python
def test_conversation_builder_creates_message_array():
    builder = ConversationBuilder()
    messages = builder.build_messages(
        user_message="Hello",
        history=[],
        system_prompt="You are helpful"
    )
    
    assert len(messages) == 2  # system + user
    assert messages[0]['role'] == 'system'
    assert messages[1]['role'] == 'user'
```

**You say:**
> "Simple test. Create a builder, build messages, verify the structure. No mocks needed - it's pure logic."

**Claude runs the test - it fails (RED).**

**You say:**
> "Red. The domain model doesn't exist yet. Let's build it."

---

### **Step 2: Create the Domain Model**

**Claude creates:** `src/prompt_manager/domain/conversation.py`

**NARRATION CUES:**

**When you see the new file:**
> "New file in the domain directory. Zero dependencies."

**Point out the code:**

**Line 1-10 (imports and class definition):**
> "Just Python. No Flask. This is pure domain logic."

**Line 12-30 (build_messages method):**
> "The logic we extracted from the route, now in its proper home. Takes domain inputs, returns domain outputs."

**Line 32-45 (auto_trim method - if we include it):**
> "Context window management. Pure business rule - 'trim when you hit 90% of limit, keep the last 5 messages.' No infrastructure."

**Accept the changes.**

**Claude runs the test - it passes (GREEN).**

**You say:**
> "Green. We have a working domain model."

---

### **Step 3: Use It in the Route**

**Claude updates:** `routes/dashboard.py`

**NARRATION CUES:**

**When you see RED lines (old helper function removed):**
> "We're removing the helper function from the route..."

**When you see GREEN lines (import and usage):**
> "...and replacing it with our domain model."

**Point out:**
- **Import:** `from src.prompt_manager.domain.conversation import ConversationBuilder`
- **Usage:** `builder = ConversationBuilder()` then `messages = builder.build_messages(...)`

**You say:**
> "Now our route just orchestrates. It doesn't contain business logic."

**Accept the changes.**

**Claude runs all tests.**

**You say:**
> "All tests still pass. The route is simpler, the domain is explicit, and the logic is portable."

---

## ACT 4: WHY THIS MATTERS (On Camera - 1.5 minutes)

**You say:**
> "Why go through all this? Three reasons:
>
> **One: Testability.** 
> Before, testing message building required mocking Flask. Now? Just instantiate the domain object and call the method. No mocks.
>
> **Two: Portability.**
> This ConversationBuilder has no Flask dependency. Use it in a CLI tool, a desktop app, anywhere. Your business logic isn't tied to a web framework.
>
> **Three: Clarity.**
> The route is simpler. It says 'build messages' not 'append system prompt, extend history, append user message.' The 'what' is clear. The 'how' is in the domain.
>
> This is Domain-Driven Design. Your domain - your business rules - is the center. Everything else serves it. Routes serve it, databases serve it, UIs serve it.
>
> Eric Evans wrote the book on this. Martin Fowler preaches it. And now you've seen it in action."

---

## CLOSING (On Camera - 30 seconds)

**You say:**
> "We started with a 78-line function mixing six concerns. We used safe refactoring to extract methods. Then dependency injection to make it testable. And finally, proper domain models to make it clean.
>
> This is how you build software that lasts. Not by avoiding mess, but by continuously refactoring toward clarity.
>
> Code on, friends."

---

## AD LIB QUESTIONS (Use as needed)

**About Domain Models:**
- "What's the difference between a domain model and a helper function?"
- "Why keep domain models dependency-free?"
- "When should you extract a domain model?"

**About DDD:**
- "What does 'domain-driven' mean?"
- "How is this different from MVC?"
- "Is this overkill for small projects?"

**About Testing:**
- "How does this make testing easier?"
- "Do you still need integration tests?"
- "What's the test coverage of your domain layer?"

---

## ALTERNATIVE: SIMPLER VERSION (If time is tight)

**Skip the test-first cycle.**

Just:
1. Show the existing domain model (linkage_manager.py) - "Here's what good looks like"
2. Show the extracted functions in the route - "This is domain logic in the wrong place"
3. Show moving one to domain/ - "Now it's in the right place"
4. Explain why: testability, portability, clarity

**This version:** ~3-4 minutes instead of 5-7 minutes.

---

## PRODUCTION NOTES

**Pacing:**
- Episode 8B is conceptual - don't rush the explanations
- Let the "why" sink in
- Show before/after architecture diagrams if helpful

**B-Roll Ideas:**
- Directory structure (routes/ vs domain/)
- Test output showing no mocks needed
- Diagram: Routes → Services → Domain (with arrows pointing inward to domain)
- Book covers (Evans' DDD, Fowler's books)

**Editing:**
- Add visual callouts for "No dependencies!" when showing domain code
- Highlight the imports section to show purity
- Before/after comparison of test complexity

**Key Takeaway:**
Domain-Driven Design = Business logic with zero dependencies = Your competitive advantage

