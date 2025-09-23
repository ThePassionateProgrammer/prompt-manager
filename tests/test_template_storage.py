import pytest
import json
import os
import tempfile
from pathlib import Path
from src.prompt_manager.template_storage import TemplateStorage


class TestTemplateStorage:
    """Test the TemplateStorage persistence layer."""
    
    def test_can_save_template_to_json_file(self):
        """Test that TemplateStorage can save a template to a JSON file."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            template_storage = TemplateStorage(str(storage_path))
            
            template_data = {
                "name": "User Story Template",
                "description": "Template for creating user stories",
                "template_text": "As a [Role], I want to [Action] so that [Benefit]",
                "combo_box_values": {
                    "Role": ["Manager", "Programmer"],
                    "Action": ["Review", "Code"],
                    "Benefit": ["Improve quality", "Save time"]
                },
                "linkage_data": {
                    "Manager": {
                        "Action": ["Review", "Meetings"]
                    },
                    "Programmer": {
                        "Action": ["Code", "Test"]
                    }
                },
                "created_at": "2025-01-23T10:30:00Z",
                "updated_at": "2025-01-23T10:30:00Z"
            }
            
            # Act
            template_storage.save_template(template_data)
            
            # Assert
            assert storage_path.exists()
            with open(storage_path, 'r') as f:
                saved_data = json.load(f)
            
            assert "User Story Template" in saved_data
            assert saved_data["User Story Template"] == template_data
    
    def test_can_load_template_from_json_file(self):
        """Test that TemplateStorage can load a template from a JSON file."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            
            # Create a test JSON file
            template_data = {
                "name": "Test Template",
                "description": "A test template",
                "template_text": "Test [Tag] template",
                "combo_box_values": {"Tag": ["Value1", "Value2"]},
                "linkage_data": {},
                "created_at": "2025-01-23T10:30:00Z",
                "updated_at": "2025-01-23T10:30:00Z"
            }
            
            with open(storage_path, 'w') as f:
                json.dump({"Test Template": template_data}, f, indent=2)
            
            template_storage = TemplateStorage(str(storage_path))
            
            # Act
            loaded_template = template_storage.load_template("Test Template")
            
            # Assert
            assert loaded_template == template_data
    
    def test_load_template_raises_error_if_not_found(self):
        """Test that loading a non-existent template raises an error."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            template_storage = TemplateStorage(str(storage_path))
            
            # Act & Assert
            with pytest.raises(ValueError, match="Template not found"):
                template_storage.load_template("Non-existent Template")
    
    def test_can_list_all_templates(self):
        """Test that TemplateStorage can list all templates in the file."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            
            # Create a test JSON file with multiple templates
            templates_data = {
                "Template 1": {
                    "name": "Template 1",
                    "description": "First template",
                    "template_text": "Template 1 [Tag]",
                    "combo_box_values": {"Tag": ["Value1"]},
                    "linkage_data": {},
                    "created_at": "2025-01-23T10:30:00Z",
                    "updated_at": "2025-01-23T10:30:00Z"
                },
                "Template 2": {
                    "name": "Template 2",
                    "description": "Second template",
                    "template_text": "Template 2 [Tag]",
                    "combo_box_values": {"Tag": ["Value2"]},
                    "linkage_data": {},
                    "created_at": "2025-01-23T10:31:00Z",
                    "updated_at": "2025-01-23T10:31:00Z"
                }
            }
            
            with open(storage_path, 'w') as f:
                json.dump(templates_data, f, indent=2)
            
            template_storage = TemplateStorage(str(storage_path))
            
            # Act
            templates = template_storage.list_templates()
            
            # Assert
            assert len(templates) == 2
            assert "Template 1" in templates
            assert "Template 2" in templates
            assert templates["Template 1"]["name"] == "Template 1"
            assert templates["Template 2"]["name"] == "Template 2"
    
    def test_can_delete_template(self):
        """Test that TemplateStorage can delete a template from the file."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            
            # Create a test JSON file
            template_data = {
                "name": "Template to Delete",
                "description": "A template that will be deleted",
                "template_text": "Delete [Tag] template",
                "combo_box_values": {"Tag": ["Value"]},
                "linkage_data": {},
                "created_at": "2025-01-23T10:30:00Z",
                "updated_at": "2025-01-23T10:30:00Z"
            }
            
            with open(storage_path, 'w') as f:
                json.dump({"Template to Delete": template_data}, f, indent=2)
            
            template_storage = TemplateStorage(str(storage_path))
            
            # Act
            result = template_storage.delete_template("Template to Delete")
            
            # Assert
            assert result == True
            with open(storage_path, 'r') as f:
                saved_data = json.load(f)
            assert "Template to Delete" not in saved_data
    
    def test_delete_template_returns_false_if_not_found(self):
        """Test that deleting a non-existent template returns False."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            template_storage = TemplateStorage(str(storage_path))
            
            # Act
            result = template_storage.delete_template("Non-existent Template")
            
            # Assert
            assert result == False
    
    def test_handles_corrupted_json_file(self):
        """Test that TemplateStorage handles corrupted JSON files gracefully."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            
            # Create a corrupted JSON file
            with open(storage_path, 'w') as f:
                f.write('{"corrupted": json}')
            
            template_storage = TemplateStorage(str(storage_path))
            
            # Act & Assert
            with pytest.raises(ValueError, match="Corrupted template file"):
                template_storage.list_templates()
    
    def test_creates_file_if_not_exists(self):
        """Test that TemplateStorage creates the file if it doesn't exist."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            template_storage = TemplateStorage(str(storage_path))
            
            template_data = {
                "name": "New Template",
                "description": "A new template",
                "template_text": "New [Tag] template",
                "combo_box_values": {"Tag": ["Value"]},
                "linkage_data": {},
                "created_at": "2025-01-23T10:30:00Z",
                "updated_at": "2025-01-23T10:30:00Z"
            }
            
            # Act
            template_storage.save_template(template_data)
            
            # Assert
            assert storage_path.exists()
            with open(storage_path, 'r') as f:
                saved_data = json.load(f)
            assert "New Template" in saved_data