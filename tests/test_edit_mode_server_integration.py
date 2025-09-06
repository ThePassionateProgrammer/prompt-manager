"""
Test Edit Mode Server Integration

Tests the server-side edit mode functionality with the template generation endpoint.
"""

import pytest
import json
from src.prompt_manager.web.app import create_app


class TestEditModeServerIntegration:
    """Test edit mode server integration."""
    
    def setup_method(self):
        """Setup test environment."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.template = "As a [Role], I want to [What], so that [Why]"
    
    def test_template_generate_regular_mode(self):
        """Test template generation in regular mode."""
        response = self.client.post('/template/generate', 
                                  json={
                                      'template': self.template,
                                      'edit_mode': False
                                  },
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should have dropdowns
        assert 'dropdowns' in data
        assert 'Role' in data['dropdowns']
        assert 'What' in data['dropdowns']
        assert 'Why' in data['dropdowns']
        
        # Should not have custom properties
        assert 'is_custom' not in data['dropdowns']['Role']
        assert 'enabled' not in data['dropdowns']['Role']
        assert 'value' not in data['dropdowns']['Role']
        
        # Should have regular options
        assert len(data['dropdowns']['Role']['options']) > 0
        assert 'Programmer' in data['dropdowns']['Role']['options']
    
    def test_template_generate_edit_mode(self):
        """Test template generation in edit mode."""
        response = self.client.post('/template/generate', 
                                  json={
                                      'template': self.template,
                                      'edit_mode': True
                                  },
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should have dropdowns
        assert 'dropdowns' in data
        assert 'Role' in data['dropdowns']
        assert 'What' in data['dropdowns']
        assert 'Why' in data['dropdowns']
        
        # Should have custom properties
        assert data['dropdowns']['Role']['is_custom'] is True
        assert 'enabled' in data['dropdowns']['Role']
        assert 'value' in data['dropdowns']['Role']
        
        # Should have custom options
        assert len(data['dropdowns']['Role']['options']) > 0
        assert 'Option 1 for Role' in data['dropdowns']['Role']['options']
    
    def test_edit_mode_cascading_behavior(self):
        """Test that edit mode has cascading behavior (only first combo box enabled)."""
        response = self.client.post('/template/generate', 
                                  json={
                                      'template': self.template,
                                      'edit_mode': True
                                  },
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # First combo box should be enabled
        assert data['dropdowns']['Role']['enabled'] is True
        
        # Subsequent combo boxes should be disabled
        assert data['dropdowns']['What']['enabled'] is False
        assert data['dropdowns']['Why']['enabled'] is False
    
    def test_edit_mode_preserves_template(self):
        """Test that edit mode preserves the original template."""
        response = self.client.post('/template/generate', 
                                  json={
                                      'template': self.template,
                                      'edit_mode': True
                                  },
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should preserve original template
        assert data['template'] == self.template
        assert data['edit_mode'] is True
    
    def test_edit_mode_with_different_template(self):
        """Test edit mode with a different template."""
        different_template = "When [User] visits [Page], they should see [Content]"
        
        response = self.client.post('/template/generate', 
                                  json={
                                      'template': different_template,
                                      'edit_mode': True
                                  },
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Should have dropdowns for different variables
        assert 'User' in data['dropdowns']
        assert 'Page' in data['dropdowns']
        assert 'Content' in data['dropdowns']
        
        # Should have custom properties
        assert data['dropdowns']['User']['is_custom'] is True
        assert data['dropdowns']['User']['enabled'] is True
        assert data['dropdowns']['Page']['enabled'] is False
        assert data['dropdowns']['Content']['enabled'] is False
