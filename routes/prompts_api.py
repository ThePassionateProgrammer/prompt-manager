"""
Prompts API Routes - Blueprint for prompt management.
"""

from flask import Blueprint, jsonify, current_app

prompts_bp = Blueprint('prompts_api', __name__)

@prompts_bp.route('/api/prompts', methods=['GET'])
def get_prompts():
    """Get all prompts."""
    try:
        manager = current_app.config['MANAGER']
        prompts = manager.list_prompts()
        
        # Convert to dict format expected by frontend
        prompts_dict = [
            {
                'id': p.id,
                'name': p.name,
                'text': p.text,
                'category': p.category,
                'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') else None,
                'modified_at': p.modified_at.isoformat() if hasattr(p, 'modified_at') else None
            }
            for p in prompts
        ]
        
        return jsonify({'prompts': prompts_dict})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompts_bp.route('/api/prompts/<prompt_id>', methods=['GET'])
def get_prompt(prompt_id):
    """Get a specific prompt."""
    try:
        manager = current_app.config['MANAGER']
        prompt = manager.get_prompt(prompt_id)
        
        if not prompt:
            return jsonify({'error': 'Prompt not found'}), 404
        
        return jsonify({
            'id': prompt.id,
            'name': prompt.name,
            'text': prompt.text,
            'category': prompt.category,
            'created_at': prompt.created_at.isoformat() if hasattr(prompt, 'created_at') else None,
            'modified_at': prompt.modified_at.isoformat() if hasattr(prompt, 'modified_at') else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

