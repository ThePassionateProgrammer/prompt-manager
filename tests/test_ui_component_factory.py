"""
Tests for UI Component Factory

Tests the factory pattern for creating UI components.
"""

import pytest
from src.prompt_manager.business.ui_component_factory import UIComponentFactory, ComponentConfiguration
from src.prompt_manager.business.template_builder_interface import UIComponentInterface


class TestUIComponentFactory:
    """Test the UI component factory."""
    
    def test_can_create_factory(self):
        """Test creating a UI component factory."""
        # Given: A UI component factory
        factory = UIComponentFactory()
        
        # Then: Should have default component types
        assert "combo_box" in factory.get_available_component_types()
        assert "text_input" in factory.get_available_component_types()
        assert "dropdown" in factory.get_available_component_types()
        assert "checkbox" in factory.get_available_component_types()
    
    def test_can_create_combo_box_component(self):
        """Test creating a combo box component through the factory."""
        # Given: A UI component factory
        factory = UIComponentFactory()
        
        # When: Creating a combo box component
        component = factory.create_component("combo_box", tag="Role", index=0, enabled=True)
        
        # Then: Should be a valid component
        assert isinstance(component, UIComponentInterface)
        assert component.get_component_type() == "combo_box"
        assert component.is_enabled() is True
    
    def test_can_create_combo_box_with_defaults(self):
        """Test creating a combo box component with default values."""
        # Given: A UI component factory
        factory = UIComponentFactory()
        
        # When: Creating a combo box component with minimal parameters
        component = factory.create_component("combo_box", tag="Test")
        
        # Then: Should use default values
        assert component.get_component_type() == "combo_box"
        assert component.is_enabled() is False  # Default is False
        config = component.get_component_config()
        assert config["index"] == 0  # Default index
        assert config["tag"] == "Test"
    
    def test_unknown_component_type_raises_error(self):
        """Test that creating an unknown component type raises an error."""
        # Given: A UI component factory
        factory = UIComponentFactory()
        
        # When/Then: Creating an unknown component type should raise an error
        with pytest.raises(ValueError, match="Unknown component type: unknown_type"):
            factory.create_component("unknown_type")
    
    def test_can_register_new_component_type(self):
        """Test registering a new component type."""
        # Given: A UI component factory and a custom component
        factory = UIComponentFactory()
        
        def create_custom_component(**kwargs):
            class CustomComponent(UIComponentInterface):
                def get_component_type(self):
                    return "custom"
                
                def get_component_config(self):
                    return {"custom": True}
                
                def is_enabled(self):
                    return True
                
                def set_enabled(self, enabled):
                    pass
            
            return CustomComponent()
        
        # When: Registering the new component type
        factory.register_component_type("custom", create_custom_component)
        
        # Then: Should be able to create the custom component
        assert "custom" in factory.get_available_component_types()
        component = factory.create_component("custom")
        assert component.get_component_type() == "custom"
    
    def test_unimplemented_component_types_raise_error(self):
        """Test that unimplemented component types raise NotImplementedError."""
        # Given: A UI component factory
        factory = UIComponentFactory()
        
        # When/Then: Creating unimplemented component types should raise errors
        with pytest.raises(NotImplementedError):
            factory.create_component("text_input")
        
        with pytest.raises(NotImplementedError):
            factory.create_component("dropdown")
        
        with pytest.raises(NotImplementedError):
            factory.create_component("checkbox")


class TestComponentConfiguration:
    """Test the component configuration class."""
    
    def test_can_create_component_configuration(self):
        """Test creating a component configuration."""
        # Given: A component configuration
        config = ComponentConfiguration("combo_box", {"tag": "Role", "enabled": True})
        
        # Then: Should have correct values
        assert config.component_type == "combo_box"
        assert config.get("tag") == "Role"
        assert config.get("enabled") is True
    
    def test_can_get_config_with_default(self):
        """Test getting configuration values with defaults."""
        # Given: A component configuration
        config = ComponentConfiguration("combo_box", {"tag": "Role"})
        
        # When: Getting a value that doesn't exist
        value = config.get("nonexistent", "default_value")
        
        # Then: Should return the default value
        assert value == "default_value"
    
    def test_can_set_config_value(self):
        """Test setting configuration values."""
        # Given: A component configuration
        config = ComponentConfiguration("combo_box", {"tag": "Role"})
        
        # When: Setting a new value
        config.set("enabled", True)
        
        # Then: Should have the new value
        assert config.get("enabled") is True
    
    def test_can_convert_to_dict(self):
        """Test converting configuration to dictionary."""
        # Given: A component configuration
        config = ComponentConfiguration("combo_box", {"tag": "Role", "enabled": True})
        
        # When: Converting to dictionary
        config_dict = config.to_dict()
        
        # Then: Should have correct structure
        assert config_dict["component_type"] == "combo_box"
        assert config_dict["config"]["tag"] == "Role"
        assert config_dict["config"]["enabled"] is True
