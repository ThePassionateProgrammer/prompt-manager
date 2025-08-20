from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_cors import CORS
import requests
import json
from typing import Dict, Any, Optional

from .api import PromptManagerAPI


class PromptManagerWeb:
    """Web interface for prompt manager."""
    
    def __init__(self, api_host: str = 'localhost', api_port: int = 5002):
        self.api_base_url = f"http://{api_host}:{api_port}/api"
        self.app = Flask(__name__)
        self.app.secret_key = 'prompt-manager-secret-key'  # For flash messages
        CORS(self.app)
        self._setup_routes()
    
    def _api_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make a request to the API."""
        url = f"{self.api_base_url}{endpoint}"
        try:
            if method == 'GET':
                response = requests.get(url, params=data)
            elif method == 'POST':
                response = requests.post(url, json=data)
            elif method == 'PUT':
                response = requests.put(url, json=data)
            elif method == 'DELETE':
                response = requests.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {'error': response.json().get('error', 'Unknown error')}
        except requests.exceptions.ConnectionError:
            return {'error': 'Could not connect to API server'}
        except Exception as e:
            return {'error': str(e)}
    
    def _setup_routes(self):
        """Setup web routes."""
        
        @self.app.route('/')
        def index():
            """Home page - list all prompts."""
            try:
                # Get search parameters
                query = request.args.get('q', '').strip()
                category = request.args.get('category', '').strip()
                
                if query or category:
                    # Use search endpoint
                    params = {}
                    if query:
                        params['q'] = query
                    if category:
                        params['category'] = category
                    prompts = self._api_request('GET', '/search', params)
                else:
                    # Get all prompts
                    prompts = self._api_request('GET', '/prompts')
                
                # Get categories for filter dropdown
                categories = self._api_request('GET', '/categories')
                
                return render_template('index.html', 
                                    prompts=prompts if isinstance(prompts, list) else [],
                                    categories=categories if isinstance(categories, list) else [],
                                    current_query=query,
                                    current_category=category)
            except Exception as e:
                flash(f'Error loading prompts: {str(e)}', 'error')
                return render_template('index.html', prompts=[], categories=[])
        
        @self.app.route('/prompt/new', methods=['GET', 'POST'])
        def new_prompt():
            """Create a new prompt."""
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                text = request.form.get('text', '').strip()
                category = request.form.get('category', 'general').strip()
                
                # Client-side validation
                if not name or not text:
                    flash('Name and text are required', 'error')
                    return render_template('prompt_form.html', 
                                        prompt=None, 
                                        categories=self._api_request('GET', '/categories'))
                
                # Server-side validation via API
                result = self._api_request('POST', '/prompts', {
                    'name': name,
                    'text': text,
                    'category': category
                })
                
                if 'error' in result:
                    flash(f'Error creating prompt: {result["error"]}', 'error')
                    return render_template('prompt_form.html', 
                                        prompt=None, 
                                        categories=self._api_request('GET', '/categories'))
                else:
                    flash('Prompt created successfully!', 'success')
                    return redirect(url_for('index'))
            
            categories = self._api_request('GET', '/categories')
            return render_template('prompt_form.html', 
                                prompt=None, 
                                categories=categories if isinstance(categories, list) else [])
        
        @self.app.route('/prompt/<prompt_id>')
        def view_prompt(prompt_id):
            """View a specific prompt."""
            prompt = self._api_request('GET', f'/prompts/{prompt_id}')
            
            if 'error' in prompt:
                flash(f'Error loading prompt: {prompt["error"]}', 'error')
                return redirect(url_for('index'))
            
            return render_template('prompt_view.html', prompt=prompt)
        
        @self.app.route('/prompt/<prompt_id>/edit', methods=['GET', 'POST'])
        def edit_prompt(prompt_id):
            """Edit a specific prompt."""
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                text = request.form.get('text', '').strip()
                category = request.form.get('category', 'general').strip()
                
                # Client-side validation
                if not name or not text:
                    flash('Name and text are required', 'error')
                    prompt = self._api_request('GET', f'/prompts/{prompt_id}')
                    categories = self._api_request('GET', '/categories')
                    return render_template('prompt_form.html', 
                                        prompt=prompt, 
                                        categories=categories if isinstance(categories, list) else [])
                
                # Server-side validation via API
                result = self._api_request('PUT', f'/prompts/{prompt_id}', {
                    'name': name,
                    'text': text,
                    'category': category
                })
                
                if 'error' in result:
                    flash(f'Error updating prompt: {result["error"]}', 'error')
                    prompt = self._api_request('GET', f'/prompts/{prompt_id}')
                    categories = self._api_request('GET', '/categories')
                    return render_template('prompt_form.html', 
                                        prompt=prompt, 
                                        categories=categories if isinstance(categories, list) else [])
                else:
                    flash('Prompt updated successfully!', 'success')
                    return redirect(url_for('index'))
            
            prompt = self._api_request('GET', f'/prompts/{prompt_id}')
            
            if 'error' in prompt:
                flash(f'Error loading prompt: {prompt["error"]}', 'error')
                return redirect(url_for('index'))
            
            categories = self._api_request('GET', '/categories')
            return render_template('prompt_form.html', 
                                prompt=prompt,
                                categories=categories if isinstance(categories, list) else [])
        
        @self.app.route('/prompt/<prompt_id>/delete', methods=['POST'])
        def delete_prompt(prompt_id):
            """Delete a prompt."""
            result = self._api_request('DELETE', f'/prompts/{prompt_id}')
            
            if 'error' in result:
                flash(f'Error deleting prompt: {result["error"]}', 'error')
            else:
                flash('Prompt deleted successfully!', 'success')
            
            return redirect(url_for('index'))
        
        @self.app.route('/api/suggestions')
        def get_suggestions():
            """Get search suggestions for autocomplete."""
            query = request.args.get('q', '').strip()
            if not query:
                return jsonify([])
            
            suggestions = self._api_request('GET', '/suggestions', {'q': query})
            return jsonify(suggestions if isinstance(suggestions, list) else [])
        
        @self.app.route('/chat', methods=['GET'])
        def chat():
            return render_template('chat.html')
        
        @self.app.route('/setup', methods=['GET'])
        def setup():
            # Fetch provider/key status from backend API
            config = self._api_request('GET', '/llm/config')
            has_key = config.get('has_key', False) if 'error' not in config else False
            return render_template('setup.html', has_key=has_key, message=None, message_type=None)
        
        @self.app.route('/api/llm/config', methods=['POST'])
        def save_llm_config():
            """Save LLM configuration."""
            data = request.get_json()
            provider = data.get('provider')
            api_key = data.get('api_key')
            
            if not provider or not api_key:
                return jsonify({'error': 'Provider and API key are required'}), 400
            
            result = self._api_request('POST', '/llm/config', {
                'provider': provider,
                'api_key': api_key
            })
            
            if 'error' in result:
                return jsonify({'error': result['error']}), 400
            else:
                return jsonify({'success': True}), 200
        
        @self.app.route('/api/llm/chat', methods=['POST'])
        def llm_chat():
            """Send a message to the LLM."""
            data = request.get_json()
            prompt = data.get('prompt')
            
            if not prompt:
                return jsonify({'error': 'Prompt is required'}), 400
            
            result = self._api_request('POST', '/llm/chat', {
                'prompt': prompt
            })
            
            if 'error' in result:
                return jsonify({'error': result['error']}), 400
            else:
                return jsonify({'response': result.get('response', '')}), 200
        
        @self.app.route('/builder', methods=['GET'])
        def prompt_builder():
            """Show the prompt builder interface."""
            return render_template('prompt_builder.html')
        
        @self.app.route('/template-builder', methods=['GET'])
        def template_builder():
            """Show the template builder interface."""
            return render_template('template_builder.html')
        
        @self.app.route('/api/prompt-builder/pieces', methods=['GET'])
        def get_prompt_pieces():
            """Get prompt pieces for the builder."""
            result = self._api_request('GET', '/prompt-builder/pieces')
            return jsonify(result)
        
        @self.app.route('/api/prompt-builder/build', methods=['POST'])
        def build_prompt():
            """Build a prompt from pieces."""
            data = request.get_json()
            result = self._api_request('POST', '/prompt-builder/build', data)
            return jsonify(result)
        
        @self.app.route('/api/template-builder/generate', methods=['POST'])
        def generate_template_combo_boxes():
            """Generate combo boxes from template."""
            data = request.get_json()
            template = data.get('template', '')
            
            if not template:
                return jsonify({'error': 'Template is required'}), 400
            
            result = self._api_request('POST', '/template-builder/generate', {
                'template': template
            })
            return jsonify(result)
        
        @self.app.route('/api/template-builder/components', methods=['GET'])
        def get_template_components():
            """Get component data for template builder."""
            result = self._api_request('GET', '/template-builder/components')
            return jsonify(result)
        
        @self.app.route('/api/template-builder/build', methods=['POST'])
        def build_template_prompt():
            """Build final prompt from template selections."""
            data = request.get_json()
            result = self._api_request('POST', '/template-builder/build', data)
            return jsonify(result)
    
    def run(self, host: str = '0.0.0.0', port: int = 8000, debug: bool = False):
        """Run the web server."""
        self.app.run(host=host, port=port, debug=debug)

    # Cascading Combo Box Integration Methods
    
    def generate_template_combo_boxes(self, template: str) -> Dict[str, Any]:
        """Generate cascading combo boxes for a template."""
        try:
            # Extract variables from template
            import re
            variables = re.findall(r'\[([^\]]+)\]', template)
            
            # Load cascading relationships
            relationships = self.load_cascading_relationships()
            
            # Generate combo boxes with cascading logic
            combo_boxes = []
            for i, variable in enumerate(variables):
                enabled = i == 0  # Only first combo box is enabled initially
                options = []
                
                if i == 0 and relationships:  # Role level
                    options = list(relationships.keys())
                elif i == 1:  # What level - will be populated based on role selection
                    options = []
                elif i == 2:  # Why level - will be populated based on role and what selection
                    options = []
                
                combo_boxes.append({
                    'tag': variable,
                    'enabled': enabled,
                    'options': options,
                    'index': i
                })
            
            return {'combo_boxes': combo_boxes}
        except Exception as e:
            return {'error': str(e)}
    
    def load_cascading_relationships(self) -> Dict[str, Any]:
        """Load cascading relationships from configuration file."""
        try:
            # Default relationships if file doesn't exist
            default_relationships = {
                "Manager": {
                    "Review Status": ["Evaluate Next Actions", "Review Performance"],
                    "File Compliance Report": ["Keep higher-ups informed", "Meet our standards"]
                },
                "Programmer": {
                    "Code Review": ["Keep Code Clean", "Propagate Good Practices"],
                    "Test Plan": ["Ensure Quality", "Prevent Bugs"]
                },
                "Fitness Coach": {
                    "Create Client Meal Plan": ["Improve Client Health", "Meet Nutritional Goals"],
                    "Work Out": ["Build Strength", "Increase Endurance"]
                }
            }
            
            # Try to load from file, fall back to defaults
            try:
                with open('cascading_relationships.json', 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                return default_relationships
        except Exception as e:
            return {}
    
    def get_what_options_for_role(self, role: str) -> list:
        """Get what options for a specific role."""
        try:
            relationships = self.load_cascading_relationships()
            if role in relationships:
                return list(relationships[role].keys())
            return []
        except Exception as e:
            return []
    
    def get_why_options_for_role_and_what(self, role: str, what: str) -> list:
        """Get why options for a specific role and what combination."""
        try:
            relationships = self.load_cascading_relationships()
            if role in relationships and what in relationships[role]:
                return relationships[role][what]
            return []
        except Exception as e:
            return []
    
    def save_cascading_state(self, state: Dict[str, Any]) -> bool:
        """Save cascading state to file."""
        try:
            with open('cascading_state.json', 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception as e:
            return False
    
    def load_cascading_state(self) -> Dict[str, Any]:
        """Load cascading state from file."""
        try:
            with open('cascading_state.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            return {}
    
    def build_final_prompt(self, template: str, selections: Dict[str, str]) -> str:
        """Build final prompt by replacing variables with selections."""
        try:
            final_prompt = template
            for variable, value in selections.items():
                final_prompt = final_prompt.replace(f'[{variable}]', value)
            return final_prompt
        except Exception as e:
            return template 