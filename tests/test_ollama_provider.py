"""
Tests for OllamaProvider service.

Test-first development: Write one test at a time, make it pass, refactor.
"""
import pytest
from unittest.mock import Mock, patch
from src.prompt_manager.business.ollama_provider import OllamaProvider


class TestOllamaProviderInitialization:
    """Test OllamaProvider initialization and configuration."""

    def test_provider_name_is_ollama(self):
        """Provider should identify itself as 'ollama'."""
        # Arrange & Act
        provider = OllamaProvider()

        # Assert
        assert provider.name == "ollama"
