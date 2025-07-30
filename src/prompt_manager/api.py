from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, Optional
import json
import os

from .prompt_manager import PromptManager
from .business.prompt_validator import PromptValidator, ValidationError
from .business.search_service import SearchService
from .business.llm_provider import OpenAIProvider
from .business.key_loader import load_openai_api_key
from .business.key_loader import save_openai_api_key
from .business.prompt_builder import PromptBuilder
import uuid

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


class PromptManagerAPI:
    """REST API for prompt manager operations."""
    
    def __init__(self, storage_file: str = "prompts.json"):
        # Single PromptManager instance
        self.manager = PromptManager(storage_file)
        
        # Initialize business logic components
        self.validator = PromptValidator()
        self.search_service = SearchService()
        self.prompt_builder = PromptBuilder()
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.json_encoder = UUIDEncoder
        CORS(self.app)
        
        # Setup routes
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
        
        @self.app.route('/api/llm/chat', methods=['POST'])
        def llm_chat():
            try:
                data = request.get_json()
                if not data or 'prompt' not in data:
                    return jsonify({'error': 'Missing prompt'}), 400
                prompt = data['prompt']
                try:
                    api_key = load_openai_api_key(env_path=ENV_PATH)
                except ValueError as e:
                    return jsonify({'error': str(e)}), 400
                provider = OpenAIProvider(api_key=api_key)
                try:
                    response = provider.send_prompt(prompt)
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
                return jsonify({'response': response}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/llm/config', methods=['GET'])
        def get_llm_config():
            provider = 'openai'  # Only OpenAI for now
            key = os.getenv('OPENAI_API_KEY')
            has_key = bool(key)
            return jsonify({'provider': provider, 'has_key': has_key}), 200

        @self.app.route('/api/llm/config', methods=['POST'])
        def set_llm_config():
            data = request.get_json()
            provider = data.get('provider')
            api_key = data.get('api_key')
            if provider != 'openai':
                return jsonify({'error': 'Only OpenAI is supported for now'}), 400
            if not api_key:
                return jsonify({'error': 'api_key is required'}), 400
            # Write to .env (overwrite or add)
            _set_env_key('OPENAI_API_KEY', api_key, ENV_PATH)
            return jsonify({'success': True}), 200
        
        @self.app.route('/api/prompt-builder/pieces', methods=['GET'])
        def get_prompt_pieces():
            """Get all available prompt pieces for the builder."""
            try:
                return jsonify({
                    'roles': self.prompt_builder.get_available_roles(),
                    'voices': self.prompt_builder.get_available_voices(),
                    'contexts': self.prompt_builder.get_available_contexts(),
                    'audiences': self.prompt_builder.get_available_audiences(),
                    'formats': self.prompt_builder.get_available_formats(),
                    'models': self.prompt_builder.get_available_models()
                }), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/prompt-builder/build', methods=['POST'])
        def build_prompt():
            """Build a prompt from selected pieces."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                result = self.prompt_builder.build_prompt(
                    role_category=data.get('role_category'),
                    role=data.get('role'),
                    voice=data.get('voice'),
                    context_category=data.get('context_category'),
                    context=data.get('context'),
                    audience=data.get('audience'),
                    format_type=data.get('format_type'),
                    custom_text=data.get('custom_text'),
                    model=data.get('model'),
                    temperature=data.get('temperature'),
                    max_tokens=data.get('max_tokens'),
                    min_tokens=data.get('min_tokens')
                )
                
                return jsonify(result), 200
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({'status': 'healthy'}), 200
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the API server."""
        self.app.run(host=host, port=port, debug=debug) 


def _set_env_key(key, value, env_path):
    """Set or update a key in the .env file."""
    lines = []
    if os.path.exists(env_path):
        with open(env_path) as f:
            lines = f.readlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f'{key}='):
            lines[i] = f'{key}={value}\n'
            found = True
            break
    if not found:
        lines.append(f'{key}={value}\n')
    with open(env_path, 'w') as f:
        f.writelines(lines) 