# Design Patterns: Preferred Solutions

> 📝 **Template Note:** Replace these examples with patterns your team actually uses. Remove this file if patterns aren't a focus.

This document lists design patterns we find useful and when to apply them. Patterns are tools, not rules—use them when they solve a real problem, not because they're clever.

---

## When to Use Patterns

**Do Use Patterns When:**
- You recognize a recurring problem
- The pattern simplifies the solution
- Team members will understand the pattern
- The pattern makes future changes easier

**Don't Use Patterns When:**
- A simpler solution exists
- You're applying patterns for their own sake
- The problem doesn't match the pattern's intent
- The pattern adds unnecessary complexity

---

## Creational Patterns

**Factory Method**
- **When:** Need to create objects without specifying exact class
- **Benefit:** Flexibility in object creation
- **Example:** Creating different types of reports, notifications, or parsers

**Builder**
- **When:** Constructing complex objects step by step
- **Benefit:** Clear, readable object construction
- **Example:** Building configuration objects, queries, or test data

---

## Structural Patterns

**Adapter**
- **When:** Need to make incompatible interfaces work together
- **Benefit:** Integrate third-party libraries without changing your code
- **Example:** Wrapping external APIs, converting data formats

**Dependency Injection**
- **When:** Components need external dependencies
- **Benefit:** Testability and flexibility
- **Example:** Passing database connections, services, or configuration to objects
- **Note:** This is arguably the most important pattern for testable code

**Repository**
- **When:** Need to separate data access from business logic
- **Benefit:** Business logic doesn't know about databases
- **Example:** UserRepository, OrderRepository abstract data storage

---

## Behavioral Patterns

**Strategy**
- **When:** Need to swap algorithms or behaviors at runtime
- **Benefit:** Flexibility without conditionals
- **Example:** Different sorting algorithms, payment processors, or validation rules

**Template Method**
- **When:** Algorithm structure stays the same, but steps vary
- **Benefit:** Reuse common structure, customize specific parts
- **Example:** Data processing pipelines, test setup/teardown

**Observer**
- **When:** Objects need to react to changes in other objects
- **Benefit:** Loose coupling between components
- **Example:** Event systems, UI updates, notification systems

---

## Patterns We Favor

List the patterns your team uses most often and specific guidance on how you prefer to implement them. Examples:

- **Dependency Injection**: Prefer constructor injection for required dependencies
- **Repository Pattern**: Keep repositories focused on a single aggregate root
- **Strategy Pattern**: Use when you have 3+ conditional branches doing similar things
- **Factory Method**: Better than complex constructors or multiple constructor overloads

---

## Anti-Patterns to Avoid

**God Objects**
- Classes that know or do too much
- **Instead:** Split into focused, single-responsibility classes

**Premature Abstraction**
- Creating patterns before you need them
- **Instead:** Wait until you see the pattern emerge naturally (Rule of Three)

**Pattern Obsession**
- Using patterns because they exist, not because they help
- **Instead:** Start simple, add patterns when complexity demands them

---

## Learning More

When facing a design challenge:
1. Understand the problem fully first
2. Consider if a simple solution exists
3. If complexity persists, explore relevant patterns
4. Apply the pattern, then refactor based on actual use
5. Document your decision in [decisions.md](decisions.md)

---

## Domain/Infrastructure Separation for Real-Time Features

**Pattern**: Separate pure domain logic from timing/polling infrastructure

**When to Use**:
- Features involving timers, intervals, or async operations
- Logic that needs to be testable without real time passing
- Real-time detection (silence, activity, timeouts)

**Structure**:
```
Domain (Pure Logic)              Infrastructure (Timing)
├── State tracking               ├── setInterval polling
├── Threshold comparisons        ├── Event coordination
├── isSomething() → boolean      ├── Callback invocation
└── Testable with fake time      └── Starts/stops intervals
```

**Example: Silence Detection**
```javascript
// Domain: SilenceDetector (testable, no timers)
class SilenceDetector {
    onSpeechStart(timestamp) { this.speechActive = true; }
    onSpeechEnd(timestamp) { this.speechActive = false; this.lastSpeechTime = timestamp; }
    isSilent(currentTime) { return !this.speechActive && (currentTime - this.lastSpeechTime) >= threshold; }
}

// Infrastructure: SilenceCheckingService (handles timing)
class SilenceCheckingService {
    start(callback) { this.interval = setInterval(() => { if (detector.isSilent()) callback(); }, 100); }
    stop() { clearInterval(this.interval); }
}
```

**Benefits**:
- Domain logic is trivially testable (pass fake timestamps)
- Infrastructure is simple (just polling)
- Debugging is clearer (domain or timing issue?)

---

## Interim Results for Continuous Activity Detection

**Pattern**: Use interim events to detect ongoing activity when final events are delayed

**Context**: Browser APIs often batch events. Chrome's speech recognition sends "final" results only at natural pauses—a user speaking for 10 seconds without pausing gets ONE final transcript.

**Problem**: Naive activity detection misses ongoing activity between final events.

**Solution**: Enable interim/partial events and treat ANY event as evidence of activity:

```javascript
recognition.interimResults = true;

recognition.onresult = function(event) {
    // ANY result = user is speaking
    activityDetector.markActive();

    // Only USE final results
    if (result.isFinal) {
        processTranscript(result);
        activityDetector.markInactive();
    }
};
```

**Applies To**:
- Speech recognition
- Streaming APIs
- Any event source with batching behavior

---

## Priority Ordering for Overlapping Detectors

**Pattern**: Check more specific conditions before general ones

**When**: Multiple patterns could match the same input, and one is a subset of another.

**Example**: "amber" (wake) vs "sleep amber" (sleep)
- User says "sleep amber"
- If we check wake first: matches "amber" → WRONG
- If we check sleep first: matches "sleep amber" → CORRECT

```javascript
detect(input) {
    if (this.matchesSpecific(input)) return 'specific';  // Check first
    if (this.matchesGeneral(input)) return 'general';    // Check second
    return null;
}
```

**General Rule**: Order from most-specific to least-specific.

---

*Update this file as you discover patterns that work well for your team and domain. Remove patterns that don't add value. Make it your own.*
