# Memory Cards: Hands-Free Voice Refactoring Session

## Card 1: RED-GREEN-REFACTOR Discipline in Practice

**Context**: Large refactoring of hands-free voice system over multiple commits

**Pattern**:
1. **RED Phase**: Write comprehensive tests FIRST (20-30 tests per module)
2. **GREEN Phase**: Implement minimal code to make tests pass
3. **REFACTOR Phase**: Extract classes, clean up, maintain tests passing
4. **Commit**: Clear commit message explaining all three phases

**Key Insight**: 
- Writing tests first forces you to think about the API design
- Tests become executable documentation
- Refactoring is safe because tests catch regressions
- Each commit should show: tests added, implementation, refactoring done

**Example**:
```
RED: Created tests/js/command_detector.test.js (23 tests)
GREEN: Created command_detector.js (passes all tests)
REFACTOR: Integrated into voice_interaction.js
COMMIT: "Add CommandDetector for Ember command word system"
```

**When to Apply**: Any feature work where you're adding new domain logic

---

## Card 2: Pure Domain Models Pattern

**Context**: Voice system needed testable business logic

**Pattern**:
- **Pure Domain Models** = Zero browser API dependencies
- Business logic in pure classes (WakeWordDetector, CommandDetector, TranscriptProcessor)
- Browser APIs only in integration layer (voice_interaction.js)
- Dependency injection for everything

**Structure**:
```javascript
// PURE (easily testable)
class WakeWordDetector {
    detect(transcript) {
        // Pure logic, no DOM, no browser APIs
        return { matched: true, type: 'wake' };
    }
}

// INTEGRATION (uses browser APIs)
voiceRecognition.onresult = (event) => {
    const transcript = event.results[0].transcript;
    const result = wakeWordDetector.detect(transcript);  // Call pure model
    // Handle result with browser APIs
};
```

**Benefits**:
- Unit tests run in milliseconds (no browser needed)
- 100% coverage of business logic
- Easy to reason about
- Future-proof (can swap browser APIs)

**When to Apply**: Any feature with complex logic

---

## Card 3: Integration Testing Strategy

**Context**: Needed to verify timing accuracy beyond unit tests

**Discovery**: Unit tests with fake timers can miss timing bugs

**Three Essential Integration Tests**:
1. **Timing Accuracy** - Use REAL timers to verify millisecond precision
2. **Complete Flow** - Happy path from start to finish (not yet implemented)
3. **Browser API Quirks** - Smoke test actual browser behavior

**Key Insight**:
- Unit tests answer: "Does this logic work?"
- Integration tests answer: "Do these pieces coordinate correctly?"
- Most verification should be unit tests (fast, reliable)
- Integration tests catch: timing, coordination, API quirks

**Example** (from silence_timing_integration.test.js):
```javascript
test('should trigger silence callback within acceptable time range', (done) => {
    const startTime = Date.now();  // REAL timer
    const onSilenceDetected = () => {
        const elapsed = Date.now() - startTime;
        expect(elapsed).toBeGreaterThanOrEqual(1000);
        expect(elapsed).toBeLessThan(1500);  // Verify actual timing
        done();
    };
    // ... test using real setInterval
});
```

**When to Apply**: Features with timing requirements, state coordination, browser API usage

---

## Card 4: Lazy Evaluation for Runtime Configuration

**Context**: SilenceDetector threshold wasn't loading from user settings

**Problem**: 
```javascript
// WRONG - captures value at construction time
constructor(options) {
    this.threshold = getSilenceThreshold();  // Gets default 3000ms
}
// Later: user loads settings, changes to 4000ms
// But detector still has 3000ms!
```

**Solution**:
```javascript
// RIGHT - lazy evaluation
constructor(options) {
    this.explicitThreshold = options.silenceThreshold ?? null;
}

getSilenceThreshold() {
    return this.explicitThreshold ?? getSilenceThreshold();  // Check runtime
}

isSilent() {
    return elapsed >= this.getSilenceThreshold();  // Call getter
}
```

**When to Apply**: 
- Configuration loaded asynchronously
- Values that can change at runtime
- Need both default and override behavior

---

## Card 5: Extracting Complex Logic to Processor Classes

**Context**: voice_interaction.js had 80+ lines of nested conditionals

**Pattern**: Extract decision logic to dedicated "Processor" class

**Before**:
```javascript
// 80 lines of nested if/else in event handler
if (wakeWord && state === 'WAKE_LISTENING') {
    if (detection.matched) {
        if (detection.type === 'wake') {
            // Handle wake
        }
    }
}
// ... 70 more lines
```

**After**:
```javascript
// Clean processor
const result = transcriptProcessor.process(transcript);
switch (result.action) {
    case 'WAKE': handleWake(); break;
    case 'SLEEP': handleSleep(); break;
    // ... etc
}
```

**Processor Returns**:
```javascript
{
    action: 'WAKE'|'SLEEP'|'PAUSE'|'RESUME'|'REPEAT'|'TRANSCRIBE'|'IGNORE',
    shouldTranscribe: boolean,
    message: string|null
}
```

**Benefits**:
- Nested conditions → flat switch statement
- Business logic fully unit-testable
- Easy to add new actions
- Clear separation of "what to do" vs "how to do it"

**When to Apply**: Complex conditional logic in event handlers

---

## Card 6: Observer Pattern vs Callbacks Decision Framework

**Context**: Deciding whether to refactor callbacks to events

**Decision Framework**:

**Use Callbacks When**:
- 1:1 relationship (one producer, one consumer)
- Handler is required for service to work
- Simple, direct flow
- Current approach: `service.start(onSuccess, onError)`

**Use Observer Pattern When**:
- Need 3+ handlers for same event
- Handlers are optional (logging, analytics, UI updates)
- Dynamic listener registration
- Building plugin/extension system
- Future approach: `service.on('success', handler1); service.on('success', handler2)`

**Hybrid Approach**:
- Keep callbacks for primary handlers
- Add events for optional/auxiliary handlers
- Gradual migration as needs evolve

**YAGNI Principle**: Don't refactor to Observer pattern "just because" - wait for actual need

**When to Apply**: Reviewing event-driven architecture

---

## Card 7: State Machine Testing Pattern

**Context**: ConversationMode has complex state transitions

**Testing Pattern**:
```javascript
test('should transition WAKE_LISTENING → LISTENING on wake word', () => {
    conversationMode.state = 'WAKE_LISTENING';
    conversationMode.onWakeWordDetected();
    expect(conversationMode.state).toBe('LISTENING');
});

test('should NOT transition if in wrong state', () => {
    conversationMode.state = 'PAUSED';
    conversationMode.onWakeWordDetected();  // Invalid transition
    expect(conversationMode.state).toBe('PAUSED');  // State unchanged
});
```

**Coverage Strategy**:
- Test each valid transition
- Test invalid transitions (should be ignored or error)
- Test state guards (conditions that prevent transitions)
- Test side effects (what happens during transition)

**When to Apply**: Any state machine implementation

---

## Card 8: Documentation Suite Pattern

**Context**: Complex feature needs user + developer docs

**Three-Document Pattern**:

1. **User Guide** (Brief, practical)
   - Quick start (5 steps)
   - Command reference
   - Troubleshooting
   - Use cases

2. **Developer Guide** (Comprehensive, technical)
   - Architecture overview
   - Module documentation with code examples
   - How to extend
   - Common patterns
   - Testing strategy

3. **Demo/Tour** (Narrative, engaging)
   - Step-by-step walkthrough
   - Real-world scenarios
   - Visual/video script

**Plus**: Discussion documents for architectural decisions (Observer Pattern)

**When to Apply**: Major feature completion

---

## Card 9: Backward Compatibility with Arrays

**Context**: Adding multiple wake words while keeping old API

**Pattern**:
```javascript
constructor(options = {}) {
    // Support both old (single) and new (array) API
    if (options.wakeWords) {
        this.wakeWords = Array.isArray(options.wakeWords) 
            ? options.wakeWords 
            : [options.wakeWords];
    } else if (options.wakeWord) {
        this.wakeWords = [options.wakeWord];  // Convert to array
    } else {
        this.wakeWords = getWakeWords();  // Default array
    }
    
    // Backward compatibility getter
    this.wakeWord = this.wakeWords[0];  // Expose first as single
}

// Internal logic uses array
detectWakeWord(transcript) {
    return this.wakeWords.some(word => matches(transcript, word));
}
```

**Benefits**:
- Old code still works: `new Detector({ wakeWord: 'hey' })`
- New code more powerful: `new Detector({ wakeWords: ['hey', 'hi'] })`
- Internal code simplified (one path through array)

**When to Apply**: Adding array support to existing single-value APIs

---

## Card 10: Commit Message Structure for Refactoring

**Context**: Need to explain complex refactorings clearly

**Template**:
```
Title: Brief summary (50 chars)

Brief description of what and why.

**RED Phase:**
- Created tests/js/X.test.js (N tests)
- Tests cover: [key scenarios]

**GREEN Phase:**
- Created src/X.js
- Implemented: [key features]

**REFACTOR Phase:**
- Updated Y.js to use new class
- Reduced complexity from X lines to Y lines
- Maintained all existing behavior

**Benefits:**
1. [Benefit 1]
2. [Benefit 2]

**Test Results:**
- All N tests passing
- No regressions

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**When to Apply**: RED-GREEN-REFACTOR commits

---

## Processes & Recipes Created

### Process 1: Test-First Feature Development
1. Write tests defining the API (RED)
2. Implement minimal code to pass (GREEN)
3. Refactor while keeping tests green (REFACTOR)
4. Commit with structured message
5. Repeat for next feature

### Process 2: Pure Domain Model Extraction
1. Identify complex logic in browser-dependent code
2. Create pure class with zero dependencies
3. Write comprehensive unit tests
4. Inject dependencies from outside
5. Integration layer uses pure model

### Process 3: Integration Test Decision
1. Check if unit tests with mocks would miss the bug
2. Consider: Timing? Coordination? Browser APIs?
3. If yes to any: Write integration test with real dependencies
4. Keep integration tests minimal (3-5 total)

### Process 4: Documentation After Feature
1. Complete implementation with tests
2. Write user guide (brief, practical)
3. Write developer guide (technical, examples)
4. Create demo script/tour (narrative)
5. Write discussion docs for decisions
6. Cross-reference all docs

---

## Meta-Learning: Memory Card Integration

**Question from User**: "How can we more fluidly integrate these memory tools into our workflow?"

**Current Gap**: 
- Memory cards created after the fact
- Not referenced during development
- Knowledge base separate from code

**Potential Improvements**:

1. **Just-in-Time Memory**:
   - Create card immediately when pattern emerges
   - Reference existing cards during development
   - "This is pattern X from card Y"

2. **Code → Memory Card Links**:
   ```javascript
   /**
    * Pure domain model - See MEMORY_CARD_2_PURE_DOMAIN_MODELS.md
    */
   class WakeWordDetector { ... }
   ```

3. **Memory-First Development**:
   - Check knowledge base before solving problem
   - Apply existing patterns first
   - Create new card only if novel

4. **Automated Pattern Detection**:
   - Tool to scan commits for patterns
   - Suggest memory cards for recurring practices
   - Prompt to document new patterns

**Open Question**: How to make memory cards searchable and discoverable during development?

