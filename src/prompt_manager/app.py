"""
Unified Flask application factory for Prompt Manager.

Creates a single Flask app with:
- Chat routes (new primary interface)
- Prompt library routes (existing)
- Web templates
"""
from flask import Flask
from flask_cors import CORS

from .prompt_manager import PromptManager
from .business.chat_service import ChatService
from .business.conversation_storage import ConversationStorage
from .business.llm_provider import OllamaProvider


def create_app(
    storage_file: str = "prompts.json",
    conversation_file: str = "conversations.json",
    ollama_url: str = "http://localhost:11434",
    ollama_model: str = "gemma3:4b"
):
    """
    Create and configure the Flask application.

    Args:
        storage_file: Path to prompts JSON file
        conversation_file: Path to conversations JSON file
        ollama_url: Ollama server URL
        ollama_model: Default Ollama model (Ember)

    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key'  # TODO: Use env var in production
    CORS(app)

    # Initialize services
    prompt_manager = PromptManager(storage_file)
    conversation_storage = ConversationStorage(conversation_file)
    llm_provider = OllamaProvider(base_url=ollama_url, default_model=ollama_model)
    chat_service = ChatService(storage=conversation_storage, llm_provider=llm_provider)

    # Store services in app config for route access
    app.config['PROMPT_MANAGER'] = prompt_manager
    app.config['CHAT_SERVICE'] = chat_service
    app.config['CONVERSATION_STORAGE'] = conversation_storage
    app.config['LLM_PROVIDER'] = llm_provider

    # Register blueprints
    from .routes import chat_routes
    app.register_blueprint(chat_routes.bp)

    # Register legacy web routes (TODO: refactor to blueprint)
    from .routes import web_routes
    web_routes.register_routes(app)

    return app


def run_dev_server(host='0.0.0.0', port=8000):
    """
    Run development server.

    Args:
        host: Host to bind to
        port: Port to listen on
    """
    app = create_app()
    print(f"Starting Prompt Manager on http://{host}:{port}")
    print("Chat interface: http://localhost:8000/chat")
    print("Prompt Library: http://localhost:8000/")
    app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    run_dev_server()
