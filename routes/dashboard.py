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

# Default system prompt
DEFAULT_SYSTEM_PROMPT = "You are a helpful, knowledgeable, and friendly AI assistant. Provide clear, accurate, and concise responses."

# Model context limits (in tokens)
MODEL_CONTEXT_LIMITS = {
    'gpt-4-turbo-preview': 128000,
    'gpt-4': 8192,
    'gpt-3.5-turbo': 4096,
    'gpt-3.5-turbo-16k': 16384
}

def estimate_tokens(text):
    """Rough token estimation (approximately 4 characters per token)."""
    return len(text) // 4

def calculate_token_usage(messages, model):
    """Calculate approximate token usage for messages."""
    total = sum(estimate_tokens(msg.get('content', '')) for msg in messages)
    context_limit = MODEL_CONTEXT_LIMITS.get(model, 4096)
    percentage = min(100, (total / context_limit) * 100)
    
    return {
        'prompt_tokens': total,
        'completion_tokens': 0,  # Updated after response
        'total_tokens': total,
        'context_limit': context_limit,
        'percentage': round(percentage, 1),
        'warning': 'Approaching context limit' if percentage > 80 else None
    }

@dashboard_bp.route('/api/chat/send', methods=['POST'])
def send_chat_message():
    """Send a chat message to a provider with history and context management."""
    try:
        data = request.get_json()
        message = data.get('message')
        provider_name = data.get('provider', 'openai')
        model = data.get('model', 'gpt-3.5-turbo')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2048)
        history = data.get('history', [])
        system_prompt = data.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
        auto_trim = data.get('auto_trim', False)
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get the provider
        provider = provider_manager.get_provider(provider_name)
        if not provider:
            return jsonify({'error': f'Provider {provider_name} not found. Please add your API key in Settings.'}), 404
        
        # Build messages array: system + history + new message
        messages = []
        
        # Add system prompt
        messages.append({
            'role': 'system',
            'content': system_prompt
        })
        
        # Add history
        messages.extend(history)
        
        # Add new user message
        messages.append({
            'role': 'user',
            'content': message
        })
        
        # Auto-trim if needed
        trimmed_count = 0
        if auto_trim:
            token_usage = calculate_token_usage(messages, model)
            if token_usage['percentage'] > 90:
                # Keep system prompt and last few messages
                keep_count = 5
                if len(messages) > keep_count + 1:  # +1 for system
                    trimmed_count = len(messages) - keep_count - 1
                    messages = [messages[0]] + messages[-(keep_count):]
        
        # Calculate token usage before sending
        token_usage = calculate_token_usage(messages, model)
        
        # Generate response using messages
        response = provider.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Update token usage with completion
        token_usage['completion_tokens'] = estimate_tokens(response)
        token_usage['total_tokens'] = token_usage['prompt_tokens'] + token_usage['completion_tokens']
        
        result = {
            'response': response,
            'provider': provider_name,
            'model': model,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'token_usage': token_usage,
            'metadata': {
                'message_count': len(messages) - 1,  # Exclude system prompt
                'has_history': len(history) > 0
            }
        }
        
        if trimmed_count > 0:
            result['trimmed'] = trimmed_count
        
        return jsonify(result)
        
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

@dashboard_bp.route('/api/models/context-limits', methods=['GET'])
def get_context_limits():
    """Get context limits for all models."""
    return jsonify({'limits': MODEL_CONTEXT_LIMITS})

@dashboard_bp.route('/api/settings/system-prompt', methods=['GET', 'POST'])
def system_prompt():
    """Get or set the system prompt."""
    if request.method == 'GET':
        # For now, return default. In future, load from user settings
        return jsonify({'prompt': DEFAULT_SYSTEM_PROMPT})
    else:
        data = request.get_json()
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # TODO: Save to user settings/database
        return jsonify({'message': 'System prompt saved successfully', 'prompt': prompt})

@dashboard_bp.route('/api/settings/system-prompt/default', methods=['GET'])
def get_default_system_prompt():
    """Get the default system prompt."""
    return jsonify({'prompt': DEFAULT_SYSTEM_PROMPT})

@dashboard_bp.route('/api/chat/estimate-tokens', methods=['POST'])
def estimate_tokens_endpoint():
    """Estimate token usage for a message and history."""
    data = request.get_json()
    message = data.get('message', '')
    history = data.get('history', [])
    system_prompt = data.get('system_prompt', DEFAULT_SYSTEM_PROMPT)
    
    # Build messages
    messages = [{'role': 'system', 'content': system_prompt}]
    messages.extend(history)
    messages.append({'role': 'user', 'content': message})
    
    # Estimate
    estimated = sum(estimate_tokens(msg.get('content', '')) for msg in messages)
    
    return jsonify({'estimated_tokens': estimated})
