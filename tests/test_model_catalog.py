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


class TestModelCatalogOllamaFiltering:
    """Test Ollama model filtering functionality."""

    def test_ollama_models_have_category_field(self):
        """Each Ollama model should have a category field."""
        # Act
        models = ModelCatalog.get_ollama_models()

        # Assert
        for model in models:
            assert 'category' in model, f"Model missing 'category': {model['name']}"
            assert model['category'] in ['general', 'code', 'multilingual', 'reasoning'], \
                f"Invalid category: {model['category']}"

    def test_filter_by_max_size(self):
        """Should filter models by maximum size in GB."""
        # Act
        small_models = ModelCatalog.get_ollama_models(max_size_gb=3)

        # Assert
        assert len(small_models) > 0, "Should have some small models"
        for model in small_models:
            assert model['size_gb'] <= 3, f"Model {model['name']} exceeds 3GB"

    def test_filter_by_category(self):
        """Should filter models by category."""
        # Act
        code_models = ModelCatalog.get_ollama_models(category='code')

        # Assert
        assert len(code_models) > 0, "Should have some code models"
        for model in code_models:
            assert model['category'] == 'code', f"Model {model['name']} is not a code model"

    def test_filter_by_size_and_category(self):
        """Should filter by both size and category."""
        # Act
        small_code_models = ModelCatalog.get_ollama_models(max_size_gb=5, category='code')

        # Assert
        for model in small_code_models:
            assert model['size_gb'] <= 5
            assert model['category'] == 'code'

    def test_filter_returns_empty_for_no_matches(self):
        """Should return empty list when no models match filters."""
        # Act - filter for very small code models (unlikely to exist)
        models = ModelCatalog.get_ollama_models(max_size_gb=0.1, category='code')

        # Assert
        assert models == []

    def test_size_tiers_defined(self):
        """Should have size tier thresholds defined."""
        # Assert
        assert hasattr(ModelCatalog, 'SIZE_TIERS')
        assert 'small' in ModelCatalog.SIZE_TIERS
        assert 'medium' in ModelCatalog.SIZE_TIERS
        assert 'large' in ModelCatalog.SIZE_TIERS

    def test_get_models_by_size_tier(self):
        """Should get models by size tier name."""
        # Act
        small_models = ModelCatalog.get_ollama_models_by_tier('small')

        # Assert
        assert len(small_models) > 0
        for model in small_models:
            assert model['size_gb'] < ModelCatalog.SIZE_TIERS['small']


class TestModelCatalogBrowseView:
    """Test enriching catalog models with installed status for browser UI."""

    def test_enrich_marks_installed_models(self):
        """Installed models should be marked with installed=True."""
        # Arrange
        catalog_models = [
            {'id': 'gemma3:4b', 'name': 'Gemma 3 (4B)', 'size_gb': 3.3,
             'category': 'general', 'description': 'Fast and efficient.'},
            {'id': 'llama3:8b', 'name': 'Llama 3 (8B)', 'size_gb': 4.7,
             'category': 'general', 'description': 'Great for most tasks.'},
        ]
        installed_ids = {'gemma3:4b'}

        # Act
        result = ModelCatalog.enrich_with_installed_status(catalog_models, installed_ids)

        # Assert
        assert result[0]['installed'] is True
        assert result[1]['installed'] is False

    def test_enrich_preserves_all_catalog_fields(self):
        """Enrichment should not lose any original catalog fields."""
        # Arrange
        catalog_models = [
            {'id': 'gemma3:4b', 'name': 'Gemma 3 (4B)', 'size_gb': 3.3,
             'category': 'general', 'description': 'Fast and efficient.'},
        ]

        # Act
        result = ModelCatalog.enrich_with_installed_status(catalog_models, set())

        # Assert
        model = result[0]
        assert model['id'] == 'gemma3:4b'
        assert model['name'] == 'Gemma 3 (4B)'
        assert model['size_gb'] == 3.3
        assert model['category'] == 'general'
        assert model['description'] == 'Fast and efficient.'

    def test_enrich_with_empty_catalog(self):
        """Should return empty list for empty catalog."""
        result = ModelCatalog.enrich_with_installed_status([], {'gemma3:4b'})
        assert result == []

    def test_enrich_with_no_installed_models(self):
        """All models should be marked not installed when none are downloaded."""
        catalog_models = ModelCatalog.get_ollama_models()

        result = ModelCatalog.enrich_with_installed_status(catalog_models, set())

        assert all(m['installed'] is False for m in result)

    def test_enrich_does_not_mutate_original(self):
        """Enrichment should not modify the original catalog models."""
        catalog_models = [
            {'id': 'gemma3:4b', 'name': 'Gemma 3 (4B)', 'size_gb': 3.3,
             'category': 'general', 'description': 'Fast.'},
        ]

        ModelCatalog.enrich_with_installed_status(catalog_models, {'gemma3:4b'})

        assert 'installed' not in catalog_models[0]

    def test_enrich_adds_size_tier(self):
        """Enriched models should include their size tier."""
        catalog_models = [
            {'id': 'tinyllama', 'name': 'TinyLlama', 'size_gb': 0.6,
             'category': 'general', 'description': 'Tiny.'},
            {'id': 'gemma3:4b', 'name': 'Gemma 3', 'size_gb': 3.3,
             'category': 'general', 'description': 'Medium.'},
            {'id': 'llama3:70b', 'name': 'Llama 3 70B', 'size_gb': 39.0,
             'category': 'general', 'description': 'Large.'},
        ]

        result = ModelCatalog.enrich_with_installed_status(catalog_models, set())

        assert result[0]['size_tier'] == 'small'
        assert result[1]['size_tier'] == 'medium'
        assert result[2]['size_tier'] == 'large'


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
