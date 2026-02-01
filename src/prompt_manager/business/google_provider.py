"""
Google Gemini LLM Provider.

Provides integration with Google's Gemini models.
"""
from typing import Optional
from .llm_provider import LLMProvider


class GoogleProvider(LLMProvider):
    """Provider for Google Gemini models.

    Uses lazy initialization pattern matching OllamaProvider.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Google provider.

        Args:
            api_key: Google API key. If None, loads from SecureKeyManager.
        """
        self._name = "google"
        self.api_key = api_key
        self._initialized = False

    def _initialize_client(self):
        """Initialize the Google Generative AI client (lazy initialization)."""
        if self._initialized:
            return

        if not self.api_key:
            try:
                from .key_loader import load_google_api_key
                self.api_key = load_google_api_key()
            except Exception:
                raise ValueError("Google API key is required")

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google client: {e}")

    @property
    def name(self) -> str:
        """Get the provider name."""
        return self._name

    def is_available(self) -> bool:
        """Check if Google API key is configured.

        Returns:
            True if API key is available, False otherwise
        """
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
            prompt: Single prompt string (legacy)
            messages: Array of message dicts with role and content
            **kwargs: model, temperature, max_tokens

        Returns:
            Generated response text
        """
        try:
            self._initialize_client()
            import google.generativeai as genai

            model_name = kwargs.get('model', 'gemini-1.5-flash')

            # Build generation config
            generation_config = {
                'temperature': kwargs.get('temperature', 0.7),
                'max_output_tokens': kwargs.get('max_tokens', 1024),
            }

            # Convert messages to Gemini format
            if messages:
                # Gemini uses 'user' and 'model' roles
                history = []
                system_instruction = None

                for msg in messages:
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')

                    if role == 'system':
                        system_instruction = content
                    elif role == 'assistant':
                        history.append({'role': 'model', 'parts': [content]})
                    else:
                        history.append({'role': 'user', 'parts': [content]})

                # Create model with system instruction if present
                if system_instruction:
                    model = genai.GenerativeModel(
                        model_name,
                        system_instruction=system_instruction
                    )
                else:
                    model = genai.GenerativeModel(model_name)

                # Start chat with history (excluding last message)
                if len(history) > 1:
                    chat = model.start_chat(history=history[:-1])
                    response = chat.send_message(
                        history[-1]['parts'][0],
                        generation_config=generation_config
                    )
                elif history:
                    response = model.generate_content(
                        history[0]['parts'][0],
                        generation_config=generation_config
                    )
                else:
                    raise ValueError("Messages array is empty")

            elif prompt:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config
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
