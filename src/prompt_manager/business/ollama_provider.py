"""
Ollama LLM Provider.

Provides integration with local Ollama models.
"""
from typing import Optional
from .llm_provider import LLMProvider


class OllamaProvider(LLMProvider):
    """Provider for Ollama local LLM models.

    Connects to local Ollama server at http://localhost:11434
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gemma3:4b"):
        """Initialize Ollama provider.

        Args:
            base_url: Ollama server URL (default: http://localhost:11434)
            model: Default model to use (default: gemma3:4b)
        """
        self._name = "ollama"
        self.base_url = base_url
        self.default_model = model

    @property
    def name(self) -> str:
        """Get the provider name."""
        return self._name

    def is_available(self) -> bool:
        """Check if Ollama server is available."""
        # TODO: Implement health check
        return False

    def generate(self, prompt: str = None, messages: list = None, **kwargs) -> str:
        """Generate text from a prompt or messages array."""
        # TODO: Implement generation
        raise NotImplementedError("Generation not yet implemented")
