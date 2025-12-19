"""Export conversations to human-readable text format."""
from datetime import datetime
from typing import TextIO
from ..domain.conversation import Conversation
from ..domain.chat_message import ChatMessage


def format_date_header(dt: datetime) -> str:
    """
    Format datetime for header display.

    Args:
        dt: Datetime to format

    Returns:
        Formatted date string (YYYY-MM-DD HH:MM:SS)
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def format_message(message: ChatMessage) -> str:
    """
    Format a single message for text export.

    Args:
        message: ChatMessage to format

    Returns:
        Formatted message string
    """
    role_label = message.role.upper()
    return f"[{role_label}]\n{message.content}\n"


def conversation_to_text(conversation: Conversation) -> str:
    """
    Convert conversation to human-readable text format.

    Format:
        === Title ===
        Model: gemma3:4b
        Created: 2025-01-15 10:30:00
        Updated: 2025-01-15 11:45:00
        ---

        [USER]
        Message content here

        [ASSISTANT]
        Response content here

    Args:
        conversation: Conversation to export

    Returns:
        Human-readable text representation
    """
    lines = [
        f"=== {conversation.title} ===",
        f"Model: {conversation.model}",
        f"Created: {format_date_header(conversation.created_at)}",
        f"Updated: {format_date_header(conversation.updated_at)}",
        "---",
        ""
    ]

    # Add each message
    for message in conversation.messages:
        lines.append(format_message(message))

    return "\n".join(lines)


def export_conversation_to_file(
    conversation: Conversation,
    output_path: str
) -> None:
    """
    Export conversation to a text file.

    Args:
        conversation: Conversation to export
        output_path: Path to output file

    Raises:
        IOError: If file write fails
    """
    text = conversation_to_text(conversation)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception as e:
        raise IOError(f"Failed to export conversation: {e}")


def export_conversations_to_directory(
    conversations: list[Conversation],
    output_dir: str
) -> list[str]:
    """
    Export multiple conversations to a directory.

    Each conversation is saved as: <sanitized_title>_<short_id>.txt

    Args:
        conversations: List of conversations to export
        output_dir: Directory to save exports

    Returns:
        List of created file paths

    Raises:
        IOError: If directory creation or file write fails
    """
    import os

    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)

    exported_files = []

    for conv in conversations:
        # Sanitize title for filename
        safe_title = "".join(
            c if c.isalnum() or c in (' ', '-', '_') else '_'
            for c in conv.title
        ).strip()[:50]

        # Use first 8 chars of ID
        short_id = conv.id[:8]

        filename = f"{safe_title}_{short_id}.txt"
        filepath = os.path.join(output_dir, filename)

        export_conversation_to_file(conv, filepath)
        exported_files.append(filepath)

    return exported_files
