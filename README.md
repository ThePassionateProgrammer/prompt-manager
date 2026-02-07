# Prompt Manager v1.0 (Archived)

**Educational code from the "Coding with Claude" YouTube series.**

This repository contains the complete, working v1.0 codebase as developed during the YouTube series. It is archived for educational purposes - no further updates will be made here.

---

## About This Project

This prompt management system was built as a learning exercise in AI-assisted pair programming with Claude. The series demonstrates:

- Test-Driven Development (TDD) with an AI partner
- Clean Architecture and Domain-Driven Design
- Refactoring legacy code safely
- Building production-quality software iteratively

## Features (v1.0)

- Multi-model AI chat interface (OpenAI models)
- Encrypted API key storage
- Token tracking with auto-trimming
- Conversation persistence
- Template builder with cascading variables
- 447 comprehensive tests

## Quick Start

```bash
# Clone and setup
git clone https://github.com/ThePassionateProgrammer/prompt-manager.git
cd prompt-manager
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python prompt_manager_app.py
```

Access at http://localhost:8000/chat

## Architecture

```
Routes (HTTP) → Business (Services) → Domain (Pure Logic)
```

The domain layer has zero framework dependencies, making the business logic portable and testable.

## Documentation

- **V1_FINAL_REPORT.md** - Complete v1.0 metrics
- **TESTING_GUIDE.md** - Testing documentation
- **Episode scripts** - Video narration guides

## YouTube Series

Watch the development journey: [Coding with Claude](https://www.youtube.com/@ThePassionateProgrammer)

## License

MIT License - See [LICENSE](LICENSE) file.

---

*Built with curiosity and Claude. May every pattern reveal a deeper simplicity.*
