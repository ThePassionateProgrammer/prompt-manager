import pytest
import json
from pathlib import Path
from prompt_manager.business.template_storage import TemplateStorage


class TestTemplateStorage:
    """Test template storage and loading functionality."""
    
    def test_save_template(self):
        """Test saving a template with its state."""
        storage = TemplateStorage()
        
        template_data = {
            "name": "User Story Template",
            "description": "Standard user story format",
            "template": "As a [Role], I want to [What], so that I can [Why]",
            "combo_boxes": [
                {"tag": "Role", "value": "Programmer", "enabled": True},
                {"tag": "What", "value": "Writing Code", "enabled": True},
                {"tag": "Why", "value": "Implement a Feature", "enabled": True}
            ],
            "created_date": "2025-08-06T20:30:00Z"
        }
        
        template_id = storage.save_template(template_data)
        
        assert template_id is not None
        assert storage.template_exists(template_id)
    
    def test_load_template(self):
        """Test loading a saved template."""
        storage = TemplateStorage()
        
        # Save a template first
        template_data = {
            "name": "Test Template",
            "description": "Test description",
            "template": "As a [Role], I want to [What]",
            "combo_boxes": [
                {"tag": "Role", "value": "Developer", "enabled": True},
                {"tag": "What", "value": "Build Features", "enabled": True}
            ],
            "created_date": "2025-08-06T20:30:00Z"
        }
        
        template_id = storage.save_template(template_data)
        
        # Load the template
        loaded_template = storage.load_template(template_id)
        
        assert loaded_template is not None
        assert loaded_template["name"] == "Test Template"
        assert loaded_template["template"] == "As a [Role], I want to [What]"
        assert len(loaded_template["combo_boxes"]) == 2
    
    def test_list_templates(self):
        """Test listing all saved templates."""
        storage = TemplateStorage()
        
        # Save multiple templates
        template1 = {
            "name": "Template 1",
            "description": "First template",
            "template": "As a [Role], I want to [What]",
            "combo_boxes": [],
            "created_date": "2025-08-06T20:30:00Z"
        }
        
        template2 = {
            "name": "Template 2", 
            "description": "Second template",
            "template": "Given [Context], when [Action], then [Result]",
            "combo_boxes": [],
            "created_date": "2025-08-06T20:30:00Z"
        }
        
        storage.save_template(template1)
        storage.save_template(template2)
        
        templates = storage.list_templates()
        
        assert len(templates) >= 2
        template_names = [t["name"] for t in templates]
        assert "Template 1" in template_names
        assert "Template 2" in template_names
    
    def test_update_template(self):
        """Test updating an existing template."""
        storage = TemplateStorage()
        
        # Save initial template
        template_data = {
            "name": "Original Template",
            "description": "Original description",
            "template": "As a [Role], I want to [What]",
            "combo_boxes": [],
            "created_date": "2025-08-06T20:30:00Z"
        }
        
        template_id = storage.save_template(template_data)
        
        # Update the template
        updated_data = {
            "name": "Updated Template",
            "description": "Updated description",
            "template": "As a [Role], I want to [What], so that I can [Why]",
            "combo_boxes": [
                {"tag": "Role", "value": "Developer", "enabled": True}
            ],
            "created_date": "2025-08-06T20:30:00Z"
        }
        
        success = storage.update_template(template_id, updated_data)
        
        assert success is True
        
        # Verify the update
        loaded_template = storage.load_template(template_id)
        assert loaded_template["name"] == "Updated Template"
        assert loaded_template["template"] == "As a [Role], I want to [What], so that I can [Why]"
    
    def test_delete_template(self):
        """Test deleting a template."""
        storage = TemplateStorage()
        
        # Save a template
        template_data = {
            "name": "Template to Delete",
            "description": "Will be deleted",
            "template": "As a [Role], I want to [What]",
            "combo_boxes": [],
            "created_date": "2025-08-06T20:30:00Z"
        }
        
        template_id = storage.save_template(template_data)
        
        # Delete the template
        success = storage.delete_template(template_id)
        
        assert success is True
        assert not storage.template_exists(template_id)
