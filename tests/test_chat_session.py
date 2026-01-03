"""
Tests for ChatSession domain model.

ChatSession represents a user's current chat session with business rules
for managing messages, settings, and session state.
"""
import pytest
from src.prompt_manager.domain.chat_session import ChatSession


class TestChatSessionCreation:
    """Test creating new chat sessions."""

    def test_create_empty_session(self):
        """A new session starts with no messages."""
        session = ChatSession()

        assert session.messages == []
        assert session.provider is None
        assert session.model is None

    def test_create_session_with_provider(self):
        """Can create session with specific provider."""
        session = ChatSession(provider='openai')

        assert session.provider == 'openai'

    def test_create_session_with_model(self):
        """Can create session with specific model."""
        session = ChatSession(provider='openai', model='gpt-4')

        assert session.provider == 'openai'
        assert session.model == 'gpt-4'


class TestAddingMessages:
    """Test adding messages to session."""

    def test_add_user_message(self):
        """Can add a user message to the session."""
        session = ChatSession()

        session.add_message(role='user', content='Hello')

        assert len(session.messages) == 1
        assert session.messages[0]['role'] == 'user'
        assert session.messages[0]['content'] == 'Hello'

    def test_add_assistant_message(self):
        """Can add an assistant message to the session."""
        session = ChatSession()

        session.add_message(role='assistant', content='Hi there!')

        assert len(session.messages) == 1
        assert session.messages[0]['role'] == 'assistant'
        assert session.messages[0]['content'] == 'Hi there!'

    def test_add_multiple_messages(self):
        """Messages are added in order."""
        session = ChatSession()

        session.add_message(role='user', content='Hello')
        session.add_message(role='assistant', content='Hi!')
        session.add_message(role='user', content='How are you?')

        assert len(session.messages) == 3
        assert session.messages[0]['content'] == 'Hello'
        assert session.messages[1]['content'] == 'Hi!'
        assert session.messages[2]['content'] == 'How are you?'


class TestSessionValidation:
    """Test session validation rules."""

    def test_cannot_add_empty_message(self):
        """Empty messages are rejected."""
        session = ChatSession()

        with pytest.raises(ValueError, match="Message cannot be empty"):
            session.add_message(role='user', content='')

    def test_cannot_add_whitespace_message(self):
        """Whitespace-only messages are rejected."""
        session = ChatSession()

        with pytest.raises(ValueError, match="Message cannot be empty"):
            session.add_message(role='user', content='   ')

    def test_cannot_add_invalid_role(self):
        """Only valid roles are allowed."""
        session = ChatSession()

        with pytest.raises(ValueError, match="Invalid role"):
            session.add_message(role='invalid', content='Hello')


class TestSessionSettings:
    """Test session settings management."""

    def test_update_provider(self):
        """Can update session provider."""
        session = ChatSession(provider='openai')

        session.update_settings(provider='ollama')

        assert session.provider == 'ollama'

    def test_update_model(self):
        """Can update session model."""
        session = ChatSession(provider='openai', model='gpt-3.5-turbo')

        session.update_settings(model='gpt-4')

        assert session.model == 'gpt-4'

    def test_update_temperature(self):
        """Can update temperature setting."""
        session = ChatSession()

        session.update_settings(temperature=0.8)

        assert session.temperature == 0.8

    def test_temperature_defaults_to_0_7(self):
        """Temperature defaults to 0.7."""
        session = ChatSession()

        assert session.temperature == 0.7


class TestClearSession:
    """Test clearing session."""

    def test_clear_removes_messages(self):
        """Clearing session removes all messages."""
        session = ChatSession()
        session.add_message(role='user', content='Hello')
        session.add_message(role='assistant', content='Hi!')

        session.clear()

        assert session.messages == []

    def test_clear_preserves_settings(self):
        """Clearing session preserves provider/model settings."""
        session = ChatSession(provider='openai', model='gpt-4')
        session.update_settings(temperature=0.9)
        session.add_message(role='user', content='Hello')

        session.clear()

        assert session.provider == 'openai'
        assert session.model == 'gpt-4'
        assert session.temperature == 0.9
        assert session.messages == []


class TestSessionState:
    """Test session state queries."""

    def test_is_empty_when_no_messages(self):
        """Session is empty with no messages."""
        session = ChatSession()

        assert session.is_empty() is True

    def test_is_not_empty_with_messages(self):
        """Session is not empty with messages."""
        session = ChatSession()
        session.add_message(role='user', content='Hello')

        assert session.is_empty() is False

    def test_message_count(self):
        """Can get message count."""
        session = ChatSession()
        session.add_message(role='user', content='Hello')
        session.add_message(role='assistant', content='Hi!')

        assert session.message_count() == 2


class TestSystemPrompt:
    """Test system prompt management."""

    def test_set_system_prompt(self):
        """Can set system prompt."""
        session = ChatSession()

        session.set_system_prompt("You are a helpful assistant.")

        assert session.system_prompt == "You are a helpful assistant."

    def test_system_prompt_defaults_to_none(self):
        """System prompt defaults to None."""
        session = ChatSession()

        assert session.system_prompt is None

    def test_get_messages_with_system_prompt(self):
        """System prompt is included in messages when set."""
        session = ChatSession()
        session.set_system_prompt("You are helpful.")
        session.add_message(role='user', content='Hello')

        messages = session.get_messages_for_llm()

        assert len(messages) == 2
        assert messages[0]['role'] == 'system'
        assert messages[0]['content'] == "You are helpful."
        assert messages[1]['role'] == 'user'
        assert messages[1]['content'] == 'Hello'

    def test_get_messages_without_system_prompt(self):
        """System prompt is not included when not set."""
        session = ChatSession()
        session.add_message(role='user', content='Hello')

        messages = session.get_messages_for_llm()

        assert len(messages) == 1
        assert messages[0]['role'] == 'user'
