"""
Test Edit Mode Toggle Functionality

Tests the edit mode toggle button and its integration with the template builder.
"""

import pytest
import json
from unittest.mock import patch, MagicMock


class TestEditModeToggle:
    """Test edit mode toggle functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.template = "As a [Role], I want to [What], so that [Why]"
    
    def test_edit_mode_toggle_button_exists(self):
        """Test that edit mode toggle button is present in template builder."""
        # This test verifies the button exists in the HTML
        with open('src/prompt_manager/templates/template_builder.html', 'r') as f:
            html_content = f.read()
        
        assert 'id="edit-mode-toggle"' in html_content
        assert 'Edit Mode: OFF' in html_content
        assert 'toggleEditMode' in html_content
    
    def test_edit_mode_toggle_button_styling(self):
        """Test that edit mode toggle button has correct initial styling."""
        with open('src/prompt_manager/templates/template_builder.html', 'r') as f:
            html_content = f.read()
        
        # Should start as outline button
        assert 'btn btn-outline-warning' in html_content
        assert 'Edit Mode: OFF' in html_content
    
    def test_edit_mode_toggle_function_exists(self):
        """Test that toggleEditMode function is defined."""
        with open('src/prompt_manager/templates/template_builder.html', 'r') as f:
            html_content = f.read()
        
        assert 'function toggleEditMode()' in html_content
        assert 'isEditMode = !isEditMode' in html_content
        assert 'updateEditModeButton()' in html_content
    
    def test_edit_mode_toggle_updates_button_text(self):
        """Test that toggleEditMode updates button text correctly."""
        with open('src/prompt_manager/templates/template_builder.html', 'r') as f:
            html_content = f.read()
        
        # Should have logic to update button text
        assert 'Edit Mode: ON' in html_content
        assert 'Edit Mode: OFF' in html_content
        assert 'btn btn-warning' in html_content  # Active state
        assert 'btn btn-outline-warning' in html_content  # Inactive state
    
    def test_edit_mode_passed_to_server(self):
        """Test that edit mode is passed to server when generating combo boxes."""
        with open('src/prompt_manager/templates/template_builder.html', 'r') as f:
            html_content = f.read()
        
        # Should pass edit_mode to server
        assert 'edit_mode: isEditMode' in html_content
        assert '/template/generate' in html_content
    
    def test_edit_mode_regenerates_combo_boxes(self):
        """Test that toggling edit mode regenerates combo boxes if they exist."""
        with open('src/prompt_manager/templates/template_builder.html', 'r') as f:
            html_content = f.read()
        
        # Should regenerate combo boxes when toggling edit mode
        assert 'generateComboBoxes()' in html_content
        assert 'currentTemplate && comboBoxes.length > 0' in html_content
