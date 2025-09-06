"""
Main Flask Application

Clean, organized Flask app using blueprints and services.
"""

from flask import Flask
from src.prompt_manager.web.routes.prompt_routes import prompt_bp
from src.prompt_manager.web.routes.template_routes import template_bp
from src.prompt_manager.web.routes.custom_combo_routes import custom_combo_bp
from src.prompt_manager.web.services.port_service import PortService


def create_app():
    """Create and configure the Flask application."""
    import os
    
    # Set template directory
    template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
    app = Flask(__name__, template_folder=template_dir)
    
    # Register blueprints
    app.register_blueprint(prompt_bp)
    app.register_blueprint(template_bp)
    app.register_blueprint(custom_combo_bp)
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # In production, use environment variable
    
    return app


def run_app(port: int = 8000, debug: bool = False):
    """Run the Flask application."""
    app = create_app()
    
    print("🚀 Starting Enhanced Simple Prompt Manager Web Server...")
    print("📋 Version: 1.5 - Clean Architecture")
    print("=" * 60)
    print(f"🌐 Web interface will be available at: http://localhost:{port}")
    print("✨ Features:")
    print("  - Browse and search prompts")
    print("  - Create and edit prompts with validation")
    print("  - Template builder with custom combo boxes")
    print("  - Flash messages for user feedback")
    print("  - Responsive design with Bootstrap")
    print("  - View prompts in modal")
    print("  - Delete prompts with confirmation")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    # Setup port
    port_service = PortService()
    port = port_service.setup_port()
    
    if port:
        run_app(port=port)
    else:
        print("❌ Failed to setup port. Exiting.")
        exit(1)
