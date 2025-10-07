"""
Dashboard routes for the Prompt Manager application.
"""

from flask import Blueprint, request, jsonify, render_template
from src.prompt_manager.business.llm_provider_manager import LLMProviderManager
from src.prompt_manager.business.llm_provider import OpenAIProvider
from src.prompt_manager.business.key_loader import SecureKeyManager

dashboard_bp = Blueprint('dashboard', __name__)

# Initialize the provider manager
provider_manager = LLMProviderManager()

@dashboard_bp.route('/dashboard')
def dashboard():
    """Render the main dashboard page."""
    return render_template('dashboard.html')

@dashboard_bp.route('/chat')
def chat_dashboard():
    """Render the enhanced chat dashboard."""
    return render_template('chat_dashboard.html')

@dashboard_bp.route('/settings')
def settings():
    """Render the settings page."""
    return render_template('settings.html')

@dashboard_bp.route('/api/providers/add', methods=['POST'])
def add_provider():
    """Add a new LLM provider."""
    try:
        data = request.get_json()
        name = data.get('name')
        api_key = data.get('api_key')
        
        if not name or not api_key:
            return jsonify({'error': 'Provider name and API key are required'}), 400
        
        # For now, only support OpenAI
        if name.lower() != 'openai':
            return jsonify({'error': 'Only OpenAI provider is currently supported'}), 400
        
        # Create the provider
        provider = OpenAIProvider(api_key=api_key)
        
        # Add to manager
        provider_manager.add_provider(name, provider)
        
        # Save the API key securely
        key_manager = SecureKeyManager()
        key_manager.save_key(f'{name.lower()}_api_key', api_key)
        
        return jsonify({
            'message': f'Provider {name} added successfully',
            'provider': {
                'name': name,
                'is_available': provider.is_available()
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/providers/list', methods=['GET'])
def list_providers():
    """List all available providers."""
    try:
        providers = {}
        for name, provider in provider_manager.providers.items():
            providers[name] = {
                'name': provider.name,
                'is_available': provider.is_available()
            }
        
        return jsonify({
            'providers': providers,
            'default_provider': provider_manager.default_provider
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/providers/remove/<provider_name>', methods=['DELETE'])
def remove_provider(provider_name):
    """Remove a provider."""
    try:
        if provider_name not in provider_manager.providers:
            return jsonify({'error': f'Provider {provider_name} not found'}), 404
        
        provider_manager.remove_provider(provider_name)
        
        # Also remove from secure storage
        key_manager = SecureKeyManager()
        key_manager.delete_key(f'{provider_name.lower()}_api_key')
        
        return jsonify({'message': f'Provider {provider_name} removed successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/providers/test', methods=['POST'])
def test_provider():
    """Test a provider connection."""
    try:
        data = request.get_json()
        provider_name = data.get('provider')
        
        if not provider_name:
            return jsonify({'error': 'Provider name is required'}), 400
        
        provider = provider_manager.get_provider(provider_name)
        if not provider:
            return jsonify({'error': f'Provider {provider_name} not found'}), 404
        
        # Test with a simple prompt
        test_prompt = "Hello! Please respond with 'Connection successful!'"
        response = provider.generate(test_prompt, max_tokens=50, temperature=0.1)
        
        return jsonify({
            'message': 'Connection test successful',
            'response': response
        })
        
    except Exception as e:
        return jsonify({'error': f'Connection test failed: {str(e)}'}), 500

@dashboard_bp.route('/api/chat/send', methods=['POST'])
def send_chat_message():
    """Send a chat message to a provider."""
    try:
        data = request.get_json()
        message = data.get('message')
        provider_name = data.get('provider', 'openai')
        model = data.get('model', 'gpt-3.5-turbo')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2048)
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get the provider and generate response
        provider = provider_manager.get_provider(provider_name)
        if not provider:
            return jsonify({'error': f'Provider {provider_name} not found. Please add your API key in Settings.'}), 404
        
        response = provider.generate(
            message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return jsonify({
            'response': response,
            'provider': provider_name,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/providers/set-default', methods=['POST'])
def set_default_provider():
    """Set the default provider."""
    try:
        data = request.get_json()
        provider_name = data.get('provider')
        
        if not provider_name:
            return jsonify({'error': 'Provider name is required'}), 400
        
        provider_manager.set_default_provider(provider_name)
        
        return jsonify({
            'message': f'Default provider set to {provider_name}',
            'default_provider': provider_name
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/models/list', methods=['GET'])
def list_models():
    """List available models for a provider."""
    provider_name = request.args.get('provider', 'openai')
    
    # OpenAI models
    if provider_name.lower() == 'openai':
        models = {
            'gpt-4-turbo-preview': {
                'name': 'GPT-4 Turbo',
                'description': 'Most capable, faster and cheaper than GPT-4',
                'context': '128K tokens'
            },
            'gpt-4': {
                'name': 'GPT-4',
                'description': 'Most capable model, best for complex tasks',
                'context': '8K tokens'
            },
            'gpt-3.5-turbo': {
                'name': 'GPT-3.5 Turbo',
                'description': 'Fast and efficient for most tasks',
                'context': '4K tokens'
            },
            'gpt-3.5-turbo-16k': {
                'name': 'GPT-3.5 Turbo 16K',
                'description': 'Extended context for longer conversations',
                'context': '16K tokens'
            }
        }
        return jsonify({'models': models})
    
    return jsonify({'models': {}})
