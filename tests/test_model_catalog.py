"""
Tests for ModelCatalog domain logic.

Test-first development: Write one test at a time, make it pass, refactor.
"""
import pytest
from src.prompt_manager.domain.model_catalog import ModelCatalog


class TestModelCatalogOllamaModels:
    """Test Ollama models in the catalog."""

    def test_get_ollama_models_returns_list(self):
        """Should return a list of Ollama model dictionaries."""
        # Act
        models = ModelCatalog.get_ollama_models()

        # Assert
        assert isinstance(models, list)
        assert len(models) > 0

    def test_ollama_models_have_required_fields(self):
        """Each Ollama model should have id, name, size_gb, and description."""
        # Act
        models = ModelCatalog.get_ollama_models()

        # Assert
        for model in models:
            assert 'id' in model, f"Model missing 'id': {model}"
            assert 'name' in model, f"Model missing 'name': {model}"
            assert 'size_gb' in model, f"Model missing 'size_gb': {model}"
            assert 'description' in model, f"Model missing 'description': {model}"

    def test_ollama_models_include_lightweight_options(self):
        """Should include at least one lightweight model (under 5GB)."""
        # Act
        models = ModelCatalog.get_ollama_models()

        # Assert
        lightweight = [m for m in models if m['size_gb'] < 5]
        assert len(lightweight) > 0, "Should have at least one lightweight model"

    def test_get_models_for_provider_returns_ollama_models(self):
        """get_models_for_provider('ollama') should return Ollama models."""
        # Act
        models = ModelCatalog.get_models_for_provider('ollama')

        # Assert
        assert len(models) > 0
        assert all('id' in m for m in models)

    def test_get_ollama_model_by_id(self):
        """Should be able to look up Ollama model by id."""
        # Arrange
        models = ModelCatalog.get_ollama_models()
        first_model_id = models[0]['id']

        # Act
        model = ModelCatalog.get_model_by_id('ollama', first_model_id)

        # Assert
        assert model is not None
        assert model['id'] == first_model_id


class TestModelCatalogExistingProviders:
    """Ensure existing provider methods still work."""

    def test_get_openai_models_still_works(self):
        """OpenAI models should still be retrievable."""
        models = ModelCatalog.get_openai_models()
        assert len(models) > 0

    def test_get_anthropic_models_still_works(self):
        """Anthropic models should still be retrievable."""
        models = ModelCatalog.get_anthropic_models()
        assert len(models) > 0

    def test_get_google_models_still_works(self):
        """Google models should still be retrievable."""
        models = ModelCatalog.get_google_models()
        assert len(models) > 0
