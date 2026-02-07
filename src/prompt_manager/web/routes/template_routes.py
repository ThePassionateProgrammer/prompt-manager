"""
Template Routes

Handle all template-related HTTP endpoints.
"""

from flask import Blueprint, request, jsonify, render_template
from src.prompt_manager.web.services.template_service import TemplateService
import json

# Create blueprint
template_bp = Blueprint('templates', __name__)
template_service = TemplateService()


@template_bp.route('/template-builder')
def template_builder():
    """Serve the template builder interface."""
    return render_template('template_builder.html')


@template_bp.route('/custom-combo-test')
def custom_combo_test():
    """Serve the custom combo box test page."""
    return render_template('custom_combo_test.html')


@template_bp.route('/template/parse', methods=['POST'])
def parse_template():
    """Parse a template and extract variables."""
    try:
        data = request.get_json()
        template_text = data.get('template', '')
        
        variables = template_service.extract_variables(template_text)
        
        return json.dumps({
            'variables': variables,
            'template': template_text
        }), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}


@template_bp.route('/template/generate-dropdowns', methods=['POST'])
def generate_dropdowns():
    """Generate dropdowns for template variables."""
    try:
        data = request.get_json()
        template_text = data.get('template', '')
        
        dropdowns = template_service.generate_regular_dropdowns(template_text)
        
        return json.dumps({
            'dropdowns': dropdowns,
            'template': template_text
        }), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}


@template_bp.route('/template/update-options', methods=['POST'])
def update_options():
    """Update dropdown options based on context."""
    try:
        data = request.get_json()
        variable = data.get('variable', '')
        context = data.get('context', '')
        
        options = template_service.update_dropdown_options(variable, context)
        
        return json.dumps({
            'options': options,
            'variable': variable,
            'context': context
        }), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}


@template_bp.route('/template/generate-final', methods=['POST'])
def generate_final_prompt():
    """Generate final prompt from template and selections."""
    try:
        data = request.get_json()
        template_text = data.get('template', '')
        selections = data.get('selections', {})
        
        final_prompt = template_service.generate_final_prompt(template_text, selections)
        
        return json.dumps({
            'final_prompt': final_prompt,
            'template': template_text,
            'selections': selections
        }), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}


@template_bp.route('/template/edit-mode', methods=['POST'])
def toggle_edit_mode():
    """Toggle edit mode for template builder."""
    try:
        data = request.get_json()
        enabled = data.get('enabled', False)
        
        return json.dumps({
            'edit_mode': enabled
        }), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}


@template_bp.route('/template/generate', methods=['POST'])
def generate_template():
    """Main generate endpoint that processes template and returns dropdowns."""
    try:
        data = request.get_json()
        template_text = data.get('template', '')
        edit_mode = data.get('edit_mode', False)
        
        dropdowns = template_service.generate_dropdowns(template_text, edit_mode)
        
        return json.dumps({
            'dropdowns': dropdowns,
            'template': template_text,
            'edit_mode': edit_mode
        }), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}
