"""
Model catalog domain logic.

Defines available models for each provider.
Pure business logic with zero dependencies.
"""
from typing import List, Dict, Set


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
    # Categories: general, code, multilingual, reasoning
    # Size tiers: small (<3GB), medium (3-6GB), large (>6GB)
    OLLAMA_MODELS = [
        # Small models (<3GB) - Great for laptops
        {
            'id': 'llama3.2:1b',
            'name': 'Llama 3.2 (1B)',
            'size_gb': 1.3,
            'category': 'general',
            'description': 'Ultra-compact. Perfect for low-resource environments.',
        },
        {
            'id': 'llama3.2:3b',
            'name': 'Llama 3.2 (3B)',
            'size_gb': 2.0,
            'category': 'general',
            'description': 'Meta\'s compact model. Good balance of speed and capability.',
        },
        {
            'id': 'phi3:mini',
            'name': 'Phi-3 Mini',
            'size_gb': 2.2,
            'category': 'reasoning',
            'description': 'Microsoft\'s small model. Excellent for coding and reasoning.',
        },
        {
            'id': 'qwen2:1.5b',
            'name': 'Qwen 2 (1.5B)',
            'size_gb': 1.1,
            'category': 'multilingual',
            'description': 'Alibaba\'s tiny multilingual model. Fast responses.',
        },
        {
            'id': 'tinyllama',
            'name': 'TinyLlama (1.1B)',
            'size_gb': 0.6,
            'category': 'general',
            'description': 'Extremely small. Good for testing and simple tasks.',
        },

        # Medium models (3-6GB) - Good for most computers
        {
            'id': 'gemma3:4b',
            'name': 'Gemma 3 (4B)',
            'size_gb': 3.3,
            'category': 'general',
            'description': 'Google\'s lightweight model. Fast and efficient for general tasks.',
        },
        {
            'id': 'mistral:7b',
            'name': 'Mistral (7B)',
            'size_gb': 4.1,
            'category': 'general',
            'description': 'Mistral AI\'s flagship. Strong general performance.',
        },
        {
            'id': 'llama3:8b',
            'name': 'Llama 3 (8B)',
            'size_gb': 4.7,
            'category': 'general',
            'description': 'Meta\'s popular model. Great for most tasks.',
        },
        {
            'id': 'codellama:7b',
            'name': 'Code Llama (7B)',
            'size_gb': 3.8,
            'category': 'code',
            'description': 'Specialized for code generation and understanding.',
        },
        {
            'id': 'deepseek-coder:6.7b',
            'name': 'DeepSeek Coder (6.7B)',
            'size_gb': 3.8,
            'category': 'code',
            'description': 'Optimized for programming tasks and code completion.',
        },
        {
            'id': 'qwen2:7b',
            'name': 'Qwen 2 (7B)',
            'size_gb': 4.4,
            'category': 'multilingual',
            'description': 'Alibaba\'s multilingual model. Strong in multiple languages.',
        },
        {
            'id': 'neural-chat:7b',
            'name': 'Neural Chat (7B)',
            'size_gb': 4.1,
            'category': 'general',
            'description': 'Intel\'s chat model. Optimized for dialogue.',
        },
        {
            'id': 'starling-lm:7b',
            'name': 'Starling LM (7B)',
            'size_gb': 4.1,
            'category': 'general',
            'description': 'Berkeley\'s RLHF model. Great for helpful responses.',
        },

        # Large models (>6GB) - For powerful machines
        {
            'id': 'llama3:70b',
            'name': 'Llama 3 (70B)',
            'size_gb': 39.0,
            'category': 'general',
            'description': 'Meta\'s largest open model. State-of-the-art performance.',
        },
        {
            'id': 'codellama:34b',
            'name': 'Code Llama (34B)',
            'size_gb': 19.0,
            'category': 'code',
            'description': 'Larger code model. Excellent for complex programming.',
        },
        {
            'id': 'mixtral:8x7b',
            'name': 'Mixtral 8x7B',
            'size_gb': 26.0,
            'category': 'general',
            'description': 'Mistral\'s MoE model. Excellent quality/speed balance.',
        },
        {
            'id': 'deepseek-coder:33b',
            'name': 'DeepSeek Coder (33B)',
            'size_gb': 19.0,
            'category': 'code',
            'description': 'Large coding model. Professional-grade code generation.',
        },
        {
            'id': 'qwen2:72b',
            'name': 'Qwen 2 (72B)',
            'size_gb': 41.0,
            'category': 'multilingual',
            'description': 'Alibaba\'s flagship. Exceptional multilingual capability.',
        },
    ]

    # Size tier thresholds (in GB)
    SIZE_TIERS = {
        'small': 3,     # < 3GB - runs on most laptops
        'medium': 6,    # 3-6GB - needs decent RAM (16GB+)
        'large': float('inf')  # > 6GB - needs 32GB+ RAM
    }

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
    def get_ollama_models(cls, max_size_gb: float = None, category: str = None) -> List[Dict]:
        """Get list of available Ollama models for download, with optional filtering.

        Args:
            max_size_gb: Maximum model size in GB (optional)
            category: Filter by category - 'general', 'code', 'multilingual', 'reasoning' (optional)

        Returns:
            List of model dictionaries with id, name, size_gb, description, category
        """
        models = [m.copy() for m in cls.OLLAMA_MODELS]

        if max_size_gb is not None:
            models = [m for m in models if m['size_gb'] <= max_size_gb]

        if category is not None:
            models = [m for m in models if m.get('category') == category]

        return models

    @classmethod
    def get_ollama_models_by_tier(cls, tier: str) -> List[Dict]:
        """Get Ollama models filtered by size tier.

        Args:
            tier: Size tier - 'small' (<3GB), 'medium' (3-6GB), 'large' (>6GB)

        Returns:
            List of model dictionaries matching the tier
        """
        if tier not in cls.SIZE_TIERS:
            return []

        threshold = cls.SIZE_TIERS[tier]

        if tier == 'small':
            return cls.get_ollama_models(max_size_gb=threshold)
        elif tier == 'medium':
            small_threshold = cls.SIZE_TIERS['small']
            models = cls.get_ollama_models()
            return [m for m in models if small_threshold <= m['size_gb'] < threshold]
        else:  # large
            medium_threshold = cls.SIZE_TIERS['medium']
            models = cls.get_ollama_models()
            return [m for m in models if m['size_gb'] >= medium_threshold]

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
    def _get_size_tier(cls, size_gb: float) -> str:
        """Determine size tier for a model based on its size in GB.

        Args:
            size_gb: Model size in gigabytes

        Returns:
            'small', 'medium', or 'large'
        """
        if size_gb < cls.SIZE_TIERS['small']:
            return 'small'
        elif size_gb < cls.SIZE_TIERS['medium']:
            return 'medium'
        else:
            return 'large'

    @classmethod
    def enrich_with_installed_status(
        cls, catalog_models: List[Dict], installed_ids: Set[str]
    ) -> List[Dict]:
        """Enrich catalog models with installed status and size tier.

        Pure domain logic: takes catalog data and installed model IDs,
        returns new list with 'installed' and 'size_tier' fields added.

        Args:
            catalog_models: List of catalog model dicts
            installed_ids: Set of installed model ID strings

        Returns:
            New list of enriched model dicts (originals not mutated)
        """
        enriched = []
        for model in catalog_models:
            enriched_model = model.copy()
            enriched_model['installed'] = model['id'] in installed_ids
            enriched_model['size_tier'] = cls._get_size_tier(model.get('size_gb', 0))
            enriched.append(enriched_model)
        return enriched

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
