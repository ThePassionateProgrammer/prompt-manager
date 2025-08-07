import pytest
import json
from pathlib import Path
from prompt_manager.business.template_parser import TemplateParser
from prompt_manager.business.component_manager import ComponentManager


class TestTemplateBuilderIntegration:
    """Test integration of template builder with cascading logic and edit mode."""
    
    def test_template_builder_generates_combo_boxes(self):
        """Test that template builder generates proper combo boxes from template."""
        parser = TemplateParser()
        manager = ComponentManager(Path("src/prompt_manager/data/components.json"))
        
        template = "As a [Role], I want to [What], so that I can [Why]"
        combo_boxes = parser.generate_combo_boxes(template)
        
        # Verify combo boxes are generated correctly
        assert len(combo_boxes) == 3
        assert combo_boxes[0]["tag"] == "Role"
        assert combo_boxes[1]["tag"] == "What"
        assert combo_boxes[2]["tag"] == "Why"
        
        # Verify initial state
        assert combo_boxes[0]["enabled"] == True
        assert combo_boxes[1]["enabled"] == False
        assert combo_boxes[2]["enabled"] == False
    
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
    
    def test_cascading_selection_updates_downstream_boxes(self):
        """Test that selecting an option updates downstream combo boxes."""
        parser = TemplateParser()
        manager = ComponentManager(Path("src/prompt_manager/data/components.json"))
        
        template = "As a [Role], I want to [What], so that I can [Why]"
        combo_boxes = parser.generate_combo_boxes(template)
        
        # Initial state
        assert combo_boxes[0]["enabled"] == True
        assert combo_boxes[1]["enabled"] == False
        assert combo_boxes[2]["enabled"] == False
        
        # Populate first combo box
        combo_boxes[0]["options"] = manager.get_component_options("Role")
        
        # Select "Programmer"
        combo_boxes[0]["value"] = "Programmer"
        
        # Update cascading selections
        combo_boxes = parser.update_cascading_selections(combo_boxes, 0)
        
        # Verify second combo box is now enabled
        assert combo_boxes[1]["enabled"] == True
        assert combo_boxes[2]["enabled"] == False
        
        # Populate second combo box with options for "Programmer"
        what_options = manager.get_component_options("What", "Programmer")
        combo_boxes[1]["options"] = what_options
        
        assert len(combo_boxes[1]["options"]) == 3
        assert "Writing Code" in combo_boxes[1]["options"]
        assert "Testing Feature" in combo_boxes[1]["options"]
        assert "Gathering Requirements" in combo_boxes[1]["options"]
    
    def test_edit_mode_allows_custom_text(self):
        """Test that edit mode allows custom text entry in combo boxes."""
        parser = TemplateParser()
        manager = ComponentManager(Path("src/prompt_manager/data/components.json"))
        
        template = "As a [Role], I want to [What], so that I can [Why]"
        combo_boxes = parser.generate_combo_boxes(template)
        
        # Simulate edit mode - user enters custom text
        combo_boxes[0]["value"] = "Custom Role"
        combo_boxes[0]["is_custom"] = True
        
        combo_boxes[1]["value"] = "Custom Task"
        combo_boxes[1]["is_custom"] = True
        
        combo_boxes[2]["value"] = "Custom Goal"
        combo_boxes[2]["is_custom"] = True
        
        # Verify custom values are preserved
        assert combo_boxes[0]["value"] == "Custom Role"
        assert combo_boxes[1]["value"] == "Custom Task"
        assert combo_boxes[2]["value"] == "Custom Goal"
        assert combo_boxes[0]["is_custom"] == True
        assert combo_boxes[1]["is_custom"] == True
        assert combo_boxes[2]["is_custom"] == True
    
    def test_generate_final_prompt_from_selections(self):
        """Test generating the final prompt from combo box selections."""
        parser = TemplateParser()
        manager = ComponentManager(Path("src/prompt_manager/data/components.json"))
        
        template = "As a [Role], I want to [What], so that I can [Why]"
        combo_boxes = parser.generate_combo_boxes(template)
        
        # Set selections
        combo_boxes[0]["value"] = "Programmer"
        combo_boxes[1]["value"] = "Writing Code"
        combo_boxes[2]["value"] = "Implement a Feature"
        
        # Generate final prompt
        final_prompt = parser.generate_prompt_from_selections(template, combo_boxes)
        
        expected_prompt = "As a Programmer, I want to Writing Code, so that I can Implement a Feature"
        assert final_prompt == expected_prompt
    
    def test_generate_prompt_with_custom_text(self):
        """Test generating prompt with custom text entries."""
        parser = TemplateParser()
        
        template = "As a [Role], I want to [What], so that I can [Why]"
        combo_boxes = [
            {"tag": "Role", "value": "Custom Developer", "is_custom": True},
            {"tag": "What", "value": "Build Amazing Features", "is_custom": True},
            {"tag": "Why", "value": "Make Users Happy", "is_custom": True}
        ]
        
        final_prompt = parser.generate_prompt_from_selections(template, combo_boxes)
        
        expected_prompt = "As a Custom Developer, I want to Build Amazing Features, so that I can Make Users Happy"
        assert final_prompt == expected_prompt
