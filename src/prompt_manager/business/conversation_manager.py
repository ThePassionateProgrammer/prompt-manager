"""
Conversation Manager - Business logic for conversation persistence.

Handles saving, loading, and organizing conversations.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ConversationManager:
    """Manages conversation storage and retrieval."""
    
    def __init__(self, storage_file: str = 'conversations/conversations.json'):
        """Initialize the conversation manager.
        
        Args:
            storage_file: Path to the JSON file for storing conversations
        """
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage if doesn't exist
        if not self.storage_file.exists():
            self._save_all({})
    
    def _load_all(self) -> Dict[str, Dict]:
        """Load all conversations from storage."""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_all(self, conversations: Dict[str, Dict]) -> None:
        """Save all conversations to storage."""
        with open(self.storage_file, 'w') as f:
            json.dump(conversations, f, indent=2)
    
    def _generate_title(self, messages: List[Dict]) -> str:
        """Generate a title from the first user message.
        
        Args:
            messages: List of message dicts
            
        Returns:
            Auto-generated title
        """
        for msg in messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                # Take first 50 chars
                title = content[:50]
                if len(content) > 50:
                    title += '...'
                return title
        return 'New Conversation'
    
    def save_conversation(self, conversation: Dict) -> Dict:
        """Save a conversation.
        
        Args:
            conversation: Conversation dict with messages, title, etc.
            
        Returns:
            Saved conversation with id and timestamp
        """
        conversations = self._load_all()
        
        # Generate ID if not provided
        if 'id' not in conversation:
            conversation['id'] = f"conv-{uuid.uuid4().hex[:12]}"
        
        # Generate title if not provided
        if 'title' not in conversation:
            conversation['title'] = self._generate_title(conversation.get('messages', []))
        
        # Add timestamp
        if 'created_at' not in conversation:
            conversation['created_at'] = datetime.now().isoformat()
        
        conversation['updated_at'] = datetime.now().isoformat()
        
        # Save
        conversations[conversation['id']] = conversation
        self._save_all(conversations)
        
        return conversation
    
    def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Load a conversation by ID.
        
        Args:
            conversation_id: ID of the conversation to load
            
        Returns:
            Conversation dict or None if not found
        """
        conversations = self._load_all()
        return conversations.get(conversation_id)
    
    def list_conversations(self, sort_by: str = 'date') -> List[Dict]:
        """List all conversations.
        
        Args:
            sort_by: Sort order ('date' or 'title')
            
        Returns:
            List of conversation summaries
        """
        conversations = self._load_all()
        
        # Create summaries
        summaries = []
        for conv_id, conv in conversations.items():
            messages = conv.get('messages', [])
            
            # Get last message for preview
            last_msg = ''
            for msg in reversed(messages):
                if msg.get('role') in ['user', 'assistant']:
                    last_msg = msg.get('content', '')[:100]
                    if len(msg.get('content', '')) > 100:
                        last_msg += '...'
                    break
            
            summaries.append({
                'id': conv.get('id'),
                'title': conv.get('title', 'Untitled'),
                'preview': last_msg,
                'last_message': last_msg,
                'message_count': len(messages),
                'created_at': conv.get('created_at'),
                'updated_at': conv.get('updated_at'),
                'model': conv.get('model', 'unknown')
            })
        
        # Sort
        if sort_by == 'date':
            summaries.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        else:
            summaries.sort(key=lambda x: x.get('title', ''))
        
        return summaries
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation.
        
        Args:
            conversation_id: ID of conversation to delete
            
        Returns:
            True if deleted, False if not found
        """
        conversations = self._load_all()
        
        if conversation_id in conversations:
            del conversations[conversation_id]
            self._save_all(conversations)
            return True
        
        return False
    
    def search_conversations(self, query: str) -> List[Dict]:
        """Search conversations by content.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching conversation summaries
        """
        all_conversations = self.list_conversations()
        query_lower = query.lower()
        
        matches = []
        for conv in all_conversations:
            # Search in title and preview
            if (query_lower in conv.get('title', '').lower() or 
                query_lower in conv.get('preview', '').lower()):
                matches.append(conv)
        
        return matches
    
    def get_conversation_count(self) -> int:
        """Get total number of saved conversations."""
        conversations = self._load_all()
        return len(conversations)
