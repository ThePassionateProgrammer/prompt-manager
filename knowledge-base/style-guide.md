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

*These are our conventions for Python development. Consistency across the codebase makes collaboration easier.*
