"""
Tests for ChatMessage domain entity.

Following the pattern from test_prompt.py - testing pure domain logic
with no external dependencies.
"""
import pytest
from datetime import datetime
import time
from src.prompt_manager.domain.chat_message import ChatMessage


class TestChatMessage:
    """Test suite for ChatMessage entity."""

    def test_create_user_message(self):
        """Test creating a user message."""
        message = ChatMessage(role='user', content='Hello, Ember!')

        assert message.role == 'user'
        assert message.content == 'Hello, Ember!'
        assert message.timestamp is not None
        assert isinstance(message.timestamp, datetime)
        assert message.id is None  # ID set by Conversation aggregate

    def test_create_assistant_message(self):
        """Test creating an assistant message."""
        message = ChatMessage(role='assistant', content='Hello! How can I help?')

        assert message.role == 'assistant'
        assert message.content == 'Hello! How can I help?'

    def test_create_system_message(self):
        """Test creating a system message."""
        message = ChatMessage(
            role='system',
            content='You are a helpful AI assistant named Ember.'
        )

        assert message.role == 'system'
        assert message.content == 'You are a helpful AI assistant named Ember.'

    def test_message_with_custom_timestamp(self):
        """Test creating a message with a specific timestamp."""
        custom_time = datetime(2025, 1, 1, 12, 0, 0)
        message = ChatMessage(role='user', content='Test', timestamp=custom_time)

        assert message.timestamp == custom_time

    def test_message_auto_timestamp(self):
        """Test that messages get automatic timestamps."""
        before = datetime.now()
        time.sleep(0.01)  # Small delay to ensure different timestamps
        message = ChatMessage(role='user', content='Test')
        time.sleep(0.01)
        after = datetime.now()

        assert before <= message.timestamp <= after

    def test_to_dict_serialization(self):
        """Test serializing message to dictionary."""
        message = ChatMessage(role='user', content='Hello')
        message.id = 0  # Set by Conversation

        data = message.to_dict()

        assert data['id'] == 0
        assert data['role'] == 'user'
        assert data['content'] == 'Hello'
        assert 'timestamp' in data
        assert isinstance(data['timestamp'], str)  # ISO format string

    def test_from_dict_deserialization(self):
        """Test creating message from dictionary."""
        data = {
            'id': 1,
            'role': 'assistant',
            'content': 'Hi there!',
            'timestamp': '2025-01-01T12:00:00.000000'
        }

        message = ChatMessage.from_dict(data)

        assert message.id == 1
        assert message.role == 'assistant'
        assert message.content == 'Hi there!'
        assert isinstance(message.timestamp, datetime)

    def test_round_trip_serialization(self):
        """Test that to_dict and from_dict are inverses."""
        original = ChatMessage(role='user', content='Test message')
        original.id = 5

        # Serialize and deserialize
        data = original.to_dict()
        restored = ChatMessage.from_dict(data)

        assert restored.id == original.id
        assert restored.role == original.role
        assert restored.content == original.content
        # Timestamps should be equal (accounting for microsecond precision)
        assert abs((restored.timestamp - original.timestamp).total_seconds()) < 0.001

    def test_empty_content_allowed(self):
        """Test that empty content is allowed (for edge cases)."""
        message = ChatMessage(role='user', content='')

        assert message.content == ''
        assert message.role == 'user'

    def test_role_values_are_strings(self):
        """Test that role values are stored as strings."""
        for role in ['user', 'assistant', 'system']:
            message = ChatMessage(role=role, content='Test')
            assert isinstance(message.role, str)
            assert message.role == role
