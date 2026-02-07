import pytest
import tempfile
from pathlib import Path
from src.prompt_manager.template_service import TemplateService


class TestTemplateService:
    """Test the TemplateService integration layer."""
    
    def test_can_save_and_load_template_integration(self):
        """Test the complete save/load workflow integration."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            template_service = TemplateService(str(storage_path))
            
            template_name = "Integration Test Template"
            template_description = "Template for integration testing"
            template_text = "As a [Role], I want to [Action] so that [Benefit]"
            combo_box_values = {
                "Role": ["Manager", "Programmer"],
                "Action": ["Review", "Code"],
                "Benefit": ["Improve quality", "Save time"]
            }
            linkage_data = {
                "Manager": {
                    "Action": ["Review", "Meetings"]
                },
                "Programmer": {
                    "Action": ["Code", "Test"]
                }
            }
            
            # Act - Save template
            template_service.save_template(
                name=template_name,
                description=template_description,
                template_text=template_text,
                combo_box_values=combo_box_values,
                linkage_data=linkage_data
            )
            
            # Act - Load template
            loaded_template = template_service.load_template(template_name)
            
            # Assert
            assert loaded_template["name"] == template_name
            assert loaded_template["description"] == template_description
            assert loaded_template["template_text"] == template_text
            assert loaded_template["combo_box_values"] == combo_box_values
            assert loaded_template["linkage_data"] == linkage_data
            assert "created_at" in loaded_template
            assert "updated_at" in loaded_template
    
    def test_can_list_saved_templates(self):
        """Test that we can list all saved templates."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            template_service = TemplateService(str(storage_path))
            
            # Save multiple templates
            template_service.save_template(
                name="Template 1",
                description="First template",
                template_text="Template 1 [Tag]",
                combo_box_values={"Tag": ["Value1"]},
                linkage_data={}
            )
            
            template_service.save_template(
                name="Template 2",
                description="Second template",
                template_text="Template 2 [Tag]",
                combo_box_values={"Tag": ["Value2"]},
                linkage_data={}
            )
            
            # Act
            templates = template_service.list_templates()
            
            # Assert
            assert len(templates) == 2
            assert "Template 1" in templates
            assert "Template 2" in templates
            assert templates["Template 1"]["name"] == "Template 1"
            assert templates["Template 2"]["name"] == "Template 2"
    
    def test_can_delete_template(self):
        """Test that we can delete a saved template."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            template_service = TemplateService(str(storage_path))
            
            # Save a template
            template_service.save_template(
                name="Template to Delete",
                description="A template that will be deleted",
                template_text="Delete [Tag] template",
                combo_box_values={"Tag": ["Value"]},
                linkage_data={}
            )
            
            # Act
            result = template_service.delete_template("Template to Delete")
            
            # Assert
            assert result == True
            templates = template_service.list_templates()
            assert "Template to Delete" not in templates
    
    def test_validation_errors_are_propagated(self):
        """Test that validation errors from TemplateManager are propagated."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            template_service = TemplateService(str(storage_path))
            
            # Act & Assert - Test malformed template text
            with pytest.raises(ValueError, match="Template text contains malformed tags"):
                template_service.save_template(
                    name="Bad Template",
                    description="Template with bad tags",
                    template_text="As a [Role, I want to [Action]",  # Missing closing bracket
                    combo_box_values={},
                    linkage_data={}
                )
            
            # Act & Assert - Test duplicate template name
            template_service.save_template(
                name="Duplicate Template",
                description="First template",
                template_text="Template 1 [Tag]",
                combo_box_values={"Tag": ["Value1"]},
                linkage_data={}
            )
            
            with pytest.raises(ValueError, match="Template name must be unique"):
                template_service.save_template(
                    name="Duplicate Template",
                    description="Second template",
                    template_text="Template 2 [Tag]",
                    combo_box_values={"Tag": ["Value2"]},
                    linkage_data={}
                )
    
    def test_can_update_existing_template(self):
        """Test that we can update an existing template."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            template_service = TemplateService(str(storage_path))
            
            # Save initial template
            template_service.save_template(
                name="Update Test Template",
                description="Original description",
                template_text="Original [Tag] template",
                combo_box_values={"Tag": ["Original"]},
                linkage_data={}
            )
            
            # Act - Update template
            updated_template = template_service.update_template(
                name="Update Test Template",
                description="Updated description",
                template_text="Updated [Tag] template",
                combo_box_values={"Tag": ["Updated"]}
            )
            
            # Assert
            assert updated_template["description"] == "Updated description"
            assert updated_template["template_text"] == "Updated [Tag] template"
            assert updated_template["combo_box_values"]["Tag"] == ["Updated"]
            assert updated_template["updated_at"] != updated_template["created_at"]
            
            # Verify it's saved
            loaded_template = template_service.load_template("Update Test Template")
            assert loaded_template["description"] == "Updated description"
    
    def test_template_exists_check(self):
        """Test that we can check if a template exists."""
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = Path(temp_dir) / "templates.json"
            template_service = TemplateService(str(storage_path))
            
            # Act & Assert - Template doesn't exist initially
            assert template_service.template_exists("Non-existent Template") == False
            
            # Save a template
            template_service.save_template(
                name="Existing Template",
                description="A template that exists",
                template_text="Existing [Tag] template",
                combo_box_values={"Tag": ["Value"]},
                linkage_data={}
            )
            
            # Act & Assert - Template exists after saving
            assert template_service.template_exists("Existing Template") == True
            assert template_service.template_exists("Still Non-existent Template") == False
