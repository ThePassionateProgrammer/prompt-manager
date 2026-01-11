# Hands-Free Voice Mode - Developer Guide

## Architecture Overview

The hands-free voice system follows a clean architecture with pure domain models and clear separation of concerns.

### Design Principles

1. **Pure Domain Models** - Business logic has zero browser API dependencies
2. **Dependency Injection** - Services receive dependencies for testability
3. **Single Responsibility** - Each class does one thing well
4. **Test-First Development** - RED-GREEN-REFACTOR discipline
5. **State Machine Pattern** - Explicit state transitions

## Core Modules

### 1. WakeWordDetector
**Location**: `src/prompt_manager/static/js/modules/wake_word_detector.js`

```javascript
import { WakeWordDetector } from './wake_word_detector.js';

const detector = new WakeWordDetector({
    wakeWords: ['hey amber', 'hi amber'],
    sleepWords: ['sleep amber', 'stop']
});

const result = detector.detect(transcript);
// { type: 'wake'|'sleep'|null, matched: boolean }
```

**Key Methods:**
- `detectWakeWord(transcript)` - Check for wake words
- `detectSleepWord(transcript)` - Check for sleep words  
- `detect(transcript)` - Check both in one call

**Testing**: 34 unit tests, 100% coverage

### 2. CommandDetector  
**Location**: `src/prompt_manager/static/js/modules/command_detector.js`

```javascript
import { CommandDetector } from './command_detector.js';

const detector = new CommandDetector({
    commandWord: 'ember',
    commands: {
        'repeat': ['repeat', 'repeat that'],
        'transcribe': ['transcribe', 'transcribe this']
    }
});

const result = detector.detect('ember repeat that');
// { matched: true, command: 'repeat' }
```

**Key Methods:**
- `detect(transcript)` - Detect command word + command
- `getSupportedCommands()` - List all command names
- `isCommandSupported(name)` - Check if command exists

**Testing**: 23 unit tests

### 3. TranscriptProcessor
**Location**: `src/prompt_manager/static/js/modules/transcript_processor.js`

```javascript
import { TranscriptProcessor } from './transcript_processor.js';

const processor = new TranscriptProcessor({
    wakeWordDetector,
    voiceCommandDetector,
    commandDetector,
    conversationMode
});

const result = processor.process(transcript);
// { 
//   action: 'WAKE'|'SLEEP'|'PAUSE'|'RESUME'|'REPEAT'|'TRANSCRIBE'|'IGNORE',
//   shouldTranscribe: boolean,
//   message: string|null
// }
```

**Actions:**
- `WAKE` - Wake word detected, activate system
- `SLEEP` - Sleep word detected, go to standby
- `PAUSE` - Pause command, stop listening
- `RESUME` - Resume command, start listening
- `REPEAT` - Repeat last response
- `TRANSCRIBE_MODE` - Future: transcription-only mode
- `TRANSCRIBE` - Add to chat input
- `IGNORE` - Discard (wrong state)

**Testing**: 21 unit tests

### 4. SilenceDetector
**Location**: `src/prompt_manager/static/js/modules/silence_detector.js`

```javascript
import { SilenceDetector } from './silence_detector.js';

const detector = new SilenceDetector({ silenceThreshold: 3000 });

detector.onSpeechStart();  // Mark speech started
detector.onSpeechEnd();    // Mark speech ended

if (detector.isSilent()) {
    // Silence threshold exceeded
}
```

**Key Methods:**
- `onSpeechStart()` - Record speech start time
- `onSpeechEnd()` - Record speech end time
- `isSilent()` - Check if threshold exceeded
- `getSilenceDuration()` - Get current silence duration
- `getSilenceThreshold()` - Get threshold (lazy evaluation)

**Testing**: 29 unit tests + 4 integration tests

### 5. SilenceCheckingService
**Location**: `src/prompt_manager/static/js/modules/silence_checking_service.js`

```javascript
import { SilenceCheckingService } from './silence_checking_service.js';

const service = new SilenceCheckingService(silenceDetector, conversationMode);

service.start(
    () => console.log('Silence detected'),
    () => console.log('Extended silence')
);

service.stop();  // Stop checking
```

**Key Methods:**
- `start(onSilence, onExtendedSilence)` - Begin checking
- `stop()` - Stop checking
- `isRunning()` - Check if active

**Testing**: 25 unit tests

### 6. VoiceCommandDetector
**Location**: `src/prompt_manager/static/js/modules/voice_command_detector.js`

```javascript
import { VoiceCommandDetector } from './voice_command_detector.js';

const detector = new VoiceCommandDetector();

const result = detector.detect('amber pause');
// { matched: true, command: 'pause' }
```

**Testing**: 30 unit tests

### 7. ConversationMode (State Machine)
**Location**: `src/prompt_manager/static/js/modules/conversation_mode.js`

```javascript
conversationMode.activate();              // Enter hands-free mode
conversationMode.onWakeWordDetected();    // WAKE_LISTENING → LISTENING
conversationMode.pauseListening();        // LISTENING → PAUSED
conversationMode.resumeListening();       // PAUSED → LISTENING
conversationMode.onSleepWordDetected();   // LISTENING → WAKE_LISTENING
conversationMode.deactivate();            // Exit hands-free mode
```

**States:**
- `IDLE` - Not in hands-free mode
- `WAKE_LISTENING` - Standby, waiting for wake word
- `LISTENING` - Active transcription
- `PAUSED` - Temporarily stopped
- `PLAYING` - Reading AI response
- `PROCESSING` - AI generating response

**Testing**: 45 state machine tests

## Configuration

**Location**: `src/prompt_manager/static/js/modules/config.js`

```javascript
export const HANDS_FREE_CONFIG = Object.freeze({
    // Wake/sleep words
    WAKE_WORDS: ['hey amber', 'hi amber', 'amber'],
    SLEEP_WORDS: ['sleep amber', 'goodbye amber', 'stop'],
    
    // Voice commands
    PAUSE_COMMANDS: ['amber pause', 'amber, pause', 'pause amber'],
    RESUME_COMMANDS: ['amber resume', 'amber, resume', 'resume amber'],
    
    // Ember commands
    COMMAND_WORD: 'ember',
    COMMANDS: {
        'repeat': ['repeat', 'repeat that'],
        'transcribe': ['transcribe', 'transcribe this']
    },
    
    // Timing
    DEFAULT_SILENCE_THRESHOLD_MS: 3000,
    EXTENDED_SILENCE_THRESHOLD_MS: 10000,
    SILENCE_CHECK_INTERVAL_MS: 100
});
```

## Testing Strategy

### Unit Tests (166 passing)
- Pure domain logic
- Fast, deterministic
- Use Jest with fake timers
- 100% coverage of business logic

### Integration Tests (4 passing)
- Silence timing accuracy (uses real timers)
- Verifies millisecond-level precision
- Catches coordination bugs

### Approvals Tests (Planned)
- Visual regression testing for UI
- Approval-based workflow

### Manual Testing
- End-to-end user flows
- Browser compatibility
- Microphone/speaker testing
- Edge cases (network issues, etc.)

## Adding New Commands

### 1. Add to Config

```javascript
// config.js
COMMANDS: {
    'repeat': ['repeat', 'repeat that'],
    'save': ['save this', 'save conversation']  // NEW
}
```

### 2. Add to TranscriptProcessor

```javascript
// transcript_processor.js
if (emberCommandDetection.command === 'save') {
    return {
        action: 'SAVE',
        shouldTranscribe: false,
        message: 'Saving conversation...'
    };
}
```

### 3. Handle Action in voice_interaction.js

```javascript
// voice_interaction.js
case 'SAVE':
    console.log('[Hands-free] Save command detected');
    saveCurrentConversation();
    if (processingResult.message) {
        showNotification(processingResult.message, 'success');
    }
    processedResultIndex = i + 1;
    continue;
```

### 4. Write Tests

```javascript
// tests/js/command_detector.test.js
test('should detect save command', () => {
    const result = detector.detect('ember save this');
    expect(result.matched).toBe(true);
    expect(result.command).toBe('save');
});
```

## Common Patterns

### Pattern 1: Normalize Text

```javascript
_normalize(text) {
    if (typeof text !== 'string') return '';
    return text.toLowerCase().trim();
}
```

### Pattern 2: Array Matching

```javascript
this.wakeWords.some(word => {
    const normalized = this._normalize(word);
    return transcript === normalized;
});
```

### Pattern 3: State Guards

```javascript
if (conversationMode.state !== 'LISTENING') {
    return { action: 'IGNORE', shouldTranscribe: false };
}
```

### Pattern 4: Lazy Evaluation

```javascript
getSilenceThreshold() {
    return this.explicitThreshold ?? getSilenceThreshold();
}
```

## Debugging Tips

### Enable Verbose Logging

```javascript
console.log('[Hands-free] State:', conversationMode.state);
console.log('[Hands-free] Transcript:', transcript);
console.log('[Hands-free] Processing result:', processingResult);
```

### Test State Transitions

```javascript
// Manual state inspection
console.log('Current state:', conversationMode.state);
conversationMode.onWakeWordDetected();
console.log('After wake:', conversationMode.state);
```

### Check Silence Detection

```javascript
const duration = silenceDetector.getSilenceDuration();
const threshold = silenceDetector.getSilenceThreshold();
console.log(`Silence: ${duration}ms / ${threshold}ms`);
```

### Verify Configuration

```javascript
console.log('Wake words:', HANDS_FREE_CONFIG.WAKE_WORDS);
console.log('Commands:', HANDS_FREE_CONFIG.COMMANDS);
```

## Performance Considerations

### Silence Checking Interval
- Default: 100ms
- Trade-off: Accuracy vs CPU usage
- Don't go below 50ms (unnecessary CPU load)

### Speech Recognition
- Continuous mode in hands-free
- Auto-restarts after `onend` event
- 300ms delay prevents rapid restart loops

### Text-to-Speech
- Cancel previous speech before starting new
- Prevents speech queue buildup
- `voiceSynthesis.cancel()` before `speak()`

## Browser Compatibility

### Required APIs
- `webkitSpeechRecognition` or `SpeechRecognition`
- `speechSynthesis`
- `Promise` (ES6)
- `Object.freeze` (ES5)

### Tested Browsers
- ✅ Chrome 90+ (primary target)
- ✅ Edge 90+ (Chromium-based)
- ⚠️ Safari (limited speech recognition)
- ❌ Firefox (no speech recognition API)

## Security & Privacy

### No External Dependencies
- Speech recognition uses browser API
- No third-party libraries for voice processing
- Audio stays local (except AI provider API)

### Microphone Permissions
- Browser requests permission on first use
- User can revoke at any time
- Graceful degradation if denied

### Data Storage
- Transcripts in memory only
- Not persisted between sessions
- Last AI response stored for repeat command

## Future Extensions

### Plugin System
- Consider Observer pattern for events
- Allow third-party command handlers
- Sandboxed execution environment

### Multi-Language Support
- Add language parameter to detectors
- Support multiple recognition languages
- Localized wake words

### Custom TTS Voices
- Voice selection UI
- Speed/pitch controls
- Per-user preferences

## Getting Help

- **Architecture Questions**: See HANDS_FREE_MODE_TOUR.md
- **User Issues**: See USER_GUIDE.md
- **Observer Pattern**: See OBSERVER_PATTERN_DISCUSSION.md
- **Tests**: Run `npm test`
