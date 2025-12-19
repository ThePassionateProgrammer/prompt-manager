"""
Tests for Conversation domain aggregate.

The Conversation is an aggregate root that manages ChatMessage entities
and enforces business rules like auto-title generation and message ordering.
"""
import pytest
from datetime import datetime
import time
from src.prompt_manager.domain.conversation import Conversation
from src.prompt_manager.domain.chat_message import ChatMessage


class TestConversation:
    """Test suite for Conversation aggregate root."""

    def test_create_new_conversation(self):
        """Test creating a new conversation with defaults."""
        conv = Conversation()

        assert conv.id is not None
        assert conv.title == "New Conversation"
        assert conv.model == "gemma3:4b"
        assert len(conv.messages) == 0
        assert conv.created_at is not None
        assert conv.updated_at == conv.created_at

    def test_create_conversation_with_custom_values(self):
        """Test creating a conversation with custom title and model."""
        conv = Conversation(title="Chat with Ember", model="gemma3:12b")

        assert conv.title == "Chat with Ember"
        assert conv.model == "gemma3:12b"

    def test_conversation_has_unique_id(self):
        """Test that each conversation gets a unique ID."""
        conv1 = Conversation()
        conv2 = Conversation()

        assert conv1.id != conv2.id

    def test_add_message_to_conversation(self):
        """Test adding a message to conversation."""
        conv = Conversation()

        message = conv.add_message(role='user', content='Hello, Ember!')

        assert len(conv.messages) == 1
        assert message.role == 'user'
        assert message.content == 'Hello, Ember!'
        assert message.id == 0  # First message gets ID 0

    def test_add_multiple_messages(self):
        """Test adding multiple messages maintains order."""
        conv = Conversation()

        msg1 = conv.add_message('user', 'Hi')
        msg2 = conv.add_message('assistant', 'Hello!')
        msg3 = conv.add_message('user', 'How are you?')

        assert len(conv.messages) == 3
        assert conv.messages[0].id == 0
        assert conv.messages[1].id == 1
        assert conv.messages[2].id == 2
        assert conv.messages[0].content == 'Hi'
        assert conv.messages[1].content == 'Hello!'
        assert conv.messages[2].content == 'How are you?'

    def test_add_message_updates_timestamp(self):
        """Test that adding a message updates the conversation timestamp."""
        conv = Conversation()
        original_time = conv.updated_at

        time.sleep(0.01)  # Small delay
        conv.add_message('user', 'Test')

        assert conv.updated_at > original_time

    def test_auto_generate_title_from_first_message(self):
        """Test that title is auto-generated from first user message."""
        conv = Conversation()  # Title starts as "New Conversation"

        conv.add_message('user', 'Help me understand quantum physics')

        assert conv.title == 'Help me understand quantum physics'

    def test_auto_generate_title_truncates_long_messages(self):
        """Test that auto-generated title is truncated to 50 chars."""
        conv = Conversation()
        long_message = 'This is a very long message that should be truncated because it exceeds fifty characters'

        conv.add_message('user', long_message)

        assert len(conv.title) == 53  # 50 chars + '...'
        assert conv.title.endswith('...')
        assert conv.title.startswith('This is a very long message')

    def test_auto_title_only_from_first_user_message(self):
        """Test that only the first user message generates the title."""
        conv = Conversation()

        conv.add_message('user', 'First message')
        conv.add_message('assistant', 'Response')
        conv.add_message('user', 'Second message')

        assert conv.title == 'First message'

    def test_custom_title_not_overridden(self):
        """Test that custom titles are not overridden by messages."""
        conv = Conversation(title="My Custom Title")

        conv.add_message('user', 'This should not change the title')

        assert conv.title == "My Custom Title"

    def test_get_messages_for_llm(self):
        """Test getting messages in Ollama format."""
        conv = Conversation()
        conv.add_message('user', 'Hi')
        conv.add_message('assistant', 'Hello!')
        conv.add_message('user', 'How are you?')

        llm_messages = conv.get_messages_for_llm()

        assert len(llm_messages) == 3
        assert llm_messages[0] == {'role': 'user', 'content': 'Hi'}
        assert llm_messages[1] == {'role': 'assistant', 'content': 'Hello!'}
        assert llm_messages[2] == {'role': 'user', 'content': 'How are you?'}

    def test_to_dict_serialization(self):
        """Test serializing conversation to dictionary."""
        conv = Conversation(title="Test Chat", model="gemma3:4b")
        conv.add_message('user', 'Hello')
        conv.add_message('assistant', 'Hi there!')

        data = conv.to_dict()

        assert data['id'] == conv.id
        assert data['title'] == "Test Chat"
        assert data['model'] == "gemma3:4b"
        assert len(data['messages']) == 2
        assert 'created_at' in data
        assert 'updated_at' in data
        assert isinstance(data['created_at'], str)  # ISO format
        assert isinstance(data['updated_at'], str)

    def test_from_dict_deserialization(self):
        """Test creating conversation from dictionary."""
        data = {
            'id': 'test-id-123',
            'title': 'Restored Chat',
            'model': 'gemma3:12b',
            'messages': [
                {
                    'id': 0,
                    'role': 'user',
                    'content': 'Hello',
                    'timestamp': '2025-01-01T12:00:00.000000'
                },
                {
                    'id': 1,
                    'role': 'assistant',
                    'content': 'Hi!',
                    'timestamp': '2025-01-01T12:00:01.000000'
                }
            ],
            'created_at': '2025-01-01T10:00:00.000000',
            'updated_at': '2025-01-01T12:00:01.000000'
        }

        conv = Conversation.from_dict(data)

        assert conv.id == 'test-id-123'
        assert conv.title == 'Restored Chat'
        assert conv.model == 'gemma3:12b'
        assert len(conv.messages) == 2
        assert conv.messages[0].content == 'Hello'
        assert conv.messages[1].content == 'Hi!'
        assert isinstance(conv.created_at, datetime)
        assert isinstance(conv.updated_at, datetime)

    def test_round_trip_serialization(self):
        """Test that to_dict and from_dict are inverses."""
        original = Conversation(title="Test", model="gemma3:4b")
        original.add_message('user', 'Test message')
        original.add_message('assistant', 'Response')

        # Serialize and deserialize
        data = original.to_dict()
        restored = Conversation.from_dict(data)

        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.model == original.model
        assert len(restored.messages) == len(original.messages)
        assert restored.messages[0].content == original.messages[0].content
        assert restored.messages[1].content == original.messages[1].content

    def test_empty_conversation_serialization(self):
        """Test serializing a conversation with no messages."""
        conv = Conversation()
        data = conv.to_dict()

        assert data['title'] == "New Conversation"
        assert data['messages'] == []

    def test_system_message_doesnt_affect_title(self):
        """Test that system messages don't trigger auto-title."""
        conv = Conversation()

        conv.add_message('system', 'You are a helpful assistant')
        assert conv.title == "New Conversation"

        conv.add_message('user', 'Hello')
        assert conv.title == "Hello"
