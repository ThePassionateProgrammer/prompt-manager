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
        # Real relationship data from our custom combo box system
        self.relationships_data = {
            "Manager": {
                "Review Status": ["Evaluate Next Actions", "Review Performance"],
                "File Compliance Report": ["Keep Higher-ups Informed", "Meet Standards"]
            },
            "Programmer": {
                "Code Review": ["Keep Code Clean", "Propagate Good Practices"],
                "Test Plan": ["Ensure Quality", "Prevent Bugs"]
            },
            "Fitness Coach": {
                "Create Client Meal Plan": ["Improve Health", "Achieve Goals"],
                "Work Out": ["Build Strength", "Increase Endurance"]
            }
        }
    
    def parse_template(self, template: str) -> List[str]:
        """Parse a template string and extract variable names."""
        return self.parser.extract_tags(template)
    
    def generate_ui_components(self, template: str) -> List[Dict[str, Any]]:
        """Generate UI components from a template."""
        return self.parser.generate_combo_boxes(template)
    
    def update_cascading_state(self, components: List[Dict[str, Any]], 
                             changed_index: int) -> List[Dict[str, Any]]:
        """Update cascading state when a component changes."""
        # First, do the basic cascading update
        updated_components = self.parser.update_cascading_selections(components, changed_index)
        
        # Then, populate options based on real relationship data
        if changed_index == 0 and len(updated_components) > 1:
            # First component changed, populate second component options
            role_value = updated_components[0].get("value", "")
            if role_value in self.relationships_data:
                updated_components[1]["options"] = list(self.relationships_data[role_value].keys())
        
        elif changed_index == 1 and len(updated_components) > 2:
            # Second component changed, populate third component options
            role_value = updated_components[0].get("value", "")
            what_value = updated_components[1].get("value", "")
            if (role_value in self.relationships_data and 
                what_value in self.relationships_data[role_value]):
                updated_components[2]["options"] = self.relationships_data[role_value][what_value]
        
        return updated_components
    
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
