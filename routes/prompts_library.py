"""
Routes for the Prompts Library CRUD interface.
"""
from flask import Blueprint, render_template, request, jsonify, current_app

prompts_library_bp = Blueprint('prompts_library', __name__)

@prompts_library_bp.route('/prompts')
def prompts_page():
    """Display the prompts library page."""
    return render_template('prompts_library.html')

