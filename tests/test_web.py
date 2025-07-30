# tests/test_web.py

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.prompt_manager.web import PromptManagerWeb


class TestPromptManagerWeb:
    def setup_method(self):
        """Setup test web interface."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            self.temp_storage = tmp.name
        
        self.web = PromptManagerWeb()
        self.client = self.web.app.test_client()
    
    def teardown_method(self):
        """Cleanup temporary files."""
        try:
            os.unlink(self.temp_storage)
        except:
            pass
    
    @patch('src.prompt_manager.web.requests.get')
    def test_index_page_empty(self, mock_get):
        """Test index page with no prompts."""
        # Mock API responses
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: []),  # prompts
            MagicMock(status_code=200, json=lambda: [])   # categories
        ]
        
        response = self.client.get('/')
        
        assert response.status_code == 200
        assert b'No prompts found' in response.data
        assert b'Create Your First Prompt' in response.data
    
    @patch('src.prompt_manager.web.requests.get')
    def test_index_page_with_prompts(self, mock_get):
        """Test index page with prompts."""
        # Mock API responses
        mock_prompts = [
            {
                'id': 'test-id-1',
                'name': 'Test Prompt 1',
                'text': 'This is test prompt 1',
                'category': 'test',
                'created_at': '2023-01-01T00:00:00',
                'modified_at': '2023-01-01T00:00:00'
            },
            {
                'id': 'test-id-2',
                'name': 'Test Prompt 2',
                'text': 'This is test prompt 2',
                'category': 'general',
                'created_at': '2023-01-02T00:00:00',
                'modified_at': '2023-01-02T00:00:00'
            }
        ]
        
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: mock_prompts),  # prompts
            MagicMock(status_code=200, json=lambda: ['test', 'general'])   # categories
        ]
        
        response = self.client.get('/')
        
        assert response.status_code == 200
        assert b'Test Prompt 1' in response.data
        assert b'Test Prompt 2' in response.data
        assert b'test' in response.data
        assert b'general' in response.data
    
    @patch('src.prompt_manager.web.requests.get')
    def test_index_page_with_search(self, mock_get):
        """Test index page with search parameters."""
        # Mock API responses
        mock_prompts = [
            {
                'id': 'test-id-1',
                'name': 'Python Tutorial',
                'text': 'Learn Python programming',
                'category': 'tutorial',
                'created_at': '2023-01-01T00:00:00',
                'modified_at': '2023-01-01T00:00:00'
            }
        ]
        
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: mock_prompts),  # search results
            MagicMock(status_code=200, json=lambda: ['tutorial'])   # categories
        ]
        
        response = self.client.get('/?q=python&category=tutorial')
        
        assert response.status_code == 200
        assert b'Python Tutorial' in response.data
        assert b'Search: "python"' in response.data
        assert b'Category: tutorial' in response.data
    
    @patch('src.prompt_manager.web.requests.get')
    def test_new_prompt_page_get(self, mock_get):
        """Test new prompt page GET request."""
        # Mock API response for categories
        mock_get.return_value = MagicMock(status_code=200, json=lambda: ['general', 'test'])
        
        response = self.client.get('/prompt/new')
        
        assert response.status_code == 200
        assert b'Create New Prompt' in response.data
        assert b'general' in response.data
        assert b'test' in response.data
    
    @patch('src.prompt_manager.web.requests.post')
    @patch('src.prompt_manager.web.requests.get')
    def test_new_prompt_page_post_success(self, mock_get, mock_post):
        """Test new prompt page POST request success."""
        # Mock API responses
        mock_post.return_value = MagicMock(status_code=201, json=lambda: {
            'id': 'new-id',
            'name': 'New Prompt',
            'text': 'New prompt text',
            'category': 'test'
        })
        mock_get.return_value = MagicMock(status_code=200, json=lambda: ['general', 'test'])
        
        response = self.client.post('/prompt/new', data={
            'name': 'New Prompt',
            'text': 'New prompt text',
            'category': 'test'
        })
        
        assert response.status_code == 302  # Redirect
        assert 'Location: /' in str(response.headers)
    
    def test_new_prompt_page_post_validation_error(self):
        """Test new prompt page POST request with validation error."""
        # Mock API responses on the specific instance
        with patch.object(self.web, '_api_request') as mock_api_request:
            mock_api_request.side_effect = [
                {'error': 'Validation failed'},  # POST /prompts
                ['general']  # GET /categories
            ]
            
            response = self.client.post('/prompt/new', data={
                'name': 'Valid Name',  # Passes client-side validation
                'text': 'Some text',
                'category': 'general'
            })
            
            assert response.status_code == 200  # Stay on form page
            assert b'Name and text are required' in response.data
    
    @patch('src.prompt_manager.web.requests.get')
    def test_view_prompt_page_success(self, mock_get):
        """Test view prompt page success."""
        # Mock API response
        mock_prompt = {
            'id': 'test-id',
            'name': 'Test Prompt',
            'text': 'This is a test prompt',
            'category': 'test',
            'created_at': '2023-01-01T00:00:00',
            'modified_at': '2023-01-01T00:00:00'
        }
        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_prompt)
        
        response = self.client.get('/prompt/test-id')
        
        assert response.status_code == 200
        assert b'Test Prompt' in response.data
        assert b'This is a test prompt' in response.data
        assert b'test' in response.data
    
    @patch('src.prompt_manager.web.requests.get')
    def test_view_prompt_page_not_found(self, mock_get):
        """Test view prompt page not found."""
        # Mock API response
        mock_get.return_value = MagicMock(status_code=404, json=lambda: {'error': 'Prompt not found'})
        
        response = self.client.get('/prompt/non-existent-id')
        
        assert response.status_code == 302  # Redirect to index
        assert 'Location: /' in str(response.headers)
    
    @patch('src.prompt_manager.web.requests.get')
    def test_edit_prompt_page_get(self, mock_get):
        """Test edit prompt page GET request."""
        # Mock API responses
        mock_prompt = {
            'id': 'test-id',
            'name': 'Test Prompt',
            'text': 'This is a test prompt',
            'category': 'test',
            'created_at': '2023-01-01T00:00:00',
            'modified_at': '2023-01-01T00:00:00'
        }
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: mock_prompt),  # prompt
            MagicMock(status_code=200, json=lambda: ['general', 'test'])   # categories
        ]
        
        response = self.client.get('/prompt/test-id/edit')
        
        assert response.status_code == 200
        assert b'Edit Prompt' in response.data
        assert b'Test Prompt' in response.data
        assert b'This is a test prompt' in response.data
    
    @patch('src.prompt_manager.web.requests.put')
    @patch('src.prompt_manager.web.requests.get')
    def test_edit_prompt_page_post_success(self, mock_get, mock_put):
        """Test edit prompt page POST request success."""
        # Mock API responses
        mock_prompt = {
            'id': 'test-id',
            'name': 'Updated Prompt',
            'text': 'Updated prompt text',
            'category': 'updated',
            'created_at': '2023-01-01T00:00:00',
            'modified_at': '2023-01-02T00:00:00'
        }
        mock_put.return_value = MagicMock(status_code=200, json=lambda: mock_prompt)
        mock_get.return_value = MagicMock(status_code=200, json=lambda: ['general', 'updated'])
        
        response = self.client.post('/prompt/test-id/edit', data={
            'name': 'Updated Prompt',
            'text': 'Updated prompt text',
            'category': 'updated'
        })
        
        assert response.status_code == 302  # Redirect to view page
        assert 'Location: /prompt/test-id' in str(response.headers)
    
    @patch('src.prompt_manager.web.requests.delete')
    def test_delete_prompt_success(self, mock_delete):
        """Test delete prompt success."""
        # Mock API response
        mock_delete.return_value = MagicMock(status_code=200, json=lambda: {'message': 'Prompt deleted successfully'})
        
        response = self.client.post('/prompt/test-id/delete')
        
        assert response.status_code == 302  # Redirect to index
        assert 'Location: /' in str(response.headers)
    
    @patch('src.prompt_manager.web.requests.delete')
    def test_delete_prompt_not_found(self, mock_delete):
        """Test delete prompt not found."""
        # Mock API response
        mock_delete.return_value = MagicMock(status_code=404, json=lambda: {'error': 'Prompt not found'})
        
        response = self.client.post('/prompt/non-existent-id/delete')
        
        assert response.status_code == 302  # Redirect to index
        assert 'Location: /' in str(response.headers)
    
    @patch('src.prompt_manager.web.requests.get')
    def test_suggestions_endpoint(self, mock_get):
        """Test suggestions endpoint."""
        # Mock API response
        mock_get.return_value = MagicMock(status_code=200, json=lambda: ['Python Tutorial', 'JavaScript Guide'])
        
        response = self.client.get('/api/suggestions?q=py')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == ['Python Tutorial', 'JavaScript Guide']
    
    @patch('src.prompt_manager.web.requests.get')
    def test_suggestions_endpoint_empty_query(self, mock_get):
        """Test suggestions endpoint with empty query."""
        response = self.client.get('/api/suggestions?q=')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []
    
    def test_web_interface_initialization(self):
        """Test web interface initialization."""
        web = PromptManagerWeb()
        assert web.api_base_url == 'http://localhost:5002/api'
        assert web.app is not None 