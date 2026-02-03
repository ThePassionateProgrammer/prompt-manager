"""
Tests for OllamaProvider.

Tests the Ollama LLM provider with mocked Ollama client to avoid requiring
a running Ollama server during tests. Includes tests for both the legacy
generate() interface and the streaming send_message_stream() interface.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from src.prompt_manager.business.llm_provider import OllamaProvider


class TestOllamaProviderInitialization:
    """Test OllamaProvider initialization and configuration."""

    @patch('ollama.Client')
    def test_create_provider_with_defaults(self, mock_client_class):
        """Test creating provider with default settings."""
        provider = OllamaProvider()

        assert provider.base_url == "http://localhost:11434"
        assert provider.default_model == "gemma3:4b"
        mock_client_class.assert_called_once_with(host="http://localhost:11434")

    @patch('ollama.Client')
    def test_create_provider_with_custom_settings(self, mock_client_class):
        """Test creating provider with custom base URL and model."""
        provider = OllamaProvider(
            base_url="http://custom:8080",
            default_model="llama3.1:8b"
        )

        assert provider.base_url == "http://custom:8080"
        assert provider.default_model == "llama3.1:8b"
        mock_client_class.assert_called_once_with(host="http://custom:8080")


class TestOllamaProviderSendPrompt:
    """Test non-streaming prompt sending."""

    @patch('ollama.Client')
    def test_send_prompt_non_streaming(self, mock_client_class):
        """Test sending a prompt without streaming."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.chat.return_value = {
            'message': {'content': 'Hello! How can I help you?'}
        }

        provider = OllamaProvider()
        response = provider.send_prompt("Hi there")

        assert response == 'Hello! How can I help you?'
        mock_client.chat.assert_called_once_with(
            model='gemma3:4b',
            messages=[{'role': 'user', 'content': 'Hi there'}],
            stream=False
        )

    @patch('ollama.Client')
    def test_send_prompt_with_custom_model(self, mock_client_class):
        """Test sending prompt with a different model."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.chat.return_value = {
            'message': {'content': 'Response'}
        }

        provider = OllamaProvider()
        provider.send_prompt("Test", model='llama3.1:8b')

        mock_client.chat.assert_called_once_with(
            model='llama3.1:8b',
            messages=[{'role': 'user', 'content': 'Test'}],
            stream=False
        )

    @patch('ollama.Client')
    def test_send_prompt_error_handling(self, mock_client_class):
        """Test error handling when Ollama request fails."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.chat.side_effect = Exception("Connection refused")

        provider = OllamaProvider()

        with pytest.raises(RuntimeError) as exc_info:
            provider.send_prompt("Test")

        assert "Ollama Error" in str(exc_info.value)
        assert "Connection refused" in str(exc_info.value)


class TestOllamaProviderStreaming:
    """Test streaming message responses."""

    @patch('ollama.Client')
    def test_send_message_stream(self, mock_client_class):
        """Test streaming message responses."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        def mock_stream():
            yield {'message': {'content': 'Hello '}}
            yield {'message': {'content': 'there! '}}
            yield {'message': {'content': 'How '}}
            yield {'message': {'content': 'can I help?'}}

        mock_client.chat.return_value = mock_stream()

        provider = OllamaProvider()
        messages = [
            {'role': 'user', 'content': 'Hi'},
            {'role': 'assistant', 'content': 'Hello!'},
            {'role': 'user', 'content': 'How are you?'}
        ]

        chunks = list(provider.send_message_stream(messages))

        assert chunks == ['Hello ', 'there! ', 'How ', 'can I help?']
        mock_client.chat.assert_called_once_with(
            model='gemma3:4b',
            messages=messages,
            stream=True
        )

    @patch('ollama.Client')
    def test_send_message_stream_with_custom_model(self, mock_client_class):
        """Test streaming with a custom model."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        def mock_stream():
            yield {'message': {'content': 'Response'}}

        mock_client.chat.return_value = mock_stream()

        provider = OllamaProvider()
        messages = [{'role': 'user', 'content': 'Test'}]

        list(provider.send_message_stream(messages, model='gemma3:12b'))

        mock_client.chat.assert_called_once_with(
            model='gemma3:12b',
            messages=messages,
            stream=True
        )

    @patch('ollama.Client')
    def test_send_message_stream_empty_response(self, mock_client_class):
        """Test handling empty streaming response."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.chat.return_value = iter([])

        provider = OllamaProvider()
        chunks = list(provider.send_message_stream([]))

        assert chunks == []

    @patch('ollama.Client')
    def test_send_message_stream_error_handling(self, mock_client_class):
        """Test error handling in streaming mode."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.chat.side_effect = Exception("Model not found")

        provider = OllamaProvider()

        with pytest.raises(RuntimeError) as exc_info:
            list(provider.send_message_stream([{'role': 'user', 'content': 'Hi'}]))

        assert "Ollama Stream Error" in str(exc_info.value)
        assert "Model not found" in str(exc_info.value)

    @patch('ollama.Client')
    def test_streaming_handles_malformed_chunks(self, mock_client_class):
        """Test that streaming gracefully handles malformed response chunks."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        def mock_stream():
            yield {'message': {'content': 'Good chunk'}}
            yield {'not_message': 'bad'}  # Malformed
            yield {'message': {'content': 'Another good chunk'}}

        mock_client.chat.return_value = mock_stream()

        provider = OllamaProvider()
        chunks = list(provider.send_message_stream([{'role': 'user', 'content': 'Test'}]))

        assert 'Good chunk' in chunks
        assert 'Another good chunk' in chunks
        assert len(chunks) == 2


class TestOllamaProviderModels:
    """Test model listing and health checks."""

    @patch('ollama.Client')
    def test_list_models(self, mock_client_class):
        """Test listing available Ollama models."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {
            'models': [
                {'name': 'gemma3:4b'},
                {'name': 'gemma3:12b'},
                {'name': 'llama3.1:8b'}
            ]
        }

        provider = OllamaProvider()
        models = provider.list_models()

        assert models == ['gemma3:4b', 'gemma3:12b', 'llama3.1:8b']
        mock_client.list.assert_called_once()

    @patch('ollama.Client')
    def test_list_models_empty(self, mock_client_class):
        """Test listing models when none are available."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {'models': []}

        provider = OllamaProvider()
        models = provider.list_models()

        assert models == []

    @patch('ollama.Client')
    def test_list_models_error(self, mock_client_class):
        """Test error handling when listing models fails."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.list.side_effect = Exception("Server unreachable")

        provider = OllamaProvider()

        with pytest.raises(RuntimeError) as exc_info:
            provider.list_models()

        assert "Failed to list models" in str(exc_info.value)

    @patch('ollama.Client')
    def test_check_ollama_health_success(self, mock_client_class):
        """Test health check when Ollama is running."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {
            'models': [
                {'name': 'gemma3:4b'},
                {'name': 'llama3.1:8b'}
            ]
        }

        provider = OllamaProvider()
        health = provider.check_ollama_health()

        assert health['connected'] is True
        assert health['available_models'] == ['gemma3:4b', 'llama3.1:8b']
        assert health['default_model'] == 'gemma3:4b'
        assert health['default_model_available'] is True

    @patch('ollama.Client')
    def test_check_ollama_health_model_not_available(self, mock_client_class):
        """Test health check when default model is not available."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {
            'models': [
                {'name': 'llama3.1:8b'}  # gemma3:4b not in list
            ]
        }

        provider = OllamaProvider()
        health = provider.check_ollama_health()

        assert health['connected'] is True
        assert health['default_model_available'] is False

    @patch('ollama.Client')
    def test_check_ollama_health_connection_failed(self, mock_client_class):
        """Test health check when Ollama is not running."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.list.side_effect = Exception("Connection refused")

        provider = OllamaProvider()
        health = provider.check_ollama_health()

        assert health['connected'] is False
        assert 'error' in health
        assert 'Connection refused' in health['error']
