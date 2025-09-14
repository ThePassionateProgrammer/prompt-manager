"""
Test Add Item Functionality

Tests the specific "Add item..." functionality in custom combo boxes.
"""

import pytest
import json
from src.prompt_manager.web.app import create_app


class TestAddItemFunctionality:
    """Test add item functionality in custom combo boxes."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.template = "As a [Role], I want to [What], so that [Why]"
    
    def test_edit_mode_first_option_is_add_item(self):
        """Test that edit mode has 'Add item...' as the first option."""
        response = self.client.post('/template/generate', 
                                  json={
                                      'template': self.template,
                                      'edit_mode': True
                                  },
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should have 'Add item...' as first option
        options = data['dropdowns']['Role']['options']
        assert len(options) > 0
        assert options[0] == 'Add item...'
    
    def test_regular_mode_no_add_item_option(self):
        """Test that regular mode does not have 'Add item...' option."""
        response = self.client.post('/template/generate', 
                                  json={
                                      'template': self.template,
                                      'edit_mode': False
                                  },
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should not have 'Add item...' option
        options = data['dropdowns']['Role']['options']
        assert 'Add item...' not in options
    
    def test_edit_mode_has_placeholder_text(self):
        """Test that edit mode has 'Type anything.' placeholder."""
        response = self.client.post('/template/generate', 
                                  json={
                                      'template': self.template,
                                      'edit_mode': True
                                  },
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should have placeholder text in the response
        assert 'placeholder' in data['dropdowns']['Role']
        assert data['dropdowns']['Role']['placeholder'] == 'Type anything.'
    
    def test_regular_mode_has_standard_placeholder(self):
        """Test that regular mode has standard placeholder."""
        response = self.client.post('/template/generate', 
                                  json={
                                      'template': self.template,
                                      'edit_mode': False
                                  },
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should have standard placeholder
        assert 'placeholder' in data['dropdowns']['Role']
        assert data['dropdowns']['Role']['placeholder'] == 'Select or enter Role...'
