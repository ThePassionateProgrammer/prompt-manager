"""
Tests for GoogleProvider service.

Test-first development: Write one test at a time, make it pass, refactor.
Updated for google-genai SDK migration.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.prompt_manager.business.google_provider import GoogleProvider


class TestGoogleProviderInitialization:
    """Test GoogleProvider initialization and configuration."""

    def test_provider_name_is_google(self):
        """Provider should identify itself as 'google'."""
        provider = GoogleProvider(api_key='test-key')
        assert provider.name == "google"

    def test_stores_api_key_when_provided(self):
        """Provider should store provided API key."""
        provider = GoogleProvider(api_key='AIzaSy-test-key')
        assert provider.api_key == 'AIzaSy-test-key'

    def test_initializes_without_api_key(self):
        """Provider should initialize without API key (deferred loading)."""
        provider = GoogleProvider()
        assert provider.api_key is None
        assert provider._initialized is False


class TestGoogleProviderAvailability:
    """Test Google API availability checks."""

    def test_is_available_when_api_key_provided(self):
        """Provider should be available when API key is provided."""
        provider = GoogleProvider(api_key='AIzaSy-test-key')
        assert provider.is_available() is True

    @patch('src.prompt_manager.business.key_loader.load_google_api_key')
    def test_is_not_available_when_no_api_key(self, mock_load_key):
        """Provider should be unavailable when no API key is available."""
        mock_load_key.side_effect = ValueError("Key not found")
        provider = GoogleProvider()
        assert provider.is_available() is False


class TestGoogleProviderGeneration:
    """Test text generation with Google Gemini using google-genai SDK."""

    @patch('google.genai.Client')
    def test_generate_with_messages(self, mock_client_class):
        """Provider should generate text from messages array."""
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.text = 'Hello! How can I help you?'
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = GoogleProvider(api_key='AIzaSy-test-key')
        messages = [{'role': 'user', 'content': 'Hello'}]

        response = provider.generate(messages=messages)

        assert response == 'Hello! How can I help you?'

    @patch('google.genai.Client')
    def test_generate_with_prompt_string(self, mock_client_class):
        """Provider should generate text from simple prompt string."""
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.text = 'Paris is the capital of France.'
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = GoogleProvider(api_key='AIzaSy-test-key')

        response = provider.generate(prompt='What is the capital of France?')

        assert response == 'Paris is the capital of France.'

    @patch('google.genai.Client')
    def test_generate_with_system_instruction(self, mock_client_class):
        """Provider should pass system instruction via config."""
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.text = 'Response'
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = GoogleProvider(api_key='AIzaSy-test-key')
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Hello'}
        ]

        provider.generate(messages=messages)

        # Verify generate_content was called with system_instruction in config
        call_kwargs = mock_client.models.generate_content.call_args
        assert call_kwargs is not None

    @patch('google.genai.Client')
    def test_generate_with_custom_model(self, mock_client_class):
        """Provider should use custom model when specified."""
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.text = 'Response'
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = GoogleProvider(api_key='AIzaSy-test-key')

        provider.generate(prompt='Test', model='gemini-1.5-pro')

        call_kwargs = mock_client.models.generate_content.call_args
        assert call_kwargs[1]['model'] == 'gemini-1.5-pro'

    @patch('google.genai.Client')
    def test_generate_with_chat_history(self, mock_client_class):
        """Provider should handle multi-turn conversation history."""
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.text = 'Response'
        mock_client.models.generate_content.return_value = mock_response
        mock_client_class.return_value = mock_client

        provider = GoogleProvider(api_key='AIzaSy-test-key')
        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'},
            {'role': 'user', 'content': 'How are you?'}
        ]

        provider.generate(messages=messages)

        # Should have been called
        mock_client.models.generate_content.assert_called_once()


class TestGoogleProviderErrorHandling:
    """Test error handling for Google API errors."""

    @patch('google.genai.Client')
    def test_raises_error_when_no_prompt_or_messages(self, mock_client_class):
        """Provider should raise error when neither prompt nor messages provided."""
        mock_client_class.return_value = MagicMock()
        provider = GoogleProvider(api_key='AIzaSy-test-key')

        with pytest.raises(RuntimeError, match="Either prompt or messages must be provided"):
            provider.generate()

    @patch('google.genai.Client')
    def test_quota_error_includes_helpful_message(self, mock_client_class):
        """Provider should include helpful message for quota errors."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("quota exceeded")
        mock_client_class.return_value = mock_client

        provider = GoogleProvider(api_key='AIzaSy-test-key')

        with pytest.raises(RuntimeError) as exc_info:
            provider.generate(prompt='Test')
        assert "quota" in str(exc_info.value).lower()
        assert "console.cloud.google.com" in str(exc_info.value)

    @patch('google.genai.Client')
    def test_invalid_key_error_includes_helpful_message(self, mock_client_class):
        """Provider should include helpful message for invalid key errors."""
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("invalid key provided")
        mock_client_class.return_value = mock_client

        provider = GoogleProvider(api_key='AIzaSy-test-key')

        with pytest.raises(RuntimeError) as exc_info:
            provider.generate(prompt='Test')
        assert "invalid" in str(exc_info.value).lower()
