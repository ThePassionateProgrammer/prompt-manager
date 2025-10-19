"""
Tests for conversation domain model.

These tests require no mocks - pure domain logic testing.
"""
import pytest
from src.prompt_manager.domain.conversation import ConversationBuilder, ContextWindowManager


class TestConversationBuilder:
    """Tests for ConversationBuilder domain model."""
    
    def test_build_messages_with_system_prompt(self):
        """Should build message array with system prompt first."""
        builder = ConversationBuilder()
        
        messages = builder.build_messages(
            user_message="Hello",
            history=[],
            system_prompt="You are helpful"
        )
        
        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == "You are helpful"
        assert messages[1]['role'] == 'user'
        assert messages[1]['content'] == "Hello"
    
    def test_build_messages_without_system_prompt(self):
        """Should build message array without system prompt if not provided."""
        builder = ConversationBuilder()
        
        messages = builder.build_messages(
            user_message="Hello",
            history=[]
        )
        
        assert len(messages) == 1
        assert messages[0]['role'] == 'user'
        assert messages[0]['content'] == "Hello"
    
    def test_build_messages_with_history(self):
        """Should include history between system prompt and user message."""
        builder = ConversationBuilder()
        
        history = [
            {'role': 'user', 'content': 'First message'},
            {'role': 'assistant', 'content': 'First response'}
        ]
        
        messages = builder.build_messages(
            user_message="Second message",
            history=history,
            system_prompt="You are helpful"
        )
        
        assert len(messages) == 4
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'
        assert messages[1]['content'] == 'First message'
        assert messages[2]['role'] == 'assistant'
        assert messages[3]['role'] == 'user'
        assert messages[3]['content'] == 'Second message'
    
    def test_build_messages_preserves_history_order(self):
        """Should maintain order of historical messages."""
        builder = ConversationBuilder()
        
        history = [
            {'role': 'user', 'content': 'Message 1'},
            {'role': 'assistant', 'content': 'Response 1'},
            {'role': 'user', 'content': 'Message 2'},
            {'role': 'assistant', 'content': 'Response 2'}
        ]
        
        messages = builder.build_messages(
            user_message="Message 3",
            history=history
        )
        
        assert messages[0]['content'] == 'Message 1'
        assert messages[1]['content'] == 'Response 1'
        assert messages[2]['content'] == 'Message 2'
        assert messages[3]['content'] == 'Response 2'
        assert messages[4]['content'] == 'Message 3'
    
    def test_validate_message_empty_string(self):
        """Should reject empty messages."""
        builder = ConversationBuilder()
        
        is_valid, error = builder.validate_message("")
        
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_validate_message_whitespace_only(self):
        """Should reject whitespace-only messages."""
        builder = ConversationBuilder()
        
        is_valid, error = builder.validate_message("   ")
        
        assert is_valid is False
        assert "whitespace" in error.lower()
    
    def test_validate_message_valid(self):
        """Should accept valid messages."""
        builder = ConversationBuilder()
        
        is_valid, error = builder.validate_message("Hello world")
        
        assert is_valid is True
        assert error == ""
    
    def test_validate_message_non_string(self):
        """Should reject non-string messages."""
        builder = ConversationBuilder()
        
        is_valid, error = builder.validate_message(123)
        
        assert is_valid is False
        assert "string" in error.lower()


class TestContextWindowManager:
    """Tests for ContextWindowManager domain model."""
    
    def test_should_trim_when_at_threshold(self):
        """Should trim when tokens reach threshold."""
        manager = ContextWindowManager()
        
        should_trim = manager.should_trim(
            current_tokens=900,
            model_limit=1000,
            threshold=0.9
        )
        
        assert should_trim is True
    
    def test_should_not_trim_when_below_threshold(self):
        """Should not trim when tokens below threshold."""
        manager = ContextWindowManager()
        
        should_trim = manager.should_trim(
            current_tokens=800,
            model_limit=1000,
            threshold=0.9
        )
        
        assert should_trim is False
    
    def test_should_trim_with_custom_threshold(self):
        """Should respect custom threshold values."""
        manager = ContextWindowManager()
        
        # At 75% with 0.75 threshold
        should_trim = manager.should_trim(
            current_tokens=750,
            model_limit=1000,
            threshold=0.75
        )
        
        assert should_trim is True
    
    def test_should_not_trim_with_zero_limit(self):
        """Should not trim if model limit is zero."""
        manager = ContextWindowManager()
        
        should_trim = manager.should_trim(
            current_tokens=100,
            model_limit=0,
            threshold=0.9
        )
        
        assert should_trim is False
    
    def test_calculate_keep_count_with_few_messages(self):
        """Should keep all messages if fewer than keep_recent."""
        manager = ContextWindowManager()
        
        keep_count = manager.calculate_keep_count(
            total_messages=3,
            keep_recent=5
        )
        
        assert keep_count == 3
    
    def test_calculate_keep_count_with_many_messages(self):
        """Should keep system prompt + recent N messages."""
        manager = ContextWindowManager()
        
        keep_count = manager.calculate_keep_count(
            total_messages=20,
            keep_recent=5
        )
        
        # System prompt + 5 recent = 6
        assert keep_count == 6
    
    def test_calculate_keep_count_with_one_message(self):
        """Should keep single message (system prompt)."""
        manager = ContextWindowManager()
        
        keep_count = manager.calculate_keep_count(
            total_messages=1,
            keep_recent=5
        )
        
        assert keep_count == 1
    
    def test_calculate_keep_count_with_custom_recent(self):
        """Should respect custom keep_recent values."""
        manager = ContextWindowManager()
        
        keep_count = manager.calculate_keep_count(
            total_messages=20,
            keep_recent=10
        )
        
        # System prompt + 10 recent = 11
        assert keep_count == 11

