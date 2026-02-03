"""
Conversation domain models.

Pure business logic for conversation/message management with zero framework dependencies.
Contains:
- ConversationBuilder: Builds message arrays for LLM conversations
- ContextWindowManager: Manages context window limits and message trimming
- Conversation: Aggregate root for chat conversations
"""
from datetime import datetime
from typing import List, Optional
import uuid
from .chat_message import ChatMessage


class ConversationBuilder:
    """Builds message arrays for LLM conversations.

    This is pure domain logic - no dependencies on Flask, databases, or infrastructure.
    Encapsulates the business rules around how conversations are structured.
    """

    def build_messages(self, user_message: str, history: list, system_prompt: str = None) -> list:
        """Build message array for LLM with system prompt, history, and new message.

        Business Rule: Messages must be ordered:
        1. System prompt (if provided)
        2. Historical messages
        3. New user message

        Args:
            user_message: The new message from the user
            history: List of previous messages in the conversation
            system_prompt: Optional system-level instructions for the LLM

        Returns:
            List of message dictionaries ready for LLM consumption
        """
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })

        # Add history
        if history:
            messages.extend(history)

        # Add new user message
        messages.append({
            'role': 'user',
            'content': user_message
        })

        return messages

    def validate_message(self, message: str) -> tuple:
        """Validate a message before adding to conversation.

        Business Rule: Messages must be non-empty strings.

        Args:
            message: The message to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not message:
            return False, "Message cannot be empty"

        if not isinstance(message, str):
            return False, "Message must be a string"

        if not message.strip():
            return False, "Message cannot be only whitespace"

        return True, ""


class ContextWindowManager:
    """Manages context window limits and message trimming.

    Pure domain logic for handling token limits and conversation trimming.
    """

    def should_trim(self, current_tokens: int, model_limit: int, threshold: float = 0.9) -> bool:
        """Determine if conversation should be trimmed.

        Business Rule: Trim when approaching threshold% of context limit.

        Args:
            current_tokens: Current number of tokens in conversation
            model_limit: Maximum tokens for the model
            threshold: Percentage of limit at which to trim (default 0.9 = 90%)

        Returns:
            True if should trim, False otherwise
        """
        if model_limit <= 0:
            return False

        usage_ratio = current_tokens / model_limit
        return usage_ratio >= threshold

    def calculate_keep_count(self, total_messages: int, keep_recent: int = 5) -> int:
        """Calculate how many messages to keep when trimming.

        Business Rule: Always keep system prompt + recent N messages.

        Args:
            total_messages: Total number of messages in conversation
            keep_recent: Number of recent messages to keep (default 5)

        Returns:
            Number of messages to keep
        """
        # Always keep at least 1 (the system prompt)
        if total_messages <= 1:
            return total_messages

        # Keep system prompt + keep_recent messages
        # (System prompt is always first, so +1)
        return min(total_messages, keep_recent + 1)


class Conversation:
    """Aggregate root for a chat conversation."""

    def __init__(
        self,
        title: str = "New Conversation",
        model: str = "gemma3:4b"
    ):
        """
        Create a new conversation.

        Args:
            title: Conversation title (defaults to "New Conversation")
            model: LLM model to use (defaults to "gemma3:4b" - Ember)
        """
        self.id = str(uuid.uuid4())
        self.title = title
        self.model = model
        self.messages: List[ChatMessage] = []
        self.created_at = datetime.now()
        self.updated_at = self.created_at

    def add_message(self, role: str, content: str) -> ChatMessage:
        """
        Add a message to the conversation.

        This method enforces business rules:
        - Auto-generates title from first user message
        - Assigns sequential IDs to messages
        - Updates conversation timestamp

        Args:
            role: Message role (user, assistant, or system)
            content: Message content

        Returns:
            The created ChatMessage
        """
        # Create the message
        message = ChatMessage(role, content)
        message.id = len(self.messages)  # Sequential ID
        self.messages.append(message)

        # Update conversation timestamp
        self.updated_at = datetime.now()

        # Auto-generate title if this is the first user message
        self._auto_generate_title_if_needed(role, content)

        return message

    def _auto_generate_title_if_needed(self, role: str, content: str) -> None:
        """
        Auto-generate conversation title from first user message.

        Business rule: If conversation has default title and this is the first
        user message, use the message content as the title (truncated to 50 chars).

        Args:
            role: Message role
            content: Message content
        """
        if role != 'user' or self.title != "New Conversation":
            return

        # Check if there are any previous user messages (excluding current)
        has_previous_user_messages = any(
            msg.role == 'user' for msg in self.messages[:-1]
        )

        if not has_previous_user_messages:
            # This is the first user message - generate title
            self.title = content[:50] + '...' if len(content) > 50 else content

    def get_messages_for_llm(self) -> List[dict]:
        """
        Get messages in Ollama/LLM format.

        Returns:
            List of message dicts with 'role' and 'content' keys
        """
        return [
            {'role': msg.role, 'content': msg.content}
            for msg in self.messages
        ]

    def to_dict(self) -> dict:
        """
        Convert conversation to dictionary for serialization.

        Returns:
            Dictionary representation of the conversation
        """
        return {
            'id': self.id,
            'title': self.title,
            'model': self.model,
            'messages': [msg.to_dict() for msg in self.messages],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Conversation':
        """
        Create a conversation from dictionary.

        Args:
            data: Dictionary with conversation data

        Returns:
            Conversation instance
        """
        conv = cls(title=data['title'], model=data['model'])
        conv.id = data['id']
        conv.created_at = datetime.fromisoformat(data['created_at'])
        conv.updated_at = datetime.fromisoformat(data['updated_at'])
        conv.messages = [ChatMessage.from_dict(msg) for msg in data['messages']]
        return conv
