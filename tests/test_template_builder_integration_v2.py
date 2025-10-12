"""
Integration tests for Template Builder in merged app.

Tests verify that the template builder works correctly when integrated
into prompt_manager_app.py alongside chat and dashboard features.
"""

import pytest


@pytest.fixture
def client():
    """Create test client with full app."""
    from prompt_manager_app import create_app
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestTemplateBuilderPageLoads:
    """First test: Verify template builder page loads."""
    
    def test_template_builder_page_accessible(self, client):
        """Template builder page should be accessible at /template-builder."""
        response = client.get('/template-builder')
        assert response.status_code == 200
        assert b'Template Builder' in response.data


class TestTemplateParseRoute:
    """Second test: Verify template parsing route exists."""
    
    def test_parse_template_extracts_variables(self, client):
        """Template parse should extract [bracketed] variables."""
        response = client.post('/template/parse',
                              json={'template': 'As a [role], I want to [action]'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'variables' in data
        assert 'role' in data['variables']
        assert 'action' in data['variables']

