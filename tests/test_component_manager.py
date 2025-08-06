import pytest
import json
from pathlib import Path
from prompt_manager.business.component_manager import ComponentManager


class TestComponentManager:
    """Test component management functionality."""
    
    def test_load_components_from_json(self):
        """Test loading components from JSON file."""
        # Create a temporary JSON file for testing
        test_data = {
            "components": {
                "Role": [
                    {"label": "Programmer", "next_tag": "What"},
                    {"label": "Marketing", "next_tag": "What"},
                    {"label": "Finance", "next_tag": "What"}
                ],
                "What": [
                    {"label": "Writing Code", "parent": "Programmer", "next_tag": "Why"},
                    {"label": "Testing Feature", "parent": "Programmer", "next_tag": "Why"},
                    {"label": "Approve ads", "parent": "Marketing", "next_tag": "Why"},
                    {"label": "Plan brochure", "parent": "Marketing", "next_tag": "Why"}
                ],
                "Why": [
                    {"label": "Implement a Feature", "parent": "Writing Code"},
                    {"label": "Fix a Bug", "parent": "Writing Code"},
                    {"label": "Improve User Experience", "parent": "Approve ads"}
                ]
            }
        }
        
        # Write test data to temporary file
        test_file = Path("test_components.json")
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        try:
            manager = ComponentManager(test_file)
            components = manager.get_all_components()
            
            assert "Role" in components
            assert "What" in components
            assert "Why" in components
            assert len(components["Role"]) == 3
            assert len(components["What"]) == 4
            assert len(components["Why"]) == 3
            
        finally:
            # Clean up test file
            test_file.unlink(missing_ok=True)
    
    def test_get_root_components(self):
        """Test getting root components (those without parents)."""
        test_data = {
            "components": {
                "Role": [
                    {"label": "Programmer", "next_tag": "What"},
                    {"label": "Marketing", "next_tag": "What"}
                ],
                "What": [
                    {"label": "Writing Code", "parent": "Programmer", "next_tag": "Why"}
                ]
            }
        }
        
        test_file = Path("test_components.json")
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        try:
            manager = ComponentManager(test_file)
            root_components = manager.get_root_components()
            
            assert "Role" in root_components
            assert len(root_components["Role"]) == 2
            assert "What" not in root_components  # Has parent, not root
            
        finally:
            test_file.unlink(missing_ok=True)
    
    def test_get_child_components(self):
        """Test getting child components for a specific parent."""
        test_data = {
            "components": {
                "Role": [
                    {"label": "Programmer", "next_tag": "What"},
                    {"label": "Marketing", "next_tag": "What"}
                ],
                "What": [
                    {"label": "Writing Code", "parent": "Programmer", "next_tag": "Why"},
                    {"label": "Testing Feature", "parent": "Programmer", "next_tag": "Why"},
                    {"label": "Approve ads", "parent": "Marketing", "next_tag": "Why"}
                ]
            }
        }
        
        test_file = Path("test_components.json")
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        try:
            manager = ComponentManager(test_file)
            programmer_children = manager.get_child_components("What", "Programmer")
            marketing_children = manager.get_child_components("What", "Marketing")
            
            assert len(programmer_children) == 2
            assert len(marketing_children) == 1
            assert any(child["label"] == "Writing Code" for child in programmer_children)
            assert any(child["label"] == "Approve ads" for child in marketing_children)
            
        finally:
            test_file.unlink(missing_ok=True) 