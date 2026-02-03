"""
Chat Service - Business layer for chat operations.

Coordinates between domain models, providers, and token management.
Supports both multi-provider chat (via LLMProviderManager) and
conversation management with SSE streaming (via ConversationStorage).
"""
from typing import Dict, List, Tuple, Optional, Generator
from src.prompt_manager.domain.conversation import ConversationBuilder, ContextWindowManager, Conversation
from .conversation_storage import ConversationStorage
from .llm_provider import LLMProvider

# Conditional imports for multi-provider support
try:
    from src.prompt_manager.business.token_manager import TokenManager
    from src.prompt_manager.business.llm_provider_manager import LLMProviderManager
    _HAS_PROVIDER_MANAGER = True
except ImportError:
    _HAS_PROVIDER_MANAGER = False


class ChatService:
    """Service for handling chat operations.

    Supports two modes:
    1. Multi-provider mode: Uses LLMProviderManager and TokenManager for
       advanced token tracking and auto-trimming across providers.
    2. Conversation mode: Uses ConversationStorage and a single LLMProvider
       for conversation management with SSE streaming.

    Both modes can coexist in the same instance.
    """

    def __init__(
        self,
        provider_manager=None,
        token_manager=None,
        storage: Optional[ConversationStorage] = None,
        llm_provider: Optional[LLMProvider] = None
    ):
        """Initialize chat service.

        Args:
            provider_manager: Manager for LLM providers (multi-provider mode)
            token_manager: Manager for token calculation and limits (multi-provider mode)
            storage: ConversationStorage instance (conversation mode, creates default if None)
            llm_provider: LLMProvider instance (conversation mode, required for sending messages)
        """
        # Multi-provider mode
        self.provider_manager = provider_manager
        self.token_manager = token_manager
        self.conversation_builder = ConversationBuilder()
        self.context_manager = ContextWindowManager()

        # Conversation mode
        self.storage = storage or ConversationStorage()
        self.llm_provider = llm_provider
        self.conversations: Dict[str, Conversation] = {}

        # Load existing conversations into cache
        self._load_conversations()

    def _load_conversations(self) -> None:
        """Load all conversations from storage into memory cache."""
        try:
            conversations = self.storage.list_conversations()
            for conv in conversations:
                self.conversations[conv.id] = conv
        except Exception:
            # Storage may not be configured; that's okay
            pass

    # ---- Multi-provider mode methods ----

    def send_message_with_provider(
        self,
        message: str,
        provider_name: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
        auto_trim: bool = False
    ) -> Dict:
        """Send a chat message via a specific provider and get response.

        Business Rules:
        - Messages must be non-empty
        - System prompt is prepended if provided
        - History is included if provided
        - Auto-trimming occurs if enabled and approaching context limit
        - Token usage is calculated and returned

        Args:
            message: User message to send
            provider_name: Name of LLM provider
            model: Model identifier
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens in response
            history: Previous messages in conversation
            system_prompt: System-level instructions
            auto_trim: Whether to auto-trim when approaching limit

        Returns:
            Dict with response, metadata, and token usage

        Raises:
            ValueError: If message is invalid or provider not found
        """
        if not self.provider_manager:
            raise RuntimeError("Provider manager not configured")

        # Validate message
        is_valid, error = self.conversation_builder.validate_message(message)
        if not is_valid:
            raise ValueError(error)

        # Get provider
        provider = self.provider_manager.get_provider(provider_name)
        if not provider:
            raise ValueError(
                f'Provider {provider_name} not found. '
                'Please add your API key in Settings.'
            )

        # Build messages array
        history = history or []
        messages = self.conversation_builder.build_messages(
            user_message=message,
            history=history,
            system_prompt=system_prompt
        )

        # Auto-trim if needed
        trimmed_count = 0
        if auto_trim and self.token_manager:
            messages, trimmed_count = self._auto_trim_if_needed(
                messages, model
            )

        # Calculate token usage before sending
        token_usage = {}
        if self.token_manager:
            token_usage = self.token_manager.calculate_token_usage(messages, model)

        # Generate response
        response = provider.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Update token usage with completion
        if self.token_manager:
            token_usage = self.token_manager.update_with_completion(
                token_usage, response
            )

        # Build result
        result = {
            'response': response,
            'provider': provider_name,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'token_usage': token_usage,
            'metadata': {
                'message_count': len(messages) - 1,  # Exclude system prompt
                'has_history': len(history) > 0
            }
        }

        if trimmed_count > 0:
            result['trimmed'] = trimmed_count

        return result

    def _auto_trim_if_needed(
        self,
        messages: List[Dict[str, str]],
        model: str
    ) -> Tuple[List[Dict[str, str]], int]:
        """Auto-trim messages if approaching context limit.

        Business Rule: Trim when at 90% of context limit,
        keeping system prompt + 5 most recent messages.

        Args:
            messages: Message list to potentially trim
            model: Model identifier for context limits

        Returns:
            Tuple of (messages, trimmed_count)
        """
        trimmed_count = 0

        if not self.token_manager:
            return messages, trimmed_count

        # Calculate current token usage
        prompt_tokens = self.token_manager.calculate_message_tokens(messages)

        # Check if trimming needed
        if self.token_manager.should_trim(prompt_tokens, model, threshold=0.9):
            # Use domain model for business rule: how many to keep
            keep_count = self.context_manager.calculate_keep_count(
                len(messages),
                keep_recent=5
            )

            # Trim messages
            messages, trimmed_count = self.token_manager.trim_messages(
                messages,
                keep_count=keep_count
            )

        return messages, trimmed_count

    # ---- Conversation management mode methods ----

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
