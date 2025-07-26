# tests/test_api.py

import pytest
import json
import tempfile
import os
from src.prompt_manager.api import PromptManagerAPI


class TestPromptManagerAPI:
    def setup_method(self):
        """Setup test API with temporary storage."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            self.temp_storage = tmp.name
        
        self.api = PromptManagerAPI(self.temp_storage)
        self.client = self.api.app.test_client()
    
    def teardown_method(self):
        """Cleanup temporary files."""
        try:
            os.unlink(self.temp_storage)
        except:
            pass
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_get_prompts_empty(self):
        """Test getting prompts when none exist."""
        response = self.client.get('/api/prompts')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []
    
    def test_create_prompt_success(self):
        """Test creating a prompt successfully."""
        prompt_data = {
            'name': 'Test Prompt',
            'text': 'This is a test prompt',
            'category': 'test'
        }
        
        response = self.client.post('/api/prompts', 
                                  data=json.dumps(prompt_data),
                                  content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['name'] == 'Test Prompt'
        assert data['text'] == 'This is a test prompt'
        assert data['category'] == 'test'
        assert 'id' in data
    
    def test_create_prompt_validation_error(self):
        """Test creating a prompt with validation errors."""
        prompt_data = {
            'name': '',  # Empty name should fail validation
            'text': 'This is a test prompt',
            'category': 'test'
        }
        
        response = self.client.post('/api/prompts', 
                                  data=json.dumps(prompt_data),
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Validation failed'
        assert len(data['errors']) > 0
    
    def test_create_prompt_no_data(self):
        """Test creating a prompt with no data."""
        response = self.client.post('/api/prompts', 
                                  data='',
                                  content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'No data provided'
    
    def test_get_prompt_by_id(self):
        """Test getting a specific prompt by ID."""
        # First create a prompt
        prompt_data = {
            'name': 'Test Prompt',
            'text': 'This is a test prompt',
            'category': 'test'
        }
        
        create_response = self.client.post('/api/prompts', 
                                         data=json.dumps(prompt_data),
                                         content_type='application/json')
        created_prompt = json.loads(create_response.data)
        prompt_id = created_prompt['id']
        
        # Then get the prompt by ID
        response = self.client.get(f'/api/prompts/{prompt_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == prompt_id
        assert data['name'] == 'Test Prompt'
    
    def test_get_prompt_not_found(self):
        """Test getting a non-existent prompt."""
        response = self.client.get('/api/prompts/non-existent-id')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Prompt not found'
    
    def test_update_prompt_success(self):
        """Test updating a prompt successfully."""
        # First create a prompt
        prompt_data = {
            'name': 'Original Name',
            'text': 'Original text',
            'category': 'original'
        }
        
        create_response = self.client.post('/api/prompts', 
                                         data=json.dumps(prompt_data),
                                         content_type='application/json')
        created_prompt = json.loads(create_response.data)
        prompt_id = created_prompt['id']
        
        # Then update the prompt
        update_data = {
            'name': 'Updated Name',
            'text': 'Updated text',
            'category': 'updated'
        }
        
        response = self.client.put(f'/api/prompts/{prompt_id}', 
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Updated Name'
        assert data['text'] == 'Updated text'
        assert data['category'] == 'updated'
    
    def test_update_prompt_not_found(self):
        """Test updating a non-existent prompt."""
        update_data = {
            'name': 'Updated Name',
            'text': 'Updated text'
        }
        
        response = self.client.put('/api/prompts/non-existent-id', 
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Prompt not found'
    
    def test_update_prompt_validation_error(self):
        """Test updating a prompt with validation errors."""
        # First create a prompt
        prompt_data = {
            'name': 'Original Name',
            'text': 'Original text',
            'category': 'original'
        }
        
        create_response = self.client.post('/api/prompts', 
                                         data=json.dumps(prompt_data),
                                         content_type='application/json')
        created_prompt = json.loads(create_response.data)
        prompt_id = created_prompt['id']
        
        # Then update with invalid data
        update_data = {
            'name': '',  # Empty name should fail validation
            'text': 'Updated text'
        }
        
        response = self.client.put(f'/api/prompts/{prompt_id}', 
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Validation failed'
    
    def test_delete_prompt_success(self):
        """Test deleting a prompt successfully."""
        # First create a prompt
        prompt_data = {
            'name': 'Test Prompt',
            'text': 'This is a test prompt',
            'category': 'test'
        }
        
        create_response = self.client.post('/api/prompts', 
                                         data=json.dumps(prompt_data),
                                         content_type='application/json')
        created_prompt = json.loads(create_response.data)
        prompt_id = created_prompt['id']
        
        # Then delete the prompt
        response = self.client.delete(f'/api/prompts/{prompt_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Prompt deleted successfully'
        
        # Verify prompt is deleted
        get_response = self.client.get(f'/api/prompts/{prompt_id}')
        assert get_response.status_code == 404
    
    def test_delete_prompt_not_found(self):
        """Test deleting a non-existent prompt."""
        response = self.client.delete('/api/prompts/non-existent-id')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Prompt not found'
    
    def test_search_prompts_by_query(self):
        """Test searching prompts by query."""
        # Create some test prompts
        prompts = [
            {'name': 'Python Tutorial', 'text': 'Learn Python programming', 'category': 'tutorial'},
            {'name': 'JavaScript Guide', 'text': 'Learn JavaScript basics', 'category': 'tutorial'},
            {'name': 'Hello World', 'text': 'Greeting prompt', 'category': 'greeting'}
        ]
        
        for prompt_data in prompts:
            self.client.post('/api/prompts', 
                           data=json.dumps(prompt_data),
                           content_type='application/json')
        
        # Search for "python"
        response = self.client.get('/api/search?q=python')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == 'Python Tutorial'
    
    def test_search_prompts_by_category(self):
        """Test searching prompts by category."""
        # Create some test prompts
        prompts = [
            {'name': 'Python Tutorial', 'text': 'Learn Python programming', 'category': 'tutorial'},
            {'name': 'JavaScript Guide', 'text': 'Learn JavaScript basics', 'category': 'tutorial'},
            {'name': 'Hello World', 'text': 'Greeting prompt', 'category': 'greeting'}
        ]
        
        for prompt_data in prompts:
            self.client.post('/api/prompts', 
                           data=json.dumps(prompt_data),
                           content_type='application/json')
        
        # Search by category
        response = self.client.get('/api/search?category=tutorial')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        for prompt in data:
            assert prompt['category'] == 'tutorial'
    
    def test_search_prompts_no_criteria(self):
        """Test search with no criteria."""
        response = self.client.get('/api/search')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'No search criteria provided'
    
    def test_get_categories(self):
        """Test getting all categories."""
        # Create prompts with different categories
        prompts = [
            {'name': 'Prompt 1', 'text': 'Text 1', 'category': 'tutorial'},
            {'name': 'Prompt 2', 'text': 'Text 2', 'category': 'greeting'},
            {'name': 'Prompt 3', 'text': 'Text 3', 'category': 'tutorial'}
        ]
        
        for prompt_data in prompts:
            self.client.post('/api/prompts', 
                           data=json.dumps(prompt_data),
                           content_type='application/json')
        
        response = self.client.get('/api/categories')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tutorial' in data
        assert 'greeting' in data
        assert len(data) == 2  # Should be unique categories
    
    def test_get_suggestions(self):
        """Test getting search suggestions."""
        # Create prompts
        prompts = [
            {'name': 'Python Tutorial', 'text': 'Learn Python programming', 'category': 'tutorial'},
            {'name': 'JavaScript Guide', 'text': 'Learn JavaScript basics', 'category': 'tutorial'}
        ]
        
        for prompt_data in prompts:
            self.client.post('/api/prompts', 
                           data=json.dumps(prompt_data),
                           content_type='application/json')
        
        response = self.client.get('/api/suggestions?q=py')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Python Tutorial' in data
    
    def test_get_suggestions_empty_query(self):
        """Test getting suggestions with empty query."""
        response = self.client.get('/api/suggestions?q=')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []
    
    def test_get_prompts_with_filtering(self):
        """Test getting prompts with query and category filtering."""
        # Create test prompts
        prompts = [
            {'name': 'Python Tutorial', 'text': 'Learn Python programming', 'category': 'tutorial'},
            {'name': 'JavaScript Guide', 'text': 'Learn JavaScript basics', 'category': 'tutorial'},
            {'name': 'Hello World', 'text': 'Greeting prompt', 'category': 'greeting'}
        ]
        
        for prompt_data in prompts:
            self.client.post('/api/prompts', 
                           data=json.dumps(prompt_data),
                           content_type='application/json')
        
        # Test filtering by category
        response = self.client.get('/api/prompts?category=tutorial')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        for prompt in data:
            assert prompt['category'] == 'tutorial'
        
        # Test filtering by query
        response = self.client.get('/api/prompts?query=python')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]['name'] == 'Python Tutorial' 