"""
Tests for ProviderFactory - centralizes provider instantiation.

TDD: Tests verify the factory creates correct provider types.
"""
import pytest
from src.prompt_manager.business.provider_factory import ProviderFactory
from src.prompt_manager.business.llm_provider import OpenAIProvider
from src.prompt_manager.business.anthropic_provider import AnthropicProvider
from src.prompt_manager.business.google_provider import GoogleProvider
from src.prompt_manager.business.ollama_provider import OllamaProvider


class TestProviderFactory:
    """Test centralized provider creation."""

    def test_create_openai_provider(self):
        """Should create OpenAI provider with API key."""
        provider = ProviderFactory.create('openai', api_key='test-key')

        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == 'test-key'

    def test_create_anthropic_provider(self):
        """Should create Anthropic provider with API key."""
        provider = ProviderFactory.create('anthropic', api_key='test-key')

        assert isinstance(provider, AnthropicProvider)
        assert provider.api_key == 'test-key'

    def test_create_google_provider(self):
        """Should create Google provider with API key."""
        provider = ProviderFactory.create('google', api_key='test-key')

        assert isinstance(provider, GoogleProvider)
        assert provider.api_key == 'test-key'

    def test_create_ollama_provider(self):
        """Should create Ollama provider without API key."""
        provider = ProviderFactory.create('ollama')

        assert isinstance(provider, OllamaProvider)

    def test_case_insensitive_provider_name(self):
        """Should handle provider names case-insensitively."""
        provider_lower = ProviderFactory.create('openai', api_key='test-key')
        provider_upper = ProviderFactory.create('OPENAI', api_key='test-key')
        provider_mixed = ProviderFactory.create('OpenAI', api_key='test-key')

        assert isinstance(provider_lower, OpenAIProvider)
        assert isinstance(provider_upper, OpenAIProvider)
        assert isinstance(provider_mixed, OpenAIProvider)

    def test_unsupported_provider_raises_error(self):
        """Should raise ValueError for unsupported provider."""
        with pytest.raises(ValueError) as exc_info:
            ProviderFactory.create('unsupported_provider', api_key='test')

        assert 'not supported' in str(exc_info.value).lower()
        assert 'supported providers' in str(exc_info.value).lower()

    def test_get_supported_providers(self):
        """Should return list of supported providers."""
        supported = ProviderFactory.get_supported_providers()

        assert 'openai' in supported
        assert 'anthropic' in supported
        assert 'google' in supported
        assert 'ollama' in supported
        assert len(supported) == 4

    def test_requires_api_key_for_cloud_providers(self):
        """Cloud providers should require API keys."""
        assert ProviderFactory.requires_api_key('openai') is True
        assert ProviderFactory.requires_api_key('anthropic') is True
        assert ProviderFactory.requires_api_key('google') is True

    def test_ollama_does_not_require_api_key(self):
        """Ollama (local) should not require API key."""
        assert ProviderFactory.requires_api_key('ollama') is False

    def test_unknown_provider_defaults_to_requiring_key(self):
        """Unknown providers should default to requiring API key."""
        assert ProviderFactory.requires_api_key('unknown_provider') is True

    def test_provider_has_correct_name(self):
        """Created providers should have correct name property."""
        openai = ProviderFactory.create('openai', api_key='test')
        anthropic = ProviderFactory.create('anthropic', api_key='test')
        google = ProviderFactory.create('google', api_key='test')
        ollama = ProviderFactory.create('ollama')

        assert openai.name == 'openai'
        assert anthropic.name == 'anthropic'
        assert google.name == 'google'
        assert ollama.name == 'ollama'
