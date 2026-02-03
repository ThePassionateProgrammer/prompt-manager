"""
Provider Factory - Centralizes LLM provider instantiation.

Single Responsibility: Create provider instances based on name.
This eliminates duplicated provider creation logic across the codebase.
"""
from typing import Optional, List

from src.prompt_manager.business.llm_provider import OpenAIProvider
from src.prompt_manager.business.anthropic_provider import AnthropicProvider
from src.prompt_manager.business.google_provider import GoogleProvider
from src.prompt_manager.business.ollama_provider import OllamaProvider


class ProviderFactory:
    """Factory for creating LLM provider instances.

    Centralizes provider instantiation logic that was previously duplicated
    in dashboard.py (_initialize_providers, add_provider) and model_catalog.py.
    """

    # Provider registry: name -> (class, requires_api_key)
    _PROVIDERS = {
        'openai': (OpenAIProvider, True),
        'anthropic': (AnthropicProvider, True),
        'google': (GoogleProvider, True),
        'ollama': (OllamaProvider, False),
    }

    @classmethod
    def create(cls, provider_name: str, api_key: Optional[str] = None):
        """Create a provider instance.

        Args:
            provider_name: Name of the provider (case-insensitive)
            api_key: API key (required for cloud providers)

        Returns:
            Provider instance

        Raises:
            ValueError: If provider is not supported
        """
        name_lower = provider_name.lower()

        if name_lower not in cls._PROVIDERS:
            supported = ', '.join(cls._PROVIDERS.keys())
            raise ValueError(
                f"Provider '{provider_name}' is not supported. "
                f"Supported providers: {supported}"
            )

        provider_class, requires_key = cls._PROVIDERS[name_lower]

        if requires_key:
            return provider_class(api_key=api_key)
        else:
            return provider_class()

    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """Get list of supported provider names."""
        return list(cls._PROVIDERS.keys())

    @classmethod
    def requires_api_key(cls, provider_name: str) -> bool:
        """Check if a provider requires an API key.

        Args:
            provider_name: Name of the provider (case-insensitive)

        Returns:
            True if provider requires API key, False otherwise
        """
        name_lower = provider_name.lower()

        if name_lower not in cls._PROVIDERS:
            return True  # Default to requiring key for unknown providers

        _, requires_key = cls._PROVIDERS[name_lower]
        return requires_key
