# Knowledge Base - Start Here

This knowledge base helps Claude Code understand your development preferences and practices. At the start of each session, share this message:

**"Please read index.md from my knowledge base"**

Claude will read this file and the core references, then work with you using your established practices.

---

## Core Files (Read at Session Start)

**Always read these two files at the beginning of each session:**

1. [style-guide.md](style-guide.md) - Your coding standards and conventions
2. [working-agreement.md](working-agreement.md) - How you and Claude collaborate

---

## Reference Files (Read on Demand)

**Read these when the topic comes up during the session:**

- [philosophy.md](philosophy.md) - Your development philosophy and values
- [testing.md](testing.md) - Test-first development and red-green-refactor cycle
- [refactoring.md](refactoring.md) - When and how to refactor code
- [design-patterns.md](design-patterns.md) - Patterns you prefer to use
- [domain-language.md](domain-language.md) - Project-specific vocabulary and terms
- [decisions.md](decisions.md) - Key architectural and design decisions

---

## When to Reference Each File

| File | Read When... |
|------|--------------|
| style-guide.md | Starting any coding task |
| working-agreement.md | Starting any session |
| philosophy.md | Discussing approach or making design decisions |
| testing.md | Writing tests or discussing test strategy |
| refactoring.md | Code needs improvement or restructuring |
| design-patterns.md | Solving a design problem or choosing an approach |
| domain-language.md | Discussing domain concepts or naming |
| decisions.md | Understanding why something was built a certain way |

---

## Keeping Your Knowledge Base Current

Update these files as you:
- Discover new preferences
- Establish new patterns
- Make important decisions
- Learn from mistakes
- Refine your process

A living knowledge base grows with your project and partnership.

---

## Tips for Effective Use

1. **Be specific** - The more concrete your guidelines, the better Claude can follow them
2. **Update regularly** - Add new learnings and decisions as they emerge
3. **Keep it concise** - Each file should be under 400 words
4. **Focus on differences** - Document what's unique to your approach, not universal practices
5. **Reference explicitly** - When something important comes up, ask Claude to "read testing.md" or reference the relevant file

---

*This knowledge base is designed for use with Claude Code and follows the starter template from [Coding with Claude](https://youtube.com/@codingwithclaude).*


---

## Development Process: When Things Break - Recovery Protocol

**Created**: January 16, 2026
**Context**: Dashboard broken after memory card implementation. Continued adding code instead of stopping to investigate.

### Critical Rule: STOP-CHECK-REVERT Protocol

When user reports breaking changes, **IMMEDIATELY STOP** all feature work and follow this protocol:

#### 1. STOP - Cease All Development
- Do NOT add more code
- Do NOT attempt fixes
- Do NOT continue with planned features

#### 2. CHECK - Identify Last Working State
```bash
# Check recent commits
git log -5 --oneline --format="%h %ai %s"

# Ask user
"When did this last work?"
"What were you able to do before?"
```

#### 3. VERIFY - Understand the Architecture
**Before modifying ANY code, confirm:**
- Which application file is actually used? (multiple Flask apps may exist)
- What URL does the user access?
- Which routes/blueprints are registered?

```bash
# Find all Flask app files
find . -name "*app*.py" -type f | grep -v venv

# Check which one is run
grep -r "if __name__ == '__main__'" . --include="*.py"
```

#### 4. REVERT - Get Back to Working State
```bash
# For uncommitted changes
git checkout HEAD -- .

# For committed but broken changes
git reset --hard <last-good-commit>

# Always backup first
cp -r conversations/ conversations.backup-$(date +%Y%m%d)
```

#### 5. VERIFY - Confirm Working State
- Ask user to test
- Confirm all features work
- Only then investigate what broke

### Critical Lesson: Always Push After Commit

**New Standard Practice:**
```bash
git add .
git commit -m "Clear, descriptive message"
git push origin <branch>  # NEVER skip this!
```

**Why**: If something breaks later, git history on GitHub provides safety net.

### Architecture Verification Checklist

Before modifying any code, answer these questions:

1. **Which app file does the user run?**
   - `prompt_manager_app.py`?
   - `src/prompt_manager/web/app.py`?
   - Something else?

2. **What URL does the user access?**
   - `/dashboard`?
   - `/`?
   - `/chat`?

3. **Which Flask app serves that route?**
   - Check route decorators
   - Check blueprint registrations

4. **Are there multiple apps in the codebase?**
   - If yes, which one is the "real" one?

### Example: The Two-App Confusion

**What happened**: Prompt Manager has TWO Flask applications:
- `prompt_manager_app.py` - Main app with dashboard at `/dashboard`
- `src/prompt_manager/web/app.py` - Secondary app for prompts at `/`

**Mistake**: Modified the wrong app, breaking nothing because user doesn't use it.

**Prevention**: Always ask "Which file do you run to start the server?"

### Red Flags That Should Trigger This Protocol

User says any of these:
- "Things are broken"
- "It doesn't work anymore"
- "Buttons don't do anything"
- "The dashboard doesn't show X"
- "We should revert"
- "Let's get back to sanity"

**Response**: STOP immediately and run the protocol.

### Recovery Success Metrics

- User confirms app works
- All conversations/data preserved
- Code reverted to known-good state
- Understanding of what broke (for prevention)
- Changes pushed to GitHub (for visibility)

---

**Key Insight**: When things break, the solution is almost never "add more code." The solution is: stop, understand, revert, then carefully fix from known-good state.

