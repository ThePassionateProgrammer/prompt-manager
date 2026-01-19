# Architectural Decision Records (ADRs)

> 📝 **Template Note:** Record your actual decisions here. The example below shows the format - replace it with your real ADRs.

This document captures important architectural and design decisions for the project. Recording decisions helps future contributors (including your future self) understand why things are the way they are.

---

## Why Document Decisions?

**Context fades quickly**
- What seemed obvious in the moment becomes mysterious later
- Without context, changes get reversed or repeated

**Decisions have consequences**
- Understanding trade-offs prevents naive "improvements" that backfire
- New team members can see the reasoning behind current architecture

**Learning compounds**
- Reviewing past decisions reveals patterns
- Mistakes become lessons when documented

---

## When to Document a Decision

Record decisions that:
- **Affect architecture** - Structure, layers, major components
- **Involve trade-offs** - You chose one approach over alternatives
- **Are controversial** - Team debated the best approach
- **Constrain future work** - Later decisions depend on this choice
- **Might surprise others** - "Why did they do it this way?"

Don't document:
- Trivial or obvious choices
- Easily reversible decisions
- Standard practices or patterns

---

## Decision Template

Use this format for each decision:

### [Decision Title] - [Date]

**Context**
What situation forced this decision? What problem are we solving?

**Decision**
What did we decide to do?

**Alternatives Considered**
What other options did we evaluate?
- Option A: [description and why we rejected it]
- Option B: [description and why we rejected it]

**Consequences**
What are the positive and negative outcomes of this decision?
- **Benefits:** What do we gain?
- **Trade-offs:** What do we lose or what becomes harder?
- **Risks:** What could go wrong?

**Status**
Active | Superseded by [Decision #] | Deprecated

---

## Example Decision Record

### Use Repository Pattern for Data Access - 2024-01-15

**Context**
We need to persist users, orders, and products. Current code directly uses database queries scattered throughout business logic, making testing difficult and coupling domain logic to SQL.

**Decision**
Implement Repository pattern to abstract data access. Each domain object gets a repository interface (UserRepository, OrderRepository) implemented by concrete database repositories.

**Alternatives Considered**
- **Active Record:** Objects save themselves. Rejected because it tightly couples domain logic to persistence.
- **Direct SQL everywhere:** Current approach. Rejected because it makes testing hard and violates separation of concerns.
- **ORM without abstraction:** Use ORM directly in business logic. Rejected because it still couples to a specific ORM library.

**Consequences**
- **Benefits:** Business logic becomes testable with mock repositories. Can swap databases without changing domain code. Clear separation of concerns.
- **Trade-offs:** Extra abstraction layer adds some complexity. More files to maintain.
- **Risks:** Over-abstraction if repositories get too generic. Must keep interfaces focused.

**Status**
Active

---

## Your Decision Records

Start adding your decisions below:

---

### Use Interim Results for Silence Detection - 2026-01-19

**Context**
Hands-free mode needs to auto-send messages after the user stops speaking. Initial implementation used Chrome's "final" transcript events to start a silence countdown. Users reported messages sending while they were still speaking.

**Root Cause Discovery**
Chrome's webkitSpeechRecognition batches continuous speech into phrases, only sending "final" results at natural pauses. A user speaking for 10 seconds without pausing receives ONE final transcript. The silence timer started after that transcript and fired 8 seconds later—even though the user continued speaking.

**Decision**
Enable `interimResults = true` in speech recognition. Treat ANY result (interim or final) as evidence of ongoing speech, resetting the silence timer. Only process final results for actual transcription.

**Alternatives Considered**
- **Longer timeout (15+ seconds):** Rejected because it makes the system feel sluggish
- **Audio level detection:** Rejected because Web Speech API doesn't expose audio levels
- **Speech-end event:** Rejected because Chrome's `onend` fires ~10 seconds after speech stops, not immediately

**Consequences**
- **Benefits:** Accurate silence detection regardless of how Chrome batches transcripts. Natural feel—users can speak as long as they want.
- **Trade-offs:** More frequent events to process (every ~100ms while speaking). Slightly more complex event handling.
- **Risks:** None identified. Interim results are the intended API for this use case.

**Status**
Active

---

### Separate Domain Logic from Timing Infrastructure - 2026-01-19

**Context**
Silence detection requires both pure logic (has enough time passed?) and timing infrastructure (polling every 100ms). Initially combined in one class, making it hard to test without real timers.

**Decision**
Split into two classes:
- `SilenceDetector` (domain): Pure logic with `onSpeechStart()`, `onSpeechEnd()`, `isSilent(timestamp)`. No timers. Testable by passing fake timestamps.
- `SilenceCheckingService` (infrastructure): Manages setInterval, checks detector, invokes callback.

**Alternatives Considered**
- **Single class with mockable timer:** More complex testing setup, mixed responsibilities
- **Event-based approach:** Overkill for simple polling, adds unnecessary abstraction

**Consequences**
- **Benefits:** Domain logic has 100% test coverage with simple unit tests. Timing bugs are isolated to one small file. Clear separation of concerns.
- **Trade-offs:** Two files instead of one. Requires understanding both to see full picture.
- **Risks:** None. Pattern is well-established (Repository pattern applies same principle to data access).

**Status**
Active

---

## Tips for Writing Good ADRs

**Be concise** - Aim for clarity, not completeness. One page is ideal.

**Capture alternatives** - Show you considered options thoughtfully.

**Focus on "why"** - The decision itself is visible in code; explain the reasoning.

**Update status** - When decisions change, mark them superseded rather than deleting them.

**Write soon after deciding** - Capture context while it's fresh.

---

*Decision records are most valuable when revisited. Review them when making related decisions, onboarding new team members, or evaluating whether to change direction.*
