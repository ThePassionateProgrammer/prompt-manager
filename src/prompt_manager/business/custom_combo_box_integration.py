"""
Custom Combo Box Integration

Final integration layer that connects our custom combo box system
with the main prompt manager application.
"""

from typing import Dict, Any, List, Optional
from .template_builder_interface import TemplateBuilderInterface
from .ui_component_factory import UIComponentFactory
from .component_event_system import EventBus, EventType, ComponentEvent, CascadingEventHandler
from .template_builder_impl import TemplateBuilderImpl


class CustomComboBoxIntegration:
    """Integration layer for custom combo box system with prompt manager."""
    
    def __init__(self):
        self.template_builder: TemplateBuilderInterface = TemplateBuilderImpl()
        self.component_factory = UIComponentFactory()
        self.event_bus = EventBus()
        self.cascading_handler = CascadingEventHandler(self.event_bus)
        
        # Set up event subscriptions
        self._setup_event_subscriptions()
    
    def _setup_event_subscriptions(self):
        """Set up event subscriptions for the integration."""
        # Subscribe cascading handler to component changes
        self.event_bus.subscribe(
            EventType.COMPONENT_CHANGED, 
            self.cascading_handler.handle_component_changed
        )
    
    def create_template_with_custom_combo_boxes(self, template: str) -> Dict[str, Any]:
        """Create a template with custom combo boxes from the template string."""
        # Parse template and generate components
        components = self.template_builder.generate_ui_components(template)
        
        # Convert to custom combo box format
        combo_boxes = []
        for i, component in enumerate(components):
            combo_box = self.component_factory.create_component(
                "combo_box",
                tag=component["tag"],
                index=component["index"],
                enabled=component["enabled"]
            )
            combo_boxes.append(combo_box.get_component_config())
        
        return {
            "template": template,
            "combo_boxes": combo_boxes,
            "variables": self.template_builder.parse_template(template)
        }
    
    def handle_combo_box_change(self, combo_box_id: str, new_value: str, 
                              combo_boxes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Handle a change in a combo box and update cascading state."""
        # Find the combo box index
        combo_box_index = None
        for i, combo_box in enumerate(combo_boxes):
            if combo_box.get("id") == combo_box_id or combo_box.get("tag") == combo_box_id:
                combo_box_index = i
                break
        
        if combo_box_index is None:
            return combo_boxes
        
        # Update the combo box value
        combo_boxes[combo_box_index]["value"] = new_value
        
        # Update cascading state
        updated_combo_boxes = self.template_builder.update_cascading_state(
            combo_boxes, combo_box_index
        )
        
        # Publish event
        event = ComponentEvent(
            EventType.COMPONENT_CHANGED,
            combo_box_id,
            {"value": new_value, "index": combo_box_index}
        )
        self.event_bus.publish(event)
        
        return updated_combo_boxes
    
    def generate_final_prompt(self, template: str, combo_boxes: List[Dict[str, Any]]) -> str:
        """Generate the final prompt from template and combo box selections."""
        return self.template_builder.generate_final_prompt(template, combo_boxes)
    
    def get_component_state(self, component_id: str) -> Dict[str, Any]:
        """Get the current state of a component."""
        return self.cascading_handler.get_component_state(component_id)
    
    def set_component_state(self, component_id: str, state: Dict[str, Any]):
        """Set the state of a component."""
        self.cascading_handler.set_component_state(component_id, state)
    
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
            variables = self.template_builder.parse_template(template)
            components = self.template_builder.generate_ui_components(template)
            
            return {
                "valid": True,
                "variables": variables,
                "component_count": len(components),
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
    
    def export_template_config(self, template: str, combo_boxes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Export template configuration for saving/loading."""
        return {
            "template": template,
            "combo_boxes": combo_boxes,
            "variables": self.template_builder.parse_template(template),
            "version": "1.0",
            "integration_type": "custom_combo_box"
        }
    
    def import_template_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Import template configuration from saved data."""
        template = config.get("template", "")
        combo_boxes = config.get("combo_boxes", [])
        
        # Validate the imported configuration
        validation = self.validate_template(template)
        if not validation["valid"]:
            raise ValueError(f"Invalid template in imported config: {validation['error']}")
        
        return {
            "template": template,
            "combo_boxes": combo_boxes,
            "variables": self.template_builder.parse_template(template)
        }
