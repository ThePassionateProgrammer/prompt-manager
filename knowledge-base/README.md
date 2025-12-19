# Knowledge Base Starter

A starter template for building your own knowledge base to use with Claude Code, optimized for **Extreme Programming (XP)** and **Domain-Driven Design (DDD)** practices.

## What is This?

This knowledge base helps Claude Code understand your development preferences, coding standards, and project-specific practices. Instead of repeating instructions in every session, you maintain a set of reference documents that Claude reads as needed.

Think of it as **teaching Claude how you work** — your philosophy, your rhythm, your patterns.

## Quick Start

1. **Fork or copy this repository** to your project
2. **Add to your project root** or docs/ folder (keep it version controlled with your code)
3. **Customize each file** to match your preferences and practices
4. **At the start of each Claude Code session**, say:
   > "Please read index.md from my knowledge base"
5. Claude will read the core files and reference others as needed during your session

## What's Included

### Core Files (Read at Session Start)
- **[index.md](index.md)** - Start here! Navigation and usage guide
- **[style-guide.md](style-guide.md)** - Coding standards and Python/Pytest conventions
- **[working-agreement.md](working-agreement.md)** - Partnership charter (includes Arlo Belshee commit notation)

### Reference Files (Read on Demand)
- **[philosophy.md](philosophy.md)** - Development philosophy: XP, DDD, test-first, pure domain model
- **[testing.md](testing.md)** - Test-first development: red-green-refactor, one test at a time
- **[refactoring.md](refactoring.md)** - When and how to refactor: green bar rule, commit after refactor
- **[design-patterns.md](design-patterns.md)** - Patterns you prefer to use
- **[domain-language.md](domain-language.md)** - Project vocabulary and ubiquitous language
- **[decisions.md](decisions.md)** - Architectural decision records (ADRs)

### Bonus
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to maintain and update your knowledge base

## Philosophy

This template embodies:

- **Extreme Programming (XP)** - Small steps, constant feedback, pair programming with AI
- **Test-First Development** - Red-green-refactor rhythm, one test at a time
- **Domain-Driven Design (DDD)** - Pure domain model, business rules in domain objects
- **Continuous Refactoring** - Commit after every green refactor
- **Arlo Belshee Commit Notation** - Risk-aware commit messages

## Customization Tips

1. **Keep it concise** - Each file should be under 400 words
2. **Be specific** - Document what's unique to your approach
3. **Update regularly** - Add learnings and decisions as they emerge
4. **Remove what doesn't fit** - Not every file may be relevant to your project
5. **Add new files** - Create additional references as needed

**Important:** This knowledge base should live in your project repository, version controlled alongside your code. It's part of your project's documentation.

## Language Agnostic (Mostly)

While the current template includes Python/Pytest conventions in `style-guide.md`, the overall structure and philosophy work with any programming language. Customize the examples and guidance to match your stack.

## Quick Start for Your Team

1. **Fork or copy this repository** to your project
2. **Customize in a team session** - Make it yours together
3. **Reference in onboarding docs** - New team members read this first
4. **Update as you learn** - Living document that grows with your project

## For YouTube Viewers

This knowledge base template comes from **[The Passionate Programmer](https://youtube.com/@ThePassionateProgrammer)** YouTube channel, where we explore how to collaborate effectively with AI for software development.

**Want to see this in action?** Check out our videos on:
- Planning Mode: Breaking down features before coding
- Knowledge Bases: Teaching Claude how you work
- Test-First Development with AI pair programming
- Domain-Driven Design with Claude Code

## Learn More

**Watch the tutorials:**
- **Planning Mode:** How to plan features before coding
- **Knowledge Bases:** Setting up your development knowledge base
- **Test-First with Claude:** Red-green-refactor workflow

**Subscribe:** [The Passionate Programmer on YouTube](https://youtube.com/@ThePassionateProgrammer)

## License

MIT License - Feel free to use, modify, and share.

---

## Getting Started

**Your first session:**

1. Open Claude Code in your project directory
2. Say: "Please read index.md from my knowledge base"
3. Start building with your preferred practices already in place

**No more repeating yourself.** Your knowledge base remembers.

---

*Built for Claude Code - Your AI pair programmer*

**Version:** 1.0
**Last Updated:** November 2024
**Maintained by:** The Passionate Programmer
