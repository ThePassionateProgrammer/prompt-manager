"""
Test suite for LLMProviderManager - Core LLM provider management functionality.
"""

import pytest
from unittest.mock import Mock, patch
from src.prompt_manager.business.llm_provider_manager import LLMProviderManager
from src.prompt_manager.business.llm_provider import LLMProvider, OpenAIProvider


class TestLLMProviderManager:
    """Test the LLMProviderManager business logic."""
    
    def test_can_create_provider_manager(self):
        """Test that we can create a new LLMProviderManager."""
        # Given/When
        manager = LLMProviderManager()
        
        # Then
        assert manager is not None
        assert manager.providers == {}
        assert manager.default_provider is None
    
    def test_can_add_provider(self):
        """Test that we can add an LLM provider to the manager."""
        # Given
        manager = LLMProviderManager()
        provider = Mock(spec=LLMProvider)
        provider.name = "test_provider"
        
        # When
        manager.add_provider("test_provider", provider)
        
        # Then
        assert "test_provider" in manager.providers
        assert manager.providers["test_provider"] == provider
    
    def test_can_get_provider_by_name(self):
        """Test that we can retrieve a provider by name."""
        # Given
        manager = LLMProviderManager()
        provider = Mock(spec=LLMProvider)
        provider.name = "test_provider"
        manager.add_provider("test_provider", provider)
        
        # When
        retrieved_provider = manager.get_provider("test_provider")
        
        # Then
        assert retrieved_provider == provider
        assert retrieved_provider.name == "test_provider"
    
    def test_get_provider_returns_none_for_unknown_provider(self):
        """Test that getting an unknown provider returns None."""
        # Given
        manager = LLMProviderManager()
        
        # When
        provider = manager.get_provider("unknown_provider")
        
        # Then
        assert provider is None
    
    def test_can_list_available_providers(self):
        """Test that we can list all available providers."""
        # Given
        manager = LLMProviderManager()
        provider1 = Mock(spec=LLMProvider)
        provider1.name = "provider1"
        provider1.is_available.return_value = True
        
        provider2 = Mock(spec=LLMProvider)
        provider2.name = "provider2"
        provider2.is_available.return_value = False
        
        manager.add_provider("provider1", provider1)
        manager.add_provider("provider2", provider2)
        
        # When
        available_providers = manager.list_available_providers()
        
        # Then
        assert len(available_providers) == 1
        assert available_providers[0].name == "provider1"
    
    def test_can_set_default_provider(self):
        """Test that we can set a default provider."""
        # Given
        manager = LLMProviderManager()
        provider = Mock(spec=LLMProvider)
        provider.name = "test_provider"
        manager.add_provider("test_provider", provider)
        
        # When
        manager.set_default_provider("test_provider")
        
        # Then
        assert manager.default_provider == "test_provider"
    
    def test_set_default_provider_validates_provider_exists(self):
        """Test that setting a default provider validates the provider exists."""
        # Given
        manager = LLMProviderManager()
        
        # When/Then
        with pytest.raises(ValueError, match="Provider 'unknown_provider' not found"):
            manager.set_default_provider("unknown_provider")
    
    def test_can_remove_provider(self):
        """Test that we can remove a provider from the manager."""
        # Given
        manager = LLMProviderManager()
        provider = Mock(spec=LLMProvider)
        provider.name = "test_provider"
        manager.add_provider("test_provider", provider)
        manager.set_default_provider("test_provider")
        
        # When
        manager.remove_provider("test_provider")
        
        # Then
        assert "test_provider" not in manager.providers
        assert manager.default_provider is None
    
    def test_remove_provider_clears_default_if_removing_default(self):
        """Test that removing the default provider clears the default setting."""
        # Given
        manager = LLMProviderManager()
        provider1 = Mock(spec=LLMProvider)
        provider1.name = "provider1"
        provider2 = Mock(spec=LLMProvider)
        provider2.name = "provider2"
        
        manager.add_provider("provider1", provider1)
        manager.add_provider("provider2", provider2)
        manager.set_default_provider("provider1")
        
        # When
        manager.remove_provider("provider1")
        
        # Then
        assert manager.default_provider is None
        assert "provider2" in manager.providers  # Other provider still exists
    
    def test_can_generate_with_default_provider(self):
        """Test that we can generate text using the default provider."""
        # Given
        manager = LLMProviderManager()
        provider = Mock(spec=LLMProvider)
        provider.name = "test_provider"
        provider.generate.return_value = "Test response"
        
        manager.add_provider("test_provider", provider)
        manager.set_default_provider("test_provider")
        
        # When
        response = manager.generate("Test prompt")
        
        # Then
        assert response == "Test response"
        provider.generate.assert_called_once_with("Test prompt")
    
    def test_generate_without_default_provider_raises_error(self):
        """Test that generating without a default provider raises an error."""
        # Given
        manager = LLMProviderManager()
        
        # When/Then
        with pytest.raises(ValueError, match="No default provider set"):
            manager.generate("Test prompt")
    
    def test_can_generate_with_specific_provider(self):
        """Test that we can generate text using a specific provider."""
        # Given
        manager = LLMProviderManager()
        provider1 = Mock(spec=LLMProvider)
        provider1.name = "provider1"
        provider1.generate.return_value = "Response from provider1"
        
        provider2 = Mock(spec=LLMProvider)
        provider2.name = "provider2"
        provider2.generate.return_value = "Response from provider2"
        
        manager.add_provider("provider1", provider1)
        manager.add_provider("provider2", provider2)
        
        # When
        response = manager.generate("Test prompt", provider_name="provider2")
        
        # Then
        assert response == "Response from provider2"
        provider2.generate.assert_called_once_with("Test prompt")
        provider1.generate.assert_not_called()
    
    def test_generate_with_unknown_specific_provider_raises_error(self):
        """Test that generating with an unknown specific provider raises an error."""
        # Given
        manager = LLMProviderManager()
        provider = Mock(spec=LLMProvider)
        provider.name = "test_provider"
        manager.add_provider("test_provider", provider)
        
        # When/Then
        with pytest.raises(ValueError, match="Provider 'unknown_provider' not found"):
            manager.generate("Test prompt", provider_name="unknown_provider")
