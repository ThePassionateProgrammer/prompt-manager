# Prompt Manager

A simple command-line tool for managing prompts with JSON persistence.

## Features

- **GUID-based identification**: Each prompt has a unique GUID for reliable identification
- **JSON persistence**: Prompts are stored in JSON format in the current working directory
- **CLI interface**: Full command-line interface for all operations
- **Search functionality**: Search prompts by name or content
- **Category organization**: Organize prompts by categories
- **Error handling**: Graceful error handling for all operations

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install pytest
   ```

## Usage

### Demo Script

The easiest way to see the prompt manager in action is to run the demo script:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the demo script
python demo_script.py
```

This will:
1. Add two sample prompts (a greeting and farewell)
2. List all prompts in storage
3. Retrieve and display the first prompt in both human-readable and JSON formats

### CLI Commands

The prompt manager provides a full CLI interface:

```bash
# Add a prompt with text
python prompt_manager.py add "My Prompt" --text "This is my prompt text"

# Add a prompt by reading from stdin
echo "This is my prompt text" | python prompt_manager.py add "My Prompt"

# List all prompts
python prompt_manager.py list

# List prompts by category
python prompt_manager.py list --category greeting

# Get a specific prompt by ID or name
python prompt_manager.py get "prompt-id-or-name"

# Delete a prompt by ID or name
python prompt_manager.py delete "prompt-id-or-name"

# Search prompts
python prompt_manager.py search "search term"

# Use a custom storage file
python prompt_manager.py --storage my_prompts.json add "My Prompt" --text "Text"
```

### Programmatic Usage

You can also use the prompt manager programmatically:

```python
from src.prompt_manager.prompt_manager import PromptManager

# Initialize with custom storage file
manager = PromptManager("my_prompts.json")

# Add a prompt
prompt_id = manager.add_prompt("My Prompt", "This is my prompt text", "category")

# Get a prompt
prompt = manager.get_prompt(prompt_id)

# List all prompts
prompts = manager.list_prompts()

# Search prompts
results = manager.search_prompts("search term")
```

## Storage

Prompts are stored in JSON format in the current working directory. The default file is `prompts.json`, but you can specify a custom path using the `--storage` option.

Example storage file structure:
```json
{
  "prompts": {
    "uuid-1": {
      "id": "uuid-1",
      "name": "Greeting Prompt",
      "text": "Hello! How can I assist you today?",
      "category": "greeting",
      "created_at": "2025-07-26T10:39:39.738929",
      "modified_at": "2025-07-26T10:39:39.738929"
    }
  }
}
```

## Testing

Run all tests:
```bash
python -m pytest tests/ -v
```

Run specific test files:
```bash
python -m pytest tests/test_prompt_manager.py -v
python -m pytest tests/test_cli.py -v
python -m pytest tests/test_demo_script.py -v
```

## Project Structure

```
prompt-manager/
├── src/prompt_manager/
│   ├── __init__.py
│   ├── prompt.py              # Prompt class
│   ├── prompt_manager.py      # Main manager class
│   ├── storage.py             # JSON persistence
│   └── cli.py                 # Command-line interface
├── tests/
│   ├── test_prompt.py
│   ├── test_prompt_manager.py
│   ├── test_storage.py
│   ├── test_cli.py
│   └── test_demo_script.py
├── demo_script.py             # Demo script
├── prompt_manager.py          # CLI entry point
└── README.md
```

## Future Enhancements

- GUI interface
- Export/import functionality
- Version history
- Template variables
- Usage statistics
- Backup/restore functionality 