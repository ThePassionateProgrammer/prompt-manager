"""Chat routes with SSE streaming support."""
import json
from flask import Blueprint, request, jsonify, Response, current_app, render_template

bp = Blueprint('chat', __name__, url_prefix='/api/chat')


@bp.route('/conversations', methods=['GET'])
def list_conversations():
    """List all conversations, sorted by most recently updated."""
    chat_service = current_app.config['CHAT_SERVICE']
    conversations = chat_service.list_conversations()

    return jsonify({
        'conversations': [
            {
                'id': conv.id,
                'title': conv.title,
                'model': conv.model,
                'message_count': len(conv.messages),
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat()
            }
            for conv in conversations
        ]
    })


@bp.route('/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation."""
    chat_service = current_app.config['CHAT_SERVICE']
    data = request.get_json() or {}

    title = data.get('title', 'New Conversation')
    model = data.get('model', 'gemma3:4b')

    conv_id = chat_service.create_conversation(title=title, model=model)
    conv = chat_service.get_conversation(conv_id)

    return jsonify({
        'id': conv.id,
        'title': conv.title,
        'model': conv.model,
        'created_at': conv.created_at.isoformat(),
        'updated_at': conv.updated_at.isoformat()
    }), 201


@bp.route('/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get conversation details with all messages."""
    chat_service = current_app.config['CHAT_SERVICE']
    conv = chat_service.get_conversation(conversation_id)

    if not conv:
        return jsonify({'error': 'Conversation not found'}), 404

    return jsonify({
        'id': conv.id,
        'title': conv.title,
        'model': conv.model,
        'messages': [
            {
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in conv.messages
        ],
        'created_at': conv.created_at.isoformat(),
        'updated_at': conv.updated_at.isoformat()
    })


@bp.route('/conversations/<conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation."""
    chat_service = current_app.config['CHAT_SERVICE']
    success = chat_service.delete_conversation(conversation_id)

    if not success:
        return jsonify({'error': 'Conversation not found'}), 404

    return '', 204


@bp.route('/conversations/<conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    """
    Send a message and stream the response using Server-Sent Events (SSE).

    This endpoint returns a text/event-stream that yields chunks as they arrive
    from the LLM, enabling real-time streaming in the UI.
    """
    chat_service = current_app.config['CHAT_SERVICE']
    data = request.get_json() or {}
    message = data.get('message', '')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    # Check if conversation exists
    conv = chat_service.get_conversation(conversation_id)
    if not conv:
        return jsonify({'error': 'Conversation not found'}), 404

    def generate():
        """Generator function for SSE streaming."""
        try:
            # Stream chunks from LLM
            for chunk in chat_service.send_message(conversation_id, message):
                # Send chunk as SSE event
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            # Send completion event
            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            # Send error event
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')


