"""
ChatMessage domain entity.

Represents a single message in a conversation with role, content, and timestamp.
This is a pure domain entity with no external dependencies.
"""
from datetime import datetime
from typing import Literal, Optional


class ChatMessage:
    """A single message in a conversation."""

    def __init__(
        self,
        role: Literal['user', 'assistant', 'system'],
        content: str,
        timestamp: Optional[datetime] = None
    ):
        """
        Create a new chat message.

        Args:
            role: The role of the message sender (user, assistant, or system)
            content: The message content
            timestamp: Optional timestamp (defaults to now)
        """
        self.role = role
        self.content = content
        self.timestamp = timestamp if timestamp is not None else datetime.now()
        self.id: Optional[int] = None  # Set by Conversation aggregate

    def to_dict(self) -> dict:
        """
        Convert message to dictionary for serialization.

        Returns:
            Dictionary representation of the message
        """
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'ChatMessage':
        """
        Create a message from dictionary.

        Args:
            data: Dictionary with message data

        Returns:
            ChatMessage instance
        """
        message = cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )
        message.id = data.get('id')
        return message
