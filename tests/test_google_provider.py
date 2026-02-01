"""
Tests for GoogleProvider service.

Test-first development: Write one test at a time, make it pass, refactor.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.prompt_manager.business.google_provider import GoogleProvider


class TestGoogleProviderInitialization:
    """Test GoogleProvider initialization and configuration."""

    def test_provider_name_is_google(self):
        """Provider should identify itself as 'google'."""
        # Arrange & Act
        provider = GoogleProvider(api_key='test-key')

        # Assert
        assert provider.name == "google"

    def test_stores_api_key_when_provided(self):
        """Provider should store provided API key."""
        # Arrange & Act
        provider = GoogleProvider(api_key='AIzaSy-test-key')

        # Assert
        assert provider.api_key == 'AIzaSy-test-key'

    def test_initializes_without_api_key(self):
        """Provider should initialize without API key (deferred loading)."""
        # Arrange & Act
        provider = GoogleProvider()

        # Assert
        assert provider.api_key is None
        assert provider._initialized is False


class TestGoogleProviderAvailability:
    """Test Google API availability checks."""

    def test_is_available_when_api_key_provided(self):
        """Provider should be available when API key is provided."""
        # Arrange
        provider = GoogleProvider(api_key='AIzaSy-test-key')

        # Act
        available = provider.is_available()

        # Assert
        assert available is True

    @patch('src.prompt_manager.business.key_loader.load_google_api_key')
    def test_is_not_available_when_no_api_key(self, mock_load_key):
        """Provider should be unavailable when no API key is available."""
        # Arrange
        mock_load_key.side_effect = ValueError("Key not found")
        provider = GoogleProvider()

        # Act
        available = provider.is_available()

        # Assert
        assert available is False


class TestGoogleProviderGeneration:
    """Test text generation with Google Gemini."""

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_generate_with_messages(self, mock_configure, mock_model_class):
        """Provider should generate text from messages array."""
        # Arrange
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = 'Hello! How can I help you?'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        provider = GoogleProvider(api_key='AIzaSy-test-key')
        messages = [{'role': 'user', 'content': 'Hello'}]

        # Act
        response = provider.generate(messages=messages)

        # Assert
        assert response == 'Hello! How can I help you?'

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_generate_with_prompt_string(self, mock_configure, mock_model_class):
        """Provider should generate text from simple prompt string (legacy)."""
        # Arrange
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = 'Paris is the capital of France.'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        provider = GoogleProvider(api_key='AIzaSy-test-key')

        # Act
        response = provider.generate(prompt='What is the capital of France?')

        # Assert
        assert response == 'Paris is the capital of France.'

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_generate_with_system_instruction(self, mock_configure, mock_model_class):
        """Provider should pass system instruction to model constructor."""
        # Arrange
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = 'Response'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        provider = GoogleProvider(api_key='AIzaSy-test-key')
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Hello'}
        ]

        # Act
        provider.generate(messages=messages)

        # Assert - system instruction should be passed to GenerativeModel
        calls = mock_model_class.call_args_list
        # Should be called with system_instruction parameter
        assert any('system_instruction' in str(call) for call in calls)

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_generate_with_custom_model(self, mock_configure, mock_model_class):
        """Provider should use custom model when specified."""
        # Arrange
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = 'Response'
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model

        provider = GoogleProvider(api_key='AIzaSy-test-key')

        # Act
        provider.generate(prompt='Test', model='gemini-1.5-pro')

        # Assert - model name should be passed to GenerativeModel
        mock_model_class.assert_called()
        call_args = mock_model_class.call_args
        assert call_args[0][0] == 'gemini-1.5-pro'

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_generate_converts_assistant_role_to_model(self, mock_configure, mock_model_class):
        """Provider should convert 'assistant' role to 'model' for Gemini."""
        # Arrange
        mock_model = Mock()
        mock_chat = Mock()
        mock_response = Mock()
        mock_response.text = 'Response'
        mock_chat.send_message.return_value = mock_response
        mock_model.start_chat.return_value = mock_chat
        mock_model_class.return_value = mock_model

        provider = GoogleProvider(api_key='AIzaSy-test-key')
        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'},
            {'role': 'user', 'content': 'How are you?'}
        ]

        # Act
        provider.generate(messages=messages)

        # Assert - start_chat should be called with history containing 'model' role
        mock_model.start_chat.assert_called()


class TestGoogleProviderErrorHandling:
    """Test error handling for Google API errors."""

    @patch('google.generativeai.configure')
    def test_raises_error_when_no_prompt_or_messages(self, mock_configure):
        """Provider should raise error when neither prompt nor messages provided."""
        # Arrange
        provider = GoogleProvider(api_key='AIzaSy-test-key')

        # Act & Assert - ValueError is caught and wrapped in RuntimeError
        with pytest.raises(RuntimeError, match="Either prompt or messages must be provided"):
            provider.generate()

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_quota_error_includes_helpful_message(self, mock_configure, mock_model_class):
        """Provider should include helpful message for quota errors."""
        # Arrange
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("quota exceeded")
        mock_model_class.return_value = mock_model

        provider = GoogleProvider(api_key='AIzaSy-test-key')

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            provider.generate(prompt='Test')
        assert "quota" in str(exc_info.value).lower()
        assert "console.cloud.google.com" in str(exc_info.value)

    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    def test_invalid_key_error_includes_helpful_message(self, mock_configure, mock_model_class):
        """Provider should include helpful message for invalid key errors."""
        # Arrange
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("invalid key provided")
        mock_model_class.return_value = mock_model

        provider = GoogleProvider(api_key='AIzaSy-test-key')

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            provider.generate(prompt='Test')
        assert "invalid" in str(exc_info.value).lower()
