from abc import ABC, abstractmethod
from typing import Optional
import openai

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        pass
    
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
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
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
    
    # Keep the old method for backward compatibility
    def send_prompt(self, prompt: str, **kwargs) -> str:
        """Send a prompt to the LLM (deprecated - use generate instead)."""
        return self.generate(prompt, **kwargs)

# Placeholder for local model support
def get_local_model_provider(*args, **kwargs):
    raise NotImplementedError("Local model provider not implemented yet.") 