# Hands-Free Voice Conversation Mode - Demo Video Script

## Opening (30 seconds)

**[Screen: Prompt Manager interface]**

"Hi! Today I'm showing you the new hands-free voice conversation mode in Prompt Manager. This feature lets you have completely hands-free conversations with AI - no clicking, no typing, just talk."

## Part 1: Activating Hands-Free Mode (45 seconds)

**[Action: Click conversation mode button]**

"To start hands-free mode, click the conversation mode button here. Notice the interface changes - we're now in standby mode, waiting for the wake word."

**[Screen shows: WAKE_LISTENING indicator]**

"See this indicator? It shows we're listening for the wake word. The default wake word is 'Hey Amber' - but you can also say 'Hi Amber' or just 'Amber'."

## Part 2: Wake Word Activation (1 minute)

**[Action: Say "Hey Amber"]**

"Hey Amber"

**[Screen: Indicator changes to LISTENING, notification appears]**

"There we go! The wake word activated the system. Now I can just start talking and it will transcribe everything I say."

**[Action: Speak naturally]**

"Tell me about the architecture of a modern web application."

**[Screen: Text appears in input, auto-sends after 3 seconds of silence]**

"Notice I didn't click anything. After 3 seconds of silence, it automatically sends my message. This is configurable in settings - you can make it shorter or longer."

## Part 3: Conversation Flow (2 minutes)

**[Screen: AI response appears, begins reading automatically]**

"The AI responds, and the system automatically reads the response aloud using text-to-speech. While it's reading, I can't interrupt - this prevents feedback loops."

**[Screen: After TTS finishes, indicator shows LISTENING again]**

"Once it finishes reading, the system automatically goes back to listening mode. I can immediately ask my follow-up question."

**[Action: Ask follow-up]**

"What about the database layer?"

**[Screen: Auto-sends after silence, receives response, plays automatically]**

"See how natural this is? No button clicking, no keyboard - just conversation. The system handles the entire flow automatically."

## Part 4: Voice Commands (1 minute 30 seconds)

**[Action: Demonstrate pause]**

"Amber, pause"

**[Screen: Changes to PAUSED state]**

"Sometimes you need to pause - maybe someone walked into the room. Just say 'Amber pause' and the system stops listening. Your conversation is preserved."

**[Action: Resume]**

"Amber, resume"

**[Screen: Back to LISTENING]**

"Say 'Amber resume' when you're ready to continue."

**[Action: Demonstrate sleep]**

"Sleep Amber"

**[Screen: Returns to WAKE_LISTENING standby]**

"Want to go back to standby? Say 'Sleep Amber' or 'Stop'. Now it's waiting for the wake word again."

## Part 5: Ember Commands (1 minute)

**[Action: Wake system again]**

"Hey Amber"

"What's the capital of France?"

**[Wait for response: "The capital of France is Paris."]**

**[Action: Use repeat command]**

"Ember, repeat that"

**[Screen: Last response plays again via TTS]**

"'Ember repeat that' replays the last AI response - useful if you missed something or got distracted. Ember commands are designed for future extensibility."

## Part 6: Extended Silence Auto-Pause (45 seconds)

**[Action: Let system sit idle for 10+ seconds]**

"If you go silent for more than 10 seconds, the system assumes you stepped away and automatically pauses."

**[Screen: Shows auto-pause notification]**

"This prevents it from listening continuously when you're not using it. Just say 'Amber resume' when you come back."

## Part 7: Configuration (1 minute)

**[Screen: Settings page]**

"Let's look at configuration. In the hands-free settings, you can adjust the auto-send timeout - that's how long it waits after you stop talking before sending your message."

**[Screen: Shows config.js]**

"For developers - wake words, sleep words, and commands are all configured here. Want to use 'OK Computer' instead of 'Hey Amber'? Just edit this array. Multiple variations are supported."

## Part 8: Technical Architecture (1 minute 30 seconds)

**[Screen: Show file structure]**

"Quick technical overview for developers. The architecture uses pure domain models - no browser API dependencies in the business logic."

**[Screen: Show class diagram or module list]**

"Key modules:
- WakeWordDetector - detects wake/sleep words
- CommandDetector - handles Ember commands
- TranscriptProcessor - processes all speech and decides actions
- SilenceCheckingService - manages silence detection timers
- VoiceCommandDetector - pause/resume commands"

**[Screen: Show test results]**

"We have 166 passing unit tests covering all the hands-free logic. The architecture follows RED-GREEN-REFACTOR discipline with test-first development."

## Part 9: Use Cases (45 seconds)

"So when would you use hands-free mode?"

**[Screen: Show different scenarios]**

"- Cooking: Get recipe help while your hands are messy
- Exercise: Ask questions while on the treadmill
- Accessibility: Hands-free is essential for users with mobility limitations
- Brainstorming: Talk through ideas naturally without typing
- Research: Rapid-fire questions without keyboard switching"

## Part 10: Future Roadmap (30 seconds)

"What's next for hands-free mode?"

**[Screen: List of future features]**

"- Custom wake words via UI (currently requires config edit)
- 'Ember transcribe' command for transcription-only mode
- Multiple AI voice options
- Speed controls for text-to-speech
- Conversation history playback"

## Closing (30 seconds)

**[Screen: Hands-free mode active, working smoothly]**

"That's hands-free voice conversation mode in Prompt Manager. It makes AI conversations natural and effortless. Give it a try and let us know what you think!"

**[Screen: End card with links]**

"Links in the description for documentation, source code, and setup instructions. Thanks for watching!"

---

## Total Time: ~10 minutes

## Props Needed:
- Working Prompt Manager instance with hands-free configured
- Sample questions prepared
- Settings page ready to show
- Code editor with architecture files open
- Test results screenshot/recording

## Recording Tips:
- Use high-quality microphone
- Quiet environment (no background noise for wake word)
- Screen recording at 1080p minimum
- Cursor highlighting for button clicks
- Zoom in on indicators/notifications when they appear
- Practice wake word activation before recording (timing can be tricky)

## Editing Notes:
- Add captions for accessibility
- Highlight indicators with circles/arrows in post
- Speed up long AI responses (2x) with note
- Add music during technical section (low volume)
- Include chapter markers in YouTube description
