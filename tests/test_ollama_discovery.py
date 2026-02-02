"""
Tests for Ollama model discovery service.

Test-first development: Write one test at a time, make it pass, refactor.
"""
import pytest
from unittest.mock import Mock, patch
from src.prompt_manager.business.ollama_discovery import OllamaDiscovery
from src.prompt_manager.domain.ollama_model import OllamaModel


class TestOllamaDiscoveryListModels:
    """Test listing downloaded Ollama models."""

    @patch('ollama.Client')
    def test_list_downloaded_models_returns_model_objects(self, mock_client_class):
        """Should return list of OllamaModel objects for downloaded models."""
        # Arrange
        mock_client = Mock()
        # Ollama client returns ListResponse object with .models attribute
        mock_model1 = Mock()
        mock_model1.model = 'gemma3:4b'
        mock_model2 = Mock()
        mock_model2.model = 'llama3:8b'

        mock_response = Mock()
        mock_response.models = [mock_model1, mock_model2]
        mock_client.list.return_value = mock_response
        mock_client_class.return_value = mock_client

        discovery = OllamaDiscovery()

        # Act
        models = discovery.list_downloaded_models()

        # Assert
        assert len(models) == 2
        assert isinstance(models[0], OllamaModel)
        assert models[0].full_name == 'gemma3:4b'
        assert models[1].full_name == 'llama3:8b'

    @patch('ollama.Client')
    def test_list_downloaded_models_when_none_exist(self, mock_client_class):
        """Should return empty list when no models downloaded."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock()
        mock_response.models = []
        mock_client.list.return_value = mock_response
        mock_client_class.return_value = mock_client

        discovery = OllamaDiscovery()

        # Act
        models = discovery.list_downloaded_models()

        # Assert
        assert models == []

    @patch('ollama.Client')
    def test_list_downloaded_models_includes_metadata(self, mock_client_class):
        """Should extract size, family, and parameter info from Ollama API."""
        # Arrange
        mock_client = Mock()

        # Ollama API returns detailed model information
        mock_model = Mock()
        mock_model.model = 'gemma3:4b'
        mock_model.size = 3338801804
        mock_model.details = Mock()
        mock_model.details.family = 'gemma3'
        mock_model.details.parameter_size = '4.3B'

        mock_response = Mock()
        mock_response.models = [mock_model]
        mock_client.list.return_value = mock_response
        mock_client_class.return_value = mock_client

        discovery = OllamaDiscovery()

        # Act
        models = discovery.list_downloaded_models()

        # Assert
        assert len(models) == 1
        model = models[0]
        assert model.full_name == 'gemma3:4b'
        assert model.size_bytes == 3338801804
        assert model.family == 'gemma3'
        assert model.parameter_size == '4.3B'
        assert model.size_display() == '3.1 GB'


class TestOllamaDiscoveryServerStatus:
    """Test Ollama server status checking."""

    @patch('ollama.Client')
    def test_is_server_running_returns_true_when_connected(self, mock_client_class):
        """Should return True when Ollama server responds."""
        # Arrange
        mock_client = Mock()
        mock_client.list.return_value = Mock(models=[])
        mock_client_class.return_value = mock_client

        discovery = OllamaDiscovery()

        # Act
        result = discovery.is_server_running()

        # Assert
        assert result is True

    @patch('ollama.Client')
    def test_is_server_running_returns_false_when_connection_fails(self, mock_client_class):
        """Should return False when Ollama server not available."""
        # Arrange
        mock_client = Mock()
        mock_client.list.side_effect = Exception("Connection refused")
        mock_client_class.return_value = mock_client

        discovery = OllamaDiscovery()

        # Act
        result = discovery.is_server_running()

        # Assert
        assert result is False


class TestOllamaDiscoveryPullModel:
    """Test pulling/downloading Ollama models."""

    @patch('ollama.Client')
    def test_pull_model_calls_ollama_pull(self, mock_client_class):
        """Should call Ollama client's pull method with model name."""
        # Arrange
        mock_client = Mock()
        mock_client.pull.return_value = iter([{'status': 'success'}])
        mock_client_class.return_value = mock_client

        discovery = OllamaDiscovery()

        # Act
        result = discovery.pull_model('gemma3:4b')

        # Assert
        mock_client.pull.assert_called_once_with('gemma3:4b', stream=True)
        assert result['success'] is True

    @patch('ollama.Client')
    def test_pull_model_returns_error_on_failure(self, mock_client_class):
        """Should return error when pull fails."""
        # Arrange
        mock_client = Mock()
        mock_client.pull.side_effect = Exception("Model not found")
        mock_client_class.return_value = mock_client

        discovery = OllamaDiscovery()

        # Act
        result = discovery.pull_model('invalid-model')

        # Assert
        assert result['success'] is False
        assert 'error' in result


class TestOllamaDiscoveryDeleteModel:
    """Test deleting Ollama models."""

    @patch('ollama.Client')
    def test_delete_model_calls_ollama_delete(self, mock_client_class):
        """Should call Ollama client's delete method with model name."""
        # Arrange
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        discovery = OllamaDiscovery()

        # Act
        result = discovery.delete_model('gemma3:4b')

        # Assert
        mock_client.delete.assert_called_once_with('gemma3:4b')
        assert result['success'] is True

    @patch('ollama.Client')
    def test_delete_model_returns_error_on_failure(self, mock_client_class):
        """Should return error when delete fails."""
        # Arrange
        mock_client = Mock()
        mock_client.delete.side_effect = Exception("Model not found")
        mock_client_class.return_value = mock_client

        discovery = OllamaDiscovery()

        # Act
        result = discovery.delete_model('nonexistent-model')

        # Assert
        assert result['success'] is False
        assert 'error' in result