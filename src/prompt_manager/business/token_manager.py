"""
Token Manager - Business logic for token estimation and context management.

Handles token counting, context limit tracking, and auto-trimming.
"""

from typing import List, Dict, Any, Tuple


class TokenManager:
    """Manages token estimation and context tracking."""
    
    # Rough estimation: approximately 4 characters per token
    CHARS_PER_TOKEN = 4
    
    # Model context limits (in tokens)
    MODEL_CONTEXT_LIMITS = {
        'gpt-4-turbo-preview': 128000,
        'gpt-4': 8192,
        'gpt-3.5-turbo': 4096,
        'gpt-3.5-turbo-16k': 16384
    }
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count from text.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        return len(text) // self.CHARS_PER_TOKEN
    
    def get_context_limit(self, model: str) -> int:
        """Get context limit for a model.
        
        Args:
            model: Model identifier
            
        Returns:
            Context limit in tokens (default 4096 if unknown)
        """
        return self.MODEL_CONTEXT_LIMITS.get(model, 4096)
    
    def calculate_message_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Calculate total tokens in a message list.
        
        Args:
            messages: List of message dicts with 'content' field
            
        Returns:
            Total estimated token count
        """
        total = 0
        for msg in messages:
            content = msg.get('content', '')
            total += self.estimate_tokens(content)
        return total
    
    def calculate_usage_percentage(self, tokens: int, model: str) -> float:
        """Calculate percentage of context limit used.
        
        Args:
            tokens: Number of tokens used
            model: Model identifier
            
        Returns:
            Percentage (0-100) of context used
        """
        limit = self.get_context_limit(model)
        percentage = (tokens / limit) * 100
        return min(100.0, percentage)
    
    def calculate_token_usage(self, messages: List[Dict[str, str]], model: str) -> Dict[str, Any]:
        """Calculate comprehensive token usage information.
        
        Args:
            messages: List of message dicts
            model: Model identifier
            
        Returns:
            Dict with token usage details:
            - prompt_tokens: Tokens in input
            - completion_tokens: Tokens in response (0 initially)
            - total_tokens: Sum of both
            - context_limit: Model's max context
            - percentage: Usage percentage
            - warning: Optional warning message if high usage
        """
        prompt_tokens = self.calculate_message_tokens(messages)
        context_limit = self.get_context_limit(model)
        percentage = self.calculate_usage_percentage(prompt_tokens, model)
        
        # Generate warning if approaching limit
        warning = None
        if percentage > 80:
            warning = 'Approaching context limit'
        
        return {
            'prompt_tokens': prompt_tokens,
            'completion_tokens': 0,  # Updated after response
            'total_tokens': prompt_tokens,
            'context_limit': context_limit,
            'percentage': round(percentage, 1),
            'warning': warning
        }
    
    def update_with_completion(self, usage: Dict[str, Any], completion_text: str) -> Dict[str, Any]:
        """Update token usage with completion tokens.
        
        Args:
            usage: Token usage dict from calculate_token_usage
            completion_text: Generated response text
            
        Returns:
            Updated usage dict with completion tokens
        """
        completion_tokens = self.estimate_tokens(completion_text)
        usage['completion_tokens'] = completion_tokens
        usage['total_tokens'] = usage['prompt_tokens'] + completion_tokens
        
        return usage
    
    def should_trim(self, tokens: int, model: str, threshold: float = 0.9) -> bool:
        """Check if messages should be trimmed.
        
        Args:
            tokens: Current token count
            model: Model identifier
            threshold: Percentage threshold (0.0-1.0) to trigger trim
            
        Returns:
            True if trimming is recommended
        """
        percentage = self.calculate_usage_percentage(tokens, model)
        return percentage >= (threshold * 100)
    
    def trim_messages(
        self, 
        messages: List[Dict[str, str]], 
        keep_count: int = 5
    ) -> Tuple[List[Dict[str, str]], int]:
        """Trim messages to keep only recent ones.
        
        Preserves system message (first message) if present, and keeps
        the most recent user/assistant exchanges.
        
        Args:
            messages: List of message dicts
            keep_count: Number of recent messages to keep (excluding system)
            
        Returns:
            Tuple of (trimmed_messages, count_removed)
        """
        if len(messages) <= keep_count + 1:  # +1 for potential system message
            return messages, 0
        
        # Check if first message is system prompt
        if messages and messages[0].get('role') == 'system':
            system_msg = [messages[0]]
            remaining = messages[1:]
        else:
            system_msg = []
            remaining = messages
        
        # Keep only recent messages
        if len(remaining) > keep_count:
            trimmed_count = len(remaining) - keep_count
            kept_messages = remaining[-keep_count:]
            return system_msg + kept_messages, trimmed_count
        
        return messages, 0
    
    def get_all_model_limits(self) -> Dict[str, int]:
        """Get all model context limits.
        
        Returns:
            Dict mapping model names to context limits
        """
        return self.MODEL_CONTEXT_LIMITS.copy()

