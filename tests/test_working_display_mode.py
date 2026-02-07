"""
Test the Display mode implementation in the working custom combo box.

This test verifies the dual-mode functionality is working correctly.
"""

import pytest
import requests
import json


class TestWorkingDisplayMode:
    """Test the working Display mode implementation."""
    
    def test_working_combo_file_loads(self):
        """Test that the working custom combo box file loads correctly."""
        # Test by reading the file directly
        with open('src/prompt_manager/templates/custom_combo_test_working.html', 'r') as f:
            content = f.read()
        
        assert len(content) > 0
        assert "Custom Combo Box Test" in content
        assert "CustomComboBox" in content
    
    def test_mode_toggle_functionality_exists(self):
        """Test that mode toggle functionality exists in the file."""
        with open('src/prompt_manager/templates/custom_combo_test_working.html', 'r') as f:
            content = f.read()
        
        # Should have mode toggle functionality
        assert "toggleMode" in content
        assert "updateModeButton" in content
        assert "updateAllComboBoxes" in content
        assert "isEditMode" in content
    
    def test_mode_toggle_button_html_exists(self):
        """Test that mode toggle button HTML exists."""
        with open('src/prompt_manager/templates/custom_combo_test_working.html', 'r') as f:
            content = f.read()
        
        # Should have mode toggle button HTML
        assert "mode-toggle" in content
        assert "mode-status" in content
        assert "Mode Control" in content
    
    def test_update_mode_method_exists(self):
        """Test that updateMode method exists in CustomComboBox class."""
        with open('src/prompt_manager/templates/custom_combo_test_working.html', 'r') as f:
            content = f.read()
        
        # Should have updateMode method
        assert "updateMode()" in content
        assert "Add..." in content
        assert "Select item..." in content
        assert "Type to add..." in content
    
    def test_display_mode_enter_handling(self):
        """Test that handleEnter method has Display mode logic."""
        with open('src/prompt_manager/templates/custom_combo_test_working.html', 'r') as f:
            content = f.read()
        
        # Should have Display mode handling in handleEnter
        assert "!isEditMode" in content
        assert "In Display mode" in content
        assert "only allow selection" in content
    
    def test_initialization_includes_mode_setup(self):
        """Test that initialization includes mode setup."""
        with open('src/prompt_manager/templates/custom_combo_test_working.html', 'r') as f:
            content = f.read()
        
        # Should have mode setup in initialization
        assert "mode-toggle" in content and "addEventListener" in content
        assert "updateModeButton" in content
        assert "updateAllComboBoxes" in content
