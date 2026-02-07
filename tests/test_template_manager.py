import pytest
from src.prompt_manager.template_manager import TemplateManager
from datetime import datetime


class TestTemplateManager:
    """Test the TemplateManager business logic class."""
    
    def test_can_create_template_data_structure(self):
        """Test that TemplateManager can create a properly structured template."""
        # Arrange
        template_manager = TemplateManager()
        template_name = "User Story Template"
        template_description = "Template for creating user stories"
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
        
        # Act
        template_data = template_manager.create_template(
            name=template_name,
            description=template_description,
            template_text=template_text,
            combo_box_values=combo_box_values,
            linkage_data=linkage_data
        )
        
        # Assert
        assert template_data["name"] == template_name
        assert template_data["description"] == template_description
        assert template_data["template_text"] == template_text
        assert template_data["combo_box_values"] == combo_box_values
        assert template_data["linkage_data"] == linkage_data
        assert "created_at" in template_data
        assert "updated_at" in template_data
        assert isinstance(template_data["created_at"], str)
        assert isinstance(template_data["updated_at"], str)
    
    def test_template_name_must_be_unique(self):
        """Test that template names must be unique."""
        # Arrange
        template_manager = TemplateManager()
        template_name = "Duplicate Template"
        
        # Act
        template_manager.create_template(
            name=template_name,
            description="First template",
            template_text="Template 1",
            combo_box_values={},
            linkage_data={}
        )
        
        # Assert
        with pytest.raises(ValueError, match="Template name must be unique"):
            template_manager.create_template(
                name=template_name,
                description="Second template",
                template_text="Template 2",
                combo_box_values={},
                linkage_data={}
            )
    
    def test_validate_template_text_well_formed_tags(self):
        """Test that template text validation works for well-formed tags."""
        # Arrange
        template_manager = TemplateManager()
        
        # Act & Assert
        assert template_manager.validate_template_text("As a [Role], I want to [Action]") == True
        assert template_manager.validate_template_text("Simple text without tags") == True
        assert template_manager.validate_template_text("[Single] tag") == True
    
    def test_validate_template_text_malformed_tags(self):
        """Test that template text validation catches malformed tags."""
        # Arrange
        template_manager = TemplateManager()
        
        # Act & Assert
        assert template_manager.validate_template_text("As a [Role, I want to [Action]") == False  # Missing closing bracket
        assert template_manager.validate_template_text("As a Role], I want to [Action]") == False  # Missing opening bracket
        assert template_manager.validate_template_text("As a [Role], I want to [Action") == False  # Missing closing bracket
        assert template_manager.validate_template_text("As a [Role], I want to Action]") == False  # Missing opening bracket
    
    def test_get_template_by_name(self):
        """Test that we can retrieve a template by name."""
        # Arrange
        template_manager = TemplateManager()
        template_name = "Test Template"
        template_data = template_manager.create_template(
            name=template_name,
            description="Test description",
            template_text="Test template",
            combo_box_values={},
            linkage_data={}
        )
        
        # Act
        retrieved_template = template_manager.get_template(template_name)
        
        # Assert
        assert retrieved_template == template_data
    
    def test_get_template_raises_error_if_not_found(self):
        """Test that getting a non-existent template raises an error."""
        # Arrange
        template_manager = TemplateManager()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Template not found"):
            template_manager.get_template("Non-existent Template")
    
    def test_list_templates(self):
        """Test that we can list all templates."""
        # Arrange
        template_manager = TemplateManager()
        template1 = template_manager.create_template(
            name="Template 1",
            description="First template",
            template_text="Template 1",
            combo_box_values={},
            linkage_data={}
        )
        template2 = template_manager.create_template(
            name="Template 2",
            description="Second template",
            template_text="Template 2",
            combo_box_values={},
            linkage_data={}
        )
        
        # Act
        templates = template_manager.list_templates()
        
        # Assert
        assert len(templates) == 2
        assert "Template 1" in templates
        assert "Template 2" in templates
        assert templates["Template 1"]["name"] == "Template 1"
        assert templates["Template 2"]["name"] == "Template 2"
