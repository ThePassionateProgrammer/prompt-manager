"""
Prompt Routes

Handle all prompt-related HTTP endpoints.
"""

from flask import Blueprint, request, jsonify, render_template_string
from src.prompt_manager.web.services.prompt_service import PromptService

# Create blueprint
prompt_bp = Blueprint('prompts', __name__)
prompt_service = PromptService()

# Predefined categories for dropdowns
PREDEFINED_CATEGORIES = [
    'General', 'Programming', 'Writing', 'Business', 'Creative',
    'Education', 'Health', 'Technology', 'Marketing', 'Other'
]


@prompt_bp.route('/')
def index():
    """Main page showing all prompts."""
    prompts = prompt_service.get_all_prompts()
    categories = prompt_service.get_categories()
    
    # HTML template for the main page
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Prompt Manager</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .prompt-card {{ margin-bottom: 1rem; }}
            .search-box {{ margin-bottom: 2rem; }}
            .category-badge {{ margin-right: 0.5rem; }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-light bg-light mb-4">
            <div class="container-fluid">
                <a class="navbar-brand" href="/"><i class="fas fa-magic me-2"></i>Prompt Manager</a>
                <div class="collapse navbar-collapse">
                    <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                        <li class="nav-item"><a class="nav-link active" href="/">Prompts</a></li>
                        <li class="nav-item"><a class="nav-link" href="/template-builder">Template Builder</a></li>
                        <li class="nav-item"><a class="nav-link" href="/custom-combo-box-builder">Custom Combo Box Builder</a></li>
                    </ul>
                </div>
            </div>
        </nav>
        
        <div class="container-fluid">
            <div class="row">
                <div class="col-12">
                    <div class="d-flex justify-content-between align-items-center mb-4">
                        <h1><i class="fas fa-magic me-2"></i>Prompt Manager</h1>
                        <div class="d-flex gap-2">
                            <a href="/export" class="btn btn-outline-secondary">
                                <i class="fas fa-download me-1"></i>Export
                            </a>
                            <a href="/import" class="btn btn-outline-secondary">
                                <i class="fas fa-upload me-1"></i>Import
                            </a>
                            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addPromptModal">
                                <i class="fas fa-plus me-1"></i>New Prompt
                            </button>
                        </div>
                    </div>
                    
                    <div class="search-box">
                        <form action="/search" method="GET" class="d-flex">
                            <input type="text" name="q" class="form-control me-2" placeholder="Search prompts..." value="">
                            <button type="submit" class="btn btn-outline-primary">Search</button>
                        </form>
                    </div>
                    
                    <div class="row" id="promptsContainer">
                        {_render_prompts(prompts)}
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Add Prompt Modal -->
        {_render_add_prompt_modal()}
        
        <!-- View Prompt Modal -->
        {_render_view_prompt_modal()}
        
        <!-- Edit Prompt Modal -->
        {_render_edit_prompt_modal()}
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            {_render_javascript()}
        </script>
    </body>
    </html>
    """
    
    return html_content


@prompt_bp.route('/add', methods=['POST'])
def add_prompt():
    """Add a new prompt."""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        text = data.get('text', '').strip()
        category = data.get('category', 'General')
        
        success, message = prompt_service.create_prompt(name, text, category)
        
        if success:
            return jsonify({'success': True, 'message': message}), 201
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@prompt_bp.route('/search')
def search_prompts():
    """Search prompts by query."""
    query = request.args.get('q', '').strip()
    prompts = prompt_service.search_prompts(query)
    
    # Return JSON for AJAX requests
    if request.headers.get('Accept') == 'application/json':
        return jsonify({'prompts': prompts, 'query': query})
    
    # Return HTML for regular requests
    return _render_search_results(prompts, query)


@prompt_bp.route('/delete/<prompt_id>', methods=['POST'])
def delete_prompt(prompt_id):
    """Delete a prompt."""
    try:
        success, message = prompt_service.delete_prompt(prompt_id)
        
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@prompt_bp.route('/edit', methods=['POST'])
def edit_prompt():
    """Edit an existing prompt."""
    try:
        data = request.get_json()
        prompt_id = data.get('id')
        name = data.get('name', '').strip()
        text = data.get('text', '').strip()
        category = data.get('category', 'General')
        
        success, message = prompt_service.update_prompt(prompt_id, name, text, category)
        
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@prompt_bp.route('/export', methods=['GET'])
def export_prompts():
    """Export all prompts as JSON."""
    try:
        json_data = prompt_service.export_prompts()
        return json_data, 200, {
            'Content-Type': 'application/json',
            'Content-Disposition': 'attachment; filename=prompts.json'
        }
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@prompt_bp.route('/import', methods=['GET', 'POST'])
def import_prompts():
    """Import prompts from JSON."""
    if request.method == 'GET':
        return _render_import_page()
    
    try:
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            json_data = file.read().decode('utf-8')
        else:
            json_data = request.form.get('json_data', '')
        
        if not json_data:
            return jsonify({'error': 'No data provided'}), 400
        
        success, message = prompt_service.import_prompts(json_data)
        
        if success:
            return jsonify({'success': True, 'message': message}), 200
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Helper functions for rendering HTML
def _render_prompts(prompts):
    """Render prompts as HTML."""
    if not prompts:
        return '<div class="col-12 text-center text-muted py-5"><p>No prompts found. Create your first prompt!</p></div>'
    
    html = ''
    for prompt in prompts:
        html += f'''
        <div class="col-md-6 col-lg-4">
            <div class="card prompt-card">
                <div class="card-body">
                    <h5 class="card-title">{prompt.get('name', 'Untitled')}</h5>
                    <span class="badge bg-secondary category-badge">{prompt.get('category', 'Uncategorized')}</span>
                    <p class="card-text">{prompt.get('text', '')[:100]}{'...' if len(prompt.get('text', '')) > 100 else ''}</p>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="viewPrompt('{prompt.get('id')}')">
                            <i class="fas fa-eye"></i> View
                        </button>
                        <button class="btn btn-sm btn-outline-warning" onclick="editPrompt('{prompt.get('id')}')">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deletePrompt('{prompt.get('id')}')">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            </div>
        </div>
        '''
    return html


def _render_add_prompt_modal():
    """Render the add prompt modal."""
    categories_html = ''.join([f'<option value="{cat}">{cat}</option>' for cat in PREDEFINED_CATEGORIES])
    
    return f'''
    <div class="modal fade" id="addPromptModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add New Prompt</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="addPromptForm">
                        <div class="mb-3">
                            <label for="promptName" class="form-label">Name</label>
                            <input type="text" class="form-control" id="promptName" required maxlength="100">
                        </div>
                        <div class="mb-3">
                            <label for="promptCategory" class="form-label">Category</label>
                            <select class="form-select" id="promptCategory" required>
                                {categories_html}
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="promptText" class="form-label">Text</label>
                            <textarea class="form-control" id="promptText" rows="8" required maxlength="5000"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="addPrompt()">Add Prompt</button>
                </div>
            </div>
        </div>
    </div>
    '''


def _render_view_prompt_modal():
    """Render the view prompt modal."""
    return '''
    <div class="modal fade" id="viewPromptModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">View Prompt</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="viewPromptContent"></div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                </div>
            </div>
        </div>
    </div>
    '''


def _render_edit_prompt_modal():
    """Render the edit prompt modal."""
    categories_html = ''.join([f'<option value="{cat}">{cat}</option>' for cat in PREDEFINED_CATEGORIES])
    
    return f'''
    <div class="modal fade" id="editPromptModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Edit Prompt</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="editPromptForm">
                        <input type="hidden" id="editPromptId">
                        <div class="mb-3">
                            <label for="editPromptName" class="form-label">Name</label>
                            <input type="text" class="form-control" id="editPromptName" required maxlength="100">
                        </div>
                        <div class="mb-3">
                            <label for="editPromptCategory" class="form-label">Category</label>
                            <select class="form-select" id="editPromptCategory" required>
                                {categories_html}
                            </select>
                        </div>
                        <div class="mb-3">
                            <label for="editPromptText" class="form-label">Text</label>
                            <textarea class="form-control" id="editPromptText" rows="8" required maxlength="5000"></textarea>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="updatePrompt()">Update Prompt</button>
                </div>
            </div>
        </div>
    </div>
    '''


def _render_search_results(prompts, query):
    """Render search results page."""
    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Search Results - Prompt Manager</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h1>Search Results for "{query}"</h1>
            <p>Found {len(prompts)} prompts</p>
            <a href="/" class="btn btn-primary">Back to All Prompts</a>
            <hr>
            {_render_prompts(prompts)}
        </div>
    </body>
    </html>
    '''


def _render_import_page():
    """Render the import page."""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Import Prompts - Prompt Manager</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
            <h1>Import Prompts</h1>
            <a href="/" class="btn btn-primary">Back to All Prompts</a>
            <hr>
            <form method="POST" enctype="multipart/form-data">
                <div class="mb-3">
                    <label for="file" class="form-label">Upload JSON File</label>
                    <input type="file" class="form-control" id="file" name="file" accept=".json">
                </div>
                <div class="mb-3">
                    <label for="json_data" class="form-label">Or Paste JSON Data</label>
                    <textarea class="form-control" id="json_data" name="json_data" rows="10" placeholder="Paste your JSON data here..."></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Import Prompts</button>
            </form>
        </div>
    </body>
    </html>
    '''


def _render_javascript():
    """Render JavaScript functions."""
    return '''
    // Add prompt functionality
    async function addPrompt() {
        const name = document.getElementById('promptName').value.trim();
        const category = document.getElementById('promptCategory').value;
        const text = document.getElementById('promptText').value.trim();
        
        if (!name || !text) {
            alert('Name and text are required');
            return;
        }
        
        try {
            const response = await fetch('/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, category, text })
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert(result.message);
                location.reload();
            } else {
                alert('Error: ' + result.message);
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
    
    // View prompt functionality
    async function viewPrompt(promptId) {
        try {
            const response = await fetch('/api/prompts/' + promptId);
            const prompt = await response.json();
            
            document.getElementById('viewPromptContent').innerHTML = `
                <h5>${prompt.name}</h5>
                <span class="badge bg-secondary">${prompt.category}</span>
                <hr>
                <p>${prompt.text}</p>
            `;
            
            new bootstrap.Modal(document.getElementById('viewPromptModal')).show();
        } catch (error) {
            alert('Error loading prompt: ' + error.message);
        }
    }
    
    // Edit prompt functionality
    async function editPrompt(promptId) {
        try {
            const response = await fetch('/api/prompts/' + promptId);
            const prompt = await response.json();
            
            document.getElementById('editPromptId').value = prompt.id;
            document.getElementById('editPromptName').value = prompt.name;
            document.getElementById('editPromptCategory').value = prompt.category;
            document.getElementById('editPromptText').value = prompt.text;
            
            new bootstrap.Modal(document.getElementById('editPromptModal')).show();
        } catch (error) {
            alert('Error loading prompt: ' + error.message);
        }
    }
    
    // Update prompt functionality
    async function updatePrompt() {
        const id = document.getElementById('editPromptId').value;
        const name = document.getElementById('editPromptName').value.trim();
        const category = document.getElementById('editPromptCategory').value;
        const text = document.getElementById('editPromptText').value.trim();
        
        if (!name || !text) {
            alert('Name and text are required');
            return;
        }
        
        try {
            const response = await fetch('/edit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, name, category, text })
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert(result.message);
                location.reload();
            } else {
                alert('Error: ' + result.message);
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
    
    // Delete prompt functionality
    async function deletePrompt(promptId) {
        if (!confirm('Are you sure you want to delete this prompt?')) {
            return;
        }
        
        try {
            const response = await fetch('/delete/' + promptId, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert(result.message);
                location.reload();
            } else {
                alert('Error: ' + result.message);
            }
        } catch (error) {
            alert('Error: ' + error.message);
        }
    }
    '''
