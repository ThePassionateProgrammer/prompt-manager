"""
Template Service

Handles template processing, dropdown generation, and custom combo box integration.
"""

import re
from typing import Dict, Any, List
from src.prompt_manager.business.custom_combo_box_integration import CustomComboBoxIntegration


class TemplateService:
    """Service for template processing and dropdown generation."""
    
    def __init__(self):
        self.custom_combo_integration = CustomComboBoxIntegration()
        self.default_options = {
            'role': ['Programmer', 'Chef', 'Soccer Coach', 'Teacher', 'Designer'],
            'what': ['Write code', 'Shop for food', 'Create tests', 'Prepare lunch', 'Plan dinner party', 'Refactor'],
            'why': ['Build better software', 'Cook delicious meals', 'Improve code quality', 'Feed my family', 'Host friends'],
            'action': ['Write code', 'Create tests', 'Refactor', 'Shop for food', 'Prepare lunch'],
            'context': ['Web development', 'Mobile app', 'Backend API', 'Kitchen', 'Restaurant']
        }
    
    def extract_variables(self, template: str) -> List[str]:
        """Extract variables from template using regex."""
        return re.findall(r'\[([^\]]+)\]', template)
    
    def generate_regular_dropdowns(self, template: str) -> Dict[str, Any]:
        """Generate regular dropdowns for non-edit mode."""
        variables = self.extract_variables(template)
        
        dropdowns = {}
        for var in variables:
            dropdowns[var] = {
                'options': self.default_options.get(var.lower(), [f'Option 1 for {var}', f'Option 2 for {var}']),
                'placeholder': f'Select or enter {var}...'
            }
        
        return dropdowns
    
    def generate_custom_dropdowns(self, template: str) -> Dict[str, Any]:
        """Generate custom dropdowns for edit mode."""
        custom_result = self.custom_combo_integration.create_template_with_custom_combo_boxes(template)
        
        # Adapt to regular format for compatibility
        dropdowns = {}
        for combo_box in custom_result["combo_boxes"]:
            tag = combo_box["tag"]
            
            # For custom combo boxes, always start with "Add item..." as first option
            # Then add default options if none exist
            default_options = [f"Option 1 for {tag}", f"Option 2 for {tag}"]
            options = combo_box["options"] if combo_box["options"] else default_options
            options_with_add = ["Add item..."] + options
            
            dropdowns[tag] = {
                "options": options_with_add,
                "enabled": combo_box["enabled"],
                "value": combo_box["value"],
                "is_custom": True,
                "placeholder": "Type anything."
            }
        
        return dropdowns
    
    def generate_dropdowns(self, template: str, edit_mode: bool = False) -> Dict[str, Any]:
        """Generate dropdowns based on edit mode."""
        if edit_mode:
            return self.generate_custom_dropdowns(template)
        else:
            return self.generate_regular_dropdowns(template)
    
    def update_dropdown_options(self, variable: str, context: str) -> List[str]:
        """Update dropdown options based on context."""
        # This could be enhanced with more sophisticated context-aware logic
        base_options = self.default_options.get(variable.lower(), [])
        if context:
            # Filter or enhance options based on context
            return [f"{context} - {option}" for option in base_options[:3]]
        return base_options
    
    def generate_final_prompt(self, template: str, selections: Dict[str, str]) -> str:
        """Generate final prompt by replacing variables with selections."""
        final_prompt = template
        for variable, value in selections.items():
            if value:  # Only replace if value is not empty
                final_prompt = final_prompt.replace(f'[{variable}]', value)
        return final_prompt
