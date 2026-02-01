"""
Anthropic LLM Provider.

Provides integration with Claude models via the Anthropic API.
"""
from typing import Optional
from .llm_provider import LLMProvider


class AnthropicProvider(LLMProvider):
    """Provider for Anthropic Claude models.

    Uses lazy initialization pattern matching OllamaProvider.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key. If None, loads from SecureKeyManager.
        """
        self._name = "anthropic"
        self.api_key = api_key
        self.client = None
        self._initialized = False

    def _get_client(self):
        """Get or create Anthropic client (lazy initialization).

        Returns:
            Configured Anthropic client
        """
        if self._initialized:
            return self.client

        if not self.api_key:
            try:
                from .key_loader import load_anthropic_api_key
                self.api_key = load_anthropic_api_key()
            except Exception:
                raise ValueError("Anthropic API key is required")

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self._initialized = True
            return self.client
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Anthropic client: {e}")

    @property
    def name(self) -> str:
        """Get the provider name."""
        return self._name

    def is_available(self) -> bool:
        """Check if Anthropic API key is configured.

        Returns:
            True if API key is available, False otherwise
        """
        try:
            if self.api_key:
                return True
            from .key_loader import load_anthropic_api_key
            self.api_key = load_anthropic_api_key()
            return bool(self.api_key)
        except Exception:
            return False

    def generate(self, prompt: str = None, messages: list = None, **kwargs) -> str:
        """Generate text using Claude.

        Args:
            prompt: Single prompt string (legacy)
            messages: Array of message dicts with role and content
            **kwargs: model, temperature, max_tokens

        Returns:
            Generated response text
        """
        try:
            client = self._get_client()

            # Handle message format - Anthropic requires system prompt separately
            if messages:
                msg_array = messages
            elif prompt:
                msg_array = [{"role": "user", "content": prompt}]
            else:
                raise ValueError("Either prompt or messages must be provided")

            # Extract system message if present (Anthropic API handles it separately)
            system_prompt = None
            filtered_messages = []
            for msg in msg_array:
                if msg.get('role') == 'system':
                    system_prompt = msg.get('content', '')
                else:
                    filtered_messages.append(msg)

            # Build API request
            api_kwargs = {
                'model': kwargs.get('model', 'claude-3-5-sonnet-20241022'),
                'max_tokens': kwargs.get('max_tokens', 1024),
                'messages': filtered_messages,
            }

            if system_prompt:
                api_kwargs['system'] = system_prompt

            # Anthropic temperature is 0-1 (OpenAI is 0-2), so we scale
            temperature = kwargs.get('temperature', 0.7)
            api_kwargs['temperature'] = min(1.0, temperature)

            response = client.messages.create(**api_kwargs)

            # Extract text from response
            return response.content[0].text

        except Exception as e:
            error_msg = str(e)
            # Add helpful context for common errors
            if 'credit' in error_msg.lower() or 'billing' in error_msg.lower():
                raise RuntimeError(
                    f"Anthropic API billing issue: {error_msg}. "
                    "Please check your account credits at https://console.anthropic.com/"
                )
            elif 'rate' in error_msg.lower():
                raise RuntimeError(
                    f"Anthropic rate limit exceeded: {error_msg}. "
                    "Please wait and try again."
                )
            elif 'authentication' in error_msg.lower() or 'invalid' in error_msg.lower() or 'api_key' in error_msg.lower():
                raise RuntimeError(
                    f"Anthropic authentication failed: {error_msg}. "
                    "Please verify your API key is correct."
                )
            raise RuntimeError(f"Anthropic API Error: {error_msg}")
