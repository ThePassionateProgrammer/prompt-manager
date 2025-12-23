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
