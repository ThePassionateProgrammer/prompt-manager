"""
Static Assets Routes

Serves JavaScript files and other static assets for the template builder.
"""

from flask import Blueprint, send_from_directory
import os

# Create blueprint
static_bp = Blueprint('static', __name__)

@static_bp.route('/static/js/custom-combo-box-working.js')
def custom_combo_box_js():
    """Serve the custom combo box JavaScript file."""
    return send_from_directory(
        'src/prompt_manager/static/js', 
        'custom-combo-box-working.js'
    )

@static_bp.route('/static/js/linkage-manager-v3.js')
def linkage_manager_js():
    """Serve the linkage manager JavaScript file."""
    return send_from_directory(
        'src/prompt_manager/static/js', 
        'linkage-manager-v3.js'
    )
