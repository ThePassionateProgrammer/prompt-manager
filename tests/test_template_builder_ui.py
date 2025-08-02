"""
Tests for Template Builder UI functionality.

These tests focus on essential behaviors and integration points.
For dynamic content testing (API responses, UI interactions), see the approval tests
in test_template_builder_approvals.py which capture the full range of scenarios
without redundancy.
"""

import pytest
from unittest.mock import patch, MagicMock
import json


class TestTemplateBuilderUI:
    """Test the Template Builder web interface functionality."""
    
    def test_template_builder_page_loads_correctly(self, client):
        """Test that the template builder page loads with proper structure."""
        response = client.get('/template-builder')
        
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        
        # Check for key UI elements
        assert 'templateInput' in html  # Bottom text field
        assert 'generateBtn' in html  # Generate button
        assert 'dropdownsArea' in html  # Top panel for dropdowns
        assert 'editModeBtn' in html  # Edit mode button
    
    def test_generate_button_triggers_template_processing(self, client):
        """Test that clicking generate button processes the template."""
        template_text = "As a [role], I want to [what]"
        
        response = client.post('/template/generate', json={
            'template': template_text
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'dropdowns' in data
        assert 'template' in data
        assert data['template'] == template_text
    
    def test_edit_mode_toggle_functionality(self, client):
        """Test that edit mode can be toggled on and off."""
        # Enable edit mode
        response = client.post('/template/edit-mode', json={'enabled': True})
        assert response.status_code == 200
        data = response.get_json()
        assert data['edit_mode'] == True
        
        # Disable edit mode
        response = client.post('/template/edit-mode', json={'enabled': False})
        assert response.status_code == 200
        data = response.get_json()
        assert data['edit_mode'] == False
    
    def test_api_endpoints_are_accessible(self, client):
        """Test that all template builder API endpoints are accessible."""
        endpoints = [
            ('/template/parse', {'template': 'Test [variable]'}),
            ('/template/generate-dropdowns', {'template': 'Test [variable]'}),
            ('/template/update-options', {'variable': 'test', 'context': {}}),
            ('/template/generate-final', {'template': 'Test [var]', 'selections': {'var': 'value'}}),
            ('/template/generate', {'template': 'Test [variable]'})
        ]
        
        for endpoint, data in endpoints:
            response = client.post(endpoint, json=data)
            assert response.status_code == 200, f"Endpoint {endpoint} failed"
            result = response.get_json()
            assert result is not None, f"Endpoint {endpoint} returned invalid JSON"


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    from enhanced_simple_server import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client 