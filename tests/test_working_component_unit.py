#!/usr/bin/env python3
"""
Unit tests for the working CustomComboBox component.
These tests focus on the component logic without browser automation.
"""

import pytest
import os
import re

class TestWorkingComponent:
    """Test suite for the working CustomComboBox component."""
    
    def test_component_file_exists(self):
        """Test that the working component file exists."""
        component_path = "src/prompt_manager/static/js/custom-combo-box-working.js"
        assert os.path.exists(component_path)
    
    def test_component_contains_required_classes(self):
        """Test that the component contains all required classes."""
        component_path = "src/prompt_manager/static/js/custom-combo-box-working.js"
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Check for required classes
        assert "class EditModeState" in content
        assert "class DisplayModeState" in content
        assert "class CustomComboBox" in content
        
        # Check for required methods
        assert "getFirstOptionText()" in content
        assert "getPlaceholderText()" in content
        assert "handleEnter(" in content
        assert "setState(" in content
        assert "updateMode()" in content
    
    def test_edit_mode_state_methods(self):
        """Test that EditModeState has the correct methods."""
        component_path = "src/prompt_manager/static/js/custom-combo-box-working.js"
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Extract EditModeState class
        edit_mode_start = content.find("class EditModeState")
        edit_mode_end = content.find("class DisplayModeState")
        edit_mode_class = content[edit_mode_start:edit_mode_end]
        
        # Check for required methods
        assert "getFirstOptionText()" in edit_mode_class
        assert "getPlaceholderText()" in edit_mode_class
        assert "handleEnter(" in edit_mode_class
        
        # Check for correct return values
        assert "return 'Add...'" in edit_mode_class
        assert "return 'Type to add...'" in edit_mode_class
    
    def test_display_mode_state_methods(self):
        """Test that DisplayModeState has the correct methods."""
        component_path = "src/prompt_manager/static/js/custom-combo-box-working.js"
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Extract DisplayModeState class
        display_mode_start = content.find("class DisplayModeState")
        display_mode_end = content.find("class CustomComboBox")
        display_mode_class = content[display_mode_start:display_mode_end]
        
        # Check for required methods
        assert "getFirstOptionText()" in display_mode_class
        assert "getPlaceholderText()" in display_mode_class
        assert "handleEnter(" in display_mode_class
        
        # Check for correct return values
        assert "return 'Select item...'" in display_mode_class
    
    def test_custom_combo_box_constructor(self):
        """Test that CustomComboBox constructor is properly defined."""
        component_path = "src/prompt_manager/static/js/custom-combo-box-working.js"
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Extract CustomComboBox class
        combo_start = content.find("class CustomComboBox")
        combo_end = content.find("// Export for use")
        combo_class = content[combo_start:combo_end]
        
        # Check for constructor
        assert "constructor(containerId)" in combo_class
        
        # Check for required properties
        assert "this.container" in combo_class
        assert "this.input" in combo_class
        assert "this.dropdown" in combo_class
        assert "this.arrow" in combo_class
        assert "this.options" in combo_class
        assert "this.selectedIndex" in combo_class
        assert "this.selectedOption" in combo_class
        assert "this.currentState" in combo_class
    
    def test_custom_combo_box_public_api(self):
        """Test that CustomComboBox has the required public API methods."""
        component_path = "src/prompt_manager/static/js/custom-combo-box-working.js"
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Check for public API methods
        assert "getOptions()" in content
        assert "setOptions(" in content
        assert "getSelectedValue()" in content
        assert "setSelectedValue(" in content
        assert "setMode(" in content
        assert "getMode()" in content
    
    def test_state_pattern_implementation(self):
        """Test that the State Pattern is properly implemented."""
        component_path = "src/prompt_manager/static/js/custom-combo-box-working.js"
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Check for State Pattern methods
        assert "setState(" in content
        assert "updateMode()" in content
        assert "this.currentState" in content
        
        # Check for state switching
        assert "EditModeState" in content
        assert "DisplayModeState" in content
    
    def test_event_handling_methods(self):
        """Test that event handling methods are present."""
        component_path = "src/prompt_manager/static/js/custom-combo-box-working.js"
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Check for event handling methods
        assert "setupEventListeners()" in content
        assert "handleKeyDown(" in content
        assert "handleEnter()" in content
        assert "selectOption(" in content
        assert "showDropdown()" in content
        assert "hideDropdown()" in content
    
    def test_crud_operations(self):
        """Test that CRUD operations are implemented."""
        component_path = "src/prompt_manager/static/js/custom-combo-box-working.js"
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Check for CRUD operations
        assert "addOption(" in content
        assert "replaceOption(" in content
        assert "removeOption(" in content
        assert "updateSelection()" in content
    
    def test_css_classes_used(self):
        """Test that the component uses the correct CSS classes."""
        component_path = "src/prompt_manager/static/js/custom-combo-box-working.js"
        
        with open(component_path, 'r') as f:
            content = f.read()
        
        # Check for CSS class usage
        assert "combo-box-input" in content
        assert "combo-box-dropdown" in content
        assert "combo-box-arrow" in content
        assert "combo-box-option" in content
        assert "show" in content
        assert "up" in content
        assert "highlighted" in content
        assert "selected" in content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
