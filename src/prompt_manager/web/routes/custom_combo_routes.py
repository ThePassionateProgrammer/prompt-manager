"""
Custom Combo Box Routes

Handle all custom combo box related HTTP endpoints.
"""

from flask import Blueprint, request, jsonify
from src.prompt_manager.business.custom_combo_box_integration import CustomComboBoxIntegration
import json

# Create blueprint
custom_combo_bp = Blueprint('custom_combo', __name__)
custom_combo_integration = CustomComboBoxIntegration()


@custom_combo_bp.route('/custom-combo-box-builder')
def custom_combo_box_builder():
    """Serve the custom combo box builder interface."""
    with open('src/prompt_manager/templates/custom_combo_box_builder.html', 'r') as f:
        return f.read()


@custom_combo_bp.route('/api/custom-combo-box/create-template', methods=['POST'])
def create_template_with_custom_combo_boxes():
    """Create a template with custom combo boxes."""
    try:
        data = request.get_json()
        if not data or 'template' not in data:
            return json.dumps({'error': 'Template is required'}), 400, {'Content-Type': 'application/json'}
        
        template = data['template']
        result = custom_combo_integration.create_template_with_custom_combo_boxes(template)
        
        return json.dumps(result), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}


@custom_combo_bp.route('/api/custom-combo-box/handle-change', methods=['POST'])
def handle_custom_combo_box_change():
    """Handle a combo box change and update cascading state."""
    try:
        data = request.get_json()
        if not data or 'combo_box_id' not in data or 'new_value' not in data or 'combo_boxes' not in data:
            return json.dumps({'error': 'combo_box_id, new_value, and combo_boxes are required'}), 400, {'Content-Type': 'application/json'}
        
        combo_box_id = data['combo_box_id']
        new_value = data['new_value']
        combo_boxes = data['combo_boxes']
        
        updated_combo_boxes = custom_combo_integration.handle_combo_box_change(
            combo_box_id, new_value, combo_boxes
        )
        
        return json.dumps({'combo_boxes': updated_combo_boxes}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}


@custom_combo_bp.route('/api/custom-combo-box/generate-prompt', methods=['POST'])
def generate_custom_combo_box_prompt():
    """Generate final prompt from template and combo box selections."""
    try:
        data = request.get_json()
        if not data or 'template' not in data or 'combo_boxes' not in data:
            return json.dumps({'error': 'template and combo_boxes are required'}), 400, {'Content-Type': 'application/json'}
        
        template = data['template']
        combo_boxes = data['combo_boxes']
        
        final_prompt = custom_combo_integration.generate_final_prompt(template, combo_boxes)
        
        return json.dumps({'final_prompt': final_prompt}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}


@custom_combo_bp.route('/api/custom-combo-box/validate-template', methods=['POST'])
def validate_custom_combo_box_template():
    """Validate a template."""
    try:
        data = request.get_json()
        if not data or 'template' not in data:
            return json.dumps({'error': 'template is required'}), 400, {'Content-Type': 'application/json'}
        
        template = data['template']
        validation = custom_combo_integration.validate_template(template)
        
        return json.dumps(validation), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}


@custom_combo_bp.route('/api/custom-combo-box/available-templates', methods=['GET'])
def get_available_templates():
    """Get available template examples."""
    try:
        templates = custom_combo_integration.get_available_templates()
        return json.dumps({'templates': templates}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}


@custom_combo_bp.route('/api/custom-combo-box/export-config', methods=['POST'])
def export_template_config():
    """Export template configuration."""
    try:
        data = request.get_json()
        if not data or 'template' not in data or 'combo_boxes' not in data:
            return json.dumps({'error': 'template and combo_boxes are required'}), 400, {'Content-Type': 'application/json'}
        
        template = data['template']
        combo_boxes = data['combo_boxes']
        
        config = custom_combo_integration.export_template_config(template, combo_boxes)
        
        return json.dumps(config), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}


@custom_combo_bp.route('/api/custom-combo-box/import-config', methods=['POST'])
def import_template_config():
    """Import template configuration."""
    try:
        data = request.get_json()
        if not data:
            return json.dumps({'error': 'Configuration data is required'}), 400, {'Content-Type': 'application/json'}
        
        result = custom_combo_integration.import_template_config(data)
        
        return json.dumps(result), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}
