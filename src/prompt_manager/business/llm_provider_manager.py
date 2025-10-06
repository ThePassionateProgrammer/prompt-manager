"""
LLM Provider Manager - Central management for all LLM providers.
"""

from typing import Dict, List, Optional
from .llm_provider import LLMProvider


class LLMProviderManager:
    """Manages LLM providers and handles provider selection and text generation."""
    
    def __init__(self):
        """Initialize the provider manager."""
        self.providers: Dict[str, LLMProvider] = {}
        self.default_provider: Optional[str] = None
    
    def add_provider(self, name: str, provider: LLMProvider) -> None:
        """Add a provider to the manager."""
        self.providers[name] = provider
    
    def get_provider(self, name: str) -> Optional[LLMProvider]:
        """Get a provider by name."""
        return self.providers.get(name)
    
    def list_available_providers(self) -> List[LLMProvider]:
        """List all available providers."""
        return [provider for provider in self.providers.values() if provider.is_available()]
    
    def set_default_provider(self, name: str) -> None:
        """Set the default provider."""
        if name not in self.providers:
            raise ValueError(f"Provider '{name}' not found")
        self.default_provider = name
    
    def remove_provider(self, name: str) -> None:
        """Remove a provider from the manager."""
        if name in self.providers:
            del self.providers[name]
            if self.default_provider == name:
                self.default_provider = None
    
    def generate(self, prompt: str, provider_name: Optional[str] = None) -> str:
        """Generate text using a provider."""
        if provider_name:
            provider = self.get_provider(provider_name)
            if not provider:
                raise ValueError(f"Provider '{provider_name}' not found")
        else:
            if not self.default_provider:
                raise ValueError("No default provider set")
            provider = self.get_provider(self.default_provider)
        
        return provider.generate(prompt)
