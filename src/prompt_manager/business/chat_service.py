"""ChatService orchestrates chat conversations with LLM streaming."""
from typing import Dict, List, Optional, Generator
from ..domain.conversation import Conversation
from .conversation_storage import ConversationStorage
from .llm_provider import LLMProvider


class ChatService:
    """
    Service layer for managing chat conversations.

    Coordinates between:
    - Domain models (Conversation, ChatMessage)
    - Storage (ConversationStorage)
    - LLM Provider (OllamaProvider)

    Responsibilities:
    - Create and manage conversations
    - Stream LLM responses with auto-save
    - Maintain in-memory cache for performance
    """

    def __init__(
        self,
        storage: Optional[ConversationStorage] = None,
        llm_provider: Optional[LLMProvider] = None
    ):
        """
        Initialize ChatService.

        Args:
            storage: ConversationStorage instance (creates default if None)
            llm_provider: LLMProvider instance (required for sending messages)
        """
        self.storage = storage or ConversationStorage()
        self.llm_provider = llm_provider
        self.conversations: Dict[str, Conversation] = {}

        # Load existing conversations into cache
        self._load_conversations()

    def _load_conversations(self) -> None:
        """Load all conversations from storage into memory cache."""
        conversations = self.storage.list_conversations()
        for conv in conversations:
            self.conversations[conv.id] = conv

    def create_conversation(
        self,
        title: str = "New Conversation",
        model: str = "gemma3:4b"
    ) -> str:
        """
        Create a new conversation.

        Args:
            title: Conversation title (default: "New Conversation")
            model: LLM model to use (default: "gemma3:4b")

        Returns:
            Conversation ID (UUID string)
        """
        conversation = Conversation(title=title, model=model)

        # Add to cache
        self.conversations[conversation.id] = conversation

        # Persist to storage
        self.storage.save_conversation(conversation)

        return conversation.id

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Get a conversation by ID.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Conversation object or None if not found
        """
        return self.conversations.get(conversation_id)

    def list_conversations(self) -> List[Conversation]:
        """
        List all conversations, sorted by updated_at descending.

        Returns:
            List of Conversation objects, most recently updated first
        """
        conversations = list(self.conversations.values())
        conversations.sort(key=lambda c: c.updated_at, reverse=True)
        return conversations

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.

        Args:
            conversation_id: Conversation UUID

        Returns:
            True if deleted, False if not found
        """
        if conversation_id not in self.conversations:
            return False

        # Remove from cache
        del self.conversations[conversation_id]

        # Remove from storage
        self.storage.delete_conversation(conversation_id)

        return True

    def send_message(
        self,
        conversation_id: str,
        message: str
    ) -> Generator[str, None, None]:
        """
        Send a message and stream the LLM response.

        This is a generator that yields response chunks as they arrive from the LLM.
        After streaming completes, the conversation is saved to storage.

        Args:
            conversation_id: Conversation UUID
            message: User message content

        Yields:
            Response chunks from LLM

        Raises:
            KeyError: If conversation not found
            RuntimeError: If LLM provider not configured or LLM error occurs
        """
        # Get conversation
        if conversation_id not in self.conversations:
            raise KeyError(f"Conversation not found: {conversation_id}")

        if self.llm_provider is None:
            raise RuntimeError("LLM provider not configured")

        conversation = self.conversations[conversation_id]

        # Add user message
        conversation.add_message('user', message)

        # Save after user message added
        self.storage.save_conversation(conversation)

        # Get messages formatted for LLM
        llm_messages = conversation.get_messages_for_llm()

        # Stream response from LLM
        response_chunks = []
        try:
            for chunk in self.llm_provider.send_message_stream(
                messages=llm_messages,
                model=conversation.model
            ):
                response_chunks.append(chunk)
                yield chunk
        finally:
            # After streaming completes (or errors), add assistant response
            full_response = ''.join(response_chunks)
            conversation.add_message('assistant', full_response)

            # Save conversation with assistant response
            self.storage.save_conversation(conversation)
