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


class TestOllamaProviderGeneration:
    """Test text generation with Ollama."""

    @patch('ollama.Client')
    def test_generate_with_messages(self, mock_client_class):
        """Provider should generate text from messages array."""
        # Arrange
        mock_client = Mock()
        mock_response = {
            'message': {
                'content': 'Hello! How can I help you?'
            }
        }
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()
        messages = [{'role': 'user', 'content': 'Hello'}]

        # Act
        response = provider.generate(messages=messages)

        # Assert
        assert response == 'Hello! How can I help you?'
        mock_client.chat.assert_called_once_with(
            model='gemma3:4b',
            messages=messages
        )

    @patch('ollama.Client')
    def test_generate_with_prompt_string(self, mock_client_class):
        """Provider should generate text from simple prompt string (legacy)."""
        # Arrange
        mock_client = Mock()
        mock_response = {
            'message': {
                'content': 'Paris is the capital of France.'
            }
        }
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()

        # Act
        response = provider.generate(prompt='What is the capital of France?')

        # Assert
        assert response == 'Paris is the capital of France.'
        mock_client.chat.assert_called_once_with(
            model='gemma3:4b',
            messages=[{'role': 'user', 'content': 'What is the capital of France?'}]
        )

    @patch('ollama.Client')
    def test_generate_with_custom_model(self, mock_client_class):
        """Provider should use custom model when specified."""
        # Arrange
        mock_client = Mock()
        mock_response = {'message': {'content': 'Response'}}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()

        # Act
        response = provider.generate(prompt='Test', model='llama3:8b')

        # Assert
        mock_client.chat.assert_called_once_with(
            model='llama3:8b',
            messages=[{'role': 'user', 'content': 'Test'}]
        )
