"""
Template Builder Interface

Defines the contract for template builders, making the system open for extension.
This follows the Open-Closed Principle - open for extension, closed for modification.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class TemplateBuilderInterface(ABC):
    """Abstract interface for template builders."""
    
    @abstractmethod
    def parse_template(self, template: str) -> List[str]:
        """Parse a template string and extract variable names."""
        pass
    
    @abstractmethod
    def generate_ui_components(self, template: str) -> List[Dict[str, Any]]:
        """Generate UI components from a template."""
        pass
    
    @abstractmethod
    def update_cascading_state(self, components: List[Dict[str, Any]], 
                             changed_index: int) -> List[Dict[str, Any]]:
        """Update cascading state when a component changes."""
        pass
    
    @abstractmethod
    def generate_final_prompt(self, template: str, 
                            components: List[Dict[str, Any]]) -> str:
        """Generate final prompt from template and component selections."""
        pass


class UIComponentInterface(ABC):
    """Abstract interface for UI components."""
    
    @abstractmethod
    def get_component_type(self) -> str:
        """Get the type of this UI component."""
        pass
    
    @abstractmethod
    def get_component_config(self) -> Dict[str, Any]:
        """Get the configuration for this component."""
        pass
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if this component is enabled."""
        pass
    
    @abstractmethod
    def set_enabled(self, enabled: bool):
        """Set whether this component is enabled."""
        pass


class TemplateStorageInterface(ABC):
    """Abstract interface for template storage."""
    
    @abstractmethod
    def save_template(self, name: str, template: str) -> bool:
        """Save a template with the given name."""
        pass
    
    @abstractmethod
    def load_template(self, name: str) -> Optional[str]:
        """Load a template by name."""
        pass
    
    @abstractmethod
    def list_templates(self) -> List[str]:
        """List all available template names."""
        pass
    
    @abstractmethod
    def delete_template(self, name: str) -> bool:
        """Delete a template by name."""
        pass
