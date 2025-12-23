"""
Ollama-specific routes for the Prompt Manager application.
"""

from flask import Blueprint, jsonify
from src.prompt_manager.business.ollama_discovery import OllamaDiscovery

ollama_bp = Blueprint('ollama', __name__)

# Initialize discovery service
ollama_discovery = OllamaDiscovery()


@ollama_bp.route('/api/ollama/models', methods=['GET'])
def list_models():
    """List all downloaded Ollama models.

    Returns:
        JSON response with list of model objects
    """
    try:
        models = ollama_discovery.list_downloaded_models()

        return jsonify({
            'models': [model.to_dict() for model in models]
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
