# Claude Code Instructions

**CRITICAL: Read the knowledge base at the start of EVERY session.**

## Session Startup Checklist

1. Read `knowledge-base/index.md`
2. Read `knowledge-base/style-guide.md`
3. Read `knowledge-base/working-agreement.md`
4. Read `knowledge-base/testing.md` before any coding
5. Review recent git commits: `git log -5 --oneline`

## Development Methodology

### Test-First Development (TDD) - MANDATORY

**NEVER write production code without a failing test first.**

The Red-Green-Refactor cycle:
1. **RED**: Write ONE failing test
2. **GREEN**: Write minimal code to pass that test
3. **REFACTOR**: Improve code quality while tests pass
4. **COMMIT**: Commit with Arlo Belshee notation
5. **REPEAT**: Next test

### Domain Model First

- Start with pure domain logic (no framework dependencies)
- Keep business rules in domain layer
- Services coordinate; domain objects contain logic
- Domain objects should be easy to test without mocks

### Commit Notation (Arlo Belshee)

- `f` = Feature (new functionality)
- `r` = Refactoring (no behavior change)
- `t` = Test only
- `d` = Documentation
- `!` = Integration risk
- `!!` = High risk

Example: `f Add OllamaProvider for local LLM support`

### Always Run Full Test Suite

```bash
PYTHONPATH="." ./venv/bin/python -m pytest tests/ -q
```

Run after EVERY change. No exceptions.

### When Things Break

Follow STOP-CHECK-REVERT protocol from knowledge-base/index.md:
1. STOP all feature work
2. CHECK last working state
3. VERIFY architecture
4. REVERT if needed
5. VERIFY working state before continuing

## Project Architecture Notes

- Main entry point: `prompt_manager_app.py`
- Dashboard at: `/dashboard`
- Two Flask apps exist - always modify `prompt_manager_app.py`
- Feature flags: `settings/feature_flags.json`

## Remember

- Clarity over cleverness
- Write as if teaching tomorrow's reader
- Tests are living documentation
- Always push after commit
