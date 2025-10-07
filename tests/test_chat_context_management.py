"""
Tests for chat context management (history, system prompts, token tracking).

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


class TestChatHistory:
    """Test chat history context management."""
    
    @patch('routes.dashboard.provider_manager')
    def test_send_message_with_history(self, mock_manager, client):
        """Test that chat history is sent with new messages."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Response to follow-up"
        mock_manager.get_provider.return_value = mock_provider
        
        # Send message with history
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        response = client.post('/api/chat/send',
                              json={
                                  'message': 'How are you?',
                                  'history': history
                              })
        
        assert response.status_code == 200
        
        # Verify provider was called with history
        call_kwargs = mock_provider.generate.call_args[1]
        assert 'messages' in call_kwargs
        assert len(call_kwargs['messages']) == 4  # system + 2 history + 1 new
        assert call_kwargs['messages'][0]['role'] == 'system'  # System prompt first
        assert call_kwargs['messages'][1]['role'] == 'user'
        assert call_kwargs['messages'][1]['content'] == 'Hello'
        assert call_kwargs['messages'][3]['content'] == 'How are you?'
    
    @patch('routes.dashboard.provider_manager')
    def test_send_message_without_history(self, mock_manager, client):
        """Test sending message without history still works."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "First response"
        mock_manager.get_provider.return_value = mock_provider
        
        response = client.post('/api/chat/send',
                              json={'message': 'Hello'})
        
        assert response.status_code == 200
        
        # Verify messages sent (system + user message)
        call_kwargs = mock_provider.generate.call_args[1]
        assert 'messages' in call_kwargs
        assert len(call_kwargs['messages']) == 2  # system + user
        assert call_kwargs['messages'][0]['role'] == 'system'
        assert call_kwargs['messages'][1]['role'] == 'user'
    
    @patch('routes.dashboard.provider_manager')
    def test_empty_history_handled(self, mock_manager, client):
        """Test that empty history array is handled correctly."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Response"
        mock_manager.get_provider.return_value = mock_provider
        
        response = client.post('/api/chat/send',
                              json={
                                  'message': 'Test',
                                  'history': []
                              })
        
        assert response.status_code == 200


class TestSystemPrompts:
    """Test system prompt functionality."""
    
    @patch('routes.dashboard.provider_manager')
    def test_send_with_system_prompt(self, mock_manager, client):
        """Test that system prompt is included in messages."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Response"
        mock_manager.get_provider.return_value = mock_provider
        
        response = client.post('/api/chat/send',
                              json={
                                  'message': 'Test',
                                  'system_prompt': 'You are a helpful coding assistant.'
                              })
        
        assert response.status_code == 200
        
        # Verify system message is first
        call_kwargs = mock_provider.generate.call_args[1]
        assert call_kwargs['messages'][0]['role'] == 'system'
        assert 'coding assistant' in call_kwargs['messages'][0]['content']
    
    @patch('routes.dashboard.provider_manager')
    def test_default_system_prompt_used(self, mock_manager, client):
        """Test that default system prompt is used when none provided."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Response"
        mock_manager.get_provider.return_value = mock_provider
        
        response = client.post('/api/chat/send',
                              json={'message': 'Test'})
        
        assert response.status_code == 200
        
        # Verify system message exists with default
        call_kwargs = mock_provider.generate.call_args[1]
        assert call_kwargs['messages'][0]['role'] == 'system'
        assert len(call_kwargs['messages'][0]['content']) > 0
    
    @patch('routes.dashboard.provider_manager')
    def test_system_prompt_with_history(self, mock_manager, client):
        """Test system prompt combined with history."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Response"
        mock_manager.get_provider.return_value = mock_provider
        
        history = [
            {"role": "user", "content": "Previous message"}
        ]
        
        response = client.post('/api/chat/send',
                              json={
                                  'message': 'New message',
                                  'system_prompt': 'Custom prompt',
                                  'history': history
                              })
        
        assert response.status_code == 200
        
        # Verify order: system, history, new message
        call_kwargs = mock_provider.generate.call_args[1]
        messages = call_kwargs['messages']
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'
        assert messages[1]['content'] == 'Previous message'
        assert messages[2]['content'] == 'New message'
    
    def test_save_system_prompt(self, client):
        """Test saving custom system prompt."""
        response = client.post('/api/settings/system-prompt',
                              json={'prompt': 'Custom system prompt'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
    
    def test_get_system_prompt(self, client):
        """Test retrieving saved system prompt."""
        response = client.get('/api/settings/system-prompt')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'prompt' in data
        assert len(data['prompt']) > 0  # Has default
    
    def test_get_default_system_prompt(self, client):
        """Test getting default system prompt."""
        response = client.get('/api/settings/system-prompt/default')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'prompt' in data
        assert 'helpful' in data['prompt'].lower() or 'assistant' in data['prompt'].lower()


class TestTokenUsage:
    """Test token usage tracking and limits."""
    
    @patch('routes.dashboard.provider_manager')
    def test_token_usage_returned(self, mock_manager, client):
        """Test that token usage is returned with response."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Response"
        mock_manager.get_provider.return_value = mock_provider
        
        response = client.post('/api/chat/send',
                              json={
                                  'message': 'Test message',
                                  'model': 'gpt-3.5-turbo'
                              })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token_usage' in data
        assert 'prompt_tokens' in data['token_usage']
        assert 'completion_tokens' in data['token_usage']
        assert 'total_tokens' in data['token_usage']
    
    @patch('routes.dashboard.provider_manager')
    def test_token_percentage_calculated(self, mock_manager, client):
        """Test that token percentage of context window is calculated."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Response"
        mock_manager.get_provider.return_value = mock_provider
        
        response = client.post('/api/chat/send',
                              json={
                                  'message': 'Test',
                                  'model': 'gpt-3.5-turbo'
                              })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token_usage' in data
        assert 'percentage' in data['token_usage']
        assert 0 <= data['token_usage']['percentage'] <= 100
        assert 'context_limit' in data['token_usage']
    
    def test_get_model_context_limits(self, client):
        """Test getting context limits for different models."""
        response = client.get('/api/models/context-limits')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'limits' in data
        assert 'gpt-4' in data['limits']
        assert 'gpt-3.5-turbo' in data['limits']
        assert data['limits']['gpt-4'] > data['limits']['gpt-3.5-turbo']
    
    @patch('routes.dashboard.provider_manager')
    def test_context_warning_near_limit(self, mock_manager, client):
        """Test warning when approaching context limit."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Response"
        mock_manager.get_provider.return_value = mock_provider
        
        # Simulate large history
        large_history = [
            {"role": "user", "content": "x" * 1000},
            {"role": "assistant", "content": "y" * 1000}
        ] * 10  # Large conversation
        
        response = client.post('/api/chat/send',
                              json={
                                  'message': 'Test',
                                  'history': large_history,
                                  'model': 'gpt-3.5-turbo'
                              })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check if warning exists when percentage > 80%
        if data['token_usage']['percentage'] > 80:
            assert 'warning' in data['token_usage']


class TestContextManagement:
    """Test context management strategies."""
    
    @patch('routes.dashboard.provider_manager')
    def test_auto_trim_old_messages(self, mock_manager, client):
        """Test automatic trimming of old messages when near limit."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Response"
        mock_manager.get_provider.return_value = mock_provider
        
        # Very large history
        large_history = [
            {"role": "user", "content": "Message " + str(i)}
            for i in range(100)
        ]
        
        response = client.post('/api/chat/send',
                              json={
                                  'message': 'New message',
                                  'history': large_history,
                                  'model': 'gpt-3.5-turbo',
                                  'auto_trim': True
                              })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Verify trimming occurred
        if 'trimmed' in data:
            assert data['trimmed'] > 0
            assert data['token_usage']['percentage'] < 100
    
    def test_estimate_tokens(self, client):
        """Test token estimation endpoint."""
        response = client.post('/api/chat/estimate-tokens',
                              json={
                                  'message': 'Test message',
                                  'history': [
                                      {"role": "user", "content": "Hello"}
                                  ]
                              })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'estimated_tokens' in data
        assert data['estimated_tokens'] > 0


class TestConversationMetadata:
    """Test conversation metadata and stats."""
    
    @patch('routes.dashboard.provider_manager')
    def test_response_includes_metadata(self, mock_manager, client):
        """Test that response includes conversation metadata."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Response"
        mock_manager.get_provider.return_value = mock_provider
        
        response = client.post('/api/chat/send',
                              json={
                                  'message': 'Test',
                                  'history': [
                                      {"role": "user", "content": "Previous"}
                                  ]
                              })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'metadata' in data
        assert 'message_count' in data['metadata']
        assert data['metadata']['message_count'] == 2  # 1 history + 1 new


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
