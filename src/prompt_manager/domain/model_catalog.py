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

    # Google Gemini models catalog (use models/ prefix for API)
    GOOGLE_MODELS = [
        {'id': 'models/gemini-2.5-flash', 'name': 'Gemini 2.5 Flash', 'context_window': 1000000},
        {'id': 'models/gemini-2.5-pro', 'name': 'Gemini 2.5 Pro', 'context_window': 1000000},
        {'id': 'models/gemini-2.0-flash', 'name': 'Gemini 2.0 Flash', 'context_window': 1000000},
        {'id': 'models/gemini-2.0-flash-lite', 'name': 'Gemini 2.0 Flash Lite', 'context_window': 1000000},
    ]

    # Ollama local models catalog (popular models available for download)
    OLLAMA_MODELS = [
        {
            'id': 'gemma3:4b',
            'name': 'Gemma 3 (4B)',
            'size_gb': 3.3,
            'description': 'Google\'s lightweight model. Fast and efficient for general tasks.',
        },
        {
            'id': 'llama3.2:3b',
            'name': 'Llama 3.2 (3B)',
            'size_gb': 2.0,
            'description': 'Meta\'s compact model. Good balance of speed and capability.',
        },
        {
            'id': 'phi3:mini',
            'name': 'Phi-3 Mini',
            'size_gb': 2.2,
            'description': 'Microsoft\'s small model. Excellent for coding and reasoning.',
        },
        {
            'id': 'mistral:7b',
            'name': 'Mistral (7B)',
            'size_gb': 4.1,
            'description': 'Mistral AI\'s flagship. Strong general performance.',
        },
        {
            'id': 'llama3:8b',
            'name': 'Llama 3 (8B)',
            'size_gb': 4.7,
            'description': 'Meta\'s popular model. Great for most tasks.',
        },
        {
            'id': 'codellama:7b',
            'name': 'Code Llama (7B)',
            'size_gb': 3.8,
            'description': 'Specialized for code generation and understanding.',
        },
        {
            'id': 'deepseek-coder:6.7b',
            'name': 'DeepSeek Coder (6.7B)',
            'size_gb': 3.8,
            'description': 'Optimized for programming tasks and code completion.',
        },
        {
            'id': 'qwen2:7b',
            'name': 'Qwen 2 (7B)',
            'size_gb': 4.4,
            'description': 'Alibaba\'s multilingual model. Strong in multiple languages.',
        },
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
    def get_ollama_models(cls) -> List[Dict]:
        """Get list of available Ollama models for download.

        Returns:
            List of model dictionaries with id, name, size_gb, description
        """
        return [m.copy() for m in cls.OLLAMA_MODELS]

    @classmethod
    def get_models_for_provider(cls, provider: str) -> List[Dict]:
        """Get models for any provider by name.

        Args:
            provider: Provider name (openai, anthropic, google, ollama)

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
        elif provider_lower == 'ollama':
            return cls.get_ollama_models()
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
