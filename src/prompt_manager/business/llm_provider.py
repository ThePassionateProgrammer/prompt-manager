from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Generator
import openai

class LLMProvider(ABC):
    @abstractmethod
    def send_prompt(self, prompt: str, **kwargs) -> str:
        """Send a single prompt and get complete response."""
        pass

    @abstractmethod
    def send_message_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Send messages and stream response chunks."""
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = None
        self._initialized = False
    
    def _initialize_client(self):
        """Lazy initialization of the OpenAI client."""
        if self._initialized:
            return
        
        # If no API key provided, try to load from secure storage
        if not self.api_key:
            try:
                from .key_loader import load_openai_api_key
                self.api_key = load_openai_api_key()
            except ValueError:
                raise ValueError("OpenAI API key is required")
        
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
            self._initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}")

    def send_prompt(self, prompt: str, **kwargs) -> str:
        """Send a prompt to the LLM."""
        try:
            self._initialize_client()

            response = self.client.chat.completions.create(
                model=kwargs.get('model', 'gpt-3.5-turbo'),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 256),
                temperature=kwargs.get('temperature', 0.7),
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM Error: {e}")

    def send_message_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Send messages and stream response chunks (not implemented for OpenAI yet)."""
        raise NotImplementedError("Streaming not yet implemented for OpenAI provider")

class OllamaProvider(LLMProvider):
    """Provider for Ollama local LLMs."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "gemma3:4b"
    ):
        """
        Initialize Ollama provider.

        Args:
            base_url: Ollama server URL
            default_model: Default model to use (Ember = gemma3:4b)
        """
        import ollama
        self.base_url = base_url
        self.default_model = default_model
        self.client = ollama.Client(host=base_url)

    def send_prompt(self, prompt: str, **kwargs) -> str:
        """Send a single prompt (non-streaming)."""
        model = kwargs.get('model', self.default_model)
        messages = [{'role': 'user', 'content': prompt}]

        try:
            response = self.client.chat(
                model=model,
                messages=messages,
                stream=False
            )
            return response['message']['content']
        except Exception as e:
            raise RuntimeError(f"Ollama Error: {e}")

    def send_message_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Send messages and stream response chunks."""
        model = model or self.default_model

        try:
            stream = self.client.chat(
                model=model,
                messages=messages,
                stream=True
            )

            for chunk in stream:
                # Ollama returns chunks as: {'message': {'content': '...'}}
                if 'message' in chunk and 'content' in chunk['message']:
                    yield chunk['message']['content']
        except Exception as e:
            raise RuntimeError(f"Ollama Stream Error: {e}")

    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            models_response = self.client.list()
            return [model['name'] for model in models_response.get('models', [])]
        except Exception as e:
            raise RuntimeError(f"Failed to list models: {e}")

    def check_ollama_health(self) -> Dict[str, any]:
        """Check Ollama server health and model availability."""
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


# Placeholder for local model support
def get_local_model_provider(*args, **kwargs):
    """Get a local model provider (Ollama)."""
    return OllamaProvider(*args, **kwargs) 