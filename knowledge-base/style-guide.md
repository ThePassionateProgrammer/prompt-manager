# Code Style Guide

> 📝 **Template Note:** Customize this file for your project's specific conventions, or delete sections that don't apply.

This guide defines coding standards and conventions for our project. Consistency makes code easier to read, maintain, and collaborate on.

---

## General Principles

**Clarity Over Cleverness**
- Write code that's easy to understand, not code that shows off
- If it needs extensive comments to explain, it probably needs refactoring
- Choose obvious solutions over clever ones

**Naming Matters**
- Use descriptive names that reveal intent
- Functions and methods should be verbs: `calculateTotal()`, `validateInput()`
- Classes and types should be nouns: `UserAccount`, `OrderProcessor`
- Booleans should read like questions: `isValid`, `hasPermission`, `canEdit`

**Keep It Small**
- Functions should do one thing well
- Classes should have a single, clear responsibility
- Files should be cohesive and focused

---

## Code Organization

**File Structure**
- Group related functionality together
- Keep public interfaces at the top
- Internal/private implementation below
- One primary class/concept per file

**Imports/Dependencies**
- Standard library first
- Third-party libraries next
- Local project imports last
- Alphabetize within each group

---

## Formatting

**Indentation**
- Use consistent indentation (typically 2 or 4 spaces, or tabs—pick one)
- Be consistent across the entire project

**Line Length**
- Aim for 80-120 characters per line
- Break long lines at logical points
- Don't sacrifice readability for line length rules

**Whitespace**
- Use blank lines to separate logical sections
- Add space around operators: `x = a + b` not `x=a+b`
- One statement per line

---

## Comments and Documentation

**When to Comment**
- Explain *why*, not *what*
- Document non-obvious decisions
- Warn about gotchas or edge cases
- Provide examples for complex APIs

**When NOT to Comment**
- Don't explain what the code obviously does
- Don't leave commented-out code (use version control instead)
- Don't apologize for code quality (fix it instead)

---

## Dead Code Policy

**Delete dead code immediately.** It's in version control if we ever need it.

Dead code includes:
- Unused functions, classes, or modules
- Commented-out code blocks
- Duplicate implementations (e.g., Python model when JavaScript is the actual runtime)
- Experimental code that didn't pan out

**Why delete?**
- Dead code creates confusion about what's actually used
- It adds maintenance burden
- It can mislead future readers (including Claude)
- Git preserves history - nothing is truly lost

**Before deleting, ask:**
- Is this code actually called anywhere?
- Is there a single source of truth? (e.g., one state machine, not two)
- Would keeping this cause confusion?

---

## Refactoring Philosophy

**"Make the change easy, then make the easy change."** -- Kent Beck

Before adding new features:
1. Examine the existing code
2. Ask: Would refactoring first make this easier?
3. Update stale documentation (code is the one true source)
4. Clean up dead code
5. Then add the feature

Refactoring is not optional cleanup -- it's preparation for the next change.


**Documentation**
- Public APIs and interfaces need clear documentation
- Include parameter descriptions and return values
- Provide usage examples for complex functionality

---

## Error Handling

- Fail fast and loudly during development
- Provide helpful error messages
- Don't swallow exceptions silently
- Validate input at boundaries

---

## Testing Considerations

- Write testable code (see [testing.md](testing.md))
- Avoid tight coupling to external dependencies
- Make dependencies explicit and injectable
- Keep side effects isolated and obvious

---

## Python Conventions

**Language:** Python 3.x

**Testing:**
- Use `pytest` as the test framework
- Use Approval Tests when appropriate for snapshot/golden master testing
- Focus on unit-level testing
- Test file naming: `test_*.py` or `*_test.py`
- One test class per production class (typically)

**Application Structure:**
- Apps should have a CLI interface
- CLI enables end-to-end testing from command line
- Keep CLI thin—delegate to domain model and services

**Code Style:**
- Follow PEP 8 conventions
- Use type hints for function signatures
- Prefer explicit over implicit
- Use descriptive variable names (not abbreviated)

**Imports:**
- Standard library first
- Third-party libraries next
- Local application imports last
- Alphabetize within each group

**Example Test Structure:**
```python
# test_order.py
import pytest
from domain.order import Order

class TestOrder:
    def test_empty_order_has_zero_total(self):
        # Arrange
        order = Order()

        # Act
        total = order.calculate_total()

        # Assert
        assert total == 0
```

---

## Git Commits

**Arlo Belshee Commit Notation**

We use Arlo Belshee's notation to communicate commit intent and risk level:

- **`f`** = Feature (new functionality added)
- **`r`** = Refactoring (code structure improved, no behavior change)
- **`t`** = Test (test added/updated, no production code change)
- **`d`** = Documentation (docs only)
- **`!`** = Risk indicator (integration concerns, breaking changes possible)
- **`!!`** = High risk indicator (significant architectural changes)

**Examples:**
- `f Add OllamaProvider for local LLM support`
- `r Extract model catalog to domain layer`
- `f! Fix broken OpenAI chat by correcting method name` (feature fix with integration risk)
- `r!! Migrate to new provider architecture` (high-risk refactoring)

**Commit Message Structure:**
```
<notation> <short summary>

What Changed:
- Bullet list of changes

Why:
- Explanation of motivation

Test Results: (if applicable)
- Before/after test counts
- Which tests were fixed/added
```

**Commit Discipline:**
- Commit after each successful red-green-refactor cycle
- One logical change per commit
- All tests must pass before committing (run full suite)
- Include test results in commit message when fixing bugs

---


*These are our conventions for Python development. Consistency across the codebase makes collaboration easier.*
