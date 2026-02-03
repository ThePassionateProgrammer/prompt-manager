"""Tests for conversation text export utility."""
import pytest
from datetime import datetime
from src.prompt_manager.domain.conversation import Conversation
from src.prompt_manager.tools.export_conversation import (
    conversation_to_text,
    export_conversation_to_file,
    format_date_header,
    format_message
)


class TestConversationExport:
    """Test suite for conversation text export."""

    def test_conversation_to_text_basic(self):
        """Test basic conversation export to text."""
        conv = Conversation(title="Test Chat", model="gemma3:4b")
        conv.add_message('user', 'Hello')
        conv.add_message('assistant', 'Hi there!')

        text = conversation_to_text(conv)

        assert "=== Test Chat ===" in text
        assert "Model: gemma3:4b" in text
        assert "[USER]" in text
        assert "Hello" in text
        assert "[ASSISTANT]" in text
        assert "Hi there!" in text

    def test_conversation_to_text_with_system_message(self):
        """Test export with system message."""
        conv = Conversation(title="System Test")
        conv.add_message('system', 'You are a helpful assistant')
        conv.add_message('user', 'Help me')
        conv.add_message('assistant', 'Of course!')

        text = conversation_to_text(conv)

        assert "[SYSTEM]" in text
        assert "You are a helpful assistant" in text
        assert "[USER]" in text
        assert "[ASSISTANT]" in text

    def test_conversation_to_text_multiline_messages(self):
        """Test export with multiline message content."""
        conv = Conversation(title="Multiline Test")
        conv.add_message('user', 'Here is a code example:\n\nprint("hello")\nprint("world")')
        conv.add_message('assistant', 'Great example!\n\nIt does two things:\n1. Prints hello\n2. Prints world')

        text = conversation_to_text(conv)

        assert 'print("hello")' in text
        assert 'print("world")' in text
        assert "1. Prints hello" in text
        assert "2. Prints world" in text

    def test_conversation_to_text_empty_conversation(self):
        """Test export of conversation with no messages."""
        conv = Conversation(title="Empty Chat")

        text = conversation_to_text(conv)

        assert "=== Empty Chat ===" in text
        assert "Model:" in text
        # Should have header but no message sections

    def test_conversation_to_text_long_title(self):
        """Test export with very long title."""
        long_title = "This is a very long conversation title that should be displayed properly"
        conv = Conversation(title=long_title)
        conv.add_message('user', 'Test')

        text = conversation_to_text(conv)

        assert long_title in text
        assert "[USER]" in text

    def test_format_date_header(self):
        """Test date header formatting."""
        dt = datetime(2025, 1, 15, 14, 30, 45)
        header = format_date_header(dt)

        assert "2025-01-15" in header
        assert "14:30:45" in header

    def test_format_message_user(self):
        """Test formatting user message."""
        conv = Conversation(title="Test")
        msg = conv.add_message('user', 'Hello world')

        formatted = format_message(msg)

        assert "[USER]" in formatted
        assert "Hello world" in formatted

    def test_format_message_assistant(self):
        """Test formatting assistant message."""
        conv = Conversation(title="Test")
        msg = conv.add_message('assistant', 'Hi there!')

        formatted = format_message(msg)

        assert "[ASSISTANT]" in formatted
        assert "Hi there!" in formatted

    def test_format_message_system(self):
        """Test formatting system message."""
        conv = Conversation(title="Test")
        msg = conv.add_message('system', 'System prompt')

        formatted = format_message(msg)

        assert "[SYSTEM]" in formatted
        assert "System prompt" in formatted

    def test_export_conversation_to_file(self, tmp_path):
        """Test exporting conversation to a file."""
        conv = Conversation(title="File Export Test")
        conv.add_message('user', 'Question')
        conv.add_message('assistant', 'Answer')

        output_file = tmp_path / "export.txt"
        export_conversation_to_file(conv, str(output_file))

        # Verify file was created
        assert output_file.exists()

        # Verify content
        content = output_file.read_text(encoding='utf-8')
        assert "=== File Export Test ===" in content
        assert "[USER]" in content
        assert "Question" in content
        assert "[ASSISTANT]" in content
        assert "Answer" in content

    def test_export_preserves_timestamps(self):
        """Test that export includes timestamp information."""
        conv = Conversation(title="Timestamp Test")
        conv.created_at = datetime(2025, 1, 15, 10, 0, 0)
        conv.updated_at = datetime(2025, 1, 15, 11, 30, 0)
        conv.add_message('user', 'Hello')

        text = conversation_to_text(conv)

        # Should include date information in header
        assert "2025-01-15" in text

    def test_export_special_characters(self):
        """Test export handles special characters properly."""
        conv = Conversation(title="Special Chars: <>|&")
        conv.add_message('user', 'Text with "quotes" and \'apostrophes\'')
        conv.add_message('assistant', 'Unicode: 你好 🤖 émojis!')

        text = conversation_to_text(conv)

        assert "Special Chars: <>|&" in text
        assert '"quotes"' in text
        assert "\'apostrophes\'" in text
        assert "你好" in text
        assert "🤖" in text
        assert "émojis" in text

    def test_export_message_ordering(self):
        """Test that messages are exported in correct order."""
        conv = Conversation(title="Order Test")
        conv.add_message('user', 'First message')
        conv.add_message('assistant', 'Second message')
        conv.add_message('user', 'Third message')
        conv.add_message('assistant', 'Fourth message')

        text = conversation_to_text(conv)

        # Find positions of each message
        first_pos = text.find('First message')
        second_pos = text.find('Second message')
        third_pos = text.find('Third message')
        fourth_pos = text.find('Fourth message')

        # Verify ordering
        assert first_pos < second_pos < third_pos < fourth_pos

    def test_export_readable_without_noise(self):
        """Test that export is clean and readable."""
        conv = Conversation(title="Clean Output Test")
        conv.add_message('user', 'Simple question')
        conv.add_message('assistant', 'Simple answer')

        text = conversation_to_text(conv)

        # Should NOT have JSON artifacts, UUIDs, or technical noise
        assert '{' not in text  # No JSON
        assert '}' not in text
        assert '"id":' not in text
        # Clean readable headers
        assert "===" in text
        assert "[USER]" in text
        assert "[ASSISTANT]" in text
