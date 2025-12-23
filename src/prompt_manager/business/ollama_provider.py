"""
Ollama LLM Provider.

Provides integration with local Ollama models.
"""
from typing import Optional
import ollama
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
        self.client = None
        self._initialized = False

    def _get_client(self) -> ollama.Client:
        """Get or create Ollama client (lazy initialization).

        Returns:
            Configured Ollama client
        """
        if not self._initialized:
            self.client = ollama.Client(host=self.base_url)
            self._initialized = True
        return self.client

    @property
    def name(self) -> str:
        """Get the provider name."""
        return self._name

    def is_available(self) -> bool:
        """Check if Ollama server is available.

        Returns:
            True if Ollama server responds, False otherwise
        """
        try:
            client = self._get_client()
            client.list()
            return True
        except Exception:
            return False

    def generate(self, prompt: str = None, messages: list = None, **kwargs) -> str:
        """Generate text from a prompt or messages array.

        Args:
            prompt: Single prompt string (legacy)
            messages: Array of message dicts with role and content (preferred)
            **kwargs: Additional parameters (model)

        Returns:
            Generated text response
        """
        # Support both prompt string and messages array
        if messages:
            msg_array = messages
        elif prompt:
            msg_array = [{"role": "user", "content": prompt}]
        else:
            raise ValueError("Either prompt or messages must be provided")

        # Get model from kwargs or use default
        model = kwargs.get('model', self.default_model)

        # Generate response using Ollama
        client = self._get_client()
        response = client.chat(model=model, messages=msg_array)

        return response['message']['content']
