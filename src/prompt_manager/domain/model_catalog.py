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

    @classmethod
    def get_openai_models(cls) -> List[Dict]:
        """Get list of available OpenAI models.

        Returns:
            List of model dictionaries with id, name, context_window
        """
        return cls.OPENAI_MODELS.copy()

    @classmethod
    def get_model_by_id(cls, provider: str, model_id: str) -> Dict | None:
        """Get model details by provider and model ID.

        Args:
            provider: Provider name (e.g., 'openai')
            model_id: Model identifier

        Returns:
            Model dictionary or None if not found
        """
        if provider.lower() == 'openai':
            for model in cls.OPENAI_MODELS:
                if model['id'] == model_id:
                    return model.copy()
        return None
