import pytest
import json
import tempfile
from pathlib import Path
from src.prompt_manager.template_service import TemplateService


class TestTemplateRoutesIsolated:
    """Test the Flask routes for template persistence with isolated storage."""
    
    @pytest.fixture(autouse=True)
    def setup_isolated_storage(self):
        """Setup isolated storage for each test."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.storage_path = Path(temp_dir) / "test_templates.json"
            yield self.storage_path
    
    def test_save_template_route(self, client, setup_isolated_storage):
        """Test the save template route."""
        # Arrange
        template_data = {
            "name": "Test Template",
            "description": "A test template",
            "template_text": "As a [Role], I want to [Action]",
            "combo_box_values": {
                "Role": ["Manager", "Programmer"],
                "Action": ["Review", "Code"]
            },
            "linkage_data": {
                "Manager": {
                    "Action": ["Review", "Meetings"]
                },
                "Programmer": {
                    "Action": ["Code", "Test"]
                }
            }
        }
        
        # Act
        response = client.post('/api/template-persistence/save', 
                             json=template_data,
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 200
        result = response.get_json()
        assert result["success"] == True
        assert result["message"] == "Template saved successfully"
    
    def test_save_template_validation_error(self, client, setup_isolated_storage):
        """Test that validation errors are returned properly."""
        # Arrange
        invalid_template_data = {
            "name": "Invalid Template",
            "description": "Template with bad tags",
            "template_text": "As a [Role, I want to [Action]",  # Missing closing bracket
            "combo_box_values": {},
            "linkage_data": {}
        }
        
        # Act
        response = client.post('/api/template-persistence/save',
                             json=invalid_template_data,
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        result = response.get_json()
        assert result["success"] == False
        assert "Template text contains malformed tags" in result["error"]
    
    def test_load_template_route(self, client, setup_isolated_storage):
        """Test the load template route."""
        # Arrange - First save a template
        template_data = {
            "name": "Load Test Template",
            "description": "Template for loading test",
            "template_text": "Load [Tag] template",
            "combo_box_values": {"Tag": ["Value1", "Value2"]},
            "linkage_data": {}
        }
        
        client.post('/api/template-persistence/save',
                   json=template_data,
                   content_type='application/json')
        
        # Act
        response = client.get('/api/template-persistence/load/Load Test Template')
        
        # Assert
        assert response.status_code == 200
        result = response.get_json()
        assert result["success"] == True
        assert result["template"]["name"] == "Load Test Template"
        assert result["template"]["template_text"] == "Load [Tag] template"
    
    def test_load_template_not_found(self, client, setup_isolated_storage):
        """Test loading a non-existent template."""
        # Act
        response = client.get('/api/template-persistence/load/Non-existent Template')
        
        # Assert
        assert response.status_code == 404
        result = response.get_json()
        assert result["success"] == False
        assert "Template not found" in result["error"]
    
    def test_list_templates_route(self, client, setup_isolated_storage):
        """Test the list templates route."""
        # Arrange - Save some templates
        template1 = {
            "name": "Template 1",
            "description": "First template",
            "template_text": "Template 1 [Tag]",
            "combo_box_values": {"Tag": ["Value1"]},
            "linkage_data": {}
        }
        
        template2 = {
            "name": "Template 2",
            "description": "Second template",
            "template_text": "Template 2 [Tag]",
            "combo_box_values": {"Tag": ["Value2"]},
            "linkage_data": {}
        }
        
        client.post('/api/template-persistence/save', json=template1, content_type='application/json')
        client.post('/api/template-persistence/save', json=template2, content_type='application/json')
        
        # Act
        response = client.get('/api/template-persistence/list')
        
        # Assert
        assert response.status_code == 200
        result = response.get_json()
        assert result["success"] == True
        templates = result["templates"]
        assert len(templates) == 2
        assert "Template 1" in templates
        assert "Template 2" in templates
        assert templates["Template 1"]["name"] == "Template 1"
        assert templates["Template 2"]["name"] == "Template 2"
    
    def test_delete_template_route(self, client, setup_isolated_storage):
        """Test the delete template route."""
        # Arrange - Save a template first
        template_data = {
            "name": "Delete Test Template",
            "description": "Template to be deleted",
            "template_text": "Delete [Tag] template",
            "combo_box_values": {"Tag": ["Value"]},
            "linkage_data": {}
        }
        
        client.post('/api/template-persistence/save',
                   json=template_data,
                   content_type='application/json')
        
        # Act
        response = client.delete('/api/template-persistence/delete/Delete Test Template')
        
        # Assert
        assert response.status_code == 200
        result = response.get_json()
        assert result["success"] == True
        assert result["message"] == "Template deleted successfully"
        
        # Verify it's actually deleted
        load_response = client.get('/api/template-persistence/load/Delete Test Template')
        assert load_response.status_code == 404
    
    def test_delete_template_not_found(self, client, setup_isolated_storage):
        """Test deleting a non-existent template."""
        # Act
        response = client.delete('/api/template-persistence/delete/Non-existent Template')
        
        # Assert
        assert response.status_code == 404
        result = response.get_json()
        assert result["success"] == False
        assert "Template not found" in result["error"]
    
    def test_template_exists_route(self, client, setup_isolated_storage):
        """Test the template exists route."""
        # Arrange - Save a template
        template_data = {
            "name": "Exists Test Template",
            "description": "Template for exists test",
            "template_text": "Exists [Tag] template",
            "combo_box_values": {"Tag": ["Value"]},
            "linkage_data": {}
        }
        
        client.post('/api/template-persistence/save',
                   json=template_data,
                   content_type='application/json')
        
        # Act - Check existing template
        response = client.get('/api/template-persistence/exists/Exists Test Template')
        
        # Assert
        assert response.status_code == 200
        result = response.get_json()
        assert result["success"] == True
        assert result["exists"] == True
        
        # Act - Check non-existing template
        response = client.get('/api/template-persistence/exists/Non-existent Template')
        
        # Assert
        assert response.status_code == 200
        result = response.get_json()
        assert result["success"] == True
        assert result["exists"] == False
