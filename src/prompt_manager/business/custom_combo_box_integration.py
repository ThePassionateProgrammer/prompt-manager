"""
Custom Combo Box Integration - Simplified Version

Minimal integration layer that provides the interface expected by the app
without the complex event system (handled by JavaScript).
"""

from typing import Dict, Any, List, Optional
import re


class CustomComboBoxIntegration:
    """Simplified integration layer for custom combo box system."""
    
    def __init__(self):
        """Initialize the integration layer."""
        pass
    
    def create_template_with_custom_combo_boxes(self, template: str) -> Dict[str, Any]:
        """Create a template with custom combo boxes from the template string."""
        # Extract variables in brackets [variable]
        variables = re.findall(r'\[([^\]]+)\]', template)
        
        # Generate simple combo boxes
        combo_boxes = []
        for i, variable in enumerate(variables):
            combo_box = {
                "tag": i + 1,  # Use 1-based indexing for tags
                "index": i,
                "enabled": True,
                "value": "",
                "options": self._get_default_options(variable)
            }
            combo_boxes.append(combo_box)
        
        return {
            "template": template,
            "combo_boxes": combo_boxes,
            "variables": variables
        }
    
    def _get_default_options(self, variable: str) -> List[str]:
        """Get default options for a variable."""
        options_map = {
            'role': ['Programmer', 'Chef', 'Soccer Coach', 'Teacher', 'Designer'],
            'what': ['Write code', 'Shop for food', 'Create tests', 'Prepare lunch', 'Plan dinner party'],
            'why': ['Build better software', 'Cook delicious meals', 'Improve code quality', 'Feed my family', 'Host friends'],
            'action': ['Write code', 'Create tests', 'Refactor', 'Shop for food', 'Prepare lunch'],
            'context': ['Web development', 'Mobile app', 'Backend API', 'Kitchen', 'Restaurant']
        }
        
        return options_map.get(variable, [f'Option 1 for {variable}', f'Option 2 for {variable}'])
    
    def get_available_templates(self) -> List[str]:
        """Get list of available templates."""
        return [
            "As a [Role], I want to [What], so that [Why]",
            "When [User] visits [Page], they should see [Content] and be able to [Action]",
            "If [Condition] then [Action] else [Alternative]",
            "The [Subject] should [Verb] the [Object]"
        ]
    
    def validate_template(self, template: str) -> Dict[str, Any]:
        """Validate a template and return validation results."""
        try:
            variables = re.findall(r'\[([^\]]+)\]', template)
            
            return {
                "valid": True,
                "variables": variables,
                "component_count": len(variables),
                "max_levels": 16,
                "within_limits": len(variables) <= 16
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "variables": [],
                "component_count": 0,
                "max_levels": 16,
                "within_limits": False
            }