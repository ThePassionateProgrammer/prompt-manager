"""
Tests for provider model listing API.

Supports both online providers (static model lists) and local providers (dynamic discovery).
"""
import pytest
from unittest.mock import Mock, patch
from flask import Flask
from routes.dashboard import dashboard_bp
from src.prompt_manager.business.ollama_provider import OllamaProvider
from src.prompt_manager.domain.ollama_model import OllamaModel


@pytest.fixture
def app():
    """Create Flask test app with dashboard blueprint."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(dashboard_bp)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestProviderModelsAPI:
    """Test API for listing models by provider."""

    def test_list_openai_models(self, client):
        """GET /api/providers/openai/models should return OpenAI model list."""
        # Act
        response = client.get('/api/providers/openai/models')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert 'models' in data
        assert len(data['models']) > 0
        # OpenAI has known models
        model_names = [m['id'] for m in data['models']]
        assert 'gpt-4' in model_names
        assert 'gpt-3.5-turbo' in model_names

    @patch('routes.dashboard.provider_manager')
    def test_list_ollama_models(self, mock_manager, client):
        """GET /api/providers/ollama/models should return Ollama models."""
        # Arrange
        mock_provider = Mock(spec=OllamaProvider)
        mock_provider.name = 'ollama'

        # Mock discovery service
        from src.prompt_manager.business.ollama_discovery import OllamaDiscovery
        with patch.object(OllamaDiscovery, 'list_downloaded_models') as mock_list:
            mock_list.return_value = [
                OllamaModel('gemma3:4b'),
                OllamaModel('llama3:8b')
            ]

            mock_manager.get_provider.return_value = mock_provider

            # Act
            response = client.get('/api/providers/ollama/models')

            # Assert
            assert response.status_code == 200
            data = response.get_json()
            assert 'models' in data
            assert len(data['models']) == 2
            assert data['models'][0]['id'] == 'gemma3:4b'
            assert data['models'][1]['id'] == 'llama3:8b'
