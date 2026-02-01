"""
Model catalog domain logic.

Defines available models for each provider.
Pure business logic with zero dependencies.
"""
from typing import List, Dict


class ModelCatalog:
    """Catalog of available models for each provider.

    This is pure domain knowledge - what models exist for each provider.
    No infrastructure dependencies.
    """

    # OpenAI models catalog (static, well-known)
    OPENAI_MODELS = [
        {'id': 'gpt-4', 'name': 'GPT-4', 'context_window': 8192},
        {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo', 'context_window': 128000},
        {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'context_window': 4096},
        {'id': 'gpt-3.5-turbo-16k', 'name': 'GPT-3.5 Turbo 16K', 'context_window': 16384},
    ]

    # Anthropic Claude models catalog
    ANTHROPIC_MODELS = [
        {'id': 'claude-opus-4-20250514', 'name': 'Claude Opus 4', 'context_window': 200000},
        {'id': 'claude-sonnet-4-20250514', 'name': 'Claude Sonnet 4', 'context_window': 200000},
        {'id': 'claude-3-5-sonnet-20241022', 'name': 'Claude 3.5 Sonnet', 'context_window': 200000},
        {'id': 'claude-3-5-haiku-20241022', 'name': 'Claude 3.5 Haiku', 'context_window': 200000},
        {'id': 'claude-3-opus-20240229', 'name': 'Claude 3 Opus', 'context_window': 200000},
    ]

    # Google Gemini models catalog
    GOOGLE_MODELS = [
        {'id': 'gemini-2.0-flash', 'name': 'Gemini 2.0 Flash', 'context_window': 1000000},
        {'id': 'gemini-1.5-pro', 'name': 'Gemini 1.5 Pro', 'context_window': 2000000},
        {'id': 'gemini-1.5-flash', 'name': 'Gemini 1.5 Flash', 'context_window': 1000000},
        {'id': 'gemini-1.5-flash-8b', 'name': 'Gemini 1.5 Flash-8B', 'context_window': 1000000},
    ]

    @classmethod
    def get_openai_models(cls) -> List[Dict]:
        """Get list of available OpenAI models.

        Returns:
            List of model dictionaries with id, name, context_window
        """
        return cls.OPENAI_MODELS.copy()

    @classmethod
    def get_anthropic_models(cls) -> List[Dict]:
        """Get list of available Anthropic Claude models.

        Returns:
            List of model dictionaries with id, name, context_window
        """
        return cls.ANTHROPIC_MODELS.copy()

    @classmethod
    def get_google_models(cls) -> List[Dict]:
        """Get list of available Google Gemini models.

        Returns:
            List of model dictionaries with id, name, context_window
        """
        return cls.GOOGLE_MODELS.copy()

    @classmethod
    def get_models_for_provider(cls, provider: str) -> List[Dict]:
        """Get models for any provider by name.

        Args:
            provider: Provider name (openai, anthropic, google)

        Returns:
            List of model dictionaries for the provider
        """
        provider_lower = provider.lower()
        if provider_lower == 'openai':
            return cls.get_openai_models()
        elif provider_lower == 'anthropic':
            return cls.get_anthropic_models()
        elif provider_lower == 'google':
            return cls.get_google_models()
        return []

    @classmethod
    def get_model_by_id(cls, provider: str, model_id: str) -> Dict | None:
        """Get model details by provider and model ID.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic', 'google')
            model_id: Model identifier

        Returns:
            Model dictionary or None if not found
        """
        models = cls.get_models_for_provider(provider)
        for model in models:
            if model['id'] == model_id:
                return model.copy()
        return None
