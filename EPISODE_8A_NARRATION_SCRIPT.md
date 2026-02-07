# Episode 8A: Safe Refactoring - Narration Script
**Target: 5-7 minutes final footage**

---

## OPENING (On Camera - 30 seconds)

**You say:**
> "We've built a working app with 10 features and 400 tests. But some functions are getting messy - mixing HTTP, business logic, and infrastructure. Today we'll use safe refactoring techniques from Fowler's 'Refactoring' and Feathers' 'Working Effectively with Legacy Code' to clean it up without breaking anything. Let's dive in."

---

## ACT 1: THE PROBLEM (Screen + Voiceover - 1 minute)

**Show:** `routes/dashboard.py` open, scroll to **line 163** (the `send_chat_message` function)

**You say:**
> "Here's our chat endpoint - 78 lines doing six different things. Let me trace through it..."

**Scroll slowly through the function, pausing at:**

- **Lines 167-175:** "HTTP parsing - getting data from the request"
- **Lines 177-183:** "Validation and provider lookup"  
- **Lines 185-201:** "Message array building - this is domain logic hiding in a route"
- **Lines 203-208:** "Token trimming - more domain logic"
- **Lines 210-211:** "Token calculation"
- **Lines 213-219:** "LLM API call"
- **Line 222:** "Token update"

**You say:**
> "Six responsibilities in one function. Can't test the message building without mocking Flask, the LLM provider, and the database. Let's fix it."

---

## ACT 2: EXTRACT METHOD #1 (Screen Recording - 2 minutes)

### **REFACTORING 1: Extract Message Building**

**Claude will make the change. You'll see the diff.**

**NARRATION CUES:**

**When you see GREEN lines (new function added around line 163):**
> "I'm extracting the message building into its own function. Notice - no Flask dependencies, no HTTP, just pure business logic. Takes three inputs, returns an array."

**Point out the new function:**
- "Clear docstring explaining what it does"
- "'Pure domain logic' - no Flask, no infrastructure"
- "Simple, focused, testable - just builds the message array"

**When you see RED lines (old code removed) and GREEN line (replacement):**
> "Now the main function just calls our extracted method. 16 lines became 1 line. The function is shorter and its intent is clearer."

**AD LIB QUESTIONS (Optional):**
- "What makes this 'safe' refactoring?"
- "Why is this function better than the original?"
- "Could we test this without Flask now?"

**Accept the changes.**

**You say:**
> "Let's prove we didn't break anything. Running tests..."

**Claude runs tests. Show output.**

**You say:**
> "All green. That's the discipline - every refactoring keeps tests passing."

---

### **REFACTORING 2: Extract Token Management**

**Claude will make the change. You'll see the diff.**

**NARRATION CUES:**

**When you see GREEN lines (new function):**
> "Same pattern. Extract the token trimming logic - it's another domain concept about context window management."

**Point out:**
- "Takes messages, model, and auto_trim flag as input"
- "Returns messages and trimmed_count as a tuple"
- "Domain logic - when to trim (90% of context), how much to keep (5 messages)"

**When you see RED/GREEN replacement:**
> "Five lines become one. The function gets even clearer."

**Accept the changes.**

**You say:**
> "Tests again..."

**Claude runs tests. Show output.**

**You say:**
> "Still green. We've extracted two domain concepts and the function shrunk from 78 lines to 60. But we're not done."

---

## ACT 3: DEPENDENCY INJECTION (Screen Recording - 2 minutes)

**You say (on camera or voiceover):**
> "These extracted functions are better, but they still use global variables. Watch what happens when we inject dependencies instead."

**Show top of file (lines 15-17) - the globals:**

**You say:**
> "See these globals? provider_manager, token_manager, conversation_manager - created when the module loads. Our functions use them directly. That makes testing hard."

**Scroll to the send_chat_message function.**

**You say:**
> "Dependency injection means: don't create your dependencies, receive them. Let me show you."

**Claude will make the change. You'll see the diff.**

**NARRATION CUES:**

**When you see GREEN lines (new DI code at top of function):**
> "Three lines. Get managers from Flask's app config. If tests inject mocks, we use those. Otherwise, fall back to the globals. Backward compatible."

**Point out the pattern:**
- "provider_mgr = current_app.config.get('PROVIDER_MANAGER', provider_manager)"
- "First parameter: what tests will inject. Second parameter: fallback to global."

**You say:**
> "Now look what changes in the function body..."

**When you see RED/GREEN replacements throughout function:**
> "Every place we used the global, we now use the injected version. provider_manager becomes provider_mgr. token_manager becomes token_mgr."

**Point out the pattern - show 2-3 examples as you scroll:**
- "provider_mgr.get_provider() instead of provider_manager.get_provider()"
- "token_mgr.calculate_token_usage() instead of token_manager.calculate_token_usage()"

**Accept the changes.**

**You say:**
> "Now tests can do this..." (show on screen or just say):

```python
app.config['PROVIDER_MANAGER'] = MockProvider()
app.config['TOKEN_MANAGER'] = MockTokenManager()
```

**You say:**
> "And our routes will use the mocks. No more global state in tests. Let's verify..."

**Claude runs tests. Show output.**

**You say:**
> "All green. Same behavior, better design."

---

## ACT 4: WHAT WE LEARNED (On Camera - 1 minute)

**You say:**
> "In 10 minutes we applied three legacy code techniques to fresh code:
>
> **Extract Method** - revealed hidden domain concepts. Message building and token trimming were hiding in that 78-line function.
>
> **Dependency Injection** - made untestable code testable. Now tests can inject mocks instead of using globals.
>
> **Tests as Safety Net** - we ran tests after every change. Green tests mean we didn't break anything.
>
> The function is shorter, clearer, and more testable. But we're not done. In Episode 8B, we'll extract those domain models properly and show you Domain-Driven Design in action.
>
> See you next time."

---

## AD LIB QUESTIONS (Use as needed)

**After Extract Method:**
- "What's the difference between Extract Method and just adding comments?"
- "How do we know what to extract?"
- "Why is 'pure domain logic' valuable?"

**After Dependency Injection:**
- "What's wrong with global variables?"
- "Why not just rewrite everything with DI from the start?"
- "How does this make testing easier?"

**After Tests:**
- "What would happen if we didn't have tests?"
- "How do we know we didn't break anything?"
- "Why run tests after every single change?"

---

## PRODUCTION NOTES

**Pacing:**
- Keep camera segments short (15-30 seconds each)
- Let the code diffs do the teaching
- Pause on diffs long enough for viewers to read

**B-Roll Ideas:**
- Test output (green checkmarks)
- Before/after line counts
- Diagram: Routes → Business → Domain layers

**Editing:**
- Cut aggressively - keep it tight
- Add captions for key terms (Extract Method, Dependency Injection)
- Music under screen recordings (low volume)

**Key Takeaway:**
Safe refactoring = Small steps + Tests always green + Reveal hidden concepts

