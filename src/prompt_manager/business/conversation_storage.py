"""Storage manager for conversations."""
import json
import os
from typing import Dict, List
from ..domain.conversation import Conversation


class ConversationStorage:
    """Manages persistence of conversations to JSON file."""

    def __init__(self, file_path: str = "conversations.json"):
        """
        Initialize conversation storage.

        Args:
            file_path: Path to JSON file for storing conversations
        """
        self.file_path = file_path

    def save_conversation(self, conversation: Conversation) -> None:
        """
        Save or update a conversation in storage.

        Args:
            conversation: Conversation to save

        Raises:
            IOError: If save operation fails
        """
        # Load existing conversations
        conversations = self._load_all()

        # Update or add this conversation
        conversations[conversation.id] = conversation.to_dict()

        # Save back to file
        self._save_all(conversations)

    def load_conversation(self, conversation_id: str) -> Conversation:
        """
        Load a conversation by ID.

        Args:
            conversation_id: ID of conversation to load

        Returns:
            Conversation object

        Raises:
            KeyError: If conversation not found
        """
        conversations = self._load_all()

        if conversation_id not in conversations:
            raise KeyError(f"Conversation not found: {conversation_id}")

        return Conversation.from_dict(conversations[conversation_id])

    def list_conversations(self) -> List[Conversation]:
        """
        List all conversations, sorted by updated_at descending.

        Returns:
            List of Conversation objects, most recently updated first
        """
        conversations = self._load_all()

        # Convert to Conversation objects
        conv_objects = [
            Conversation.from_dict(conv_data)
            for conv_data in conversations.values()
        ]

        # Sort by updated_at, most recent first
        conv_objects.sort(key=lambda c: c.updated_at, reverse=True)

        return conv_objects

    def delete_conversation(self, conversation_id: str) -> None:
        """
        Delete a conversation by ID.

        Args:
            conversation_id: ID of conversation to delete

        Note:
            Silently succeeds if conversation doesn't exist
        """
        conversations = self._load_all()

        if conversation_id in conversations:
            del conversations[conversation_id]
            self._save_all(conversations)

    def _load_all(self) -> Dict[str, dict]:
        """
        Load all conversations from file.

        Returns:
            Dictionary mapping conversation IDs to conversation dicts
        """
        if not os.path.exists(self.file_path):
            return {}

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # File exists but is invalid/empty
            return {}
        except Exception as e:
            raise IOError(f"Failed to load conversations: {e}")

    def _save_all(self, conversations: Dict[str, dict]) -> None:
        """
        Save all conversations to file.

        Args:
            conversations: Dictionary mapping conversation IDs to dicts

        Raises:
            IOError: If save operation fails
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise IOError(f"Failed to save conversations: {e}")
