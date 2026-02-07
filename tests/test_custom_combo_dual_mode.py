"""
Test Custom Combo Box Dual Mode Functionality

Tests the dual-mode custom combo box behavior (Edit vs Display mode).
"""

import pytest
import json
from src.prompt_manager.web.app import create_app


class TestCustomComboDualMode:
    """Test custom combo box dual mode functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_custom_combo_test_page_loads(self):
        """Test that custom combo test page loads correctly."""
        response = self.client.get('/custom-combo-test')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have test page elements
        assert 'Custom Combo Box Test' in html_content
        assert 'mode-toggle' in html_content
        assert 'Mode: DISPLAY' in html_content
        assert 'generate-test' in html_content
        assert 'run-tests' in html_content
    
    def test_mode_toggle_button_exists(self):
        """Test that mode toggle button exists and has correct initial state."""
        response = self.client.get('/custom-combo-test')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have mode toggle button
        assert 'id="mode-toggle"' in html_content
        assert 'Mode: DISPLAY' in html_content
        assert 'btn btn-outline-warning' in html_content
    
    def test_mode_toggle_functions_exist(self):
        """Test that mode toggle functions are defined."""
        response = self.client.get('/custom-combo-test')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have toggle functions
        assert 'function toggleMode()' in html_content
        assert 'function updateModeButton()' in html_content
        assert 'isEditMode = !isEditMode' in html_content
    
    def test_edit_mode_behavior_functions_exist(self):
        """Test that edit mode behavior functions are defined."""
        response = self.client.get('/custom-combo-test')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have edit mode functions
        assert 'function handleEditModeChange()' in html_content
        assert 'function handleDisplayModeChange()' in html_content
        assert 'function getModeOptions()' in html_content
        assert 'function getModePlaceholder()' in html_content
    
    def test_test_functions_exist(self):
        """Test that test functions are defined."""
        response = self.client.get('/custom-combo-test')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have test functions
        assert 'function runTests()' in html_content
        assert 'function testModeSwitching()' in html_content
        assert 'function testEditModeBehavior()' in html_content
        assert 'function testDisplayModeBehavior()' in html_content
        assert 'function testCascadingBehavior()' in html_content
    
    def test_edit_mode_placeholder_logic(self):
        """Test that edit mode placeholder logic is correct."""
        response = self.client.get('/custom-combo-test')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have placeholder logic
        assert 'Enter ${tag}' in html_content
        assert 'Select ${tag}' in html_content
        assert 'isEditMode' in html_content
    
    def test_display_mode_placeholder_logic(self):
        """Test that display mode placeholder logic is correct."""
        response = self.client.get('/custom-combo-test')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have placeholder logic
        assert 'Enter ${tag}' in html_content
        assert 'Select ${tag}' in html_content
        assert 'isEditMode' in html_content
    
    def test_mode_options_logic(self):
        """Test that mode options logic is correct."""
        response = self.client.get('/custom-combo-test')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have mode options logic
        assert 'Add item' in html_content
        assert 'Select item' in html_content
        assert 'isEditMode' in html_content
    
    def test_cascading_behavior_functions_exist(self):
        """Test that cascading behavior functions are defined."""
        response = self.client.get('/custom-combo-test')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have cascading functions
        assert 'function updateTestCascadingSelections()' in html_content
        assert 'function handleTestComboBoxChange()' in html_content
    
    def test_reset_functionality_exists(self):
        """Test that reset functionality exists."""
        response = self.client.get('/custom-combo-test')
        
        assert response.status_code == 200
        html_content = response.data.decode('utf-8')
        
        # Should have reset functionality
        assert 'function resetTest()' in html_content
        assert 'reset-test' in html_content
        assert 'Reset' in html_content
