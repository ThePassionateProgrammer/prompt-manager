#!/usr/bin/env python3
"""
Prompt Manager - Main Application Entry Point

A clean, modular prompt management system with template building and linkage capabilities.
"""

from flask import Flask
from src.prompt_manager.prompt_manager import PromptManager
from src.prompt_manager.business.custom_combo_box_integration import CustomComboBoxIntegration
from src.prompt_manager.template_service import TemplateService

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
               template_folder='src/prompt_manager/templates',
               static_folder='src/prompt_manager/static')
    app.secret_key = 'your-secret-key-here'
    
    # Initialize services
    app.config['MANAGER'] = PromptManager()
    app.config['CUSTOM_COMBO_INTEGRATION'] = CustomComboBoxIntegration()
    app.config['TEMPLATE_SERVICE'] = TemplateService('templates/templates.json')
    
    # Initialize separate API instance (runs its own Flask app for /api/* routes)
    # Note: The API routes are in src/prompt_manager/api.py
    # For now, we'll create a simple prompts route in a new blueprint
    
    # Register blueprints
    from routes.linkage import linkage_bp
    from routes.static import static_bp
    from routes.dashboard import dashboard_bp
    from routes.prompts_api import prompts_bp
    from routes.prompts_library import prompts_library_bp
    
    app.register_blueprint(linkage_bp)
    app.register_blueprint(static_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(prompts_bp)
    app.register_blueprint(prompts_library_bp)
    
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
    print("📋 Version: 2.0 - Clean Architecture")
    print("=" * 60)
    
    port = setup_port()
    app = create_app()
    
    print(f"\n🌐 Web interface available at: http://localhost:{port}")
    print(f"📊 Main Dashboard: http://localhost:{port}/dashboard")
    print(f"📚 Prompts Library: http://localhost:{port}/prompts")
    print(f"🔧 Template Builder: http://localhost:{port}/template-builder")
    print(f"⚙️  Settings: http://localhost:{port}/settings")
    print("\n✨ Features:")
    print("  - AI Chat with conversation history & persistence")
    print("  - Multiple OpenAI models (GPT-4, GPT-3.5)")
    print("  - Secure API key management (persistent)")
    print("  - Prompt library with CRUD operations")
    print("  - Template builder with custom combo boxes") 
    print("  - Linkage system for dynamic templates")
    print("  - Token usage tracking & auto-trimming")
    print("  - Clean, modular architecture")
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
