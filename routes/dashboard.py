"""
Dashboard routes for the Prompt Manager application.
"""

from flask import Blueprint, request, jsonify, render_template
from src.prompt_manager.business.llm_provider_manager import LLMProviderManager
from src.prompt_manager.business.llm_provider import OpenAIProvider
from src.prompt_manager.business.key_loader import SecureKeyManager
from src.prompt_manager.business.conversation_manager import ConversationManager
from src.prompt_manager.business.token_manager import TokenManager
from src.prompt_manager.domain.conversation import ConversationBuilder, ContextWindowManager

dashboard_bp = Blueprint('dashboard', __name__)

# Initialize managers
provider_manager = LLMProviderManager()
conversation_manager = ConversationManager()
token_manager = TokenManager()

# Load saved API keys and initialize providers on startup
def _initialize_providers():
    """Load saved API keys and initialize providers."""
    key_manager = SecureKeyManager()
    saved_keys = key_manager.load_all_keys()
    
    # Initialize providers from saved keys
    for key_name, key_value in saved_keys.items():
        # Extract provider name from key name (e.g., 'openai_api_key' -> 'openai')
        if key_name.endswith('_api_key'):
            provider_name = key_name.replace('_api_key', '')
            
            # Create provider based on name
            if provider_name.lower() == 'openai':
                provider = OpenAIProvider(api_key=key_value)
                provider_manager.add_provider('openai', provider)
                
                # Set as default if it's the first one
                if provider_manager.default_provider is None:
                    provider_manager.set_default_provider('openai')
            # Add other providers here as we support them (anthropic, google, etc.)

# Initialize providers on module load
_initialize_providers()

@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/')
def dashboard():
    """Render the main dashboard page (chat interface)."""
    return render_template('chat_dashboard.html')

@dashboard_bp.route('/chat')
def chat_redirect():
    """Redirect /chat to /dashboard for backward compatibility."""
    from flask import redirect, url_for
    return redirect(url_for('dashboard.dashboard'))

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


def _auto_trim_if_needed(messages, model, auto_trim, token_manager):
    """Automatically trim messages if they approach context limit.
    
    Uses ContextWindowManager domain model for trimming logic.
    Returns (messages, trimmed_count) tuple.
    """
    trimmed_count = 0
    
    if auto_trim:
        prompt_tokens = token_manager.calculate_message_tokens(messages)
        if token_manager.should_trim(prompt_tokens, model, threshold=0.9):
            # Use domain model for business rule: how many messages to keep?
            context_mgr = ContextWindowManager()
            keep_count = context_mgr.calculate_keep_count(len(messages), keep_recent=5)
            messages, trimmed_count = token_manager.trim_messages(messages, keep_count=keep_count)
    
    return messages, trimmed_count

@dashboard_bp.route('/api/chat/send', methods=['POST'])
def send_chat_message():
    """Send a chat message to a provider with history and context management."""
    try:
        # Dependency Injection - get managers from app config instead of globals
        from flask import current_app
        provider_mgr = current_app.config.get('PROVIDER_MANAGER', provider_manager)
        token_mgr = current_app.config.get('TOKEN_MANAGER', token_manager)
        conversation_mgr = current_app.config.get('CONVERSATION_MANAGER', conversation_manager)
        
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
        provider = provider_mgr.get_provider(provider_name)
        if not provider:
            return jsonify({'error': f'Provider {provider_name} not found. Please add your API key in Settings.'}), 404
        
        # Build messages array: system + history + new message
        conversation_builder = ConversationBuilder()
        messages = conversation_builder.build_messages(message, history, system_prompt)
        
        # Auto-trim if needed
        messages, trimmed_count = _auto_trim_if_needed(messages, model, auto_trim, token_mgr)
        
        # Calculate token usage before sending
        token_usage = token_mgr.calculate_token_usage(messages, model)
        
        # Generate response using messages
        response = provider.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Update token usage with completion
        token_usage = token_mgr.update_with_completion(token_usage, response)
        
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
    return jsonify({'limits': token_manager.get_all_model_limits()})

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
    
    # Estimate using TokenManager
    estimated = token_manager.calculate_message_tokens(messages)
    
    return jsonify({'estimated_tokens': estimated})

# Conversation persistence routes
@dashboard_bp.route('/api/conversations/save', methods=['POST'])
def save_conversation():
    """Save a conversation."""
    try:
        data = request.get_json()
        saved = conversation_manager.save_conversation(data)
        
        return jsonify({
            'message': 'Conversation saved successfully',
            'id': saved['id'],
            'title': saved['title'],
            'created_at': saved.get('created_at'),
            'updated_at': saved.get('updated_at')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/conversations/load/<conversation_id>', methods=['GET'])
def load_conversation(conversation_id):
    """Load a conversation by ID."""
    try:
        conversation = conversation_manager.load_conversation(conversation_id)
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        return jsonify(conversation)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/conversations/list', methods=['GET'])
def list_conversations():
    """List all conversations."""
    try:
        sort_by = request.args.get('sort', 'date')
        conversations = conversation_manager.list_conversations(sort_by=sort_by)
        
        return jsonify({'conversations': conversations})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/conversations/delete/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation."""
    try:
        deleted = conversation_manager.delete_conversation(conversation_id)
        
        if not deleted:
            return jsonify({'error': 'Conversation not found'}), 404
        
        return jsonify({'message': 'Conversation deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/api/conversations/search', methods=['GET'])
def search_conversations():
    """Search conversations."""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        results = conversation_manager.search_conversations(query)
        
        return jsonify({'conversations': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
