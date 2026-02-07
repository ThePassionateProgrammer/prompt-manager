"""
Tests for chat dashboard routes.

Following TDD principles - tests written first!
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from routes.dashboard import dashboard_bp
from src.prompt_manager.business.llm_provider_manager import LLMProviderManager


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


class TestChatRoutes:
    """Test chat dashboard routes."""
    
    @pytest.mark.skip(reason="Template rendering tests require full app context")
    def test_chat_dashboard_renders(self, client):
        """Test that chat dashboard page loads."""
        response = client.get('/chat')
        assert response.status_code == 200
        assert b'Chat - Prompt Manager' in response.data
        assert b'control-panel' in response.data
    
    @pytest.mark.skip(reason="Template rendering tests require full app context")
    def test_chat_dashboard_has_model_selection(self, client):
        """Test that chat dashboard includes model selection dropdown."""
        response = client.get('/chat')
        assert b'model-select' in response.data
        assert b'gpt-4-turbo-preview' in response.data
        assert b'gpt-3.5-turbo' in response.data
    
    @pytest.mark.skip(reason="Template rendering tests require full app context")
    def test_chat_dashboard_has_collapsible_controls(self, client):
        """Test that chat dashboard has collapsible control panel."""
        response = client.get('/chat')
        assert b'toggle-panel-btn' in response.data
        assert b'Hide Controls' in response.data
    
    @pytest.mark.skip(reason="Template rendering tests require full app context")
    def test_chat_dashboard_has_quick_actions(self, client):
        """Test that chat dashboard has quick action buttons."""
        response = client.get('/chat')
        assert b'prompts-btn' in response.data
        assert b'regenerate-btn' in response.data
        assert b'export-btn' in response.data
        assert b'clear-btn' in response.data


class TestSettingsRoute:
    """Test settings page route."""
    
    @pytest.mark.skip(reason="Template rendering tests require full app context")
    def test_settings_page_renders(self, client):
        """Test that settings page loads."""
        response = client.get('/settings')
        assert response.status_code == 200
        assert b'Settings' in response.data
        assert b'API Key' in response.data
    
    @pytest.mark.skip(reason="Template rendering tests require full app context")
    def test_settings_has_provider_selection(self, client):
        """Test that settings page has provider dropdown."""
        response = client.get('/settings')
        assert b'openai' in response.data
        assert b'anthropic' in response.data
        assert b'google' in response.data
    
    @pytest.mark.skip(reason="Template rendering tests require full app context")
    def test_settings_has_back_button(self, client):
        """Test that settings page has back to chat button."""
        response = client.get('/settings')
        assert b'Back to Chat' in response.data
        assert b'/chat' in response.data


class TestChatSendAPI:
    """Test chat message sending API."""
    
    @patch('routes.dashboard.provider_manager')
    def test_send_message_success(self, mock_manager, client):
        """Test successful message sending."""
        # Setup mock
        mock_provider = Mock()
        mock_provider.generate.return_value = "Test response from LLM"
        mock_manager.get_provider.return_value = mock_provider
        
        # Send request
        response = client.post('/api/chat/send',
                              json={
                                  'message': 'Test message',
                                  'provider': 'openai',
                                  'model': 'gpt-3.5-turbo',
                                  'temperature': 0.7,
                                  'max_tokens': 2048
                              })
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['response'] == "Test response from LLM"
        assert data['model'] == 'gpt-3.5-turbo'
        assert data['temperature'] == 0.7
        
        # Verify provider was called with messages array
        call_kwargs = mock_provider.generate.call_args[1]
        assert 'messages' in call_kwargs
        assert call_kwargs['model'] == 'gpt-3.5-turbo'
        assert call_kwargs['temperature'] == 0.7
        assert call_kwargs['max_tokens'] == 2048
    
    @patch('routes.dashboard.provider_manager')
    def test_send_message_missing_provider(self, mock_manager, client):
        """Test sending message when provider not found."""
        mock_manager.get_provider.return_value = None
        
        response = client.post('/api/chat/send',
                              json={
                                  'message': 'Test message',
                                  'provider': 'nonexistent'
                              })
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error'].lower()
    
    def test_send_message_missing_message(self, client):
        """Test sending request without message."""
        response = client.post('/api/chat/send',
                              json={
                                  'provider': 'openai'
                              })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'required' in data['error'].lower()
    
    @patch('routes.dashboard.provider_manager')
    def test_send_message_with_defaults(self, mock_manager, client):
        """Test that defaults are applied when not provided."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Response"
        mock_manager.get_provider.return_value = mock_provider
        
        response = client.post('/api/chat/send',
                              json={'message': 'Test'})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['provider'] == 'openai'  # default
        assert data['model'] == 'gpt-3.5-turbo'  # default
        assert data['temperature'] == 0.7  # default
        assert data['max_tokens'] == 2048  # default
    
    @patch('routes.dashboard.provider_manager')
    def test_send_message_provider_error(self, mock_manager, client):
        """Test handling of provider errors."""
        mock_provider = Mock()
        mock_provider.generate.side_effect = Exception("API Error")
        mock_manager.get_provider.return_value = mock_provider
        
        response = client.post('/api/chat/send',
                              json={'message': 'Test'})
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data


class TestModelsListAPI:
    """Test models list API."""
    
    def test_list_openai_models(self, client):
        """Test listing OpenAI models."""
        response = client.get('/api/models/list?provider=openai')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'models' in data
        assert 'gpt-4-turbo-preview' in data['models']
        assert 'gpt-4' in data['models']
        assert 'gpt-3.5-turbo' in data['models']
        assert 'gpt-3.5-turbo-16k' in data['models']
    
    def test_list_models_default_provider(self, client):
        """Test listing models with default provider."""
        response = client.get('/api/models/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'models' in data
        # Should default to openai
        assert len(data['models']) > 0
    
    def test_list_models_unknown_provider(self, client):
        """Test listing models for unknown provider."""
        response = client.get('/api/models/list?provider=unknown')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'models' in data
        assert len(data['models']) == 0
    
    def test_model_details_included(self, client):
        """Test that model details are included."""
        response = client.get('/api/models/list?provider=openai')
        
        data = json.loads(response.data)
        gpt4_turbo = data['models']['gpt-4-turbo-preview']
        
        assert 'name' in gpt4_turbo
        assert 'description' in gpt4_turbo
        assert 'context' in gpt4_turbo
        assert 'GPT-4 Turbo' in gpt4_turbo['name']


class TestProvidersAPI:
    """Test providers management API."""
    
    @patch('routes.dashboard.provider_manager')
    @patch('routes.dashboard.SecureKeyManager')
    @patch('routes.dashboard.OpenAIProvider')
    def test_add_provider_success(self, mock_provider_class, mock_key_manager_class, mock_manager, client):
        """Test successfully adding a provider."""
        # Setup mocks
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider_class.return_value = mock_provider
        
        mock_key_manager = Mock()
        mock_key_manager.save_key.return_value = True
        mock_key_manager_class.return_value = mock_key_manager
        
        # Send request
        response = client.post('/api/providers/add',
                              json={
                                  'name': 'openai',
                                  'api_key': 'sk-test123'
                              })
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'openai' in data['message'].lower()
        
        # Verify provider was added
        mock_manager.add_provider.assert_called_once()
        
        # Verify key was saved
        mock_key_manager.save_key.assert_called_once_with('openai_api_key', 'sk-test123')
    
    def test_add_provider_missing_fields(self, client):
        """Test adding provider without required fields."""
        response = client.post('/api/providers/add',
                              json={'name': 'openai'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_add_provider_unsupported(self, client):
        """Test adding unsupported provider."""
        response = client.post('/api/providers/add',
                              json={
                                  'name': 'unsupported',
                                  'api_key': 'test123'
                              })
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'currently supported' in data['error'].lower()
    
    @patch('routes.dashboard.provider_manager')
    def test_list_providers(self, mock_manager, client):
        """Test listing all providers."""
        # Setup mock
        mock_provider = Mock()
        mock_provider.name = 'openai'
        mock_provider.is_available.return_value = True
        mock_manager.providers = {'openai': mock_provider}
        mock_manager.default_provider = None
        
        response = client.get('/api/providers/list')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'providers' in data
        assert 'openai' in data['providers']
        assert data['providers']['openai']['is_available'] == True
    
    @patch('routes.dashboard.provider_manager')
    @patch('routes.dashboard.SecureKeyManager')
    def test_remove_provider(self, mock_key_manager_class, mock_manager, client):
        """Test removing a provider."""
        # Setup mocks
        mock_manager.providers = {'openai': Mock()}
        mock_key_manager = Mock()
        mock_key_manager_class.return_value = mock_key_manager
        
        response = client.delete('/api/providers/remove/openai')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        
        # Verify provider was removed
        mock_manager.remove_provider.assert_called_once_with('openai')
        
        # Verify key was deleted
        mock_key_manager.delete_key.assert_called_once_with('openai_api_key')
    
    @patch('routes.dashboard.provider_manager')
    def test_remove_nonexistent_provider(self, mock_manager, client):
        """Test removing a provider that doesn't exist."""
        mock_manager.providers = {}
        
        response = client.delete('/api/providers/remove/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


class TestChatIntegration:
    """Integration tests for chat functionality."""
    
    @patch('routes.dashboard.provider_manager')
    def test_full_chat_workflow(self, mock_manager, client):
        """Test complete chat workflow."""
        # Setup
        mock_provider = Mock()
        mock_provider.generate.return_value = "Hello! How can I help?"
        mock_manager.get_provider.return_value = mock_provider
        
        # 1. Send first message
        response1 = client.post('/api/chat/send',
                               json={
                                   'message': 'Hello',
                                   'model': 'gpt-4'
                               })
        assert response1.status_code == 200
        
        # 2. Send follow-up message
        mock_provider.generate.return_value = "I can help with that!"
        response2 = client.post('/api/chat/send',
                               json={
                                   'message': 'Can you help me?',
                                   'model': 'gpt-4'
                               })
        assert response2.status_code == 200
        
        # Verify both calls were made
        assert mock_provider.generate.call_count == 2
    
    @patch('routes.dashboard.provider_manager')
    def test_model_switching(self, mock_manager, client):
        """Test switching between models."""
        mock_provider = Mock()
        mock_provider.generate.return_value = "Response"
        mock_manager.get_provider.return_value = mock_provider
        
        # Send with GPT-3.5
        client.post('/api/chat/send',
                   json={'message': 'Test', 'model': 'gpt-3.5-turbo'})
        
        # Send with GPT-4
        client.post('/api/chat/send',
                   json={'message': 'Test', 'model': 'gpt-4'})
        
        # Verify different models were used
        calls = mock_provider.generate.call_args_list
        assert calls[0][1]['model'] == 'gpt-3.5-turbo'
        assert calls[1][1]['model'] == 'gpt-4'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
