"""
Ollama-specific routes for the Prompt Manager application.
"""

from flask import Blueprint, jsonify, request
from src.prompt_manager.business.ollama_discovery import OllamaDiscovery
from src.prompt_manager.domain.model_catalog import ModelCatalog

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


@ollama_bp.route('/api/ollama/status', methods=['GET'])
def server_status():
    """Check if Ollama server is running.

    Returns:
        JSON response with server status
    """
    is_running = ollama_discovery.is_server_running()

    return jsonify({
        'running': is_running,
        'status': 'connected' if is_running else 'disconnected'
    })


@ollama_bp.route('/api/ollama/models/pull', methods=['POST'])
def pull_model():
    """Pull/download a model from Ollama library.

    Expected JSON body: {"model": "model_name:tag"}

    Returns:
        JSON response with success status
    """
    data = request.get_json() or {}
    model_name = data.get('model')

    if not model_name:
        return jsonify({'error': 'Model name is required'}), 400

    result = ollama_discovery.pull_model(model_name)

    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400


@ollama_bp.route('/api/ollama/models/available', methods=['GET'])
def list_available_models():
    """List available Ollama models that can be downloaded.

    Returns:
        JSON response with catalog of downloadable models
    """
    models = ModelCatalog.get_ollama_models()
    return jsonify({'models': models})


@ollama_bp.route('/api/ollama/models/<path:model_name>', methods=['DELETE'])
def delete_model(model_name):
    """Delete a downloaded model.

    Args:
        model_name: Model to delete (URL path parameter)

    Returns:
        JSON response with success status
    """
    result = ollama_discovery.delete_model(model_name)

    if result['success']:
        return jsonify(result)
    else:
        return jsonify(result), 400