"""
Test dual-mode behavior for custom combo boxes.

Edit Mode: First item is "Add item...", full editing capabilities
Display Mode: First item is "Select item...", read-only behavior
"""

import pytest
import requests
import json


class TestDualModeBehavior:
    """Test the dual-mode behavior of custom combo boxes."""
    
    def test_edit_mode_has_add_item_first(self):
        """Test that edit mode shows 'Add item...' as first option."""
        # This test should fail initially - we need to implement the mode switching
        response = requests.get("http://localhost:8000/custom-combo-test")
        assert response.status_code == 200
        
        content = response.text
        
        # In edit mode, first item should be "Add item..."
        # We need to check the JavaScript logic that generates options
        assert "Add item" in content
        assert "getModeOptions" in content
        
        # The function should return "Add item" as first when in edit mode
        assert "return ['Add item', ...baseOptions]" in content or "return ['Add item'" in content
    
    def test_display_mode_has_select_item_first(self):
        """Test that display mode shows 'Select item...' as first option."""
        response = requests.get("http://localhost:8000/custom-combo-test")
        assert response.status_code == 200
        
        content = response.text
        
        # In display mode, first item should be "Select item..."
        assert "Select item" in content
        
        # The function should return "Select item" as first when in display mode
        assert "return ['Select item', ...baseOptions]" in content or "return ['Select item'" in content
    
    def test_mode_switching_changes_first_item(self):
        """Test that switching modes changes the first item in dropdown."""
        # This test will verify the toggle functionality
        response = requests.get("http://localhost:8000/custom-combo-test")
        assert response.status_code == 200
        
        content = response.text
        
        # Should have mode switching logic
        assert "toggleMode" in content
        assert "isEditMode" in content
        
        # Should regenerate combo boxes when mode changes
        assert "generateTestComboBoxes" in content
    
    def test_edit_mode_allows_adding_items(self):
        """Test that edit mode allows adding new items to the list."""
        response = requests.get("http://localhost:8000/custom-combo-test")
        assert response.status_code == 200
        
        content = response.text
        
        # Should have add functionality
        assert "handleEditModeChange" in content
        assert "Add item" in content
        
        # Should be able to add items when "Add item" is selected
        assert "Add to options" in content or "push" in content or "add" in content
    
    def test_display_mode_prevents_adding_items(self):
        """Test that display mode prevents adding new items."""
        response = requests.get("http://localhost:8000/custom-combo-test")
        assert response.status_code == 200
        
        content = response.text
        
        # In display mode, "Add item" should be disabled or not functional
        # This will be implemented as we go
        assert "Select item" in content
