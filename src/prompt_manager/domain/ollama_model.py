"""
OllamaModel domain model.

Pure business logic for Ollama model representation with zero dependencies.
"""


class OllamaModel:
    """Represents an Ollama model with name and tag.

    Ollama models follow the pattern: name:tag (e.g., gemma3:4b)
    This is pure domain logic - no dependencies on Ollama client or infrastructure.
    """

    def __init__(self, full_name: str):
        """Parse Ollama model name into components.

        Args:
            full_name: Full model identifier (e.g., "gemma3:4b")
        """
        parts = full_name.split(':')
        self.name = parts[0]
        self.tag = parts[1] if len(parts) > 1 else 'latest'
        self.full_name = full_name
