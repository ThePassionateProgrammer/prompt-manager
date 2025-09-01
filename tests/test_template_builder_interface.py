"""
Tests for Template Builder Interface

Tests the new interface abstractions to ensure they work correctly
and maintain compatibility with existing functionality.
"""

import pytest
from src.prompt_manager.business.template_builder_interface import (
    TemplateBuilderInterface, UIComponentInterface, TemplateStorageInterface
)
from src.prompt_manager.business.template_builder_impl import (
    TemplateBuilderImpl, ComboBoxComponent, SimpleTemplateStorage
)


class TestTemplateBuilderInterface:
    """Test the template builder interface implementation."""
    
    def test_can_create_template_builder_impl(self):
        """Test that we can create a concrete implementation."""
        # Given: A template builder implementation
        builder = TemplateBuilderImpl()
        
        # Then: Should be an instance of the interface
        assert isinstance(builder, TemplateBuilderInterface)
    
    def test_can_parse_simple_template(self):
        """Test parsing a simple template with the new interface."""
        # Given: A template builder and simple template
        builder = TemplateBuilderImpl()
        template = "As a [Role], I want to [What], so that [Why]"
        
        # When: Parsing the template
        variables = builder.parse_template(template)
        
        # Then: Should extract the correct variables
        assert variables == ["Role", "What", "Why"]
    
    def test_can_generate_ui_components(self):
        """Test generating UI components from a template."""
        # Given: A template builder and template
        builder = TemplateBuilderImpl()
        template = "As a [Role], I want to [What]"
        
        # When: Generating UI components
        components = builder.generate_ui_components(template)
        
        # Then: Should generate correct number of components
        assert len(components) == 2
        assert components[0]["tag"] == "Role"
        assert components[1]["tag"] == "What"
        assert components[0]["enabled"] is True  # First component enabled
        assert components[1]["enabled"] is False  # Second component disabled
    
    def test_can_update_cascading_state(self):
        """Test updating cascading state when a component changes."""
        # Given: A template builder and components
        builder = TemplateBuilderImpl()
        template = "As a [Role], I want to [What], so that [Why]"
        components = builder.generate_ui_components(template)
        
        # Set some values
        components[0]["value"] = "Manager"
        components[1]["value"] = "Review Code"
        
        # When: Updating cascading state (changing first component)
        updated_components = builder.update_cascading_state(components, 0)
        
        # Then: Downstream components should be reset
        assert updated_components[0]["value"] == "Manager"  # Changed component keeps value
        assert updated_components[1]["value"] == ""  # Downstream component reset
        assert updated_components[2]["value"] == ""  # Downstream component reset
        assert updated_components[1]["enabled"] is True  # Next component enabled
        assert updated_components[2]["enabled"] is False  # Further component disabled
    
    def test_can_generate_final_prompt(self):
        """Test generating final prompt from template and selections."""
        # Given: A template builder, template, and component selections
        builder = TemplateBuilderImpl()
        template = "As a [Role], I want to [What], so that [Why]"
        components = [
            {"tag": "Role", "value": "Manager"},
            {"tag": "What", "value": "Review Code"},
            {"tag": "Why", "value": "Ensure Quality"}
        ]
        
        # When: Generating final prompt
        final_prompt = builder.generate_final_prompt(template, components)
        
        # Then: Should generate correct prompt
        expected = "As a Manager, I want to Review Code, so that Ensure Quality"
        assert final_prompt == expected


class TestComboBoxComponent:
    """Test the combo box component implementation."""
    
    def test_can_create_combo_box_component(self):
        """Test creating a combo box component."""
        # Given: A combo box component
        component = ComboBoxComponent("Role", 0, enabled=True)
        
        # Then: Should be an instance of the interface
        assert isinstance(component, UIComponentInterface)
        assert component.get_component_type() == "combo_box"
        assert component.is_enabled() is True
    
    def test_can_get_component_config(self):
        """Test getting component configuration."""
        # Given: A combo box component
        component = ComboBoxComponent("Role", 0, enabled=True)
        component.value = "Manager"
        component.options = ["Manager", "Developer", "Designer"]
        
        # When: Getting component config
        config = component.get_component_config()
        
        # Then: Should return correct configuration
        assert config["tag"] == "Role"
        assert config["index"] == 0
        assert config["enabled"] is True
        assert config["value"] == "Manager"
        assert config["options"] == ["Manager", "Developer", "Designer"]
    
    def test_can_toggle_enabled_state(self):
        """Test toggling the enabled state of a component."""
        # Given: A disabled combo box component
        component = ComboBoxComponent("Role", 0, enabled=False)
        assert component.is_enabled() is False
        
        # When: Enabling the component
        component.set_enabled(True)
        
        # Then: Should be enabled
        assert component.is_enabled() is True


class TestSimpleTemplateStorage:
    """Test the simple template storage implementation."""
    
    def test_can_create_template_storage(self):
        """Test creating template storage."""
        # Given: A template storage
        storage = SimpleTemplateStorage()
        
        # Then: Should be an instance of the interface
        assert isinstance(storage, TemplateStorageInterface)
    
    def test_can_save_and_load_template(self):
        """Test saving and loading a template."""
        # Given: A template storage
        storage = SimpleTemplateStorage()
        template = "As a [Role], I want to [What]"
        
        # When: Saving a template
        success = storage.save_template("User Story", template)
        
        # Then: Should save successfully
        assert success is True
        
        # When: Loading the template
        loaded_template = storage.load_template("User Story")
        
        # Then: Should load the correct template
        assert loaded_template == template
    
    def test_can_list_templates(self):
        """Test listing saved templates."""
        # Given: A template storage with saved templates
        storage = SimpleTemplateStorage()
        storage.save_template("Template 1", "Template 1 content")
        storage.save_template("Template 2", "Template 2 content")
        
        # When: Listing templates
        templates = storage.list_templates()
        
        # Then: Should return all template names
        assert "Template 1" in templates
        assert "Template 2" in templates
        assert len(templates) == 2
    
    def test_can_delete_template(self):
        """Test deleting a template."""
        # Given: A template storage with a saved template
        storage = SimpleTemplateStorage()
        storage.save_template("To Delete", "Template content")
        assert "To Delete" in storage.list_templates()
        
        # When: Deleting the template
        success = storage.delete_template("To Delete")
        
        # Then: Should delete successfully
        assert success is True
        assert "To Delete" not in storage.list_templates()
        assert storage.load_template("To Delete") is None
    
    def test_delete_nonexistent_template_returns_false(self):
        """Test deleting a template that doesn't exist."""
        # Given: A template storage
        storage = SimpleTemplateStorage()
        
        # When: Deleting a non-existent template
        success = storage.delete_template("Non Existent")
        
        # Then: Should return False
        assert success is False
