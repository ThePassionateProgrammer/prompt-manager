"""
UI Component Factory

Factory for creating different types of UI components.
This makes the system open for extension with new component types.
"""

from typing import Dict, Any, List
from .template_builder_interface import UIComponentInterface
from .template_builder_impl import ComboBoxComponent


class UIComponentFactory:
    """Factory for creating UI components."""
    
    def __init__(self):
        self._component_types = {
            "combo_box": self._create_combo_box,
            "text_input": self._create_text_input,
            "dropdown": self._create_dropdown,
            "checkbox": self._create_checkbox
        }
    
    def create_component(self, component_type: str, **kwargs) -> UIComponentInterface:
        """Create a UI component of the specified type."""
        if component_type not in self._component_types:
            raise ValueError(f"Unknown component type: {component_type}")
        
        return self._component_types[component_type](**kwargs)
    
    def register_component_type(self, component_type: str, factory_method):
        """Register a new component type with its factory method."""
        self._component_types[component_type] = factory_method
    
    def get_available_component_types(self) -> List[str]:
        """Get list of available component types."""
        return list(self._component_types.keys())
    
    def _create_combo_box(self, **kwargs) -> ComboBoxComponent:
        """Create a combo box component."""
        tag = kwargs.get("tag", "")
        index = kwargs.get("index", 0)
        enabled = kwargs.get("enabled", False)
        return ComboBoxComponent(tag, index, enabled)
    
    def _create_text_input(self, **kwargs) -> UIComponentInterface:
        """Create a text input component."""
        # Placeholder for future implementation
        raise NotImplementedError("Text input components not yet implemented")
    
    def _create_dropdown(self, **kwargs) -> UIComponentInterface:
        """Create a dropdown component."""
        # Placeholder for future implementation
        raise NotImplementedError("Dropdown components not yet implemented")
    
    def _create_checkbox(self, **kwargs) -> UIComponentInterface:
        """Create a checkbox component."""
        # Placeholder for future implementation
        raise NotImplementedError("Checkbox components not yet implemented")


class ComponentConfiguration:
    """Configuration for UI components."""
    
    def __init__(self, component_type: str, config: Dict[str, Any]):
        self.component_type = component_type
        self.config = config
    
    def get(self, key: str, default=None):
        """Get a configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set a configuration value."""
        self.config[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "component_type": self.component_type,
            "config": self.config
        }
