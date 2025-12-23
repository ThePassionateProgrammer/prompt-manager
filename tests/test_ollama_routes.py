"""
Tests for Ollama-specific API routes.

Test-first development: Write one test at a time, make it pass, refactor.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
from routes.ollama import ollama_bp
from src.prompt_manager.domain.ollama_model import OllamaModel


@pytest.fixture
def app():
    """Create Flask test app with Ollama blueprint."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(ollama_bp)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestOllamaModelsAPI:
    """Test API endpoint for listing Ollama models."""

    @patch('routes.ollama.ollama_discovery')
    def test_list_downloaded_models(self, mock_discovery, client):
        """GET /api/ollama/models should return list of downloaded models."""
        # Arrange
        mock_model1 = OllamaModel('gemma3:4b')
        mock_model2 = OllamaModel('llama3:8b')
        mock_discovery.list_downloaded_models.return_value = [mock_model1, mock_model2]

        # Act
        response = client.get('/api/ollama/models')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['models']) == 2
        assert data['models'][0]['name'] == 'gemma3'
        assert data['models'][0]['tag'] == '4b'
        assert data['models'][0]['full_name'] == 'gemma3:4b'
        assert data['models'][1]['full_name'] == 'llama3:8b'
