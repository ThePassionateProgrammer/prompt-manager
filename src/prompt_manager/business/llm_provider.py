from abc import ABC, abstractmethod
from typing import Optional
import openai

class LLMProvider(ABC):
    @abstractmethod
    def send_prompt(self, prompt: str, **kwargs) -> str:
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

# Placeholder for local model support
def get_local_model_provider(*args, **kwargs):
    raise NotImplementedError("Local model provider not implemented yet.") 