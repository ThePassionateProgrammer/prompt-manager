from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Generator
import openai

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        pass

    def send_prompt(self, prompt: str, **kwargs) -> str:
        """Send a single prompt and get complete response. Defaults to generate()."""
        return self.generate(prompt, **kwargs)

    def send_message_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Send messages and stream response chunks. Override for streaming support."""
        raise NotImplementedError(f"{self.name} does not support streaming")

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the provider name."""
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = None
        self._initialized = False
        self._name = "openai"
    
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

    @property
    def name(self) -> str:
        """Get the provider name."""
        return self._name
    
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured."""
        try:
            if not self.api_key:
                from .key_loader import load_openai_api_key
                self.api_key = load_openai_api_key()
            return bool(self.api_key)
        except (ValueError, ImportError):
            return False
    
    def generate(self, prompt: str = None, messages: list = None, **kwargs) -> str:
        """Generate text from a prompt or messages array.

        Args:
            prompt: Single prompt string (legacy)
            messages: Array of message dicts with role and content (preferred)
            **kwargs: Additional parameters (model, temperature, max_tokens)

        Returns:
            Generated text response
        """
        try:
            self._initialize_client()

            # Support both prompt string and messages array
            if messages:
                msg_array = messages
            elif prompt:
                msg_array = [{"role": "user", "content": prompt}]
            else:
                raise ValueError("Either prompt or messages must be provided")


            response = self.client.chat.completions.create(
                model=kwargs.get('model', 'gpt-3.5-turbo'),
                messages=msg_array,
                max_tokens=kwargs.get('max_tokens', 256),
                temperature=kwargs.get('temperature', 0.7),
            )
            return response.choices[0].message.content

        except openai.RateLimitError as e:
            # 429 errors - distinguish between quota/billing and rate limiting
            error_msg = str(e)
            if 'quota' in error_msg.lower() or 'billing' in error_msg.lower():
                raise RuntimeError(
                    "OpenAI API quota exceeded. This usually means:\n"
                    "1. Your account has insufficient credits\n"
                    "2. You've exceeded your spending limit\n"
                    "Please visit https://platform.openai.com/account/billing to add credits."
                )
            raise RuntimeError(
                f"OpenAI rate limit exceeded. Please wait and retry. Details: {error_msg}"
            )

        except openai.AuthenticationError as e:
            # Provide specific guidance for common key issues
            error_detail = str(e)
            if 'sk-test' in error_detail or 'test' in self.api_key.lower() if self.api_key else False:
                raise RuntimeError(
                    "OpenAI authentication failed: You appear to be using a test/placeholder API key.\n"
                    "Please replace it with a valid API key from https://platform.openai.com/api-keys"
                )
            raise RuntimeError(
                "OpenAI authentication failed: Invalid API key.\n"
                "Please check your API key at https://platform.openai.com/api-keys\n"
                "Common issues:\n"
                "- Key may have been revoked or expired\n"
                "- Key may have been copied incorrectly\n"
                "- Key may belong to a different organization"
            )

        except openai.BadRequestError as e:
            raise RuntimeError(f"OpenAI request error: {e}")

        except Exception as e:
            raise RuntimeError(f"LLM Error: {e}")
    
    # Keep the old method for backward compatibility
    def send_prompt(self, prompt: str, **kwargs) -> str:
        """Send a prompt to the LLM (deprecated - use generate instead)."""
        return self.generate(prompt, **kwargs)

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

    @property
    def name(self) -> str:
        return 'ollama'

    def is_available(self) -> bool:
        try:
            self.client.list()
            return True
        except Exception:
            return False

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        return self.send_prompt(prompt, **kwargs)

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