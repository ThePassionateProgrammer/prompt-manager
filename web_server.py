#!/usr/bin/env python3
"""
Web Server for Prompt Manager

Run this script to start the web interface server.
Make sure the API server is running on port 5000 first.
"""

from src.prompt_manager.web import PromptManagerWeb


def main():
    """Start the web server."""
    print("Starting Prompt Manager Web Server...")
    print("Web interface will be available at: http://localhost:8000")
    print("Make sure the API server is running on http://localhost:5000")
    print()
    print("Features:")
    print("  - Browse and search prompts")
    print("  - Create and edit prompts")
    print("  - Copy prompts to clipboard")
    print("  - Organize by categories")
    print("  - Responsive design")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    web = PromptManagerWeb()
    web.run(host='0.0.0.0', port=8000, debug=True)


if __name__ == '__main__':
    main() 