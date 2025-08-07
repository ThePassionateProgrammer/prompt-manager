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
from .business.template_parser import TemplateParser
from .business.component_manager import ComponentManager
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
        self.template_parser = TemplateParser()
        self.component_manager = ComponentManager()
        
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
                
                # Validate required fields
                if not name:
                    return jsonify({'error': 'Name is required'}), 400
                if not text:
                    return jsonify({'error': 'Text is required'}), 400
                
                # Validate prompt using business logic
                try:
                    self.validator.validate_prompt(name, text, category)
                except ValidationError as e:
                    return jsonify({'error': str(e)}), 400
                
                # Create prompt
                prompt = self.manager.create_prompt(name, text, category)
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
                
                name = data.get('name', '').strip()
                text = data.get('text', '').strip()
                category = data.get('category', 'general').strip()
                
                # Validate required fields
                if not name:
                    return jsonify({'error': 'Name is required'}), 400
                if not text:
                    return jsonify({'error': 'Text is required'}), 400
                
                # Validate prompt using business logic
                try:
                    self.validator.validate_prompt(name, text, category)
                except ValidationError as e:
                    return jsonify({'error': str(e)}), 400
                
                # Update prompt
                prompt = self.manager.update_prompt(prompt_id, name, text, category)
                if not prompt:
                    return jsonify({'error': 'Prompt not found'}), 404
                
                return jsonify(prompt.to_dict()), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/prompts/<prompt_id>', methods=['DELETE'])
        def delete_prompt(prompt_id: str):
            """Delete a prompt."""
            try:
                success = self.manager.delete_prompt(prompt_id)
                if not success:
                    return jsonify({'error': 'Prompt not found'}), 404
                
                return jsonify({'message': 'Prompt deleted successfully'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/search', methods=['GET'])
        def search_prompts():
            """Search prompts by query and category."""
            try:
                query = request.args.get('q', '').strip()
                category = request.args.get('category', '').strip()
                
                prompts = self.manager.list_prompts()
                
                if category:
                    prompts = self.search_service.get_prompts_by_category(prompts, category)
                
                if query:
                    prompts = self.search_service.search_prompts(prompts, query)
                
                return jsonify([prompt.to_dict() for prompt in prompts]), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/categories', methods=['GET'])
        def get_categories():
            """Get all available categories."""
            try:
                prompts = self.manager.list_prompts()
                categories = self.search_service.get_all_categories(prompts)
                return jsonify(categories), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/suggestions', methods=['GET'])
        def get_suggestions():
            """Get search suggestions for autocomplete."""
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
            """Send a message to the LLM."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                prompt = data.get('prompt', '').strip()
                if not prompt:
                    return jsonify({'error': 'Prompt is required'}), 400
                
                # Load API key
                api_key = load_openai_api_key(ENV_PATH)
                if not api_key:
                    return jsonify({'error': 'OpenAI API key not configured'}), 400
                
                # Initialize provider and send message
                provider = OpenAIProvider(api_key)
                response = provider.send_message(prompt)
                
                return jsonify({'response': response}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/llm/config', methods=['GET'])
        def get_llm_config():
            """Get LLM configuration status."""
            try:
                api_key = load_openai_api_key(ENV_PATH)
                return jsonify({'has_key': bool(api_key)}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/llm/config', methods=['POST'])
        def set_llm_config():
            """Set LLM configuration."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                api_key = data.get('api_key', '').strip()
                if not api_key:
                    return jsonify({'error': 'API key is required'}), 400
                
                save_openai_api_key(api_key, ENV_PATH)
                return jsonify({'message': 'API key saved successfully'}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/prompt-builder/pieces', methods=['GET'])
        def get_prompt_pieces():
            """Get prompt pieces for the builder."""
            try:
                pieces = self.prompt_builder.pieces_data
                return jsonify(pieces), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/prompt-builder/build', methods=['POST'])
        def build_prompt():
            """Build a prompt from pieces."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                result = self.prompt_builder.build_prompt(**data)
                return jsonify(result), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Template Builder Endpoints
        @self.app.route('/api/template-builder/generate', methods=['POST'])
        def generate_template_combo_boxes():
            """Generate combo boxes from template."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                template = data.get('template', '').strip()
                if not template:
                    return jsonify({'error': 'Template is required'}), 400
                
                combo_boxes = self.template_parser.generate_combo_boxes(template)
                return jsonify({'combo_boxes': combo_boxes}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/template-builder/components', methods=['GET'])
        def get_template_components():
            """Get component data for template builder."""
            try:
                components = self.component_manager.get_all_components()
                return jsonify({'components': components}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/template-builder/build', methods=['POST'])
        def build_template_prompt():
            """Build final prompt from template selections."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'No data provided'}), 400
                
                template = data.get('template', '').strip()
                combo_boxes = data.get('combo_boxes', [])
                
                if not template:
                    return jsonify({'error': 'Template is required'}), 400
                
                final_prompt = self.template_parser.generate_prompt_from_selections(template, combo_boxes)
                return jsonify({'prompt': final_prompt}), 200
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
    """Set a key-value pair in the .env file."""
    try:
        # Read existing .env file
        env_vars = {}
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        env_vars[k.strip()] = v.strip()
        
        # Update the key
        env_vars[key] = value
        
        # Write back to .env file
        with open(env_path, 'w') as f:
            for k, v in env_vars.items():
                f.write(f"{k}={v}\n")
        
        return True
    except Exception as e:
        print(f"Error setting environment variable: {e}")
        return False 