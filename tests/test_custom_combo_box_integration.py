"""
Tests for Custom Combo Box Integration

Tests integrating our custom combo box system with the new abstractions.
This follows the Red-Green-Refactor cycle for integration.
"""

import pytest
import json
import os
from src.prompt_manager.business.template_builder_interface import TemplateBuilderInterface
from src.prompt_manager.business.ui_component_factory import UIComponentFactory
from src.prompt_manager.business.component_event_system import EventBus, EventType, ComponentEvent
from src.prompt_manager.business.template_builder_impl import TemplateBuilderImpl
from src.prompt_manager.business.custom_combo_box_integration import CustomComboBoxIntegration


class TestCustomComboBoxIntegration:
    """Test integrating custom combo box with new abstractions."""
    
    def test_can_integrate_custom_combo_box_with_template_builder(self):
        """Test that custom combo box can be integrated with template builder."""
        # Given: A template builder and custom combo box system
        template_builder = TemplateBuilderImpl()
        event_bus = EventBus()
        component_factory = UIComponentFactory()
        
        # When: Creating a template with custom combo boxes
        template = "As a [Role], I want to [What], so that [Why]"
        components = template_builder.generate_ui_components(template)
        
        # Then: Should generate combo box components
        assert len(components) == 3
        assert components[0]["tag"] == "Role"
        assert components[1]["tag"] == "What"
        assert components[2]["tag"] == "Why"
    
    def test_custom_combo_box_can_trigger_cascading_events(self):
        """Test that custom combo box changes trigger cascading events."""
        # Given: Event bus and custom combo box system
        event_bus = EventBus()
        received_events = []
        
        def event_listener(event):
            received_events.append(event)
        
        event_bus.subscribe(EventType.COMPONENT_CHANGED, event_listener)
        
        # When: Simulating a custom combo box change
        combo_box_event = ComponentEvent(
            EventType.COMPONENT_CHANGED,
            "role_combo_box",
            {"value": "Manager", "index": 0}
        )
        event_bus.publish(combo_box_event)
        
        # Then: Should receive the event
        assert len(received_events) == 1
        assert received_events[0].source_component_id == "role_combo_box"
        assert received_events[0].data["value"] == "Manager"
    
    def test_custom_combo_box_can_update_cascading_state(self):
        """Test that custom combo box updates trigger cascading state changes."""
        # Given: Template builder and event system
        template_builder = TemplateBuilderImpl()
        event_bus = EventBus()
        
        # When: Updating a component and triggering cascade
        template = "As a [Role], I want to [What], so that [Why]"
        components = template_builder.generate_ui_components(template)
        
        # Simulate changing the first component
        updated_components = template_builder.update_cascading_state(components, 0)
        
        # Then: Downstream components should be reset
        assert updated_components[0]["enabled"] is True  # First component stays enabled
        assert updated_components[1]["enabled"] is True  # Second component becomes enabled
        assert updated_components[2]["enabled"] is False  # Third component stays disabled
        assert updated_components[1]["value"] == ""  # Second component value reset
        assert updated_components[2]["value"] == ""  # Third component value reset
    
    def test_custom_combo_box_can_generate_final_prompt(self):
        """Test that custom combo box selections can generate final prompt."""
        # Given: Template builder with custom combo box selections
        template_builder = TemplateBuilderImpl()
        template = "As a [Role], I want to [What], so that [Why]"
        
        # Simulate combo box selections
        components = [
            {"tag": "Role", "value": "Manager"},
            {"tag": "What", "value": "Review Code"},
            {"tag": "Why", "value": "Ensure Quality"}
        ]
        
        # When: Generating final prompt
        final_prompt = template_builder.generate_final_prompt(template, components)
        
        # Then: Should generate correct prompt
        expected = "As a Manager, I want to Review Code, so that Ensure Quality"
        assert final_prompt == expected
    
    def test_custom_combo_box_integration_with_n_level_cascading(self):
        """Test that custom combo box supports N-level cascading from our test system."""
        # Given: Template with multiple levels
        template_builder = TemplateBuilderImpl()
        template = "When [User] visits [Page], they should see [Content] and be able to [Action]"
        
        # When: Generating components for N-level template
        components = template_builder.generate_ui_components(template)
        
        # Then: Should support N-level cascading
        assert len(components) == 4
        assert components[0]["tag"] == "User"
        assert components[1]["tag"] == "Page"
        assert components[2]["tag"] == "Content"
        assert components[3]["tag"] == "Action"
        
        # Test cascading behavior
        updated_components = template_builder.update_cascading_state(components, 1)
        assert updated_components[2]["enabled"] is True  # Next component enabled
        assert updated_components[3]["enabled"] is False  # Further component disabled
    
    def test_custom_combo_box_persistent_state_integration(self):
        """Test that custom combo box state persistence works with new abstractions."""
        # Given: Event bus and state management
        event_bus = EventBus()
        from src.prompt_manager.business.component_event_system import CascadingEventHandler
        
        cascading_handler = CascadingEventHandler(event_bus)
        
        # When: Setting component state
        component_id = "role_combo_box"
        state = {"value": "Manager", "enabled": True, "options": ["Manager", "Developer"]}
        cascading_handler.set_component_state(component_id, state)
        
        # Then: Should persist state
        retrieved_state = cascading_handler.get_component_state(component_id)
        assert retrieved_state["value"] == "Manager"
        assert retrieved_state["enabled"] is True
        assert retrieved_state["options"] == ["Manager", "Developer"]
    
    def test_custom_combo_box_factory_integration(self):
        """Test that custom combo box can be created through the factory."""
        # Given: Component factory
        component_factory = UIComponentFactory()
        
        # When: Creating custom combo box through factory
        combo_box = component_factory.create_component(
            "combo_box",
            tag="Role",
            index=0,
            enabled=True
        )
        
        # Then: Should create valid combo box
        assert combo_box.get_component_type() == "combo_box"
        assert combo_box.is_enabled() is True
        config = combo_box.get_component_config()
        assert config["tag"] == "Role"
        assert config["index"] == 0
    
    def test_real_custom_combo_box_data_integration(self):
        """Test integration with real custom combo box data from our test system."""
        # Given: Real relationship data from our test system
        relationships_data = {
            "Manager": {
                "Review Status": ["Evaluate Next Actions", "Review Performance"],
                "File Compliance Report": ["Keep Higher-ups Informed", "Meet Standards"]
            },
            "Programmer": {
                "Code Review": ["Keep Code Clean", "Propagate Good Practices"],
                "Test Plan": ["Ensure Quality", "Prevent Bugs"]
            },
            "Fitness Coach": {
                "Create Client Meal Plan": ["Improve Health", "Achieve Goals"],
                "Work Out": ["Build Strength", "Increase Endurance"]
            }
        }
        
        # When: Creating template builder with real data
        template_builder = TemplateBuilderImpl()
        template = "As a [Role], I want to [What], so that [Why]"
        components = template_builder.generate_ui_components(template)
        
        # Simulate real user interactions
        # User selects "Manager" in Role combo box
        components[0]["value"] = "Manager"
        components[0]["options"] = list(relationships_data.keys())
        
        # Update cascading state
        updated_components = template_builder.update_cascading_state(components, 0)
        
        # Then: Should enable next component and populate options
        assert updated_components[1]["enabled"] is True
        assert updated_components[1]["value"] == ""  # Reset
        
        # Simulate user selecting "Review Status" in What combo box
        updated_components[1]["value"] = "Review Status"
        updated_components[1]["options"] = list(relationships_data["Manager"].keys())
        
        # Update cascading state again
        final_components = template_builder.update_cascading_state(updated_components, 1)
        
        # Then: Should enable final component and populate options
        assert final_components[2]["enabled"] is True
        assert final_components[2]["value"] == ""  # Reset
        assert final_components[2]["options"] == relationships_data["Manager"]["Review Status"]
    
    def test_custom_combo_box_with_template_parsing_integration(self):
        """Test that our template parsing works with custom combo box system."""
        # Given: Template builder and various templates
        template_builder = TemplateBuilderImpl()
        
        # Test different template formats
        templates = [
            "As a [Role], I want to [What], so that [Why]",
            "When [User] visits [Page], they should see [Content]",
            "If [Condition] then [Action] else [Alternative]",
            "The [Subject] should [Verb] the [Object]"
        ]
        
        # When: Parsing each template
        for template in templates:
            components = template_builder.generate_ui_components(template)
            
            # Then: Should generate correct number of components
            expected_variables = template_builder.parse_template(template)
            assert len(components) == len(expected_variables)
            
            # And: Each component should have correct tag
            for i, component in enumerate(components):
                assert component["tag"] == expected_variables[i]
    
    def test_custom_combo_box_state_persistence_with_real_data(self):
        """Test state persistence with real custom combo box data."""
        # Given: Event system and real data
        event_bus = EventBus()
        from src.prompt_manager.business.component_event_system import CascadingEventHandler, ComponentEventLogger
        
        cascading_handler = CascadingEventHandler(event_bus)
        event_logger = ComponentEventLogger()
        
        # Subscribe logger to events
        event_bus.subscribe(EventType.COMPONENT_CHANGED, event_logger.log_event)
        
        # When: Simulating real user interactions
        interactions = [
            ("role_combo_box", "Manager"),
            ("what_combo_box", "Review Status"),
            ("why_combo_box", "Evaluate Next Actions")
        ]
        
        for component_id, value in interactions:
            event = ComponentEvent(
                EventType.COMPONENT_CHANGED,
                component_id,
                {"value": value, "timestamp": "2025-08-20T15:30:00Z"}
            )
            # Publish event directly to event bus
            event_bus.publish(event)
            # Also handle with cascading handler
            cascading_handler.handle_component_changed(event)
        
        # Then: Should have logged all events
        recent_events = event_logger.get_recent_events()
        assert len(recent_events) == 3
        
        # And: Should have state for all components
        for component_id, value in interactions:
            state = cascading_handler.get_component_state(component_id)
            assert state["value"] == value


class TestFinalIntegration:
    """Test the final integration layer that connects everything together."""
    
    def test_can_create_custom_combo_box_integration(self):
        """Test creating the final integration layer."""
        # Given: Custom combo box integration
        integration = CustomComboBoxIntegration()
        
        # Then: Should be created successfully
        assert integration.template_builder is not None
        assert integration.component_factory is not None
        assert integration.event_bus is not None
        assert integration.cascading_handler is not None
    
    def test_can_create_template_with_custom_combo_boxes(self):
        """Test creating a template with custom combo boxes."""
        # Given: Custom combo box integration
        integration = CustomComboBoxIntegration()
        template = "As a [Role], I want to [What], so that [Why]"
        
        # When: Creating template with custom combo boxes
        result = integration.create_template_with_custom_combo_boxes(template)
        
        # Then: Should return correct structure
        assert result["template"] == template
        assert len(result["combo_boxes"]) == 3
        assert result["variables"] == ["Role", "What", "Why"]
        
        # And: Combo boxes should have correct structure
        for i, combo_box in enumerate(result["combo_boxes"]):
            assert combo_box["tag"] == result["variables"][i]
            assert combo_box["index"] == i
            assert combo_box["enabled"] == (i == 0)  # Only first enabled
    
    def test_can_handle_combo_box_change(self):
        """Test handling combo box changes through integration."""
        # Given: Custom combo box integration and template
        integration = CustomComboBoxIntegration()
        template = "As a [Role], I want to [What], so that [Why]"
        result = integration.create_template_with_custom_combo_boxes(template)
        combo_boxes = result["combo_boxes"]
        
        # When: Handling a combo box change
        updated_combo_boxes = integration.handle_combo_box_change(
            "Role", "Manager", combo_boxes
        )
        
        # Then: Should update the combo box value
        assert updated_combo_boxes[0]["value"] == "Manager"
        
        # And: Should enable next component
        assert updated_combo_boxes[1]["enabled"] is True
    
    def test_can_generate_final_prompt_through_integration(self):
        """Test generating final prompt through integration."""
        # Given: Custom combo box integration and template with selections
        integration = CustomComboBoxIntegration()
        template = "As a [Role], I want to [What], so that [Why]"
        result = integration.create_template_with_custom_combo_boxes(template)
        combo_boxes = result["combo_boxes"]
        
        # Set values
        combo_boxes[0]["value"] = "Manager"
        combo_boxes[1]["value"] = "Review Code"
        combo_boxes[2]["value"] = "Ensure Quality"
        
        # When: Generating final prompt
        final_prompt = integration.generate_final_prompt(template, combo_boxes)
        
        # Then: Should generate correct prompt
        expected = "As a Manager, I want to Review Code, so that Ensure Quality"
        assert final_prompt == expected
    
    def test_can_validate_templates(self):
        """Test template validation through integration."""
        # Given: Custom combo box integration
        integration = CustomComboBoxIntegration()
        
        # When: Validating a valid template
        valid_template = "As a [Role], I want to [What], so that [Why]"
        validation = integration.validate_template(valid_template)
        
        # Then: Should be valid
        assert validation["valid"] is True
        assert validation["variables"] == ["Role", "What", "Why"]
        assert validation["component_count"] == 3
        assert validation["within_limits"] is True
        
        # When: Validating an invalid template (too many variables)
        invalid_template = "[" + "][".join([f"Var{i}" for i in range(20)]) + "]"
        validation = integration.validate_template(invalid_template)
        
        # Then: Should be invalid
        assert validation["valid"] is True  # Still valid, just too many variables
        assert validation["within_limits"] is False
    
    def test_can_export_and_import_template_config(self):
        """Test exporting and importing template configurations."""
        # Given: Custom combo box integration and template
        integration = CustomComboBoxIntegration()
        template = "As a [Role], I want to [What], so that [Why]"
        result = integration.create_template_with_custom_combo_boxes(template)
        combo_boxes = result["combo_boxes"]
        
        # When: Exporting template configuration
        exported_config = integration.export_template_config(template, combo_boxes)
        
        # Then: Should have correct structure
        assert exported_config["template"] == template
        assert exported_config["combo_boxes"] == combo_boxes
        assert exported_config["variables"] == ["Role", "What", "Why"]
        assert exported_config["version"] == "1.0"
        assert exported_config["integration_type"] == "custom_combo_box"
        
        # When: Importing template configuration
        imported_result = integration.import_template_config(exported_config)
        
        # Then: Should match original
        assert imported_result["template"] == template
        assert imported_result["combo_boxes"] == combo_boxes
        assert imported_result["variables"] == ["Role", "What", "Why"]
    
    def test_can_get_available_templates(self):
        """Test getting available templates through integration."""
        # Given: Custom combo box integration
        integration = CustomComboBoxIntegration()
        
        # When: Getting available templates
        templates = integration.get_available_templates()
        
        # Then: Should return list of templates
        assert len(templates) == 4
        assert "As a [Role], I want to [What], so that [Why]" in templates
        assert "When [User] visits [Page], they should see [Content] and be able to [Action]" in templates
        assert "If [Condition] then [Action] else [Alternative]" in templates
        assert "The [Subject] should [Verb] the [Object]" in templates
    
    def test_can_manage_component_state_through_integration(self):
        """Test managing component state through integration."""
        # Given: Custom combo box integration
        integration = CustomComboBoxIntegration()
        component_id = "role_combo_box"
        state = {"value": "Manager", "enabled": True, "options": ["Manager", "Developer"]}
        
        # When: Setting component state
        integration.set_component_state(component_id, state)
        
        # Then: Should be able to retrieve state
        retrieved_state = integration.get_component_state(component_id)
        assert retrieved_state["value"] == "Manager"
        assert retrieved_state["enabled"] is True
        assert retrieved_state["options"] == ["Manager", "Developer"]

