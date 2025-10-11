"""
Tests for TokenManager - Token estimation and context management.
"""

import pytest
from src.prompt_manager.business.token_manager import TokenManager


@pytest.fixture
def token_manager():
    """Fixture providing a TokenManager instance."""
    return TokenManager()


class TestTokenEstimation:
    """Tests for token estimation."""
    
    def test_estimate_tokens_empty_string(self, token_manager):
        """Test estimating tokens for empty string."""
        assert token_manager.estimate_tokens("") == 0
    
    def test_estimate_tokens_short_text(self, token_manager):
        """Test estimating tokens for short text."""
        # "Hello" = 5 chars / 4 = 1 token
        assert token_manager.estimate_tokens("Hello") == 1
    
    def test_estimate_tokens_longer_text(self, token_manager):
        """Test estimating tokens for longer text."""
        # "This is a test message" = 22 chars / 4 = 5 tokens
        text = "This is a test message"
        assert token_manager.estimate_tokens(text) == 5
    
    def test_estimate_tokens_very_long_text(self, token_manager):
        """Test estimating tokens for very long text."""
        text = "A" * 400  # 400 chars = 100 tokens
        assert token_manager.estimate_tokens(text) == 100


class TestContextLimits:
    """Tests for model context limits."""
    
    def test_get_context_limit_gpt4_turbo(self, token_manager):
        """Test getting context limit for GPT-4 Turbo."""
        assert token_manager.get_context_limit('gpt-4-turbo-preview') == 128000
    
    def test_get_context_limit_gpt4(self, token_manager):
        """Test getting context limit for GPT-4."""
        assert token_manager.get_context_limit('gpt-4') == 8192
    
    def test_get_context_limit_gpt35(self, token_manager):
        """Test getting context limit for GPT-3.5."""
        assert token_manager.get_context_limit('gpt-3.5-turbo') == 4096
    
    def test_get_context_limit_gpt35_16k(self, token_manager):
        """Test getting context limit for GPT-3.5 16K."""
        assert token_manager.get_context_limit('gpt-3.5-turbo-16k') == 16384
    
    def test_get_context_limit_unknown_model(self, token_manager):
        """Test getting context limit for unknown model returns default."""
        assert token_manager.get_context_limit('unknown-model') == 4096
    
    def test_get_all_model_limits(self, token_manager):
        """Test getting all model limits."""
        limits = token_manager.get_all_model_limits()
        assert len(limits) == 4
        assert 'gpt-4-turbo-preview' in limits
        assert limits['gpt-4'] == 8192


class TestMessageTokenCalculation:
    """Tests for calculating tokens in messages."""
    
    def test_calculate_message_tokens_empty_list(self, token_manager):
        """Test calculating tokens for empty message list."""
        assert token_manager.calculate_message_tokens([]) == 0
    
    def test_calculate_message_tokens_single_message(self, token_manager):
        """Test calculating tokens for single message."""
        messages = [{'role': 'user', 'content': 'Hello world'}]
        # "Hello world" = 11 chars / 4 = 2 tokens
        assert token_manager.calculate_message_tokens(messages) == 2
    
    def test_calculate_message_tokens_multiple_messages(self, token_manager):
        """Test calculating tokens for multiple messages."""
        messages = [
            {'role': 'user', 'content': 'Hello'},  # 5 chars = 1 token
            {'role': 'assistant', 'content': 'Hi there'},  # 8 chars = 2 tokens
            {'role': 'user', 'content': 'How are you?'}  # 12 chars = 3 tokens
        ]
        assert token_manager.calculate_message_tokens(messages) == 6
    
    def test_calculate_message_tokens_missing_content(self, token_manager):
        """Test calculating tokens when messages have no content."""
        messages = [
            {'role': 'user'},  # No content
            {'role': 'assistant', 'content': 'Test'}
        ]
        # Only 'Test' = 4 chars = 1 token
        assert token_manager.calculate_message_tokens(messages) == 1


class TestUsagePercentage:
    """Tests for calculating usage percentage."""
    
    def test_calculate_usage_percentage_zero(self, token_manager):
        """Test calculating 0% usage."""
        percentage = token_manager.calculate_usage_percentage(0, 'gpt-3.5-turbo')
        assert percentage == 0.0
    
    def test_calculate_usage_percentage_half(self, token_manager):
        """Test calculating 50% usage."""
        # GPT-3.5 has 4096 token limit, 2048 = 50%
        percentage = token_manager.calculate_usage_percentage(2048, 'gpt-3.5-turbo')
        assert percentage == 50.0
    
    def test_calculate_usage_percentage_high(self, token_manager):
        """Test calculating high usage."""
        # 3686 / 4096 = ~90%
        percentage = token_manager.calculate_usage_percentage(3686, 'gpt-3.5-turbo')
        assert 89 < percentage < 91
    
    def test_calculate_usage_percentage_over_limit(self, token_manager):
        """Test calculating over 100% usage caps at 100."""
        percentage = token_manager.calculate_usage_percentage(5000, 'gpt-3.5-turbo')
        assert percentage == 100.0


class TestTokenUsageCalculation:
    """Tests for comprehensive token usage calculation."""
    
    def test_calculate_token_usage_empty(self, token_manager):
        """Test calculating usage for empty messages."""
        usage = token_manager.calculate_token_usage([], 'gpt-3.5-turbo')
        
        assert usage['prompt_tokens'] == 0
        assert usage['completion_tokens'] == 0
        assert usage['total_tokens'] == 0
        assert usage['context_limit'] == 4096
        assert usage['percentage'] == 0.0
        assert usage['warning'] is None
    
    def test_calculate_token_usage_normal(self, token_manager):
        """Test calculating usage for normal conversation."""
        messages = [
            {'role': 'user', 'content': 'A' * 400},  # 100 tokens
            {'role': 'assistant', 'content': 'B' * 400}  # 100 tokens
        ]
        usage = token_manager.calculate_token_usage(messages, 'gpt-3.5-turbo')
        
        assert usage['prompt_tokens'] == 200
        assert usage['total_tokens'] == 200
        assert usage['context_limit'] == 4096
        assert 4 < usage['percentage'] < 5
        assert usage['warning'] is None
    
    def test_calculate_token_usage_high_triggers_warning(self, token_manager):
        """Test that high usage triggers warning."""
        # Create messages using 85% of context
        messages = [
            {'role': 'user', 'content': 'A' * 13900}  # ~3475 tokens (85% of 4096)
        ]
        usage = token_manager.calculate_token_usage(messages, 'gpt-3.5-turbo')
        
        assert usage['percentage'] > 80
        assert usage['warning'] == 'Approaching context limit'
    
    def test_update_with_completion(self, token_manager):
        """Test updating usage with completion tokens."""
        messages = [{'role': 'user', 'content': 'Test'}]
        usage = token_manager.calculate_token_usage(messages, 'gpt-3.5-turbo')
        
        # Simulate completion
        completion_text = 'A' * 200  # 50 tokens
        updated = token_manager.update_with_completion(usage, completion_text)
        
        assert updated['completion_tokens'] == 50
        assert updated['total_tokens'] == updated['prompt_tokens'] + 50


class TestAutoTrimming:
    """Tests for auto-trimming functionality."""
    
    def test_should_trim_below_threshold(self, token_manager):
        """Test should_trim returns False below threshold."""
        # 50% usage, threshold 90%
        assert not token_manager.should_trim(2048, 'gpt-3.5-turbo', 0.9)
    
    def test_should_trim_at_threshold(self, token_manager):
        """Test should_trim returns True at threshold."""
        # Exactly 90% usage: 4096 * 0.9 = 3686.4
        assert token_manager.should_trim(3687, 'gpt-3.5-turbo', 0.9)
    
    def test_should_trim_above_threshold(self, token_manager):
        """Test should_trim returns True above threshold."""
        # 95% usage
        assert token_manager.should_trim(3891, 'gpt-3.5-turbo', 0.9)
    
    def test_trim_messages_no_trimming_needed(self, token_manager):
        """Test trimming when no trimming is needed."""
        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi'}
        ]
        trimmed, count = token_manager.trim_messages(messages, keep_count=5)
        
        assert len(trimmed) == 2
        assert count == 0
    
    def test_trim_messages_with_system_prompt(self, token_manager):
        """Test trimming preserves system prompt."""
        messages = [
            {'role': 'system', 'content': 'You are helpful'},
            {'role': 'user', 'content': 'Msg 1'},
            {'role': 'assistant', 'content': 'Reply 1'},
            {'role': 'user', 'content': 'Msg 2'},
            {'role': 'assistant', 'content': 'Reply 2'},
            {'role': 'user', 'content': 'Msg 3'},
            {'role': 'assistant', 'content': 'Reply 3'},
        ]
        trimmed, count = token_manager.trim_messages(messages, keep_count=3)
        
        # Should keep system + last 3 messages (Msg 3, Reply 3, and Msg 2 going back)
        # Actually: system + Reply 2, Msg 3, Reply 3 (last 3 messages)
        assert len(trimmed) == 4
        assert trimmed[0]['role'] == 'system'
        assert trimmed[1]['content'] == 'Reply 2'  # Last 3 from the 6 non-system messages
        assert count == 3  # Removed Msg1, Reply1, Msg2
    
    def test_trim_messages_without_system_prompt(self, token_manager):
        """Test trimming without system prompt."""
        messages = [
            {'role': 'user', 'content': 'Msg 1'},
            {'role': 'assistant', 'content': 'Reply 1'},
            {'role': 'user', 'content': 'Msg 2'},
            {'role': 'assistant', 'content': 'Reply 2'},
            {'role': 'user', 'content': 'Msg 3'},
        ]
        trimmed, count = token_manager.trim_messages(messages, keep_count=3)
        
        # Should keep last 3 messages
        assert len(trimmed) == 3
        assert trimmed[0]['content'] == 'Msg 2'
        assert count == 2
    
    def test_trim_messages_exact_count(self, token_manager):
        """Test trimming when message count equals keep_count."""
        messages = [
            {'role': 'user', 'content': 'Msg 1'},
            {'role': 'assistant', 'content': 'Reply 1'},
            {'role': 'user', 'content': 'Msg 2'},
        ]
        trimmed, count = token_manager.trim_messages(messages, keep_count=3)
        
        assert len(trimmed) == 3
        assert count == 0

