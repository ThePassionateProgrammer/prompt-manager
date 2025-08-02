"""
Tests for Template Builder UI functionality.

These tests focus on user behaviors and interactions rather than implementation details,
supporting refactoring and design evolution.
"""

import pytest
from unittest.mock import patch, MagicMock
import json


class TestTemplateBuilderUI:
    """Test the Template Builder web interface functionality."""
    
    def test_template_parsing_detects_bracketed_variables(self, client):
        """Test that template text with bracketed variables is correctly parsed."""
        template_text = "As a [role], I want to [what], so that I can [why]"
        
        response = client.post('/template/parse', json={'template': template_text})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'variables' in data
        assert len(data['variables']) == 3
        assert 'role' in data['variables']
        assert 'what' in data['variables']
        assert 'why' in data['variables']
    
    def test_template_parsing_handles_no_variables(self, client):
        """Test that template without variables is handled gracefully."""
        template_text = "This is a simple prompt without variables"
        
        response = client.post('/template/parse', json={'template': template_text})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'variables' in data
        assert len(data['variables']) == 0
    
    def test_dropdown_generation_creates_combo_boxes(self, client):
        """Test that detected variables generate appropriate dropdown options."""
        template_text = "As a [role], I want to [what]"
        
        response = client.post('/template/generate-dropdowns', json={
            'template': template_text
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'dropdowns' in data
        assert len(data['dropdowns']) == 2
        
        # Check role dropdown
        role_dropdown = data['dropdowns']['role']
        assert 'options' in role_dropdown
        assert 'Programmer' in role_dropdown['options']
        assert 'Chef' in role_dropdown['options']
        assert 'Soccer Coach' in role_dropdown['options']
        
        # Check what dropdown
        what_dropdown = data['dropdowns']['what']
        assert 'options' in what_dropdown
        assert 'Write code' in what_dropdown['options']
        assert 'Shop for food' in what_dropdown['options']
    
    def test_context_aware_dropdowns_update_based_on_selection(self, client):
        """Test that dropdown options change based on previous selections."""
        # First, select "Programmer" for role
        response = client.post('/template/update-options', json={
            'variable': 'what',
            'context': {'role': 'Programmer'}
        })
        
        assert response.status_code == 200
        data = response.get_json()
        options = data['options']
        
        # Should contain programming-related options
        assert 'Write code' in options
        assert 'Create tests' in options
        assert 'Refactor' in options
        assert 'Shop for food' not in options  # Chef-specific option
        
        # Now select "Chef" for role
        response = client.post('/template/update-options', json={
            'variable': 'what',
            'context': {'role': 'Chef'}
        })
        
        assert response.status_code == 200
        data = response.get_json()
        options = data['options']
        
        # Should contain cooking-related options
        assert 'Shop for food' in options
        assert 'Prepare lunch' in options
        assert 'Plan dinner party' in options
        assert 'Write code' not in options  # Programming-specific option
    
    def test_final_prompt_generation_with_user_selections(self, client):
        """Test that user selections populate the template correctly."""
        template_text = "As a [role], I want to [what], so that I can [why]"
        user_selections = {
            'role': 'Programmer',
            'what': 'Write code',
            'why': 'Build better software'
        }
        
        response = client.post('/template/generate-final', json={
            'template': template_text,
            'selections': user_selections
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'final_prompt' in data
        expected = "As a Programmer, I want to Write code, so that I can Build better software"
        assert data['final_prompt'] == expected
    
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


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    from enhanced_simple_server import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client 