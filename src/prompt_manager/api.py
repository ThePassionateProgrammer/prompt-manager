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
# Removed unused imports: template_parser, component_manager, template_storage
import uuid
from .business.custom_combo_box_integration import CustomComboBoxIntegration

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
        # Removed TemplateParser - using simple regex parsing instead
        # Removed ComponentManager and TemplateStorage - using simpler alternatives
        
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.json_encoder = UUIDEncoder
        CORS(self.app)
        
        # Initialize custom combo box integration
        self.custom_combo_integration = CustomComboBoxIntegration()
        
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
                is_valid, errors = self.validator.validate_prompt_creation(name, text, category)
                if not is_valid:
                    error_messages = [f"{error.field}: {error.message}" for error in errors]
                    return jsonify({'error': '; '.join(error_messages)}), 400
                
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
                
                name = data.get('name', '').strip()
                text = data.get('text', '').strip()
                category = data.get('category', 'general').strip()
                
                # Validate required fields
                if not name:
                    return jsonify({'error': 'Name is required'}), 400
                if not text:
                    return jsonify({'error': 'Text is required'}), 400
                
                # Validate prompt using business logic
                is_valid, errors = self.validator.validate_prompt_creation(name, text, category)
                if not is_valid:
                    error_messages = [f"{error.field}: {error.message}" for error in errors]
                    return jsonify({'error': '; '.join(error_messages)}), 400
                
                # Update prompt
                success = self.manager.update_prompt(prompt_id, name, text, category)
                if not success:
                    return jsonify({'error': 'Prompt not found'}), 404
                
                # Get the updated prompt
                prompt = self.manager.get_prompt(prompt_id)
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
                categories = self.search_service.get_categories(prompts)
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
        
        # Template endpoints are now handled by routes/linkage.py
        # Removed duplicate template builder and storage routes
        
        # Custom Combo Box Integration Endpoints
        @self.app.route('/api/custom-combo-box/create-template', methods=['POST'])
        def create_template_with_custom_combo_boxes():
            """Create a template with custom combo boxes."""
            try:
                data = request.get_json()
                if not data or 'template' not in data:
                    return jsonify({'error': 'Template is required'}), 400
                
                template = data['template']
                result = self.custom_combo_integration.create_template_with_custom_combo_boxes(template)
                
                return jsonify(result), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/custom-combo-box/handle-change', methods=['POST'])
        def handle_combo_box_change():
            """Handle a combo box change and update cascading state."""
            try:
                data = request.get_json()
                if not data or 'combo_box_id' not in data or 'new_value' not in data or 'combo_boxes' not in data:
                    return jsonify({'error': 'combo_box_id, new_value, and combo_boxes are required'}), 400
                
                combo_box_id = data['combo_box_id']
                new_value = data['new_value']
                combo_boxes = data['combo_boxes']
                
                updated_combo_boxes = self.custom_combo_integration.handle_combo_box_change(
                    combo_box_id, new_value, combo_boxes
                )
                
                return jsonify({'combo_boxes': updated_combo_boxes}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/custom-combo-box/generate-prompt', methods=['POST'])
        def generate_final_prompt():
            """Generate final prompt from template and combo box selections."""
            try:
                data = request.get_json()
                if not data or 'template' not in data or 'combo_boxes' not in data:
                    return jsonify({'error': 'template and combo_boxes are required'}), 400
                
                template = data['template']
                combo_boxes = data['combo_boxes']
                
                final_prompt = self.custom_combo_integration.generate_final_prompt(template, combo_boxes)
                
                return jsonify({'final_prompt': final_prompt}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/custom-combo-box/validate-template', methods=['POST'])
        def validate_template():
            """Validate a template."""
            try:
                data = request.get_json()
                if not data or 'template' not in data:
                    return jsonify({'error': 'template is required'}), 400
                
                template = data['template']
                validation = self.custom_combo_integration.validate_template(template)
                
                return jsonify(validation), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/custom-combo-box/available-templates', methods=['GET'])
        def get_available_templates():
            """Get list of available templates."""
            try:
                templates = self.custom_combo_integration.get_available_templates()
                return jsonify({'templates': templates}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/custom-combo-box/export-config', methods=['POST'])
        def export_template_config():
            """Export template configuration."""
            try:
                data = request.get_json()
                if not data or 'template' not in data or 'combo_boxes' not in data:
                    return jsonify({'error': 'template and combo_boxes are required'}), 400
                
                template = data['template']
                combo_boxes = data['combo_boxes']
                
                config = self.custom_combo_integration.export_template_config(template, combo_boxes)
                
                return jsonify(config), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/custom-combo-box/import-config', methods=['POST'])
        def import_template_config():
            """Import template configuration."""
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'error': 'config data is required'}), 400
                
                result = self.custom_combo_integration.import_template_config(data)
                
                return jsonify(result), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """Health check endpoint."""
            return jsonify({'status': 'healthy'}), 200
        
        # New Template Persistence Routes (Phase 1)
        @self.app.route('/api/template-persistence/save', methods=['POST'])
        def save_template_persistence():
            """Save a template to persistent storage using new TemplateService."""
            try:
                data = request.get_json()
                
                # Validate required fields
                required_fields = ['name', 'description', 'template_text', 'combo_box_values', 'linkage_data']
                for field in required_fields:
                    if field not in data:
                        return jsonify({
                            "success": False,
                            "error": f"Missing required field: {field}"
                        }), 400
                
                # Initialize template service
                from .template_service import TemplateService
                template_service = TemplateService('templates.json')
                
                # Save template
                template_service.save_template(
                    name=data['name'],
                    description=data['description'],
                    template_text=data['template_text'],
                    combo_box_values=data['combo_box_values'],
                    linkage_data=data['linkage_data']
                )
                
                return jsonify({
                    "success": True,
                    "message": "Template saved successfully"
                }), 200
                
            except ValueError as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 400
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Unexpected error: {str(e)}"
                }), 500

        @self.app.route('/api/template-persistence/load/<template_name>', methods=['GET'])
        def load_template_persistence(template_name):
            """Load a template by name using new TemplateService."""
            try:
                from .template_service import TemplateService
                template_service = TemplateService('templates.json')
                template = template_service.load_template(template_name)
                
                return jsonify({
                    "success": True,
                    "template": template
                }), 200
                
            except ValueError as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 404
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Unexpected error: {str(e)}"
                }), 500

        @self.app.route('/api/template-persistence/list', methods=['GET'])
        def list_templates_persistence():
            """List all saved templates using new TemplateService."""
            try:
                from .template_service import TemplateService
                template_service = TemplateService('templates.json')
                templates = template_service.list_templates()
                
                return jsonify({
                    "success": True,
                    "templates": templates
                }), 200
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Unexpected error: {str(e)}"
                }), 500

        @self.app.route('/api/template-persistence/delete/<template_name>', methods=['DELETE'])
        def delete_template_persistence(template_name):
            """Delete a template by name using new TemplateService."""
            try:
                from .template_service import TemplateService
                template_service = TemplateService('templates.json')
                
                if not template_service.template_exists(template_name):
                    return jsonify({
                        "success": False,
                        "error": "Template not found"
                    }), 404
                
                template_service.delete_template(template_name)
                
                return jsonify({
                    "success": True,
                    "message": "Template deleted successfully"
                }), 200
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Unexpected error: {str(e)}"
                }), 500

        @self.app.route('/api/template-persistence/exists/<template_name>', methods=['GET'])
        def template_exists_persistence(template_name):
            """Check if a template exists using new TemplateService."""
            try:
                from .template_service import TemplateService
                template_service = TemplateService('templates.json')
                exists = template_service.template_exists(template_name)
                
                return jsonify({
                    "success": True,
                    "exists": exists
                }), 200
                
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": f"Unexpected error: {str(e)}"
                }), 500
        
    
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