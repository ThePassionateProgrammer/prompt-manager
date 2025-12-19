"""Tests for ConversationStorage."""
import pytest
import json
import os
from datetime import datetime
from src.prompt_manager.business.conversation_storage import ConversationStorage
from src.prompt_manager.domain.conversation import Conversation


class TestConversationStorage:
    """Test suite for ConversationStorage."""

    def test_save_conversation(self, tmp_path):
        """Test saving a conversation to storage."""
        storage_file = tmp_path / "conversations.json"
        storage = ConversationStorage(str(storage_file))

        conv = Conversation(title="Test Chat", model="gemma3:4b")
        conv.add_message('user', 'Hello')
        conv.add_message('assistant', 'Hi there!')

        storage.save_conversation(conv)

        # Verify file was created
        assert storage_file.exists()

        # Verify content is valid JSON
        with open(storage_file, 'r') as f:
            data = json.load(f)

        assert conv.id in data
        assert data[conv.id]['title'] == "Test Chat"
        assert data[conv.id]['model'] == "gemma3:4b"
        assert len(data[conv.id]['messages']) == 2

    def test_load_conversation(self, tmp_path):
        """Test loading a conversation from storage."""
        storage_file = tmp_path / "conversations.json"
        storage = ConversationStorage(str(storage_file))

        # Save first
        conv = Conversation(title="Load Test", model="gemma3:4b")
        conv.add_message('user', 'Question')
        conv.add_message('assistant', 'Answer')
        storage.save_conversation(conv)

        # Load it back
        loaded = storage.load_conversation(conv.id)

        assert loaded.id == conv.id
        assert loaded.title == "Load Test"
        assert loaded.model == "gemma3:4b"
        assert len(loaded.messages) == 2
        assert loaded.messages[0].content == "Question"
        assert loaded.messages[1].content == "Answer"

    def test_load_nonexistent_conversation(self, tmp_path):
        """Test loading a conversation that doesn't exist."""
        storage_file = tmp_path / "conversations.json"
        storage = ConversationStorage(str(storage_file))

        with pytest.raises(KeyError):
            storage.load_conversation("nonexistent-id")

    def test_list_conversations(self, tmp_path):
        """Test listing all conversations."""
        storage_file = tmp_path / "conversations.json"
        storage = ConversationStorage(str(storage_file))

        # Create multiple conversations
        conv1 = Conversation(title="First Chat")
        conv1.add_message('user', 'Hello')
        storage.save_conversation(conv1)

        conv2 = Conversation(title="Second Chat")
        conv2.add_message('user', 'Hi')
        storage.save_conversation(conv2)

        # List them
        conversations = storage.list_conversations()

        assert len(conversations) == 2
        titles = [c.title for c in conversations]
        assert "First Chat" in titles
        assert "Second Chat" in titles

    def test_list_conversations_sorted_by_updated_at(self, tmp_path):
        """Test that conversations are sorted by updated_at descending."""
        storage_file = tmp_path / "conversations.json"
        storage = ConversationStorage(str(storage_file))

        # Create conversations with different timestamps
        conv1 = Conversation(title="Older")
        conv1.created_at = datetime(2025, 1, 1, 10, 0, 0)
        conv1.updated_at = datetime(2025, 1, 1, 10, 0, 0)
        storage.save_conversation(conv1)

        conv2 = Conversation(title="Newer")
        conv2.created_at = datetime(2025, 1, 2, 10, 0, 0)
        conv2.updated_at = datetime(2025, 1, 2, 10, 0, 0)
        storage.save_conversation(conv2)

        conversations = storage.list_conversations()

        # Newer should be first
        assert conversations[0].title == "Newer"
        assert conversations[1].title == "Older"

    def test_list_empty_storage(self, tmp_path):
        """Test listing when no conversations exist."""
        storage_file = tmp_path / "conversations.json"
        storage = ConversationStorage(str(storage_file))

        conversations = storage.list_conversations()
        assert conversations == []

    def test_delete_conversation(self, tmp_path):
        """Test deleting a conversation."""
        storage_file = tmp_path / "conversations.json"
        storage = ConversationStorage(str(storage_file))

        # Save conversation
        conv = Conversation(title="To Delete")
        conv.add_message('user', 'Hello')
        storage.save_conversation(conv)

        # Verify it exists
        assert len(storage.list_conversations()) == 1

        # Delete it
        storage.delete_conversation(conv.id)

        # Verify it's gone
        assert len(storage.list_conversations()) == 0

        # Verify loading raises error
        with pytest.raises(KeyError):
            storage.load_conversation(conv.id)

    def test_delete_nonexistent_conversation(self, tmp_path):
        """Test deleting a conversation that doesn't exist."""
        storage_file = tmp_path / "conversations.json"
        storage = ConversationStorage(str(storage_file))

        # Should not raise error, just silently succeed
        storage.delete_conversation("nonexistent-id")

    def test_update_existing_conversation(self, tmp_path):
        """Test updating an existing conversation."""
        storage_file = tmp_path / "conversations.json"
        storage = ConversationStorage(str(storage_file))

        # Save initial conversation
        conv = Conversation(title="Chat")
        conv.add_message('user', 'Hello')
        storage.save_conversation(conv)

        # Add more messages and save again
        conv.add_message('assistant', 'Hi!')
        conv.add_message('user', 'How are you?')
        storage.save_conversation(conv)

        # Load and verify
        loaded = storage.load_conversation(conv.id)
        assert len(loaded.messages) == 3
        assert loaded.messages[2].content == "How are you?"

    def test_multiple_conversations_persist(self, tmp_path):
        """Test that multiple conversations can coexist in storage."""
        storage_file = tmp_path / "conversations.json"
        storage = ConversationStorage(str(storage_file))

        conversations = []
        for i in range(5):
            conv = Conversation(title=f"Chat {i}")
            conv.add_message('user', f'Message {i}')
            storage.save_conversation(conv)
            conversations.append(conv)

        # Verify all exist
        all_convs = storage.list_conversations()
        assert len(all_convs) == 5

        # Verify each can be loaded
        for conv in conversations:
            loaded = storage.load_conversation(conv.id)
            assert loaded.title == conv.title

    def test_storage_creates_file_if_not_exists(self, tmp_path):
        """Test that storage file is created if it doesn't exist."""
        storage_file = tmp_path / "conversations.json"
        assert not storage_file.exists()

        storage = ConversationStorage(str(storage_file))
        conv = Conversation(title="First")
        storage.save_conversation(conv)

        assert storage_file.exists()

    def test_preserves_conversation_metadata(self, tmp_path):
        """Test that all conversation metadata is preserved."""
        storage_file = tmp_path / "conversations.json"
        storage = ConversationStorage(str(storage_file))

        # Create conversation with specific metadata
        conv = Conversation(title="Metadata Test", model="gemma3:4b")
        conv.add_message('user', 'Test message')

        original_id = conv.id
        original_created = conv.created_at
        original_updated = conv.updated_at

        storage.save_conversation(conv)
        loaded = storage.load_conversation(conv.id)

        # Verify all metadata preserved
        assert loaded.id == original_id
        assert loaded.title == "Metadata Test"
        assert loaded.model == "gemma3:4b"
        assert loaded.created_at == original_created
        assert loaded.updated_at == original_updated

    def test_message_ids_preserved(self, tmp_path):
        """Test that message IDs are preserved during save/load."""
        storage_file = tmp_path / "conversations.json"
        storage = ConversationStorage(str(storage_file))

        conv = Conversation(title="ID Test")
        msg1 = conv.add_message('user', 'First')
        msg2 = conv.add_message('assistant', 'Second')
        msg3 = conv.add_message('user', 'Third')

        storage.save_conversation(conv)
        loaded = storage.load_conversation(conv.id)

        # Verify sequential IDs preserved
        assert loaded.messages[0].id == 0
        assert loaded.messages[1].id == 1
        assert loaded.messages[2].id == 2
