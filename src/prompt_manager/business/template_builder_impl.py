"""
Template Builder Implementation

Concrete implementation of the template builder interface using existing code.
This refactors existing functionality to work with the new interface.
"""

from typing import List, Dict, Any, Optional
from .template_builder_interface import TemplateBuilderInterface, UIComponentInterface, TemplateStorageInterface
from .template_parser import TemplateParser


class ComboBoxComponent(UIComponentInterface):
    """Concrete implementation of a combo box UI component."""
    
    def __init__(self, tag: str, index: int, enabled: bool = False):
        self.tag = tag
        self.index = index
        self.enabled = enabled
        self.value = ""
        self.options = []
        self.is_custom = False
    
    def get_component_type(self) -> str:
        return "combo_box"
    
    def get_component_config(self) -> Dict[str, Any]:
        return {
            "tag": self.tag,
            "index": self.index,
            "enabled": self.enabled,
            "value": self.value,
            "options": self.options,
            "is_custom": self.is_custom
        }
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled


class TemplateBuilderImpl(TemplateBuilderInterface):
    """Concrete implementation of template builder using existing TemplateParser."""
    
    def __init__(self):
        self.parser = TemplateParser()
    
    def parse_template(self, template: str) -> List[str]:
        """Parse a template string and extract variable names."""
        return self.parser.extract_tags(template)
    
    def generate_ui_components(self, template: str) -> List[Dict[str, Any]]:
        """Generate UI components from a template."""
        return self.parser.generate_combo_boxes(template)
    
    def update_cascading_state(self, components: List[Dict[str, Any]], 
                             changed_index: int) -> List[Dict[str, Any]]:
        """Update cascading state when a component changes."""
        return self.parser.update_cascading_selections(components, changed_index)
    
    def generate_final_prompt(self, template: str, 
                            components: List[Dict[str, Any]]) -> str:
        """Generate final prompt from template and component selections."""
        return self.parser.generate_prompt_from_selections(template, components)


class SimpleTemplateStorage(TemplateStorageInterface):
    """Simple in-memory template storage implementation."""
    
    def __init__(self):
        self.templates: Dict[str, str] = {}
    
    def save_template(self, name: str, template: str) -> bool:
        """Save a template with the given name."""
        self.templates[name] = template
        return True
    
    def load_template(self, name: str) -> Optional[str]:
        """Load a template by name."""
        return self.templates.get(name)
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())
    
    def delete_template(self, name: str) -> bool:
        """Delete a template by name."""
        if name in self.templates:
            del self.templates[name]
            return True
        return False
