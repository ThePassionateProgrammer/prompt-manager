import pytest
from prompt_manager.business.template_parser import TemplateParser
from prompt_manager.business.component_manager import ComponentManager
from pathlib import Path


class TestCascadingLogic:
    """Test cascading logic between template parser and component manager."""
    
    def test_populate_combo_boxes_with_components(self):
        """Test populating combo boxes with component options."""
        parser = TemplateParser()
        manager = ComponentManager(Path("src/prompt_manager/data/components.json"))
        
        template = "As a [Role], I want to [What], so that I can [Why]"
        combo_boxes = parser.generate_combo_boxes(template)
        
        # Populate first combo box with root components
        role_options = manager.get_component_options("Role")
        combo_boxes[0]["options"] = role_options
        
        assert len(combo_boxes[0]["options"]) == 5
        assert "Programmer" in combo_boxes[0]["options"]
        assert "Marketing" in combo_boxes[0]["options"]
    
    def test_cascading_selection_logic(self):
        """Test how selections cascade to update downstream combo boxes."""
        parser = TemplateParser()
        manager = ComponentManager(Path("src/prompt_manager/data/components.json"))
        
        template = "As a [Role], I want to [What], so that I can [Why]"
        combo_boxes = parser.generate_combo_boxes(template)
        
        # Initial state - only first combo box enabled
        assert combo_boxes[0]["enabled"] == True
        assert combo_boxes[1]["enabled"] == False
        assert combo_boxes[2]["enabled"] == False
        
        # Populate first combo box
        combo_boxes[0]["options"] = manager.get_component_options("Role")
        
        # Simulate selecting "Programmer"
        combo_boxes[0]["value"] = "Programmer"
        
        # Update second combo box based on selection
        what_options = manager.get_component_options("What", "Programmer")
        combo_boxes[1]["options"] = what_options
        combo_boxes[1]["enabled"] = True
        
        assert len(combo_boxes[1]["options"]) == 3
        assert "Writing Code" in combo_boxes[1]["options"]
        assert "Testing Feature" in combo_boxes[1]["options"]
        assert "Gathering Requirements" in combo_boxes[1]["options"]
        
        # Simulate selecting "Writing Code"
        combo_boxes[1]["value"] = "Writing Code"
        
        # Update third combo box based on selection
        why_options = manager.get_component_options("Why", "Writing Code")
        combo_boxes[2]["options"] = why_options
        combo_boxes[2]["enabled"] = True
        
        assert len(combo_boxes[2]["options"]) == 3
        assert "Implement a Feature" in combo_boxes[2]["options"]
        assert "Fix a Bug" in combo_boxes[2]["options"]
        assert "Improve Performance" in combo_boxes[2]["options"]
    
    def test_reset_downstream_selections(self):
        """Test that changing a selection resets downstream combo boxes."""
        parser = TemplateParser()
        manager = ComponentManager(Path("src/prompt_manager/data/components.json"))
        
        template = "As a [Role], I want to [What], so that I can [Why]"
        combo_boxes = parser.generate_combo_boxes(template)
        
        # Set up initial state with selections
        combo_boxes[0]["value"] = "Programmer"
        combo_boxes[1]["value"] = "Writing Code"
        combo_boxes[2]["value"] = "Implement a Feature"
        
        # Change first selection from "Programmer" to "Marketing"
        combo_boxes[0]["value"] = "Marketing"
        
        # Use the cascading update method to reset downstream selections
        combo_boxes = parser.update_cascading_selections(combo_boxes, 0)
        
        # Second and third combo boxes should be reset
        assert combo_boxes[1]["value"] == ""
        assert combo_boxes[2]["value"] == ""
        assert combo_boxes[1]["enabled"] == True  # Next combo box should be enabled
        assert combo_boxes[2]["enabled"] == False  # But not the one after that
        
        # Update second combo box with new options
        what_options = manager.get_component_options("What", "Marketing")
        combo_boxes[1]["options"] = what_options
        
        assert len(combo_boxes[1]["options"]) == 3
        assert "Approve ads" in combo_boxes[1]["options"]
        assert "Plan brochure" in combo_boxes[1]["options"]
        assert "Create campaign" in combo_boxes[1]["options"] 