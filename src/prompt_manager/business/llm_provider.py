from abc import ABC, abstractmethod
from typing import Optional
import openai

class LLMProvider(ABC):
    @abstractmethod
    def send_prompt(self, prompt: str, **kwargs) -> str:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str]):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = openai.OpenAI(api_key=api_key)

    def send_prompt(self, prompt: str, **kwargs) -> str:
        try:
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