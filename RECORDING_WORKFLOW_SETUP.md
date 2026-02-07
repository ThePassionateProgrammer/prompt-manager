# Recording Workflow Setup
**Real-time conversation with Claude on camera**

---

## 🎙️ TEXT-TO-SPEECH OPTIONS (Free & Good Quality)

### **Recommended: macOS Built-in (Best for Real-time)**
**Pros:**
- Already installed
- Fast, no lag
- Natural voices (Samantha, Alex)
- Can use via Terminal or System Preferences

**How to use:**
```bash
# Test voices
say -v "?" | grep en_US

# Best voices for technical content:
say -v Samantha "This is the chat endpoint. Let me walk you through it."
say -v Alex "The domain is your competitive advantage."

# Use in real-time during recording:
# Just paste my response into Terminal and run 'say'
```

**Setup:**
1. Open Terminal on second monitor
2. When I respond, paste into: `say -v Samantha "PASTE_HERE"`
3. Records in real-time with your screen capture

---

### **Alternative: Balabolka (Windows/macOS via Wine)**
- High quality
- Multiple voices
- But requires download

### **Alternative: Natural Reader (Web-based)**
- naturalreaders.com
- Free tier available
- Good for post-production

---

## 🎬 YOUR PROPOSED WORKFLOW

### **Monitor Setup**
**Monitor 1 (Recording):** VS Code + Terminal (large fonts)  
**Monitor 2 (Reference):** Script + Terminal for TTS

### **Process:**
1. **Read script prompt** (Monitor 2) → **Enter in Cursor** (Monitor 1)
2. **I respond** → **You copy to Terminal** (Monitor 2) → **`say` command**
3. **Voice plays** → **Captured by screen recorder**
4. **We navigate code together** (Monitor 1)

### **Second Pass:**
- Record yourself on camera reading prompts
- Use in edit as cutaways

---

## 🎯 THIS WILL WORK - HERE'S WHY

**Real-time conversation:**
- You ask questions naturally
- I respond (text appears)
- TTS reads my response immediately
- Feels like a conversation

**Code navigation:**
- You control the navigation
- Just tell me what you want to see
- "Show me the chat endpoint"
- "Scroll down to line 200"
- You drive, I guide

---

## 📋 HOW I'LL FOLLOW THE SCRIPT

### **My Role:**
I'll follow the **spirit** of the script, not word-for-word. Here's why:

**The script provides:**
- Key points to cover
- Order of topics
- Important quotes/insights

**But in real-time I'll:**
- Respond naturally to your actual questions
- Adapt if you want to go deeper on something
- Keep us on track toward the key learning moments
- Make sure we hit the important beats

**Example:**

**Script says:**
> "The chat endpoint. 78 lines. Let me trace through it..."

**But you might ask:**
> "Claude, what's our biggest mess?"

**I'll respond:**
> "The `/api/chat/send` endpoint in `routes/dashboard.py`. It's 78 lines mixing six different concerns. Want me to walk through it?"

**Same destination, natural conversation.**

---

## 🗺️ CODE NAVIGATION - HOW WE'LL DO IT

### **You Navigate, I Guide**

**Option 1: I tell you where to go**
```
ME: "Open routes/dashboard.py, line 135"
YOU: [Opens file, scrolls to line]
ME: "This is the chat endpoint. Notice how it starts with HTTP parsing..."
```

**Option 2: You share screen, I see what you see**
- If Cursor share is enabled, I can see your screen
- I can guide: "Scroll down... stop... see line 160?"
- More interactive

**Option 3: You use Find**
- I say: "Search for 'def send_message'"
- You: Cmd+F, jump there
- Fast navigation

### **For Code Walkthroughs:**

**I'll structure like this:**
```
ME: "Let's look at routes/dashboard.py around line 135."

[YOU navigate there]

ME: "This function does six things. Let me trace through them:
     - Lines 140-145: HTTP parsing
     - Lines 150-155: Validation
     - Lines 160-175: Message building
     [etc.]"

YOU: "Show me the message building part."

[YOU scroll to 160]

ME: "See how it's building an array? This is domain logic hiding in a route..."
```

**Natural, conversational, educational.**

---

## ⚙️ TECHNICAL SETUP CHECKLIST

### **Before Recording:**

**Monitor 1 (Primary - Being Recorded):**
- [ ] VS Code open, font size 16pt
- [ ] Terminal open, font size 18pt
- [ ] Dark theme (easier on eyes)
- [ ] Close distracting notifications
- [ ] Project root: `/Users/davidbernstein/Dropbox/Dev/Python/Projects/prompt-manager`

**Monitor 2 (Reference - Not Recorded):**
- [ ] `EPISODE_8AB_PRODUCTION_PLAN.md` open for script reference
- [ ] Terminal window for TTS commands
- [ ] Cursor chat open for our conversation

**Recording Software:**
- [ ] QuickTime or OBS set to record Monitor 1 only
- [ ] Audio input set to capture system audio (for TTS)
- [ ] Test recording 30 seconds - can you hear TTS playback?

**TTS Test:**
```bash
say -v Samantha "Testing text to speech for the recording."
```
- [ ] Can you hear it?
- [ ] Is it captured by screen recorder?

---

## 🎭 DURING RECORDING - THE FLOW

### **Episode 8A: System Overview & Safe Refactoring**

**Scene 1: System Overview**
1. **YOU:** "Claude, give me the 30,000-foot view. What's the architecture?"
2. **I respond** (you paste to TTS)
3. **YOU navigate:** File tree, show structure
4. **Conversation continues...**

**Scene 2: Problem Deep Dive**
1. **YOU:** "Show me the worst offender."
2. **I guide:** "routes/dashboard.py, line 135 - the send_message function"
3. **YOU navigate** to that function
4. **I walk through:** Tracing the six concerns
5. **Conversation continues...**

**Scene 3: Safe Refactoring**
1. **I propose:** "Let's extract the message building logic"
2. **YOU code** (or I guide you through it)
3. **YOU run tests:** `pytest tests/test_chat_routes.py -v`
4. **GREEN** - we celebrate!
5. **Repeat for 2-3 more extractions**

**Scene 4: Pinning & DI**
1. **I explain** characterization tests
2. **We write one together**
3. **We inject dependencies**
4. **Tests stay green**

**Scene 5: Reflection**
1. **YOU:** "What did we accomplish?"
2. **I summarize** the journey
3. **YOU:** "Episode 8B next time..."

---

## 🎬 CAN I FOLLOW THE SCRIPT?

**Yes, with flexibility:**

### **I WILL hit these beats:**
- System architecture overview
- Identify the 78-line problem function
- Extract 2-3 methods (safe refactoring)
- Write characterization test
- Inject dependencies
- Reflect on what we learned

### **I WON'T be robotic:**
- If you ask a different question than the script, I'll answer naturally
- If you want to dive deeper on something, we'll explore it
- If something surprising happens (test fails, bug appears), we'll handle it
- The conversation will be real

### **Think of it like:**
- Jazz musician with a lead sheet
- I know the melody and changes
- But I'll improvise the solo based on what you play

---

## 🚨 POTENTIAL ISSUES & SOLUTIONS

### **Issue: TTS lag**
**Solution:** 
- Keep my responses concise (3-4 sentences max)
- You can edit out pauses in post
- Or do longer explanations in post-production

### **Issue: Code navigation gets clunky**
**Solution:**
- Prepare a few key files open in tabs beforehand
- Use Cmd+P for quick file jumping
- I'll give you file:line references for easy jumping

### **Issue: We go off-script**
**Solution:**
- That's okay! Best content is often unscripted
- I'll gently guide us back: "This connects to [script topic]..."
- The script is a safety net, not a straitjacket

### **Issue: Test fails unexpectedly**
**Solution:**
- **This is gold!** Real debugging on camera
- Shows the reality of refactoring
- We fix it together, audience learns more

---

## 📦 PRE-STAGING FOR SMOOTH RECORDING

### **Before You Hit Record:**

```bash
# Ensure server is stopped
pkill -f "python.*prompt_manager_app"

# Ensure we're on the right branch
git status

# Ensure tests pass
pytest tests/ -v

# Open key files in VS Code tabs (in order):
# 1. routes/dashboard.py (line 135 visible)
# 2. src/prompt_manager/business/llm_provider_manager.py
# 3. src/prompt_manager/domain/linkage_manager.py
# 4. tests/test_chat_routes.py

# Have terminal ready with activated venv
source venv/bin/activate
```

**This way we can jump between files smoothly.**

---

## ✅ FINAL CHECKLIST BEFORE "ACTION"

- [ ] Screen recorder ready (Monitor 1 only)
- [ ] TTS tested and working
- [ ] Script visible on Monitor 2
- [ ] VS Code open with key files tabbed
- [ ] Terminal ready with venv activated
- [ ] Tests passing
- [ ] Cursor chat open for our conversation
- [ ] Notifications silenced
- [ ] Glass of water nearby (talking is thirsty work!)

---

## 🎯 SIMPLIFIED WORKFLOW

**The simplest version:**

1. **YOU ask** (reading from script or improvising)
2. **I respond** in Cursor
3. **YOU copy my response** to Terminal on Monitor 2
4. **YOU run:** `say -v Samantha "PASTE"`
5. **TTS voice plays** (captured by screen recorder)
6. **YOU navigate code** based on my guidance
7. **Repeat**

**Post-production:**
- Edit for pacing
- Add on-camera segments
- Add B-roll (diagrams, metrics)
- Optionally replace TTS with better TTS or your voice reading my parts

---

## 🚀 READY TO ROLL?

**When you say "Let's start recording," I'll:**
- Keep responses concise (2-4 sentences)
- Give clear file:line references for navigation
- Follow the script's learning arc
- Respond naturally to your questions
- Make sure we hit the key teaching moments

**You:**
- Drive the conversation
- Navigate the code
- Keep us moving forward
- Trust the process

**Together we'll create something valuable.** 🎬

---

## 💬 ALTERNATIVE: SKIP REAL-TIME TTS?

**If TTS during recording is too complex:**

**Option A: Record conversation without TTS**
- Just capture you asking questions
- My text responses appear
- You pause to read them
- Add my voice in post-production

**Option B: You read my responses**
- You ask the question
- You read my response out loud
- More natural but requires you to process my technical explanations quickly

**My recommendation:** Try real-time TTS for Episode 8A. If it's clunky, do post-production voice for Episode 8B.

**What do you think?** 🎙️

