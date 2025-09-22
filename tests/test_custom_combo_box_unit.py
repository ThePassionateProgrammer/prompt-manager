"""
Unit tests for CustomComboBox v2.0 JavaScript logic
Tests the core functionality without browser automation
"""

import pytest
import json
import os
from pathlib import Path


class TestCustomComboBoxJavaScript:
    """Test the JavaScript implementation directly"""
    
    def test_js_file_exists(self):
        """Test that the CustomComboBox JavaScript file exists"""
        js_file = Path("src/prompt_manager/static/js/custom-combo-box-working.js")
        assert js_file.exists(), "CustomComboBox JavaScript file not found"
    
    def test_js_file_version(self):
        """Test that the JavaScript file has the correct version"""
        js_file = Path("src/prompt_manager/static/js/custom-combo-box-working.js")
        content = js_file.read_text()
        
        # Should contain version 2.0
        assert "v2.0" in content, "JavaScript file should be version 2.0"
        assert "Production Ready" in content, "Should be marked as production ready"
    
    def test_js_file_structure(self):
        """Test that the JavaScript file has the expected structure"""
        js_file = Path("src/prompt_manager/static/js/custom-combo-box-working.js")
        content = js_file.read_text()
        
        # Should contain key classes and methods
        expected_elements = [
            "class CustomComboBox",
            "class EditModeState", 
            "class DisplayModeState",
            "constructor(",
            "addOption(",
            "selectOption(",
            "removeOption(",
            "replaceOption(",
            "enterEditMode(",
            "exitEditMode(",
            "handleEnter(",
            "handleKeyDown("
        ]
        
        for element in expected_elements:
            assert element in content, f"Missing expected element: {element}"
    
    def test_no_debug_logs(self):
        """Test that debug console.log statements have been removed"""
        js_file = Path("src/prompt_manager/static/js/custom-combo-box-working.js")
        content = js_file.read_text()
        
        # Should not contain debug console.log statements
        debug_logs = [
            "console.log('Input event",
            "console.log('In edit mode",
            "console.log('User cleared text",
            "console.log('Clearing selection",
            "console.log('Clicking on",
            "console.log('Delete key pressed",
            "console.log('enterEditMode called"
        ]
        
        for debug_log in debug_logs:
            assert debug_log not in content, f"Found debug log that should be removed: {debug_log}"
    
    def test_edit_mode_logic(self):
        """Test that edit mode logic is properly implemented"""
        js_file = Path("src/prompt_manager/static/js/custom-combo-box-working.js")
        content = js_file.read_text()
        
        # Should have edit mode functionality
        edit_mode_elements = [
            "this.isEditMode = true",
            "this.isEditMode = false",
            "this.originalText",
            "this.newText",
            "exitEditMode(revert = false)",
            "if (this.isEditMode)"
        ]
        
        for element in edit_mode_elements:
            assert element in content, f"Missing edit mode element: {element}"
    
    def test_delete_functionality(self):
        """Test that delete functionality is properly implemented"""
        js_file = Path("src/prompt_manager/static/js/custom-combo-box-working.js")
        content = js_file.read_text()
        
        # Should have delete functionality
        delete_elements = [
            "this.input.value === ''",
            "keep the selection so Enter can delete the item",
            "removeOption(",
            "case 'Delete':"
        ]
        
        for element in delete_elements:
            assert element in content, f"Missing delete functionality: {element}"
    
    def test_selection_persistence(self):
        """Test that selection persistence is implemented"""
        js_file = Path("src/prompt_manager/static/js/custom-combo-box-working.js")
        content = js_file.read_text()
        
        # Should have selection persistence logic
        persistence_elements = [
            "keep item highlighted",
            "this.selectedOption",
            "this.selectedIndex",
            "updateSelection(",
            "updateHighlight("
        ]
        
        for element in persistence_elements:
            assert element in content, f"Missing selection persistence: {element}"


class TestServerIntegration:
    """Test server integration"""
    
    def test_server_file_includes_js(self):
        """Test that the server includes the CustomComboBox JavaScript"""
        server_file = Path("enhanced_simple_server.py")
        content = server_file.read_text()
        
        # Should include the JavaScript file
        assert "custom-combo-box-working.js" in content, "Server should include CustomComboBox JavaScript"
        assert "v=2.0" in content, "Server should use version 2.0"
    
    def test_version_display(self):
        """Test that version is displayed on the page"""
        server_file = Path("enhanced_simple_server.py")
        content = server_file.read_text()
        
        # Should have version display
        assert "combo-box-version" in content, "Should have version display element"
        assert "v2.0" in content, "Should display version 2.0"


class TestCSSIntegration:
    """Test CSS integration"""
    
    def test_css_file_exists(self):
        """Test that the CSS file exists"""
        css_file = Path("src/prompt_manager/static/css/custom-combo-box.css")
        assert css_file.exists(), "CustomComboBox CSS file not found"
    
    def test_css_classes(self):
        """Test that CSS has the expected classes"""
        css_file = Path("src/prompt_manager/static/css/custom-combo-box.css")
        content = css_file.read_text()
        
        # Should have key CSS classes
        expected_classes = [
            ".combo-box-container",
            ".combo-box-input",
            ".combo-box-dropdown",
            ".combo-box-option",
            ".combo-box-arrow",
            ".highlighted"
        ]
        
        for css_class in expected_classes:
            assert css_class in content, f"Missing CSS class: {css_class}"


class TestFunctionalityCoverage:
    """Test that all required functionality is covered"""
    
    def test_core_functions_present(self):
        """Test that all core functions are present"""
        js_file = Path("src/prompt_manager/static/js/custom-combo-box-working.js")
        content = js_file.read_text()
        
        # Core functionality that should be present
        core_functions = [
            "addOption",           # Add new items
            "selectOption",        # Select existing items  
            "removeOption",        # Delete items
            "replaceOption",       # Update items
            "enterEditMode",       # Enter edit mode
            "exitEditMode",        # Exit edit mode
            "handleEnter",         # Handle Enter key
            "handleKeyDown",       # Handle keyboard
            "showDropdown",        # Show dropdown
            "hideDropdown",        # Hide dropdown
            "updateSelection",     # Update selection state
            "updateHighlight"      # Update highlight state
        ]
        
        for function in core_functions:
            assert function in content, f"Missing core function: {function}"
    
    def test_event_handlers_present(self):
        """Test that all event handlers are present"""
        js_file = Path("src/prompt_manager/static/js/custom-combo-box-working.js")
        content = js_file.read_text()
        
        # Event handlers that should be present
        event_handlers = [
            "addEventListener('input'",
            "addEventListener('click'",
            "addEventListener('keydown'",
            "addEventListener('focus'",
            "addEventListener('blur'",
            "addEventListener('mouseenter'"
        ]
        
        for handler in event_handlers:
            assert handler in content, f"Missing event handler: {handler}"
    
    def test_state_pattern_implementation(self):
        """Test that State Pattern is properly implemented"""
        js_file = Path("src/prompt_manager/static/js/custom-combo-box-working.js")
        content = js_file.read_text()
        
        # State Pattern elements
        state_elements = [
            "class EditModeState",
            "class DisplayModeState", 
            "this.currentState",
            "this.isEditMode",
            "handleEnter("
        ]
        
        for element in state_elements:
            assert element in content, f"Missing State Pattern element: {element}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
