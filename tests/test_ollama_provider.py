"""
Tests for OllamaProvider service.

Test-first development: Write one test at a time, make it pass, refactor.
"""
import pytest
from unittest.mock import Mock, patch
from src.prompt_manager.business.ollama_provider import OllamaProvider


class TestOllamaProviderInitialization:
    """Test OllamaProvider initialization and configuration."""

    def test_provider_name_is_ollama(self):
        """Provider should identify itself as 'ollama'."""
        # Arrange & Act
        provider = OllamaProvider()

        # Assert
        assert provider.name == "ollama"

    def test_default_model_is_gemma3_4b(self):
        """Provider should default to gemma3:4b model."""
        # Arrange & Act
        provider = OllamaProvider()

        # Assert
        assert provider.default_model == "gemma3:4b"

    def test_custom_base_url(self):
        """Provider should accept custom base URL."""
        # Arrange & Act
        provider = OllamaProvider(base_url="http://custom:11434")

        # Assert
        assert provider.base_url == "http://custom:11434"


class TestOllamaProviderAvailability:
    """Test Ollama server availability checks."""

    @patch('ollama.Client')
    def test_is_available_when_ollama_running(self, mock_client_class):
        """Provider should be available when Ollama server responds."""
        # Arrange
        mock_client = Mock()
        mock_client.list.return_value = {'models': []}
        mock_client_class.return_value = mock_client
        provider = OllamaProvider()

        # Act
        available = provider.is_available()

        # Assert
        assert available is True
        mock_client_class.assert_called_once_with(host="http://localhost:11434")

    @patch('ollama.Client')
    def test_is_not_available_when_ollama_not_running(self, mock_client_class):
        """Provider should be unavailable when Ollama server doesn't respond."""
        # Arrange
        mock_client_class.side_effect = Exception("Connection refused")
        provider = OllamaProvider()

        # Act
        available = provider.is_available()

        # Assert
        assert available is False
