"""
Google Gemini LLM Provider.

Provides integration with Google's Gemini models using the google-genai SDK.
"""
from typing import Optional
from .llm_provider import LLMProvider


class GoogleProvider(LLMProvider):
    """Provider for Google Gemini models.

    Uses the google-genai SDK with lazy initialization.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Google provider.

        Args:
            api_key: Google API key. If None, loads from SecureKeyManager.
        """
        self._name = "google"
        self.api_key = api_key
        self._initialized = False
        self._client = None

    def _initialize_client(self):
        """Initialize the Google GenAI client (lazy initialization)."""
        if self._initialized:
            return

        if not self.api_key:
            try:
                from .key_loader import load_google_api_key
                self.api_key = load_google_api_key()
            except Exception:
                raise ValueError("Google API key is required")

        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            self._initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google client: {e}")

    @property
    def name(self) -> str:
        """Get the provider name."""
        return self._name

    def is_available(self) -> bool:
        """Check if Google API key is configured."""
        try:
            if self.api_key:
                return True
            from .key_loader import load_google_api_key
            self.api_key = load_google_api_key()
            return bool(self.api_key)
        except Exception:
            return False

    def generate(self, prompt: str = None, messages: list = None, **kwargs) -> str:
        """Generate text using Gemini.

        Args:
            prompt: Single prompt string
            messages: Array of message dicts with role and content
            **kwargs: model, temperature, max_tokens

        Returns:
            Generated response text
        """
        try:
            self._initialize_client()
            from google.genai import types

            model_name = kwargs.get('model', 'gemini-2.0-flash')

            # Build generation config
            config_kwargs = {
                'temperature': kwargs.get('temperature', 0.7),
                'max_output_tokens': kwargs.get('max_tokens', 1024),
            }

            if messages:
                # Extract system instruction and build contents
                system_instruction = None
                contents = []

                for msg in messages:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')

                    if role == 'system':
                        system_instruction = content
                    elif role == 'assistant':
                        contents.append(types.Content(
                            role='model',
                            parts=[types.Part.from_text(text=content)]
                        ))
                    else:
                        contents.append(types.Content(
                            role='user',
                            parts=[types.Part.from_text(text=content)]
                        ))

                if system_instruction:
                    config_kwargs['system_instruction'] = system_instruction

                if not contents:
                    raise ValueError("Messages array is empty")

                response = self._client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(**config_kwargs)
                )

            elif prompt:
                response = self._client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(**config_kwargs)
                )
            else:
                raise ValueError("Either prompt or messages must be provided")

            return response.text

        except Exception as e:
            error_msg = str(e)
            if 'quota' in error_msg.lower():
                raise RuntimeError(
                    f"Google API quota exceeded: {error_msg}. "
                    "Please check your quota at https://console.cloud.google.com/"
                )
            elif 'invalid' in error_msg.lower() and 'key' in error_msg.lower():
                raise RuntimeError(
                    f"Google API key invalid: {error_msg}. "
                    "Please verify your API key is correct."
                )
            elif 'api_key' in error_msg.lower():
                raise RuntimeError(
                    f"Google API authentication failed: {error_msg}. "
                    "Please verify your API key."
                )
            raise RuntimeError(f"Google API Error: {error_msg}")
