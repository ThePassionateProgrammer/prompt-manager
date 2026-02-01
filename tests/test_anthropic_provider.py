"""
Tests for AnthropicProvider service.

Test-first development: Write one test at a time, make it pass, refactor.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.prompt_manager.business.anthropic_provider import AnthropicProvider


class TestAnthropicProviderInitialization:
    """Test AnthropicProvider initialization and configuration."""

    def test_provider_name_is_anthropic(self):
        """Provider should identify itself as 'anthropic'."""
        # Arrange & Act
        provider = AnthropicProvider(api_key='test-key')

        # Assert
        assert provider.name == "anthropic"

    def test_stores_api_key_when_provided(self):
        """Provider should store provided API key."""
        # Arrange & Act
        provider = AnthropicProvider(api_key='sk-ant-test-key')

        # Assert
        assert provider.api_key == 'sk-ant-test-key'

    def test_initializes_without_api_key(self):
        """Provider should initialize without API key (deferred loading)."""
        # Arrange & Act
        provider = AnthropicProvider()

        # Assert
        assert provider.api_key is None
        assert provider._initialized is False


class TestAnthropicProviderAvailability:
    """Test Anthropic API availability checks."""

    def test_is_available_when_api_key_provided(self):
        """Provider should be available when API key is provided."""
        # Arrange
        provider = AnthropicProvider(api_key='sk-ant-test-key')

        # Act
        available = provider.is_available()

        # Assert
        assert available is True

    @patch('src.prompt_manager.business.key_loader.load_anthropic_api_key')
    def test_is_not_available_when_no_api_key(self, mock_load_key):
        """Provider should be unavailable when no API key is available."""
        # Arrange
        mock_load_key.side_effect = ValueError("Key not found")
        provider = AnthropicProvider()

        # Act
        available = provider.is_available()

        # Assert
        assert available is False


class TestAnthropicProviderGeneration:
    """Test text generation with Anthropic Claude."""

    @patch('anthropic.Anthropic')
    def test_generate_with_messages(self, mock_anthropic_class):
        """Provider should generate text from messages array."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text='Hello! How can I help you?')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        provider = AnthropicProvider(api_key='sk-ant-test-key')
        messages = [{'role': 'user', 'content': 'Hello'}]

        # Act
        response = provider.generate(messages=messages)

        # Assert
        assert response == 'Hello! How can I help you?'
        mock_client.messages.create.assert_called_once()

    @patch('anthropic.Anthropic')
    def test_generate_with_prompt_string(self, mock_anthropic_class):
        """Provider should generate text from simple prompt string (legacy)."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text='Paris is the capital of France.')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        provider = AnthropicProvider(api_key='sk-ant-test-key')

        # Act
        response = provider.generate(prompt='What is the capital of France?')

        # Assert
        assert response == 'Paris is the capital of France.'

    @patch('anthropic.Anthropic')
    def test_generate_extracts_system_prompt(self, mock_anthropic_class):
        """Provider should extract system prompt and pass separately to API."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text='Response')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        provider = AnthropicProvider(api_key='sk-ant-test-key')
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Hello'}
        ]

        # Act
        provider.generate(messages=messages)

        # Assert - system prompt should be passed separately
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['system'] == 'You are a helpful assistant.'
        # Messages should not contain system message
        assert all(msg.get('role') != 'system' for msg in call_kwargs['messages'])

    @patch('anthropic.Anthropic')
    def test_generate_with_custom_model(self, mock_anthropic_class):
        """Provider should use custom model when specified."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text='Response')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        provider = AnthropicProvider(api_key='sk-ant-test-key')

        # Act
        provider.generate(prompt='Test', model='claude-3-opus-20240229')

        # Assert
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['model'] == 'claude-3-opus-20240229'

    @patch('anthropic.Anthropic')
    def test_generate_caps_temperature_at_one(self, mock_anthropic_class):
        """Provider should cap temperature at 1.0 (Anthropic's max)."""
        # Arrange
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock(text='Response')]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client

        provider = AnthropicProvider(api_key='sk-ant-test-key')

        # Act - pass temperature > 1.0 (OpenAI allows up to 2.0)
        provider.generate(prompt='Test', temperature=1.5)

        # Assert - should be capped at 1.0
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs['temperature'] == 1.0


class TestAnthropicProviderErrorHandling:
    """Test error handling for Anthropic API errors."""

    @patch('anthropic.Anthropic')
    def test_raises_error_when_no_prompt_or_messages(self, mock_anthropic_class):
        """Provider should raise error when neither prompt nor messages provided."""
        # Arrange
        mock_anthropic_class.return_value = Mock()
        provider = AnthropicProvider(api_key='sk-ant-test-key')

        # Act & Assert - ValueError is caught and wrapped in RuntimeError
        with pytest.raises(RuntimeError, match="Either prompt or messages must be provided"):
            provider.generate()

    @patch('anthropic.Anthropic')
    def test_billing_error_includes_helpful_message(self, mock_anthropic_class):
        """Provider should include helpful message for billing errors."""
        # Arrange
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("credit balance is too low")
        mock_anthropic_class.return_value = mock_client

        provider = AnthropicProvider(api_key='sk-ant-test-key')

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            provider.generate(prompt='Test')
        assert "billing" in str(exc_info.value).lower()
        assert "console.anthropic.com" in str(exc_info.value)

    @patch('anthropic.Anthropic')
    def test_auth_error_includes_helpful_message(self, mock_anthropic_class):
        """Provider should include helpful message for authentication errors."""
        # Arrange
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("invalid api_key")
        mock_anthropic_class.return_value = mock_client

        provider = AnthropicProvider(api_key='sk-ant-test-key')

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            provider.generate(prompt='Test')
        assert "authentication" in str(exc_info.value).lower()
