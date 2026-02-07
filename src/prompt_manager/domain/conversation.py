"""
Conversation domain model.

Pure business logic for conversation/message management with zero dependencies.
"""


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
    
    def validate_message(self, message: str) -> tuple[bool, str]:
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

