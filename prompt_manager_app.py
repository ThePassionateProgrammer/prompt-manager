#!/usr/bin/env python3
"""
Prompt Manager - Main Application Entry Point

A clean, modular prompt management system with template building and linkage capabilities.
"""

import os
import warnings
from flask import Flask
from src.prompt_manager.prompt_manager import PromptManager
from src.prompt_manager.business.custom_combo_box_integration import CustomComboBoxIntegration
from src.prompt_manager.template_service import TemplateService
from src.prompt_manager.business.feature_flags import (
    template_builder_enabled,
    linkages_enabled,
    get_all_flags
)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__,
               template_folder='src/prompt_manager/templates',
               static_folder='src/prompt_manager/static')

    # Load SECRET_KEY from environment variable, with fallback for development
    secret_key = os.environ.get('FLASK_SECRET_KEY')
    if not secret_key:
        warnings.warn(
            "FLASK_SECRET_KEY not set. Using development key. "
            "Set FLASK_SECRET_KEY environment variable for production.",
            RuntimeWarning
        )
        secret_key = 'dev-only-not-for-production'
    app.secret_key = secret_key

    # Store feature flags in app config for templates
    app.config['FEATURE_FLAGS'] = get_all_flags()

    # Initialize services
    app.config['MANAGER'] = PromptManager()
    app.config['CUSTOM_COMBO_INTEGRATION'] = CustomComboBoxIntegration()
    app.config['TEMPLATE_SERVICE'] = TemplateService('templates/templates.json')

    # Register core blueprints (always enabled)
    from routes.static import static_bp
    from routes.dashboard import dashboard_bp
    from routes.prompts_api import prompts_bp
    from routes.prompts_library import prompts_library_bp
    from routes.ollama import ollama_bp

    app.register_blueprint(static_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(prompts_bp)
    app.register_blueprint(prompts_library_bp)
    app.register_blueprint(ollama_bp)

    # Conditionally register experimental features
    if linkages_enabled():
        from routes.linkage import linkage_bp
        app.register_blueprint(linkage_bp)

    # Template builder route is in static_bp, but we control UI visibility via flags

    return app

def setup_port():
    """Simple port setup - kill processes on 8000 if needed."""
    import socket
    import subprocess
    import time
    
    def check_port_available(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def kill_processes_on_port(port):
        try:
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        print(f"Killing process {pid} on port {port}")
                        subprocess.run(['kill', '-9', pid])
                return True
            return False
        except FileNotFoundError:
            return False
    
    default_port = 8000
    
    if check_port_available(default_port):
        print(f"✅ Port {default_port} is available")
        return default_port
    
    print(f"❌ Port {default_port} is in use")
    print("🛠️  Automatically killing processes on port 8000...")
    
    if kill_processes_on_port(default_port):
        time.sleep(2)
        if check_port_available(default_port):
            print(f"✅ Port {default_port} is now available")
            return default_port
    
    # Find alternative port
    for port in range(8001, 8020):
        if check_port_available(port):
            print(f"✅ Found available port: {port}")
            return port
    
    print("❌ No available ports found. Using port 8000 anyway...")
    return default_port

if __name__ == '__main__':
    print("🚀 Starting Prompt Manager...")
    print("📋 Version: 2.0 - Public Beta")
    print("=" * 60)

    port = setup_port()
    app = create_app()

    print(f"\n🌐 Web interface available at: http://localhost:{port}")
    print(f"📊 Main Dashboard: http://localhost:{port}/dashboard")
    print(f"📚 Prompts Library: http://localhost:{port}/prompts")
    print(f"⚙️  Settings: http://localhost:{port}/settings")

    # Only show template builder if enabled
    if template_builder_enabled():
        print(f"🔧 Template Builder: http://localhost:{port}/template-builder")

    print("\n✨ Features:")
    print("  - AI Chat with conversation history & persistence")
    print("  - Multiple AI providers (OpenAI, Ollama local models)")
    print("  - Secure API key management (persistent)")
    print("  - Prompt library with CRUD operations")
    print("  - Voice input/output with customizable settings")
    print("  - Token usage tracking & auto-trimming")

    # Show experimental features if enabled
    flags = get_all_flags()
    enabled_experimental = [k for k, v in flags.items() if v]
    if enabled_experimental:
        print("\n🧪 Experimental Features Enabled:")
        for flag in enabled_experimental:
            print(f"  - {flag.replace('_', ' ').title()}")

    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)

    app.run(host='0.0.0.0', port=port, debug=False)
