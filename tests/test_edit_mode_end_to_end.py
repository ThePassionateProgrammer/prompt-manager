"""
Test Edit Mode End-to-End Functionality

Tests the complete edit mode functionality from UI to server.
"""

import pytest
import json
from src.prompt_manager.web.app import create_app


class TestEditModeEndToEnd:
    """Test edit mode end-to-end functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_template_builder_page_loads(self):
        """Test that template builder page loads correctly."""
        response = self.client.get('/template-builder')
        
        assert response.status_code == 200
        assert b'Template Builder' in response.data
        assert b'edit-mode-toggle' in response.data
        assert b'Edit Mode: OFF' in response.data
    
    def test_template_builder_has_edit_mode_button(self):
        """Test that template builder has edit mode toggle button."""
        response = self.client.get('/template-builder')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have edit mode toggle button
        assert 'id="edit-mode-toggle"' in html_content
        assert 'btn btn-outline-warning' in html_content
        assert 'Edit Mode: OFF' in html_content
        
        # Should have toggle function
        assert 'function toggleEditMode()' in html_content
        assert 'updateEditModeButton()' in html_content
    
    def test_template_builder_has_generate_button(self):
        """Test that template builder has generate combo boxes button."""
        response = self.client.get('/template-builder')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have generate button
        assert 'id="generate-combo-boxes"' in html_content
        assert 'Generate Combo Boxes' in html_content
        
        # Should have generate function
        assert 'function generateComboBoxes()' in html_content
    
    def test_template_builder_has_example_template(self):
        """Test that template builder has example template loaded."""
        response = self.client.get('/template-builder')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have example template in textarea (check for key parts)
        assert 'As a [Role]' in html_content
        assert '[What]' in html_content
        assert '[Why]' in html_content
    
    def test_template_builder_has_custom_combo_box_styling(self):
        """Test that template builder has custom combo box styling."""
        response = self.client.get('/template-builder')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have custom combo box styling
        assert 'border-warning bg-light' in html_content
        assert 'Custom combo box with linkages' in html_content
        assert 'is_custom' in html_content
