"""
Tests for OllamaModel domain model.

Test-first development: Write one test at a time, make it pass, refactor.
"""
import pytest
from src.prompt_manager.domain.ollama_model import OllamaModel


class TestOllamaModelValidation:
    """Test model name validation rules."""

    def test_valid_model_name_with_tag(self):
        """Valid model name with tag should be accepted."""
        # Arrange & Act
        model = OllamaModel("gemma3:4b")

        # Assert
        assert model.name == "gemma3"
        assert model.tag == "4b"
        assert model.full_name == "gemma3:4b"

    def test_model_name_without_tag_defaults_to_latest(self):
        """Model name without tag should default to 'latest'."""
        # Arrange & Act
        model = OllamaModel("llama3")

        # Assert
        assert model.name == "llama3"
        assert model.tag == "latest"
        assert model.full_name == "llama3"

    def test_empty_model_name_raises_error(self):
        """Empty model name should raise ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            OllamaModel("")

    def test_whitespace_only_model_name_raises_error(self):
        """Whitespace-only model name should raise ValueError."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Model name cannot be empty"):
            OllamaModel("   ")


class TestOllamaModelSerialization:
    """Test model serialization for persistence."""

    def test_to_dict_with_tag(self):
        """Model with tag should serialize correctly."""
        # Arrange
        model = OllamaModel("gemma3:4b")

        # Act
        data = model.to_dict()

        # Assert
        assert data == {
            'name': 'gemma3',
            'tag': '4b',
            'full_name': 'gemma3:4b'
        }

    def test_from_dict_with_tag(self):
        """Model should deserialize correctly from dictionary."""
        # Arrange
        data = {
            'name': 'gemma3',
            'tag': '4b',
            'full_name': 'gemma3:4b'
        }

        # Act
        model = OllamaModel.from_dict(data)

        # Assert
        assert model.name == 'gemma3'
        assert model.tag == '4b'
        assert model.full_name == 'gemma3:4b'
