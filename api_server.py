#!/usr/bin/env python3
"""
API Server for Prompt Manager

Run this script to start the REST API server.
"""

from src.prompt_manager.api import PromptManagerAPI


def main():
    """Start the API server."""
    print("Starting Prompt Manager API Server...")
    print("Server will be available at: http://localhost:5000")
    print("API endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/prompts")
    print("  POST /api/prompts")
    print("  GET  /api/prompts/<id>")
    print("  PUT  /api/prompts/<id>")
    print("  DELETE /api/prompts/<id>")
    print("  GET  /api/search")
    print("  GET  /api/categories")
    print("  GET  /api/suggestions")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    api = PromptManagerAPI()
    api.run(host='0.0.0.0', port=5002, debug=True)


if __name__ == '__main__':
    main() 