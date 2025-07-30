#!/usr/bin/env python3
"""
Enhanced Simple Web Server for Prompt Manager

A working web interface that directly uses the PromptManager with improvements.
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash
from src.prompt_manager.prompt_manager import PromptManager
import json
import socket
import subprocess
import sys
import os

def check_port_available(port):
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def get_processes_using_port(port):
    """Get list of processes using a specific port."""
    try:
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Skip header line
                return lines[1:]  # Return process lines
        return []
    except FileNotFoundError:
        return []

def kill_processes_on_port(port):
    """Kill processes using a specific port."""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"Killing process {pid} on port {port}")
                    subprocess.run(['kill', '-9', pid])
            return True
        return False
    except FileNotFoundError:
        return False

def find_available_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if check_port_available(port):
            return port
    return None

def setup_port():
    """Setup port with user interaction."""
    default_port = 8000
    
    print("🔍 Checking port availability...")
    
    if check_port_available(default_port):
        print(f"✅ Port {default_port} is available")
        return default_port
    
    print(f"❌ Port {default_port} is in use")
    
    # Show what's using the port
    processes = get_processes_using_port(default_port)
    if processes:
        print(f"📋 Processes using port {default_port}:")
        for process in processes:
            print(f"   {process}")
    
    while True:
        print("\n🛠️  Port Management Options:")
        print("1. Kill processes on port 8000 and use it")
        print("2. Use a different port")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            if kill_processes_on_port(default_port):
                print(f"✅ Killed processes on port {default_port}")
                # Wait a moment for the port to be released
                import time
                time.sleep(1)
                if check_port_available(default_port):
                    print(f"✅ Port {default_port} is now available")
                    return default_port
                else:
                    print(f"❌ Port {default_port} still not available")
            else:
                print(f"❌ Failed to kill processes on port {default_port}")
        
        elif choice == "2":
            print("🔍 Finding available port...")
            available_port = find_available_port(8001, 20)
            if available_port:
                print(f"✅ Found available port: {available_port}")
                return available_port
            else:
                print("❌ No available ports found in range 8001-8020")
        
        elif choice == "3":
            print("👋 Goodbye!")
            sys.exit(0)
        
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Initialize the prompt manager
manager = PromptManager()

# Initialize template builder
from test_template_builder import TemplateBuilder, PromptTemplate

template_builder = TemplateBuilder()

# Add some default templates
user_story_template = PromptTemplate(
    name="User Story",
    pattern="As a {role}, I want to {action} so that {reason}.",
    slots={
        "role": ["developer", "designer", "manager"],
        "action": ["create", "improve", "fix", "optimize"],
        "reason": ["users benefit", "system works better", "team is efficient"]
    }
)

code_review_template = PromptTemplate(
    name="Code Review",
    pattern="Review this code as a {role} with focus on {aspect}.",
    slots={
        "role": ["senior developer", "junior developer", "architect"],
        "aspect": ["security", "performance", "readability", "best practices"]
    }
)

template_builder.add_template(user_story_template)
template_builder.add_template(code_review_template)

# Enhanced HTML template with Bootstrap and flash messages
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prompt Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1><i class="fas fa-comments me-2"></i>Prompt Manager</h1>
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addPromptModal">
                        <i class="fas fa-plus me-1"></i>New Prompt
                    </button>
                </div>
            </div>
        </div>

        <!-- Search Section -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title"><i class="fas fa-search me-2"></i>Search Prompts</h5>
                        <form method="GET" action="/search" class="row g-3">
                            <div class="col-md-8">
                                <input type="text" name="q" class="form-control" placeholder="Search term..." value="{{ current_query or '' }}">
                            </div>
                            <div class="col-md-4">
                                <button type="submit" class="btn btn-success w-100">
                                    <i class="fas fa-search me-1"></i>Search
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- Prompts List -->
        <div class="row">
            {% if prompts %}
                <div class="col-12">
                    <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
                        {% for prompt in prompts %}
                            <div class="col">
                                <div class="card h-100">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between align-items-start mb-2">
                                            <h5 class="card-title mb-0">{{ prompt.name }}</h5>
                                            <span class="badge bg-secondary">{{ prompt.category }}</span>
                                        </div>
                                        <p class="card-text">{{ prompt.text[:100] }}{% if prompt.text|length > 100 %}...{% endif %}</p>
                                        <div class="text-muted small">
                                            <i class="fas fa-clock me-1"></i>
                                            Created: {{ prompt.created_at.split('T')[0] if 'T' in prompt.created_at else prompt.created_at }}
                                        </div>
                                    </div>
                                    <div class="card-footer bg-transparent">
                                        <div class="btn-group w-100" role="group">
                                            <button class="btn btn-outline-primary btn-sm" onclick="viewPrompt('{{ prompt.id }}', '{{ prompt.name }}', '{{ prompt.text|replace("'", "\\'")|replace('"', '\\"') }}')">
                                                <i class="fas fa-eye me-1"></i>View
                                            </button>
                                            <button class="btn btn-outline-danger btn-sm" onclick="deletePrompt('{{ prompt.id }}', '{{ prompt.name }}')">
                                                <i class="fas fa-trash me-1"></i>Delete
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        {% endfor %}
                    </div>
                </div>
            {% else %}
                <div class="col-12">
                    <div class="text-center py-5">
                        <i class="fas fa-comments fa-3x text-muted mb-3"></i>
                        <h3 class="text-muted">No prompts found</h3>
                        {% if current_query %}
                            <p class="text-muted">Try adjusting your search criteria.</p>
                        {% else %}
                            <p class="text-muted">Get started by creating your first prompt!</p>
                        {% endif %}
                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addPromptModal">
                            <i class="fas fa-plus me-1"></i>Create Your First Prompt
                        </button>
                    </div>
                </div>
            {% endif %}
        </div>
    </div>

    <!-- Add Prompt Modal -->
    <div class="modal fade" id="addPromptModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Add New Prompt</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form method="POST" action="/add">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="name" class="form-label">Name</label>
                            <input type="text" class="form-control" id="name" name="name" required>
                        </div>
                        <div class="mb-3">
                            <label for="text" class="form-label">Text</label>
                            <textarea class="form-control" id="text" name="text" rows="4" required></textarea>
                        </div>
                        <div class="mb-3">
                            <label for="category" class="form-label">Category</label>
                            <input type="text" class="form-control" id="category" name="category" value="general">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add Prompt</button>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <!-- View Prompt Modal -->
    <div class="modal fade" id="viewPromptModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="viewPromptTitle"></h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Text</label>
                        <textarea class="form-control" id="viewPromptText" rows="8" readonly></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-primary" onclick="copyToClipboard()">
                        <i class="fas fa-copy me-1"></i>Copy to Clipboard
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Confirm Delete</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>Are you sure you want to delete the prompt "<span id="delete-prompt-name"></span>"?</p>
                    <p class="text-danger"><small>This action cannot be undone.</small></p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <form id="delete-form" method="POST" style="display: inline;">
                        <button type="submit" class="btn btn-danger">Delete</button>
                    </form>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function viewPrompt(id, name, text) {
            document.getElementById('viewPromptTitle').textContent = name;
            document.getElementById('viewPromptText').value = text;
            const modal = new bootstrap.Modal(document.getElementById('viewPromptModal'));
            modal.show();
        }

        function deletePrompt(promptId, promptName) {
            document.getElementById('delete-prompt-name').textContent = promptName;
            document.getElementById('delete-form').action = `/delete/${promptId}`;
            const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
            modal.show();
        }

        function copyToClipboard() {
            const textArea = document.getElementById('viewPromptText');
            textArea.select();
            document.execCommand('copy');
            alert('Copied to clipboard!');
        }
    </script>
</body>
</html>
"""

# Template Builder HTML Template
TEMPLATE_BUILDER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Template Builder - Prompt Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="row">
            <div class="col-12">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h1><i class="fas fa-puzzle-piece me-2"></i>Template Builder</h1>
                    <a href="/" class="btn btn-secondary">
                        <i class="fas fa-arrow-left me-1"></i>Back to Prompts
                    </a>
                </div>
            </div>
        </div>

        <!-- Template Selection -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title"><i class="fas fa-list me-2"></i>Select Template</h5>
                        <select id="templateSelect" class="form-select">
                            <option value="">Choose a template...</option>
                            {% for template in templates %}
                                <option value="{{ template.name }}">{{ template.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
            </div>
        </div>

        <!-- Template Builder Form -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title"><i class="fas fa-edit me-2"></i>Build Prompt</h5>
                        <form id="templateForm">
                            <div id="slotFields">
                                <!-- Slot fields will be dynamically added here -->
                            </div>
                            <button type="submit" class="btn btn-primary mt-3">
                                <i class="fas fa-magic me-1"></i>Generate Prompt
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <!-- Generated Prompt -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title"><i class="fas fa-file-alt me-2"></i>Generated Prompt</h5>
                        <div id="generatedPrompt" class="alert alert-info" style="display: none;">
                            <!-- Generated prompt will appear here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        const templates = {{ templates|tojson }};
        
        document.getElementById('templateSelect').addEventListener('change', function() {
            const templateName = this.value;
            const template = templates.find(t => t.name === templateName);
            
            if (template) {
                generateSlotFields(template);
            } else {
                document.getElementById('slotFields').innerHTML = '';
            }
        });
        
        function generateSlotFields(template) {
            const slotFields = document.getElementById('slotFields');
            slotFields.innerHTML = '';
            
            for (const [slotName, options] of Object.entries(template.slots)) {
                const fieldGroup = document.createElement('div');
                fieldGroup.className = 'mb-3';
                
                fieldGroup.innerHTML = `
                    <label for="${slotName}" class="form-label">${slotName.charAt(0).toUpperCase() + slotName.slice(1)}</label>
                    <select name="${slotName}" id="${slotName}" class="form-select" required>
                        <option value="">Choose ${slotName}...</option>
                        ${options.map(option => `<option value="${option}">${option}</option>`).join('')}
                    </select>
                `;
                
                slotFields.appendChild(fieldGroup);
            }
        }
        
        document.getElementById('templateForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const templateName = document.getElementById('templateSelect').value;
            const values = {};
            
            // Collect form values
            const formData = new FormData(this);
            for (const [key, value] of formData.entries()) {
                if (value) {
                    values[key] = value;
                }
            }
            
            // Send to API
            fetch('/api/templates/build', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    template_name: templateName,
                    values: values
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    const promptDiv = document.getElementById('generatedPrompt');
                    promptDiv.innerHTML = data.prompt;
                    promptDiv.style.display = 'block';
                }
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Home page - list all prompts."""
    try:
        prompts = manager.list_prompts()
        # Convert prompts to dict format for template
        prompt_dicts = []
        for prompt in prompts:
            prompt_dict = {
                'id': prompt.id,
                'name': prompt.name,
                'text': prompt.text,
                'category': prompt.category,
                'created_at': prompt.created_at.isoformat() if prompt.created_at else '',
                'modified_at': prompt.modified_at.isoformat() if prompt.modified_at else ''
            }
            prompt_dicts.append(prompt_dict)
        
        return render_template_string(HTML_TEMPLATE, prompts=prompt_dicts, current_query='')
    except Exception as e:
        flash(f'Error loading prompts: {str(e)}', 'error')
        return render_template_string(HTML_TEMPLATE, prompts=[], current_query='')

@app.route('/add', methods=['POST'])
def add_prompt():
    """Add a new prompt."""
    try:
        name = request.form.get('name', '').strip()
        text = request.form.get('text', '').strip()
        category = request.form.get('category', 'general').strip()
        
        if not name or not text:
            flash('Name and text are required', 'error')
            return redirect(url_for('index'))
        
        prompt_id = manager.add_prompt(name, text, category)
        flash('Prompt created successfully!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error creating prompt: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/search')
def search():
    """Search prompts."""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))
    
    try:
        results = manager.search_prompts(query)
        # Convert prompts to dict format for template
        prompt_dicts = []
        for prompt in results:
            prompt_dict = {
                'id': prompt.id,
                'name': prompt.name,
                'text': prompt.text,
                'category': prompt.category,
                'created_at': prompt.created_at.isoformat() if prompt.created_at else '',
                'modified_at': prompt.modified_at.isoformat() if prompt.modified_at else ''
            }
            prompt_dicts.append(prompt_dict)
        
        return render_template_string(HTML_TEMPLATE, prompts=prompt_dicts, current_query=query)
    except Exception as e:
        flash(f'Error searching prompts: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/delete/<prompt_id>', methods=['POST'])
def delete_prompt(prompt_id):
    """Delete a prompt."""
    try:
        manager.delete_prompt(prompt_id)
        flash('Prompt deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting prompt: {str(e)}', 'error')
    
    return redirect(url_for('index'))

# Template Builder Routes
@app.route('/api/templates')
def get_templates():
    """Get available templates as JSON."""
    try:
        templates = []
        for template in template_builder.templates:
            templates.append({
                "name": template.name,
                "pattern": template.pattern,
                "slots": template.slots
            })
        return json.dumps(templates), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/api/templates/build', methods=['POST'])
def build_prompt():
    """Build a prompt from template and values."""
    try:
        data = request.get_json()
        template_name = data.get('template_name')
        values = data.get('values', {})
        
        template = template_builder.get_template_by_name(template_name)
        if not template:
            return json.dumps({"error": "Template not found"}), 404, {'Content-Type': 'application/json'}
        
        result = template.build_prompt(values)
        return json.dumps({"prompt": result}), 200, {'Content-Type': 'application/json'}
    except ValueError as e:
        return json.dumps({"error": str(e)}), 400, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/templates')
def template_builder_page():
    """Template builder page."""
    try:
        templates = []
        for template in template_builder.templates:
            templates.append({
                "name": template.name,
                "pattern": template.pattern,
                "slots": template.slots
            })
        return render_template_string(TEMPLATE_BUILDER_HTML, templates=templates)
    except Exception as e:
        flash(f'Error loading templates: {str(e)}', 'error')
        return render_template_string(TEMPLATE_BUILDER_HTML, templates=[])

if __name__ == '__main__':
    print("🚀 Starting Enhanced Simple Prompt Manager Web Server...")
    print("=" * 60)
    
    # Setup port
    port = setup_port()
    
    print(f"\n🌐 Web interface will be available at: http://localhost:{port}")
    print("✨ Features:")
    print("  - Browse and search prompts")
    print("  - Create and edit prompts with validation")
    print("  - Flash messages for user feedback")
    print("  - Responsive design with Bootstrap")
    print("  - View prompts in modal")
    print("  - Delete prompts with confirmation")
    print("  - Prompt Builder (coming soon)")
    print()
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=port, debug=False) 