# Testing: Test-First Development

We practice strict test-first development using the red-green-refactor cycle. Tests aren't just verification—they're design tools that reveal how the code wants to be shaped.

---

## The Red-Green-Refactor Cycle

**One Test at a Time**
We write exactly one test, make it pass, refactor, and commit. Then move to the next test. This disciplined rhythm creates quality code through small, verified steps.

**🔴 RED - Write a Failing Test**
- Write ONE test for the next small piece of behavior
- Run it and watch it fail (proving the test works)
- The failure message should be clear and specific
- Don't write the next test yet

**🟢 GREEN - Make It Pass**
- Write the simplest code that makes THIS test pass
- Don't worry about perfection—just get to green
- It's okay if the implementation is naive or even hardcoded
- Don't anticipate future tests—solve only the current one

**🔵 REFACTOR - Improve the Design**
- Now that tests pass, improve the code
- Listen to what the code is telling you
- Remove duplication, clarify names, extract concepts
- Run tests after each small refactoring
- Commit when refactoring is complete and tests are green

**Repeat** - Write the next test. One test at a time reveals the design incrementally.

---

## Why Test First?

**Discovery**
- Tests reveal how the code wants to be shaped
- Writing tests first exposes design problems immediately
- The code emerges from the tests, not the other way around
- Small steps prevent over-engineering

**Better Design**
- Forces you to think about behavior before implementation
- Encourages small, focused, testable units
- Makes dependencies explicit (especially with pure domain model)

**Confidence**
- Every line of code has a test that drove it into existence
- Safe to refactor fearlessly—tests catch mistakes
- Green bar means the system works

**Truth**
- Tests don't lie—they either pass or fail
- The red-green-refactor cycle provides constant feedback
- You always know where you stand

---

## What to Test

**Do Test:**
- Behavior, not implementation
- Business rules in the domain model
- Edge cases and boundary conditions
- Public interfaces and contracts
- Recently fixed bugs (regression prevention)

**Don't Test:**
- Private implementation details (test through public interface)
- Framework or library code (trust it works)
- Trivial pass-through code
- How the code works internally (only what it does)

---

## Writing Good Tests

**One Behavior Per Test**
- Each test should verify one specific thing
- Clear pass/fail: either it works or it doesn't
- Name tests to describe the behavior: `test_empty_cart_has_zero_total()`

**Arrange-Act-Assert Pattern**
```
# Arrange - Set up test data and conditions
cart = ShoppingCart()

# Act - Execute the behavior being tested
total = cart.calculate_total()

# Assert - Verify the expected outcome
assert total == 0
```

**Keep Tests Simple**
- Tests should be easier to understand than the code they test
- Avoid complex logic in tests
- Make test failures obvious and debuggable

---

## Test-Driven Development Tips

**Discipline Creates Freedom**
- Write exactly one test at a time—resist writing multiple
- Take the smallest possible step to green
- Let the test tell you what code to write
- Never skip the refactor step (that's where design emerges)
- Commit after each green refactor
- Trust the process—quality emerges from rhythm

**Always Run the Full Test Suite**
- **CRITICAL**: Run the complete test suite, not just the test you're working on
- Tests are fast enough to run all of them every time
- Catches regressions immediately (changes that break existing functionality)
- Prevents integration gaps (when unit tests pass but full system fails)
- Example: Your new test mocks method A, but production calls method B
- Full suite reveals what actually works vs what you think works
- Make this part of your testing methodology—no exceptions

**Pure Domain Model Benefits**
- Business logic has no external dependencies
- Tests run fast (no I/O, no mocks)
- Domain objects are easy to construct and test
- Services coordinate; domain objects contain logic

---

## When Tests Are Hard to Write

If testing feels difficult, your code might be:
- Doing too much (violating single responsibility)
- Too tightly coupled to dependencies
- Missing clear interfaces
- Mixing concerns (business logic with infrastructure)

**Solution:** Refactor to make code more testable. See [refactoring.md](refactoring.md).

---

## Debugging with Timestamps

When debugging timing-related issues (async, events, timeouts), add timestamps to trace the actual flow:

**Pattern**: Log timestamps at key points, then analyze the gaps

```javascript
console.log('[Feature] Event A at', Date.now());
// ... later ...
console.log('[Feature] Event B at', Date.now());
```

**Analysis**:
```
Event A at 1768849318117
Event B at 1768849326118  ← 8 seconds gap, expected was 5
```

**Key Insight**: The problem is often not your code—it's understanding when external systems send events. Log timestamps to discover actual behavior vs assumed behavior.

**Example Discovery**: Chrome's speech recognition sends "final" transcripts at natural pauses, not continuously. Timestamps revealed 10-second gaps between transcripts during continuous speech.

---

## Browser API Behavior Discovery

Browser APIs often behave differently than documentation suggests. When debugging:

1. **Don't trust assumptions** - Log actual event timing
2. **Read between the lines** - "Continuous" recognition may still batch results
3. **Enable all events** - Interim/partial events reveal hidden activity
4. **Test edge cases** - What happens during rapid speech? Long pauses? Interruptions?

**Example**: `webkitSpeechRecognition` with `continuous: true` still only sends final results at phrase boundaries—not after every word.

---

*Testing is a skill that improves with practice. Start simple, stay disciplined with the red-green-refactor cycle, and let tests guide you toward better design.*
