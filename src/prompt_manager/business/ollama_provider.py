"""
Ollama LLM Provider.

Provides integration with local Ollama models.
Supports both synchronous generation and streaming responses.
"""
from typing import Optional, List, Dict, Generator
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

    def send_prompt(self, prompt: str, **kwargs) -> str:
        """Send a single prompt (non-streaming).

        Args:
            prompt: The prompt text
            **kwargs: Additional parameters (model)

        Returns:
            Generated text response
        """
        model = kwargs.get('model', self.default_model)
        messages = [{'role': 'user', 'content': prompt}]

        try:
            client = self._get_client()
            response = client.chat(model=model, messages=messages, stream=False)
            return response['message']['content']
        except Exception as e:
            raise RuntimeError(f"Ollama Error: {e}")

    def send_message_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Stream response chunks for a message sequence.

        Args:
            messages: List of message dicts with role and content
            model: Model to use (defaults to self.default_model)

        Yields:
            Response text chunks as they arrive
        """
        model = model or self.default_model

        try:
            client = self._get_client()
            stream = client.chat(model=model, messages=messages, stream=True)

            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
        except Exception as e:
            raise RuntimeError(f"Ollama Stream Error: {e}")

    def list_models(self) -> List[str]:
        """List available Ollama models.

        Returns:
            List of model name strings
        """
        try:
            client = self._get_client()
            models_response = client.list()
            return [model['name'] for model in models_response.get('models', [])]
        except Exception as e:
            raise RuntimeError(f"Failed to list models: {e}")

    def check_ollama_health(self) -> Dict[str, any]:
        """Check Ollama server health and model availability.

        Returns:
            Dict with connection status and available models
        """
        try:
            models = self.list_models()
            has_default = self.default_model in models

            return {
                'connected': True,
                'available_models': models,
                'default_model': self.default_model,
                'default_model_available': has_default
            }
        except Exception as e:
            return {
                'connected': False,
                'error': str(e)
            }
