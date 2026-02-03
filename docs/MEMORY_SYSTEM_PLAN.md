# Memory System Implementation Plan
**Status**: Deferred - Voice work prioritized
**Created**: January 16, 2026
**Context**: Plan for giving Ember (and other AIs in Prompt Manager) long-term memory

## Executive Summary

This plan outlines how to integrate a memory card system into Prompt Manager, enabling AIs like Ember to:
- Store and retrieve learned patterns across sessions
- Search accumulated knowledge
- Build on prior insights rather than starting fresh each time
- Create a feedback loop: learn → capture → reference → refine

**Core Philosophy**: The memory system should be a **muse, not a rulebook** - it surfaces relevant insights at the right time without constraining creativity.

---

## What We Learned From Today's Recovery

### Key Lessons (January 16, 2026)

1. **Two Flask Applications Exist**:
   - `prompt_manager_app.py` (root level) - The REAL app users run, serves `/dashboard`
   - `src/prompt_manager/web/app.py` - Different app, serves `/`, not actively used
   - **Critical**: Always verify which app the user actually runs before making changes

2. **Always Push After Commit**:
   - Had 10 commits from Sunday (Jan 11) that weren't pushed to GitHub
   - User couldn't see commit history or revert easily
   - **New Protocol**: Immediately push after every commit

3. **STOP-CHECK-REVERT Protocol** (added to knowledge base):
   - When user reports breaking changes: STOP immediately
   - Don't try to fix forward by adding more code
   - Check git status and identify last good commit
   - Revert to known good state first
   - Then investigate what went wrong

4. **Conversation Backup Strategy**:
   - Multiple backup files saved the day: `conversations.json.recovery-20260116-154334`
   - Important conversation with Ember recovered successfully
   - **Backup before major changes**: Always create timestamped backups

---

## Memory Card Data Model

### Core Structure

```python
@dataclass
class MemoryCard:
    """
    A memory card captures a learned pattern or insight.
    Designed to be muse-like: inspires, doesn't constrain.
    """
    id: str                          # UUID
    user_id: str                     # Owner of this memory card
    title: str                       # Brief, searchable title
    context: str                     # What problem/situation sparked this?
    pattern: str                     # The solution/approach
    key_insight: str                 # Core learning (1-2 sentences)
    example: Optional[str] = None    # Code example or usage
    benefits: Optional[str] = None   # Why this pattern works
    when_to_apply: Optional[str] = None  # Specific use cases
    process: Optional[str] = None    # Step-by-step recipe if applicable
    open_questions: Optional[str] = None  # Unanswered problems
    tags: List[str] = None           # Suggested + custom tags
    related_cards: List[str] = None  # IDs of related memory cards
    session_context: Optional[str] = None  # Session where this emerged
    created_at: datetime = None
    updated_at: datetime = None
    use_count: int = 0               # Track how often referenced
```

### Why This Structure

- Captures both **what** (pattern) and **why** (insight, benefits)
- `tags` enable discovery without rigid categorization
- `use_count` surfaces most valuable patterns over time
- `open_questions` captures learning edges
- `session_context` provides continuity between sessions
- **Per-User Design**: Each user has their own memory cards for privacy/personalization

---

## Implementation Architecture

### Phase 1: Backend Foundation

**New Files to Create**:
1. `src/prompt_manager/domain/memory_card.py` - Pure domain model
2. `src/prompt_manager/storage/memory_storage.py` - JSON-based persistence
3. `src/prompt_manager/business/memory_service.py` - Business logic layer
4. `src/prompt_manager/business/search_service.py` - Search with text + tags
5. `memory_cards.json` - Data storage file

**Key Patterns**:
- **Repository Pattern**: MemoryStorage abstracts persistence
- **Service Layer**: MemoryService coordinates operations
- **Pure Domain Models**: Zero dependencies on infrastructure

### Phase 2: API Routes

**New File**: `src/prompt_manager/web/routes/memory_routes.py`

API Endpoints:
- `GET /api/memory/cards` - List all cards with filters
- `GET /api/memory/cards/<id>` - Get specific card
- `POST /api/memory/cards` - Create new card
- `PUT /api/memory/cards/<id>` - Update card
- `DELETE /api/memory/cards/<id>` - Delete card
- `GET /api/memory/tags` - Get all tags
- `POST /api/memory/suggest` - Context-aware suggestions
- `POST /api/memory/cards/<id>/reference` - Track usage

**IMPORTANT**: These routes will go in `prompt_manager_app.py`, NOT `src/prompt_manager/web/app.py`

### Phase 3: Frontend UI

**New Files**:
1. `src/prompt_manager/templates/memory_cards.html` - Browser UI
2. `src/prompt_manager/static/js/memory-cards.js` - Frontend logic
3. `src/prompt_manager/static/css/memory-cards.css` - Styling

**UI Features**:
- Card browser with search and tag filtering
- Create/edit modal with all memory card fields
- Sort by: Most Recent, Most Used, Alphabetical
- Tag autocomplete with existing tags
- Related cards display

### Phase 4: Integration

**Chat Interface Integration**:
- Add "💡 Suggestions" panel that shows relevant memory cards based on conversation context
- Simple text matching initially (can upgrade to semantic search in v2)
- Click card to view full details
- Track when cards are referenced (increment use_count)

**Prompt Linking** (optional):
- Add `memory_card_refs` field to Prompt model
- Link prompts to relevant memory cards for cross-reference

---

## Search Strategy

### Text Search Algorithm

1. Search across multiple fields:
   - Title (highest weight)
   - Context
   - Pattern
   - Key insight
   - Example

2. Tag filtering (AND/OR logic)

3. Relevance ranking:
   - Exact title match = highest
   - Tag match + text match = high
   - Text match in key_insight = medium
   - Text match in example = lower

4. Sort by: relevance score, then use_count, then recency

### Context-Aware Suggestions

Given current conversation context, suggest relevant cards:
- Extract keywords from last 3 messages
- Search memory cards with those keywords
- Rank by relevance + use_count
- Show top 3-5 suggestions

---

## Migration & Import

### Import Existing Memory Cards

**Script**: `scripts/import_memory_cards.py`

Parse existing memory card documents (like `MEMORY_CARDS_REFACTORING_SESSION.md`) and convert to JSON format.

Features:
- Parse markdown sections (## Card headers)
- Extract Context, Pattern, Key Insight, etc.
- Generate UUIDs
- Set timestamps
- Auto-tag based on content keywords

### Export to Markdown

Support exporting memory cards to markdown for:
- Version control (Git)
- Sharing with others
- Backup/archival
- Documentation

---

## Key Design Decisions

### 1. Scope for V1
✅ **Include chat suggestions** - Show relevant cards based on conversation
✅ **Per-user private cards** - Each user builds their own knowledge base
✅ **Suggested + custom tags** - Autocomplete with common tags, allow new ones
✅ **Simple text search** - V2 can add semantic/vector search

### 2. Storage
✅ **JSON file-based** - Follows existing StorageManager pattern
✅ **One file per user** - Can split later if needed

### 3. Access Control
✅ **Private by default** - Memory cards belong to individual users
⏸️ **Sharing (future)** - V2 could add collaborative cards

---

## Example Memory Cards

### Card 1: RED-GREEN-REFACTOR Discipline

**Context**: Large refactoring of hands-free voice system with 225 tests

**Pattern**: Write tests first (RED), implement minimal code to pass (GREEN), then refactor (REFACTOR). Never skip to refactoring without green tests.

**Key Insight**: Test-first development prevents regression and builds confidence during complex refactors.

**Example**:
```python
# 1. RED - Write failing test
def test_silence_detection():
    assert silence_detector.is_silent(audio_data) == True

# 2. GREEN - Minimal implementation
def is_silent(audio_data):
    return True  # Simplest thing that passes

# 3. REFACTOR - Improve without changing behavior
def is_silent(audio_data):
    rms = audioop.rms(audio_data, 2)
    return rms < threshold
```

**Tags**: testing, tdd, workflow, discipline

**When to Apply**: During any feature development or refactoring with existing tests

---

### Card 2: STOP-CHECK-REVERT Protocol

**Context**: Dashboard broke after memory card implementation, user reported serious issues

**Pattern**: When user reports breaking changes:
1. STOP immediately - don't add more code
2. CHECK git status - identify last good commit
3. REVERT to known good state
4. Then investigate what went wrong

**Key Insight**: Fixing forward when things are broken often makes it worse. Revert first, understand second.

**Benefits**:
- Gets user back to working state quickly
- Prevents compounding errors
- Creates clean baseline for debugging

**When to Apply**: Any time user reports "things are broken" or "this used to work"

**Tags**: debugging, git, recovery, protocol

---

### Card 3: Two-App Architecture Awareness

**Context**: Modified wrong Flask app (src/prompt_manager/web/app.py) instead of the one user runs (prompt_manager_app.py)

**Pattern**: Before making changes, verify which entry point user actually runs:
1. Ask user how they start the app
2. Check which file they execute
3. Verify routes in that specific app
4. Test in the correct app, not assumptions

**Key Insight**: Multiple Flask apps can exist in same codebase. Always verify which one is actually being used.

**Open Questions**: Should we consolidate to one app? Or document the split better?

**Tags**: architecture, flask, verification, debugging

---

## Success Metrics

1. **Adoption**: Memory cards created per week
2. **Usefulness**: Average use_count per card (cards actually referenced)
3. **Discoverability**: Search → card view conversion rate
4. **Integration**: Prompts with memory_card_refs
5. **Continuity**: Evidence of session-to-session knowledge retention

---

## Future Enhancements (V2+)

1. **Semantic Search**: Vector embeddings for similarity matching
2. **Graph Visualization**: Show card relationships as interactive graph
3. **Auto-Suggest**: AI generates memory cards from conversations
4. **Version Control**: Track card evolution over time
5. **Collaborative Cards**: Multiple users contribute/refine
6. **Card Templates**: Pre-structured formats for different pattern types
7. **Integration with Git**: Link cards to commits/PRs

---

## Files Modified/Created (When We Resume)

### New Files:
1. `src/prompt_manager/domain/memory_card.py`
2. `src/prompt_manager/storage/memory_storage.py`
3. `src/prompt_manager/business/memory_service.py`
4. `src/prompt_manager/web/routes/memory_routes.py`
5. `src/prompt_manager/templates/memory_cards.html`
6. `src/prompt_manager/static/js/memory-cards.js`
7. `src/prompt_manager/static/css/memory-cards.css`
8. `scripts/import_memory_cards.py`
9. `memory_cards.json`

### Modified Files:
1. **`prompt_manager_app.py`** (NOT src/prompt_manager/web/app.py!) - Register memory routes
2. `src/prompt_manager/business/search_service.py` - Add memory card search
3. `src/prompt_manager/prompt.py` - Add memory_card_refs field
4. `src/prompt_manager/templates/chat_dashboard.html` - Add suggestions panel
5. `src/prompt_manager/static/js/chat_dashboard.js` - Add suggestion logic

---

## Related Documents

- Full implementation plan from plan mode: `/Users/davidbernstein/.claude/plans/toasty-juggling-mist.md`
- Knowledge base: `knowledge-base/index.md` (now includes recovery protocol)
- This document: `docs/MEMORY_SYSTEM_PLAN.md`

---

## Meta Note

This memory system implementation plan is itself an example of what memory cards enable - capturing complex multi-session knowledge so we can pick up exactly where we left off, without re-explaining context or re-making decisions.

**The Memory System is Its Own First Use Case** - we're capturing the process of building it!

When we're ready to implement this, we'll start with Phase 1 (backend foundation) and work incrementally, with tests and commits at each step.

---

**Status**: Ready to implement when voice work is complete and user is ready to proceed.

**Last Updated**: January 16, 2026
