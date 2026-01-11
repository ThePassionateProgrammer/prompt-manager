# Hands-Free Voice Mode - User Guide

## Quick Start

1. **Activate**: Click the conversation mode button
2. **Wake**: Say "Hey Amber" or "Hi Amber"
3. **Talk**: Ask your question naturally
4. **Wait**: System auto-sends after 3 seconds of silence
5. **Listen**: AI response plays automatically

## Voice Commands

### Wake Words (Standby → Active)
- "Hey Amber"
- "Hi Amber"  
- "Amber"

### Sleep Words (Active → Standby)
- "Sleep Amber"
- "Goodbye Amber"
- "Stop"

### Control Commands
- "Amber, pause" - Pause listening (keeps conversation)
- "Amber, resume" - Resume listening
- "Ember, repeat that" - Replay last AI response

## States

**WAKE_LISTENING (Standby)**
- Waiting for wake word
- Not transcribing speech
- Yellow indicator

**LISTENING (Active)**
- Transcribing everything you say
- Auto-sends after silence
- Green indicator

**PAUSED**
- Not listening
- Say "Amber resume" to continue
- Orange indicator

**PLAYING**
- Reading AI response
- Cannot interrupt
- Blue indicator

## Settings

**Auto-Send Timeout** (Settings → Hands-Free)
- How long to wait after you stop talking
- Default: 3 seconds
- Range: 1-10 seconds

**Wake/Sleep Words** (config.js - Developer)
- Edit arrays to customize
- Supports multiple variations

## Tips

✅ **DO:**
- Speak clearly and at normal pace
- Wait for indicator before speaking
- Use pause if interrupted
- Let responses finish playing

❌ **DON'T:**
- Talk while AI is responding
- Expect instant activation (wake word takes ~1s)
- Use wake word in your questions
- Forget to say sleep word when done

## Troubleshooting

**Wake word not working?**
- Check microphone permissions
- Speak clearly: "Hey Amber"
- Wait 1 second after activation
- Try different variation: "Hi Amber"

**Not auto-sending?**
- Make sure you stop talking completely
- Check silence timeout in settings
- System waits 3 seconds by default

**Response not playing?**
- Check browser audio permissions
- System may be in PAUSED state
- Click play button manually if needed

**Accidentally activates?**
- Use sleep word: "Sleep Amber"
- Or say "Amber pause"
- Avoid similar-sounding phrases

## Use Cases

**Cooking** 🍳
- Get recipe help hands-free
- Ask measurement conversions
- Timer and temperature checks

**Exercise** 🏃
- Workout questions while moving
- Form tips and guidance
- Motivation and pacing

**Accessibility** ♿
- Essential for mobility limitations
- Eyes-free interaction
- Voice-first design

**Brainstorming** 💡
- Natural conversation flow
- Rapid idea exploration
- No typing friction

**Research** 📚
- Quick fact-checking
- Follow-up questions
- Information gathering

## Keyboard Shortcuts

- `Esc` - Deactivate hands-free mode
- `Ctrl/Cmd + K` - Toggle microphone
- `Enter` - Manual send (if you don't want to wait)

## Privacy & Security

- Voice processing happens in browser
- No audio sent to external services (except AI provider)
- Transcripts stored locally until cleared
- Microphone permission required

---

**Need Help?** Check HANDS_FREE_MODE_TOUR.md for technical details.
