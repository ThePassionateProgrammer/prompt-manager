# JavaScript Testing with Jest

This document describes how we test JavaScript modules in the Prompt Manager project.

---

## Testing Stack

**Framework:** Jest 29.7.0 with jsdom
- Modern JavaScript testing framework
- ES module support via experimental VM modules
- Browser API mocking via jsdom
- Comprehensive assertion library

**Test Environment:**
- Node.js with `--experimental-vm-modules` flag
- jsdom for DOM and browser API simulation
- Custom setup file for global mocks

---

## Running Tests

```bash
# Run all JavaScript tests
npm test

# Watch mode for development
npm run test:watch

# Generate coverage report
npm run test:coverage
```

**Test Location:**
- All JavaScript tests: `tests/js/**/*.test.js`
- Test setup: `tests/js/setup.js`
- Configuration: `package.json` (jest section)

---

## Test Structure

We follow the same Arrange-Act-Assert pattern as Python tests:

```javascript
test('should calculate total correctly', () => {
    // Arrange
    const cart = new ShoppingCart();
    cart.addItem({ price: 10.00, quantity: 2 });

    // Act
    const total = cart.calculateTotal();

    // Assert
    expect(total).toBe(20.00);
});
```

**Test Organization:**
- Group related tests with `describe()` blocks
- One behavior per test
- Clear, descriptive test names
- Use `beforeEach()` for test isolation

---

## Browser API Mocking

Our `setup.js` provides mocks for common browser APIs:

**Mocked APIs:**
- `localStorage` - Storage API
- `speechSynthesis` - Text-to-speech
- `SpeechSynthesisUtterance` - TTS utterance class
- `SpeechRecognition` - Speech-to-text
- DOM manipulation via jsdom

**Example:**
```javascript
beforeEach(() => {
    // localStorage is automatically mocked
    localStorage.clear();

    // DOM is reset
    document.body.innerHTML = '';

    // All mocks are cleared
    jest.clearAllMocks();
});
```

---

## Module Testing Pattern

**ES Module Import:**
```javascript
import { describe, test, expect, jest, beforeEach } from '@jest/globals';

let moduleUnderTest;

beforeEach(async () => {
    // Reset module state
    jest.resetModules();

    // Re-import for fresh instance
    moduleUnderTest = await import('../../src/path/to/module.js');
});
```

**Why `resetModules()`?**
- Clears module cache between tests
- Ensures each test gets fresh module state
- Prevents test interdependence
- Critical for testing stateful modules

---

## Test Coverage Goals

**Aim For:**
- 90%+ code coverage
- All public APIs tested
- Edge cases and error conditions
- State transitions (for stateful modules)

**Current Coverage:**
- Notifications: ~95%
- Error Handler: ~95%
- Conversation State Indicator: ~95%
- Voice Settings: ~90%

---

## Common Testing Patterns

### Testing DOM Manipulation

```javascript
test('should create element in DOM', () => {
    module.createNotification('Test');

    const element = document.querySelector('.notification');
    expect(element).toBeTruthy();
    expect(element.textContent).toContain('Test');
});
```

### Testing Async Functions

```javascript
test('should handle async operation', async () => {
    const result = await module.fetchData();

    expect(result).toBeDefined();
});
```

### Testing Event Handlers

```javascript
test('should respond to button click', () => {
    const button = document.createElement('button');
    button.addEventListener('click', module.handleClick);

    button.click();

    expect(module.wasClicked).toBe(true);
});
```

### Testing With Timers

```javascript
test('should execute after delay', () => {
    jest.useFakeTimers();

    module.delayedAction();
    jest.advanceTimersByTime(1000);

    expect(module.executed).toBe(true);

    jest.useRealTimers();
});
```

### Testing localStorage

```javascript
test('should persist to localStorage', () => {
    module.saveSetting('key', 'value');

    expect(localStorage.setItem).toHaveBeenCalledWith(
        'key',
        JSON.stringify('value')
    );
});
```

---

## Test Discipline

Following the same principles as Python testing:

**Red-Green-Refactor:**
1. Write one failing test
2. Make it pass with simplest code
3. Refactor while tests are green
4. Commit

**Run Full Suite:**
- Always run ALL tests, not just current test
- `npm test` runs entire suite
- Catches regressions immediately
- Fast enough to run after every change

**One Test at a Time:**
- Resist urge to write multiple tests
- Focus on current behavior
- Let design emerge incrementally

---

## Debugging Tests

**Run Single Test File:**
```bash
npm test -- tests/js/notifications.test.js
```

**Run Single Test:**
```javascript
test.only('should do specific thing', () => {
    // Only this test runs
});
```

**Debug Output:**
```javascript
test('something', () => {
    console.log('Debug value:', someValue);
    // Appears in test output
});
```

**Inspect DOM:**
```javascript
test('creates element', () => {
    module.createElement();
    console.log(document.body.innerHTML);
});
```

---

## Best Practices

**Do:**
- Test behavior, not implementation
- Use descriptive test names
- Keep tests simple and readable
- Mock external dependencies
- Reset state between tests
- Run full suite frequently

**Don't:**
- Test private implementation details
- Create test interdependencies
- Skip the refactor step
- Write tests for trivial code
- Leave failing tests uncommitted
- Mock what you own (test real implementation)

---

## Current Test Suites

**notifications.test.js** (39 tests)
- Notification creation and display
- Type variants (success, error, warning, info)
- Queueing and dismissal
- Input validation
- Helper functions

**error_handler.test.js** (40 tests)
- Error handling and logging
- Message translation
- Async function wrapping
- Retry with backoff
- Error classification
- Safe execution

**conversation_state_indicator.test.js** (28 tests)
- State transitions
- Visual feedback
- DOM manipulation
- Accessibility
- Animations

**voice_settings.test.js** (35 tests)
- TTS/STT settings
- localStorage persistence
- UI panel generation
- Voice selection
- Event handling

---

## Integration with Python Tests

**Complementary Testing:**
- Python tests: Backend logic, domain model, services
- JavaScript tests: Frontend modules, UI behavior, browser APIs
- Both follow red-green-refactor cycle
- Both aim for >90% coverage

**Running All Tests:**
```bash
# Python tests
python3 -m pytest tests/ -v

# JavaScript tests
npm test

# Full suite
python3 -m pytest tests/ -v && npm test
```

---

*JavaScript testing follows the same disciplined approach as Python testing. Write tests first, commit frequently, and let the tests guide your design.*
