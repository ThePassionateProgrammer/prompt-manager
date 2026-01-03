"""
ChatSession domain model.

Pure business logic for managing a user's chat session with zero dependencies.
Encapsulates session state, message management, and session settings.
"""
from typing import Optional, List, Dict


class ChatSession:
    """Represents a user's current chat session.

    Business Rules:
    - Sessions track messages, provider, model, and settings
    - Messages must be non-empty and have valid roles
    - Settings (provider, model, temperature) can be updated
    - Sessions can be cleared (removes messages, preserves settings)
    - System prompt is optional and prepended to messages when set
    """

    VALID_ROLES = {'user', 'assistant', 'system'}

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """Initialize a new chat session.

        Args:
            provider: LLM provider (e.g., 'openai', 'ollama')
            model: Model name (e.g., 'gpt-4', 'gemma:7b')
            temperature: Sampling temperature (0.0-2.0), default 0.7
            max_tokens: Maximum tokens in response, default 2000
        """
        self.messages: List[Dict[str, str]] = []
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_prompt: Optional[str] = None

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the session.

        Business Rule: Messages must be non-empty and have valid roles.

        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content

        Raises:
            ValueError: If content is empty or role is invalid
        """
        # Validate content
        if not content or not content.strip():
            raise ValueError("Message cannot be empty")

        # Validate role
        if role not in self.VALID_ROLES:
            raise ValueError(f"Invalid role: {role}. Must be one of {self.VALID_ROLES}")

        # Add message
        self.messages.append({
            'role': role,
            'content': content
        })

    def update_settings(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> None:
        """Update session settings.

        Args:
            provider: New provider (if provided)
            model: New model (if provided)
            temperature: New temperature (if provided)
            max_tokens: New max tokens (if provided)
        """
        if provider is not None:
            self.provider = provider
        if model is not None:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
        if max_tokens is not None:
            self.max_tokens = max_tokens

    def clear(self) -> None:
        """Clear all messages from the session.

        Business Rule: Clearing preserves settings (provider, model, temperature).
        """
        self.messages = []

    def is_empty(self) -> bool:
        """Check if session has no messages.

        Returns:
            True if no messages, False otherwise
        """
        return len(self.messages) == 0

    def message_count(self) -> int:
        """Get number of messages in session.

        Returns:
            Number of messages
        """
        return len(self.messages)

    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt for this session.

        Args:
            prompt: System prompt content
        """
        self.system_prompt = prompt

    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        """Get messages formatted for LLM, including system prompt if set.

        Business Rule: System prompt is always first if present.

        Returns:
            List of message dicts ready for LLM consumption
        """
        messages = []

        # Add system prompt if set
        if self.system_prompt:
            messages.append({
                'role': 'system',
                'content': self.system_prompt
            })

        # Add all conversation messages
        messages.extend(self.messages)

        return messages
