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
