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


class TestOllamaServerStatus:
    """Test API endpoint for Ollama server status."""

    @patch('routes.ollama.ollama_discovery')
    def test_server_status_when_running(self, mock_discovery, client):
        """GET /api/ollama/status should return running when server available."""
        # Arrange
        mock_discovery.is_server_running.return_value = True

        # Act
        response = client.get('/api/ollama/status')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['running'] is True
        assert data['status'] == 'connected'

    @patch('routes.ollama.ollama_discovery')
    def test_server_status_when_not_running(self, mock_discovery, client):
        """GET /api/ollama/status should return not running when server unavailable."""
        # Arrange
        mock_discovery.is_server_running.return_value = False

        # Act
        response = client.get('/api/ollama/status')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['running'] is False
        assert data['status'] == 'disconnected'


class TestOllamaPullModelAPI:
    """Test API endpoint for pulling/downloading Ollama models."""

    @patch('routes.ollama.ollama_discovery')
    def test_pull_model_success(self, mock_discovery, client):
        """POST /api/ollama/models/pull should download model successfully."""
        # Arrange
        mock_discovery.pull_model.return_value = {'success': True}

        # Act
        response = client.post('/api/ollama/models/pull', json={'model': 'gemma3:4b'})

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        mock_discovery.pull_model.assert_called_once_with('gemma3:4b')

    @patch('routes.ollama.ollama_discovery')
    def test_pull_model_failure(self, mock_discovery, client):
        """POST /api/ollama/models/pull should return error on failure."""
        # Arrange
        mock_discovery.pull_model.return_value = {'success': False, 'error': 'Model not found'}

        # Act
        response = client.post('/api/ollama/models/pull', json={'model': 'invalid-model'})

        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data

    def test_pull_model_missing_model_name(self, client):
        """POST /api/ollama/models/pull should require model name."""
        # Act
        response = client.post('/api/ollama/models/pull', json={})

        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestOllamaDeleteModelAPI:
    """Test API endpoint for deleting Ollama models."""

    @patch('routes.ollama.ollama_discovery')
    def test_delete_model_success(self, mock_discovery, client):
        """DELETE /api/ollama/models/<model> should delete model successfully."""
        # Arrange
        mock_discovery.delete_model.return_value = {'success': True}

        # Act
        response = client.delete('/api/ollama/models/gemma3:4b')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        mock_discovery.delete_model.assert_called_once_with('gemma3:4b')

    @patch('routes.ollama.ollama_discovery')
    def test_delete_model_failure(self, mock_discovery, client):
        """DELETE /api/ollama/models/<model> should return error on failure."""
        # Arrange
        mock_discovery.delete_model.return_value = {'success': False, 'error': 'Model not found'}

        # Act
        response = client.delete('/api/ollama/models/nonexistent')

        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data


class TestOllamaAvailableModelsAPI:
    """Test API endpoint for listing available models to download."""

    def test_list_available_models(self, client):
        """GET /api/ollama/models/available should return catalog of downloadable models."""
        # Act
        response = client.get('/api/ollama/models/available')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert 'models' in data
        assert len(data['models']) > 0

    def test_available_models_have_required_fields(self, client):
        """Available models should have id, name, size_gb, description."""
        # Act
        response = client.get('/api/ollama/models/available')
        data = response.get_json()

        # Assert
        for model in data['models']:
            assert 'id' in model
            assert 'name' in model
            assert 'size_gb' in model
            assert 'description' in model

    def test_filter_models_by_max_size(self, client):
        """GET /api/ollama/models/available?max_size=3 should filter by size."""
        # Act
        response = client.get('/api/ollama/models/available?max_size=3')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        for model in data['models']:
            assert model['size_gb'] <= 3, f"Model {model['name']} exceeds 3GB"

    def test_filter_models_by_category(self, client):
        """GET /api/ollama/models/available?category=code should filter by category."""
        # Act
        response = client.get('/api/ollama/models/available?category=code')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        for model in data['models']:
            assert model['category'] == 'code', f"Model {model['name']} is not a code model"

    def test_filter_models_by_size_and_category(self, client):
        """Should filter by both size and category."""
        # Act
        response = client.get('/api/ollama/models/available?max_size=5&category=general')

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        for model in data['models']:
            assert model['size_gb'] <= 5
            assert model['category'] == 'general'