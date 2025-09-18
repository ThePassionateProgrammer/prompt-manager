#!/usr/bin/env python3
"""
Integration tests for the Template Builder.
Tests the areas where CustomComboBox will be integrated.
"""

import pytest
import requests
import json
import time

class TestTemplateBuilderIntegration:
    """Test suite for Template Builder integration points."""
    
    def setup_method(self):
        """Set up test environment."""
        self.base_url = "http://localhost:8000"
        self.test_template = "As a [Role], I want to [Action], so that I can [Goal]"
    
    def test_template_builder_page_loads(self):
        """Test that the template builder page loads correctly."""
        response = requests.get(f"{self.base_url}/template-builder")
        assert response.status_code == 200
        
        content = response.text
        assert "Template Builder" in content
        assert "template" in content.lower()
    
    def test_template_parsing_endpoint(self):
        """Test the template parsing endpoint."""
        test_data = {
            "template": self.test_template
        }
        
        response = requests.post(
            f"{self.base_url}/template/parse",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should extract tags
        assert "tags" in data
        assert "Role" in data["tags"]
        assert "Action" in data["tags"]
        assert "Goal" in data["tags"]
    
    def test_dropdown_generation_endpoint(self):
        """Test the dropdown generation endpoint."""
        test_data = {
            "template": self.test_template,
            "edit_mode": False
        }
        
        response = requests.post(
            f"{self.base_url}/template/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have dropdowns
        assert "dropdowns" in data
        assert "Role" in data["dropdowns"]
        assert "Action" in data["dropdowns"]
        assert "Goal" in data["dropdowns"]
        
        # Check dropdown structure
        role_dropdown = data["dropdowns"]["Role"]
        assert "options" in role_dropdown
        assert "placeholder" in role_dropdown
    
    def test_edit_mode_dropdown_generation(self):
        """Test dropdown generation in edit mode."""
        test_data = {
            "template": self.test_template,
            "edit_mode": True
        }
        
        response = requests.post(
            f"{self.base_url}/template/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check edit mode specific properties
        role_dropdown = data["dropdowns"]["Role"]
        assert "is_custom" in role_dropdown
        assert role_dropdown["is_custom"] == True
        
        # Should have "Add item..." as first option
        options = role_dropdown["options"]
        assert options[0] == "Add item..."
    
    def test_display_mode_dropdown_generation(self):
        """Test dropdown generation in display mode."""
        test_data = {
            "template": self.test_template,
            "edit_mode": False
        }
        
        response = requests.post(
            f"{self.base_url}/template/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check display mode specific properties
        role_dropdown = data["dropdowns"]["Role"]
        assert "is_custom" in role_dropdown
        assert role_dropdown["is_custom"] == True
        
        # Should have "Select item..." as first option
        options = role_dropdown["options"]
        assert options[0] == "Select item..."
    
    def test_template_storage_structure(self):
        """Test the template storage structure for CustomComboBox integration."""
        # This tests the JSON structure we'll use for persistence
        template_data = {
            "templateText": self.test_template,
            "comboBoxes": [
                {
                    "tag": "Role",
                    "index": 0,
                    "options": ["Developer", "Designer", "Manager"],
                    "linkages": {
                        "Developer": ["Fix bugs", "Write tests", "Deploy code"],
                        "Designer": ["Create mockups", "User research", "Prototype"],
                        "Manager": ["Plan sprints", "Review work", "Team meetings"]
                    }
                },
                {
                    "tag": "Action",
                    "index": 1,
                    "options": ["Fix bugs", "Write tests", "Deploy code"],
                    "linkages": {
                        "Fix bugs": ["Save time", "Improve quality", "Reduce errors"],
                        "Write tests": ["Prevent regressions", "Document behavior", "Enable refactoring"],
                        "Deploy code": ["Deliver features", "Update production", "Rollback if needed"]
                    }
                },
                {
                    "tag": "Goal",
                    "index": 2,
                    "options": ["Save time", "Improve quality", "Reduce errors"],
                    "linkages": {}
                }
            ],
            "lastModified": "2025-09-14T14:30:00.000Z"
        }
        
        # Validate structure
        assert "templateText" in template_data
        assert "comboBoxes" in template_data
        assert len(template_data["comboBoxes"]) == 3
        
        # Check combo box structure
        for combo_box in template_data["comboBoxes"]:
            assert "tag" in combo_box
            assert "index" in combo_box
            assert "options" in combo_box
            assert "linkages" in combo_box
            assert isinstance(combo_box["options"], list)
            assert isinstance(combo_box["linkages"], dict)
    
    def test_hierarchical_linkage_validation(self):
        """Test that hierarchical linkages are properly structured."""
        # Test the linkage structure
        linkages = {
            "Developer": ["Fix bugs", "Write tests", "Deploy code"],
            "Designer": ["Create mockups", "User research", "Prototype"],
            "Manager": ["Plan sprints", "Review work", "Team meetings"]
        }
        
        # Validate linkage structure
        for source, targets in linkages.items():
            assert isinstance(source, str)
            assert isinstance(targets, list)
            assert len(targets) > 0
            
            for target in targets:
                assert isinstance(target, str)
                assert len(target.strip()) > 0
    
    def test_template_builder_html_structure(self):
        """Test that the template builder HTML has the right structure for integration."""
        response = requests.get(f"{self.base_url}/template-builder")
        assert response.status_code == 200
        
        content = response.text
        
        # Should have areas where we'll inject CustomComboBox
        assert "combo-box-container" in content or "dropdown" in content.lower()
        
        # Should have mode toggle functionality
        assert "edit" in content.lower() or "mode" in content.lower()
        
        # Should have template input area
        assert "template" in content.lower()
    
    def test_custom_combo_test_page(self):
        """Test that the custom combo test page works."""
        response = requests.get(f"{self.base_url}/custom-combo-test")
        assert response.status_code == 200
        
        content = response.text
        assert "Custom Combo Box Test" in content
        assert "combo-box" in content.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])