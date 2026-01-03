"""
Chat Service - Business layer for chat operations.

Coordinates between domain models, providers, and token management.
Keeps routes thin by handling business logic and coordination.
"""
from typing import Dict, List, Tuple, Optional
from src.prompt_manager.domain.conversation import ConversationBuilder, ContextWindowManager
from src.prompt_manager.business.token_manager import TokenManager
from src.prompt_manager.business.llm_provider_manager import LLMProviderManager


class ChatService:
    """Service for handling chat operations.

    Coordinates between:
    - Domain models (ConversationBuilder, ContextWindowManager)
    - Business services (TokenManager, LLMProviderManager)
    - LLM providers

    Keeps business logic out of routes.
    """

    def __init__(
        self,
        provider_manager: LLMProviderManager,
        token_manager: TokenManager
    ):
        """Initialize chat service.

        Args:
            provider_manager: Manager for LLM providers
            token_manager: Manager for token calculation and limits
        """
        self.provider_manager = provider_manager
        self.token_manager = token_manager
        self.conversation_builder = ConversationBuilder()
        self.context_manager = ContextWindowManager()

    def send_message(
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
        """Send a chat message and get response.

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
        if auto_trim:
            messages, trimmed_count = self._auto_trim_if_needed(
                messages, model
            )

        # Calculate token usage before sending
        token_usage = self.token_manager.calculate_token_usage(messages, model)

        # Generate response
        response = provider.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Update token usage with completion
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
