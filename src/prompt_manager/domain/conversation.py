"""
Conversation domain aggregate root.

A Conversation is the aggregate root that manages a collection of ChatMessage entities.
It enforces business rules like auto-title generation and message ordering.
"""
from datetime import datetime
from typing import List, Optional
import uuid
from .chat_message import ChatMessage


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

        # Auto-generate title from first user message
        # Check if this is the first user message (regardless of position)
        if role == 'user' and self.title == "New Conversation":
            # Check if there are any previous user messages
            has_previous_user_messages = any(
                msg.role == 'user' for msg in self.messages[:-1]  # Exclude the current message
            )
            if not has_previous_user_messages:
                # This is the first user message, auto-generate title
                if len(content) > 50:
                    self.title = content[:50] + '...'
                else:
                    self.title = content

        return message

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
