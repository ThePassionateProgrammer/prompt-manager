"""
Legacy web routes shim.

TODO: Refactor web.py into proper blueprint structure.
For now, this registers the existing web routes.
"""
from flask import render_template


def register_routes(app):
    """
    Register legacy web routes.

    This is a temporary shim to keep existing functionality working
    while we migrate to the new architecture.

    Args:
        app: Flask application
    """
    # TODO: Move web.py routes here as blueprints

    @app.route('/')
    def index():
        """Render the prompt library (legacy home page)."""
        return render_template('index.html')

    @app.route('/chat')
    def chat():
        """Render the chat interface."""
        return render_template('chat.html')
