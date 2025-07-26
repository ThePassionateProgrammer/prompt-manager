from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, Optional
import json

from .prompt_manager import PromptManager
from .business.prompt_validator import PromptValidator, ValidationError
from .business.search_service import SearchService


class PromptManagerAPI:
    """REST API for prompt manager operations."""
    
    def __init__(self, storage_file: str = "prompts.json"):
        self.manager = PromptManager(storage_file)
        self.validator = PromptValidator()
        self.search_service = SearchService()
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.route('/api/prompts', methods=['GET'])
        def get_prompts():
            """Get all prompts with optional filtering."""
            try:
                category = request.args.get('category')
                query = request.args.get('query')
                
                if category or query:
                    # Use search service for filtered results
                    prompts = self.manager.list_prompts()
                    if category:
                        prompts = self.search_service.get_prompts_by_category(prompts, category)
                    if query:
                        prompts = self.search_service.search_prompts(prompts, query)
                else:
                    prompts = self.manager.list_prompts()
                
                return jsonify([prompt.to_dict() for prompt in prompts]), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/prompts/<prompt_id>', methods=['GET'])
        def get_prompt(prompt_id: str):
            """Get a specific prompt by ID."""
            try:
                prompt = self.manager.get_prompt(prompt_id)
                if not prompt:
                    return jsonify({'error': 'Prompt not found'}), 404
                
                return jsonify(prompt.to_dict()), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/prompts', methods=['POST'])
        def create_prompt():
            """Create a new prompt."""
            try:
                # Handle empty or invalid JSON data
                if not request.data:
                    return jsonify({'error': 'No data provided'}), 400
                
                try:
                    data = request.get_json()
                except Exception:
                    return jsonify({'error': 'Invalid JSON data'}), 400
                
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                name = data.get('name', '').strip()
                text = data.get('text', '').strip()
                category = data.get('category', 'general').strip()
                
                # Validate input
                is_valid, errors = self.validator.validate_prompt_creation(name, text, category)
                if not is_valid:
                    return jsonify({
                        'error': 'Validation failed',
                        'errors': [{'field': e.field, 'message': e.message} for e in errors]
                    }), 400
                
                # Create prompt
                prompt_id = self.manager.add_prompt(name, text, category)
                prompt = self.manager.get_prompt(prompt_id)
                
                return jsonify(prompt.to_dict()), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/prompts/<prompt_id>', methods=['PUT'])
        def update_prompt(prompt_id: str):
            """Update an existing prompt."""
            try:
                # Handle empty or invalid JSON data
                if not request.data:
                    return jsonify({'error': 'No data provided'}), 400
                
                try:
                    data = request.get_json()
                except Exception:
                    return jsonify({'error': 'Invalid JSON data'}), 400
                
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                # Check if prompt exists
                existing_prompt = self.manager.get_prompt(prompt_id)
                if not existing_prompt:
                    return jsonify({'error': 'Prompt not found'}), 404
                
                # Extract update fields
                name = data.get('name')
                text = data.get('text')
                category = data.get('category')
                
                # Validate input
                is_valid, errors = self.validator.validate_prompt_update(
                    name=name, text=text, category=category
                )
                if not is_valid:
                    return jsonify({
                        'error': 'Validation failed',
                        'errors': [{'field': e.field, 'message': e.message} for e in errors]
                    }), 400
                
                # Update prompt
                success = self.manager.update_prompt(prompt_id, name, text, category)
                if not success:
                    return jsonify({'error': 'Failed to update prompt'}), 500
                
                updated_prompt = self.manager.get_prompt(prompt_id)
                return jsonify(updated_prompt.to_dict()), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/prompts/<prompt_id>', methods=['DELETE'])
        def delete_prompt(prompt_id: str):
            """Delete a prompt."""
            try:
                # Check if prompt exists
                existing_prompt = self.manager.get_prompt(prompt_id)
                if not existing_prompt:
                    return jsonify({'error': 'Prompt not found'}), 404
                
                # Delete prompt
                success = self.manager.delete_prompt(prompt_id)
                if not success:
                    return jsonify({'error': 'Failed to delete prompt'}), 500
                
                return jsonify({'message': 'Prompt deleted successfully'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/search', methods=['GET'])
        def search_prompts():
            """Search prompts with various filters."""
            try:
                query = request.args.get('q', '').strip()
                category = request.args.get('category', '').strip()
                max_results = request.args.get('max_results', type=int)
                
                if not query and not category:
                    return jsonify({'error': 'No search criteria provided'}), 400
                
                prompts = self.manager.list_prompts()
                results = self.search_service.search_with_filters(
                    prompts, query=query, category=category, max_results=max_results
                )
                
                return jsonify([prompt.to_dict() for prompt in results]), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/categories', methods=['GET'])
        def get_categories():
            """Get all unique categories."""
            try:
                prompts = self.manager.list_prompts()
                categories = self.search_service.get_categories(prompts)
                
                return jsonify(categories), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/suggestions', methods=['GET'])
        def get_suggestions():
            """Get search suggestions."""
            try:
                query = request.args.get('q', '').strip()
                if not query:
                    return jsonify([]), 200
                
                prompts = self.manager.list_prompts()
                suggestions = self.search_service.get_search_suggestions(prompts, query)
                
                return jsonify(suggestions), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({'status': 'healthy'}), 200
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the API server."""
        self.app.run(host=host, port=port, debug=debug) 