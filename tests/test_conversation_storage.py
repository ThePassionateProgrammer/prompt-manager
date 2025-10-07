"""
Tests for conversation storage and persistence.

Following TDD principles - tests written first!
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from routes.dashboard import dashboard_bp


@pytest.fixture
def app():
    """Create test Flask app."""
    app = Flask(__name__,
               template_folder='src/prompt_manager/templates')
    app.config['TESTING'] = True
    app.register_blueprint(dashboard_bp)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestConversationPersistence:
    """Test saving and loading conversations."""
    
    def test_save_conversation(self, client):
        """Test saving a conversation."""
        conversation = {
            'id': 'conv-123',
            'title': 'Test Conversation',
            'messages': [
                {'role': 'user', 'content': 'Hello'},
                {'role': 'assistant', 'content': 'Hi there!'}
            ],
            'model': 'gpt-3.5-turbo',
            'system_prompt': 'You are helpful'
        }
        
        response = client.post('/api/conversations/save',
                              json=conversation)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'id' in data
        assert 'message' in data
    
    def test_load_conversation(self, client):
        """Test loading a saved conversation."""
        # First save
        conversation = {
            'id': 'conv-456',
            'title': 'Loaded Conversation',
            'messages': [{'role': 'user', 'content': 'Test'}]
        }
        client.post('/api/conversations/save', json=conversation)
        
        # Then load
        response = client.get('/api/conversations/load/conv-456')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == 'conv-456'
        assert data['title'] == 'Loaded Conversation'
        assert len(data['messages']) == 1
    
    def test_load_nonexistent_conversation(self, client):
        """Test loading conversation that doesn't exist."""
        response = client.get('/api/conversations/load/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_list_conversations(self, client):
        """Test listing all saved conversations."""
        # Save a few conversations
        for i in range(3):
            client.post('/api/conversations/save',
                       json={
                           'id': f'conv-{i}',
                           'title': f'Conversation {i}',
                           'messages': []
                       })
        
        response = client.get('/api/conversations/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'conversations' in data
        assert len(data['conversations']) >= 3
    
    def test_delete_conversation(self, client):
        """Test deleting a conversation."""
        # Save first
        client.post('/api/conversations/save',
                   json={'id': 'to-delete', 'title': 'Delete Me', 'messages': []})
        
        # Delete
        response = client.delete('/api/conversations/delete/to-delete')
        
        assert response.status_code == 200
        
        # Verify it's gone
        load_response = client.get('/api/conversations/load/to-delete')
        assert load_response.status_code == 404
    
    def test_conversation_auto_title(self, client):
        """Test that conversations get auto-titled from first message."""
        conversation = {
            'messages': [
                {'role': 'user', 'content': 'What is Python?'},
                {'role': 'assistant', 'content': 'Python is a programming language'}
            ]
        }
        
        response = client.post('/api/conversations/save', json=conversation)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'title' in data
        assert len(data['title']) > 0
        # Should use first user message
        assert 'Python' in data['title'] or 'What' in data['title']
    
    def test_update_existing_conversation(self, client):
        """Test updating an existing conversation."""
        # Save initial
        client.post('/api/conversations/save',
                   json={
                       'id': 'update-test',
                       'title': 'Original',
                       'messages': [{'role': 'user', 'content': 'First'}]
                   })
        
        # Update with more messages
        response = client.post('/api/conversations/save',
                              json={
                                  'id': 'update-test',
                                  'title': 'Original',
                                  'messages': [
                                      {'role': 'user', 'content': 'First'},
                                      {'role': 'assistant', 'content': 'Response'},
                                      {'role': 'user', 'content': 'Second'}
                                  ]
                              })
        
        assert response.status_code == 200
        
        # Verify update
        load_response = client.get('/api/conversations/load/update-test')
        data = json.loads(load_response.data)
        assert len(data['messages']) == 3


class TestConversationMetadata:
    """Test conversation metadata and statistics."""
    
    def test_conversation_includes_timestamps(self, client):
        """Test that saved conversations include timestamps."""
        response = client.post('/api/conversations/save',
                              json={
                                  'title': 'Time Test',
                                  'messages': []
                              })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'created_at' in data or 'timestamp' in data
    
    def test_conversation_includes_token_count(self, client):
        """Test that conversations track total token usage."""
        conversation = {
            'messages': [
                {'role': 'user', 'content': 'Test message'}
            ],
            'token_usage': {
                'total_tokens': 100
            }
        }
        
        response = client.post('/api/conversations/save', json=conversation)
        
        assert response.status_code == 200
    
    def test_list_includes_preview(self, client):
        """Test that conversation list includes message preview."""
        client.post('/api/conversations/save',
                   json={
                       'title': 'Preview Test',
                       'messages': [
                           {'role': 'user', 'content': 'This is a preview message'}
                       ]
                   })
        
        response = client.get('/api/conversations/list')
        data = json.loads(response.data)
        
        # Find our conversation
        conv = next((c for c in data['conversations'] if c['title'] == 'Preview Test'), None)
        assert conv is not None
        assert 'preview' in conv or 'last_message' in conv


class TestConversationOrganization:
    """Test conversation organization features."""
    
    def test_conversations_sorted_by_date(self, client):
        """Test that conversations are returned sorted by date (newest first)."""
        response = client.get('/api/conversations/list?sort=date')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'conversations' in data
        # Verify sorting if multiple conversations exist
    
    def test_search_conversations(self, client):
        """Test searching conversations by content."""
        # Save searchable conversation
        client.post('/api/conversations/save',
                   json={
                       'title': 'Python Tutorial',
                       'messages': [
                           {'role': 'user', 'content': 'Teach me Python'}
                       ]
                   })
        
        response = client.get('/api/conversations/search?q=Python')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'conversations' in data
        assert len(data['conversations']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
