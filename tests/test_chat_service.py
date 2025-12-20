"""Tests for ChatService."""
import pytest
from unittest.mock import MagicMock, patch
from src.prompt_manager.business.chat_service import ChatService
from src.prompt_manager.domain.conversation import Conversation
from src.prompt_manager.business.llm_provider import LLMProvider


class TestChatService:
    """Test suite for ChatService."""

    @pytest.fixture
    def mock_storage(self):
        """Mock ConversationStorage."""
        storage = MagicMock()
        storage.list_conversations.return_value = []
        return storage

    @pytest.fixture
    def mock_llm(self):
        """Mock LLMProvider."""
        llm = MagicMock(spec=LLMProvider)
        llm.send_message_stream.return_value = iter(['Hello', ' ', 'world', '!'])
        return llm

    @pytest.fixture
    def chat_service(self, mock_storage, mock_llm):
        """ChatService with mocked dependencies."""
        return ChatService(storage=mock_storage, llm_provider=mock_llm)

    def test_create_conversation(self, chat_service, mock_storage):
        """Test creating a new conversation."""
        conv_id = chat_service.create_conversation(title="Test Chat", model="gemma3:4b")

        # Should return a UUID
        assert isinstance(conv_id, str)
        assert len(conv_id) > 0

        # Should save to storage
        mock_storage.save_conversation.assert_called_once()

        # Should be in memory cache
        assert conv_id in chat_service.conversations

    def test_create_conversation_with_defaults(self, chat_service):
        """Test creating conversation with default values."""
        conv_id = chat_service.create_conversation()

        conv = chat_service.conversations[conv_id]
        assert conv.title == "New Conversation"
        assert conv.model == "gemma3:4b"

    def test_get_conversation(self, chat_service):
        """Test retrieving a conversation by ID."""
        # Create first
        conv_id = chat_service.create_conversation(title="Test")

        # Get it back
        conv = chat_service.get_conversation(conv_id)

        assert conv is not None
        assert conv.id == conv_id
        assert conv.title == "Test"

    def test_get_nonexistent_conversation(self, chat_service):
        """Test getting conversation that doesn't exist."""
        conv = chat_service.get_conversation("nonexistent-id")
        assert conv is None

    def test_list_conversations(self, chat_service):
        """Test listing all conversations."""
        # Create multiple conversations
        id1 = chat_service.create_conversation(title="First")
        id2 = chat_service.create_conversation(title="Second")

        conversations = chat_service.list_conversations()

        assert len(conversations) == 2
        titles = [c.title for c in conversations]
        assert "First" in titles
        assert "Second" in titles

    def test_list_conversations_empty(self, chat_service):
        """Test listing when no conversations exist."""
        conversations = chat_service.list_conversations()
        assert conversations == []

    def test_delete_conversation(self, chat_service, mock_storage):
        """Test deleting a conversation."""
        # Create conversation
        conv_id = chat_service.create_conversation(title="To Delete")

        # Delete it
        result = chat_service.delete_conversation(conv_id)

        assert result is True
        assert conv_id not in chat_service.conversations
        mock_storage.delete_conversation.assert_called_with(conv_id)

    def test_delete_nonexistent_conversation(self, chat_service):
        """Test deleting conversation that doesn't exist."""
        result = chat_service.delete_conversation("nonexistent-id")
        assert result is False

    def test_send_message_streaming(self, chat_service, mock_llm, mock_storage):
        """Test sending a message with streaming response."""
        # Create conversation
        conv_id = chat_service.create_conversation(title="Stream Test")

        # Send message and collect chunks
        chunks = list(chat_service.send_message(conv_id, "Hello"))

        # Should yield all chunks
        assert chunks == ['Hello', ' ', 'world', '!']

        # Should add user message and assistant response to conversation
        conv = chat_service.get_conversation(conv_id)
        assert len(conv.messages) == 2
        assert conv.messages[0].role == 'user'
        assert conv.messages[0].content == 'Hello'
        assert conv.messages[1].role == 'assistant'
        assert conv.messages[1].content == 'Hello world!'

        # Should save to storage after streaming completes
        assert mock_storage.save_conversation.call_count >= 2

    def test_send_message_updates_conversation(self, chat_service):
        """Test that sending message updates conversation timestamp."""
        conv_id = chat_service.create_conversation()
        conv = chat_service.get_conversation(conv_id)
        original_updated = conv.updated_at

        # Send message
        list(chat_service.send_message(conv_id, "Test"))

        # Timestamp should be updated
        assert conv.updated_at > original_updated

    def test_send_message_to_nonexistent_conversation(self, chat_service):
        """Test sending message to conversation that doesn't exist."""
        with pytest.raises(KeyError):
            list(chat_service.send_message("nonexistent-id", "Hello"))

    def test_send_message_formats_for_llm(self, chat_service, mock_llm):
        """Test that messages are properly formatted for LLM."""
        conv_id = chat_service.create_conversation()

        # Add system message first
        conv = chat_service.get_conversation(conv_id)
        conv.add_message('system', 'You are Ember.')

        # Send user message
        list(chat_service.send_message(conv_id, "Hello"))

        # Verify LLM was called with properly formatted messages
        mock_llm.send_message_stream.assert_called_once()
        call_kwargs = mock_llm.send_message_stream.call_args[1]
        messages = call_kwargs['messages']

        # Should include system message and user message
        assert len(messages) >= 2
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'

    def test_send_message_with_custom_model(self, chat_service, mock_llm):
        """Test sending message with conversation's model."""
        conv_id = chat_service.create_conversation(model="gemma3:12b")

        list(chat_service.send_message(conv_id, "Test"))

        # Should pass model to LLM
        mock_llm.send_message_stream.assert_called_once()
        call_kwargs = mock_llm.send_message_stream.call_args[1]
        assert call_kwargs['model'] == "gemma3:12b"

    def test_send_message_handles_llm_error(self, chat_service, mock_llm):
        """Test handling LLM errors during streaming."""
        mock_llm.send_message_stream.side_effect = RuntimeError("LLM error")

        conv_id = chat_service.create_conversation()

        with pytest.raises(RuntimeError, match="LLM error"):
            list(chat_service.send_message(conv_id, "Hello"))

    def test_load_conversations_from_storage(self, mock_storage, mock_llm):
        """Test loading existing conversations from storage on init."""
        # Create mock conversations in storage
        conv1 = Conversation(title="Loaded 1")
        conv2 = Conversation(title="Loaded 2")
        mock_storage.list_conversations.return_value = [conv1, conv2]

        # Create service (should load from storage)
        service = ChatService(storage=mock_storage, llm_provider=mock_llm)

        # Should have loaded conversations in cache
        assert len(service.conversations) == 2
        assert conv1.id in service.conversations
        assert conv2.id in service.conversations

    def test_create_conversation_auto_saves(self, chat_service, mock_storage):
        """Test that creating conversation saves to storage."""
        chat_service.create_conversation(title="Auto Save Test")

        # Should call save_conversation
        assert mock_storage.save_conversation.called

    def test_send_message_accumulates_chunks(self, chat_service, mock_llm):
        """Test that streaming chunks are accumulated correctly."""
        mock_llm.send_message_stream.return_value = iter(['Hello', ' ', 'world', '!'])

        conv_id = chat_service.create_conversation()
        list(chat_service.send_message(conv_id, "Test"))

        # Assistant message should have full accumulated content
        conv = chat_service.get_conversation(conv_id)
        assistant_msg = conv.messages[1]
        assert assistant_msg.content == 'Hello world!'

    def test_send_message_with_empty_response(self, chat_service, mock_llm):
        """Test handling empty LLM response."""
        mock_llm.send_message_stream.return_value = iter([])

        conv_id = chat_service.create_conversation()
        chunks = list(chat_service.send_message(conv_id, "Test"))

        assert chunks == []

        # Should still add user message but assistant message is empty
        conv = chat_service.get_conversation(conv_id)
        assert len(conv.messages) == 2
        assert conv.messages[1].content == ''

    def test_multiple_messages_in_conversation(self, chat_service, mock_llm):
        """Test multiple back-and-forth messages."""
        conv_id = chat_service.create_conversation()

        # First exchange
        mock_llm.send_message_stream.return_value = iter(['Response 1'])
        list(chat_service.send_message(conv_id, "Question 1"))

        # Second exchange
        mock_llm.send_message_stream.return_value = iter(['Response 2'])
        list(chat_service.send_message(conv_id, "Question 2"))

        # Should have 4 messages total
        conv = chat_service.get_conversation(conv_id)
        assert len(conv.messages) == 4
        assert conv.messages[0].content == "Question 1"
        assert conv.messages[1].content == "Response 1"
        assert conv.messages[2].content == "Question 2"
        assert conv.messages[3].content == "Response 2"

    def test_conversation_title_auto_generated(self, chat_service, mock_llm):
        """Test that conversation title is auto-generated from first message."""
        mock_llm.send_message_stream.return_value = iter(['Response'])

        conv_id = chat_service.create_conversation()  # Default title: "New Conversation"

        # Send first message
        list(chat_service.send_message(conv_id, "What is test-first development?"))

        # Title should be auto-generated from user message
        conv = chat_service.get_conversation(conv_id)
        assert conv.title == "What is test-first development?"

    def test_list_conversations_sorted_by_updated(self, chat_service):
        """Test that conversations are sorted by updated_at descending."""
        # Create conversations
        id1 = chat_service.create_conversation(title="First")
        id2 = chat_service.create_conversation(title="Second")

        # Update first conversation (makes it most recent)
        list(chat_service.send_message(id1, "Update"))

        conversations = chat_service.list_conversations()

        # First should now be first in list (most recently updated)
        assert conversations[0].id == id1
        assert conversations[1].id == id2
