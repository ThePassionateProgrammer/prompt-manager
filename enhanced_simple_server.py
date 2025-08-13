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
from datetime import datetime

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

# Predefined categories for better organization
PREDEFINED_CATEGORIES = [
    "general",
    "writing",
    "coding",
    "analysis",
    "creative",
    "business",
    "education",
    "research",
    "template",
    "custom"
]

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
                    <div class="d-flex gap-2">
                        <a href="/template-builder" class="btn btn-outline-primary">
                            <i class="fas fa-magic me-1"></i>Template Builder
                        </a>
                        <a href="/export" class="btn btn-outline-success">
                            <i class="fas fa-download me-1"></i>Export
                        </a>
                        <a href="/import" class="btn btn-outline-info">
                            <i class="fas fa-upload me-1"></i>Import
                        </a>
                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addPromptModal">
                            <i class="fas fa-plus me-1"></i>New Prompt
                        </button>
                    </div>
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
                                            <button class="btn btn-outline-warning btn-sm" onclick="editPrompt('{{ prompt.id }}', '{{ prompt.name }}', '{{ prompt.text|replace("'", "\\'")|replace('"', '\\"') }}', '{{ prompt.category }}')">
                                                <i class="fas fa-edit me-1"></i>Edit
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
                            <select class="form-select" id="category" name="category">
                                {% for cat in predefined_categories %}
                                    <option value="{{ cat }}" {% if cat == 'general' %}selected{% endif %}>{{ cat|title }}</option>
                                {% endfor %}
                            </select>
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

    <!-- Edit Prompt Modal -->
    <div class="modal fade" id="editPromptModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Edit Prompt</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <form method="POST" action="/edit" id="editForm">
                    <input type="hidden" id="editPromptId" name="prompt_id">
                    <div class="modal-body">
                        <div class="mb-3">
                            <label for="editName" class="form-label">Name</label>
                            <input type="text" class="form-control" id="editName" name="name" required>
                        </div>
                        <div class="mb-3">
                            <label for="editText" class="form-label">Text</label>
                            <textarea class="form-control" id="editText" name="text" rows="4" required></textarea>
                        </div>
                        <div class="mb-3">
                            <label for="editCategory" class="form-label">Category</label>
                            <select class="form-select" id="editCategory" name="category">
                                {% for cat in predefined_categories %}
                                    <option value="{{ cat }}">{{ cat|title }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="submit" class="btn btn-primary">Update Prompt</button>
                    </div>
                </form>
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

        function editPrompt(promptId, promptName, promptText, promptCategory) {
            document.getElementById('editPromptId').value = promptId;
            document.getElementById('editName').value = promptName;
            document.getElementById('editText').value = promptText;
            
            // Set the selected category in the dropdown
            const categorySelect = document.getElementById('editCategory');
            categorySelect.value = promptCategory;
            
            const modal = new bootstrap.Modal(document.getElementById('editPromptModal'));
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
    <style>
        .template-builder-container {
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .top-panel {
            flex: 1;
            background-color: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            padding: 20px;
            overflow-y: auto;
        }
        .bottom-panel {
            flex: 0 0 200px;
            background-color: #ffffff;
            border-top: 2px solid #dee2e6;
            padding: 20px;
        }
        .dropdown-container {
            margin-bottom: 15px;
        }
        .dropdown-label {
            font-weight: 600;
            margin-bottom: 5px;
            color: #495057;
        }
        .edit-mode-active {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
        }
        .final-prompt {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="template-builder-container">
        <!-- Header -->
        <div class="bg-primary text-white p-3">
            <div class="d-flex justify-content-between align-items-center">
                <h1 class="h3 mb-0"><i class="fas fa-puzzle-piece me-2"></i>Template Builder</h1>
                <div>
                    <button id="editModeBtn" class="btn btn-outline-light me-2">
                        <i class="fas fa-edit me-1"></i>Edit Mode
                    </button>
                    <a href="/" class="btn btn-outline-light">
                        <i class="fas fa-arrow-left me-1"></i>Back to Prompts
                    </a>
                </div>
            </div>
        </div>

        <!-- Top Panel - Dropdowns Area -->
        <div class="top-panel">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <h4 class="mb-3"><i class="fas fa-list me-2"></i>Template Variables</h4>
                        <div id="dropdownsArea">
                            <div class="text-center text-muted py-5">
                                <i class="fas fa-arrow-down fa-2x mb-3"></i>
                                <p>Enter a template below and click "Generate" to create dropdowns</p>
                            </div>
                        </div>
                        <div id="finalPromptArea" class="final-prompt" style="display: none;">
                            <h5><i class="fas fa-file-alt me-2"></i>Final Prompt</h5>
                            <div id="finalPromptText"></div>
                            <button id="savePromptBtn" class="btn btn-success btn-sm mt-2">
                                <i class="fas fa-save me-1"></i>Save as Prompt
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Bottom Panel - Template Input -->
        <div class="bottom-panel">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1 me-3">
                                <label for="templateInput" class="form-label">
                                    <i class="fas fa-edit me-1"></i>Template Text
                                </label>
                                <textarea id="templateInput" class="form-control" rows="3" 
                                    placeholder="Enter template with variables in brackets, e.g., 'As a [role], I want to [what], so that I can [why]'"></textarea>
                            </div>
                            <div class="flex-shrink-0">
                                <button id="generateBtn" class="btn btn-primary btn-lg">
                                    <i class="fas fa-magic me-1"></i>Generate
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let editMode = false;
        let currentTemplate = '';
        let currentSelections = {};
        let dropdownsData = {};

        // Edit Mode Toggle
        document.getElementById('editModeBtn').addEventListener('click', function() {
            editMode = !editMode;
            this.classList.toggle('btn-outline-light');
            this.classList.toggle('btn-warning');
            
            if (editMode) {
                this.innerHTML = '<i class="fas fa-check me-1"></i>Edit Mode Active';
                document.getElementById('dropdownsArea').classList.add('edit-mode-active');
            } else {
                this.innerHTML = '<i class="fas fa-edit me-1"></i>Edit Mode';
                document.getElementById('dropdownsArea').classList.remove('edit-mode-active');
            }
            
            // Toggle edit mode on server
            fetch('/template/edit-mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: editMode })
            });
        });

        // Generate Button
        document.getElementById('generateBtn').addEventListener('click', function() {
            const templateText = document.getElementById('templateInput').value.trim();
            if (!templateText) {
                alert('Please enter a template text');
                return;
            }
            
            currentTemplate = templateText;
            
            fetch('/template/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ template: templateText })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert('Error: ' + data.error);
                } else {
                    dropdownsData = data.dropdowns;
                    createDropdowns(data.dropdowns);
                }
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        });

        function createDropdowns(dropdowns) {
            const dropdownsArea = document.getElementById('dropdownsArea');
            dropdownsArea.innerHTML = '';
            
            const variables = Object.keys(dropdowns);
            
            variables.forEach((variable, index) => {
                const dropdownContainer = document.createElement('div');
                dropdownContainer.className = 'dropdown-container';
                dropdownContainer.innerHTML = `
                    <div class="dropdown-label">${variable.charAt(0).toUpperCase() + variable.slice(1)}</div>
                    <select id="dropdown_${variable}" class="form-select" data-variable="${variable}">
                        <option value="">Select ${variable}...</option>
                        ${dropdowns[variable].options.map(option => 
                            `<option value="${option}">${option}</option>`
                        ).join('')}
                    </select>
                `;
                
                dropdownsArea.appendChild(dropdownContainer);
                
                // Add change listener for context-aware updates
                const dropdown = document.getElementById(`dropdown_${variable}`);
                dropdown.addEventListener('change', function() {
                    const selectedValue = this.value;
                    const variableName = this.dataset.variable;
                    
                    if (selectedValue) {
                        currentSelections[variableName] = selectedValue;
                        
                        // Update subsequent dropdowns based on this selection
                        updateSubsequentDropdowns(variableName, selectedValue, index);
                    }
                    
                    // Generate final prompt
                    generateFinalPrompt();
                });
            });
        }

        function updateSubsequentDropdowns(changedVariable, selectedValue, changedIndex) {
            const variables = Object.keys(dropdownsData);
            
            // Update dropdowns to the right of the changed one
            for (let i = changedIndex + 1; i < variables.length; i++) {
                const variableName = variables[i];
                const dropdown = document.getElementById(`dropdown_${variableName}`);
                
                // Get context from previous selections
                const context = {};
                for (let j = 0; j < i; j++) {
                    const prevVariable = variables[j];
                    const prevDropdown = document.getElementById(`dropdown_${prevVariable}`);
                    if (prevDropdown.value) {
                        context[prevVariable] = prevDropdown.value;
                    }
                }
                
                // Update options for this dropdown
                fetch('/template/update-options', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        variable: variableName,
                        context: context
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.options) {
                        // Update dropdown options
                        dropdown.innerHTML = `<option value="">Select ${variableName}...</option>` +
                            data.options.map(option => `<option value="${option}">${option}</option>`).join('');
                        
                        // Clear the selection since options changed
                        dropdown.value = '';
                        delete currentSelections[variableName];
                        
                        // Clear subsequent dropdowns
                        for (let k = i + 1; k < variables.length; k++) {
                            const nextVariable = variables[k];
                            const nextDropdown = document.getElementById(`dropdown_${nextVariable}`);
                            nextDropdown.value = '';
                            delete currentSelections[nextVariable];
                        }
                        
                        generateFinalPrompt();
                    }
                })
                .catch(error => console.error('Error updating options:', error));
            }
        }

        function generateFinalPrompt() {
            if (Object.keys(currentSelections).length === 0) {
                document.getElementById('finalPromptArea').style.display = 'none';
                return;
            }
            
            fetch('/template/generate-final', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template: currentTemplate,
                    selections: currentSelections
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.final_prompt) {
                    document.getElementById('finalPromptText').textContent = data.final_prompt;
                    document.getElementById('finalPromptArea').style.display = 'block';
                }
            })
            .catch(error => console.error('Error generating final prompt:', error));
        }

        // Save Prompt Button
        document.getElementById('savePromptBtn').addEventListener('click', function() {
            const finalPrompt = document.getElementById('finalPromptText').textContent;
            if (!finalPrompt) {
                alert('No prompt to save');
                return;
            }
            
            // Create a name for the prompt
            const promptName = `Template: ${Object.keys(currentSelections).join(' → ')}`;
            
            // Save to prompts (you can implement this as needed)
            fetch('/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: `name=${encodeURIComponent(promptName)}&text=${encodeURIComponent(finalPrompt)}&category=template`
            })
            .then(response => {
                if (response.ok) {
                    alert('Prompt saved successfully!');
                } else {
                    alert('Error saving prompt');
                }
            })
            .catch(error => {
                alert('Error saving prompt: ' + error);
            });
        });
    </script>
</body>
</html>
"""

# Import Template
IMPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Import Prompts - Prompt Manager</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-4">
        <h1><i class="fas fa-upload me-2"></i>Import Prompts from JSON</h1>
        <p>Select a JSON file containing prompt data to import.</p>
        
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

        <form method="POST" enctype="multipart/form-data" action="/import">
            <div class="mb-3">
                <label for="jsonFile" class="form-label">
                    <i class="fas fa-file-upload me-1"></i>Choose JSON File
                </label>
                <input type="file" class="form-control" id="jsonFile" name="file" accept=".json" required>
            </div>
            <button type="submit" class="btn btn-primary">
                <i class="fas fa-upload me-1"></i>Import Prompts
            </button>
        </form>
        <a href="/" class="btn btn-secondary mt-3">
            <i class="fas fa-arrow-left me-1"></i>Back to Prompts
        </a>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
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
        
        return render_template_string(HTML_TEMPLATE, prompts=prompt_dicts, current_query='', predefined_categories=PREDEFINED_CATEGORIES)
    except Exception as e:
        flash(f'Error loading prompts: {str(e)}', 'error')
        return render_template_string(HTML_TEMPLATE, prompts=[], current_query='', predefined_categories=PREDEFINED_CATEGORIES)

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
        
        return render_template_string(HTML_TEMPLATE, prompts=prompt_dicts, current_query=query, predefined_categories=PREDEFINED_CATEGORIES)
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

@app.route('/edit', methods=['POST'])
def edit_prompt():
    """Edit a prompt."""
    try:
        prompt_id = request.form.get('prompt_id', '').strip()
        name = request.form.get('name', '').strip()
        text = request.form.get('text', '').strip()
        category = request.form.get('category', 'general').strip()
        
        if not prompt_id or not name or not text:
            flash('Prompt ID, name, and text are required', 'error')
            return redirect(url_for('index'))
        
        # Get the existing prompt to update it
        prompt = manager.get_prompt(prompt_id)
        if not prompt:
            flash('Prompt not found', 'error')
            return redirect(url_for('index'))
        
        # Update the prompt
        prompt.name = name
        prompt.text = text
        prompt.category = category
        prompt.update_text(text)  # This updates the modified_at timestamp
        
        # Save the updated prompt
        manager.save_prompts()
        
        flash('Prompt updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating prompt: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/export', methods=['GET'])
def export_prompts():
    """Export all prompts to a JSON file."""
    try:
        # Get all prompts
        prompts = manager.get_all_prompts()
        
        # Convert to JSON-serializable format
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_prompts': len(prompts),
            'prompts': []
        }
        
        for prompt in prompts:
            export_data['prompts'].append({
                'id': prompt.id,
                'name': prompt.name,
                'text': prompt.text,
                'category': prompt.category,
                'created_at': prompt.created_at,
                'modified_at': prompt.modified_at
            })
        
        # Create response with JSON file
        from flask import send_file
        import tempfile
        import os
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(export_data, f, indent=2)
            temp_file = f.name
        
        # Send file and clean up
        response = send_file(
            temp_file,
            as_attachment=True,
            download_name=f'prompts_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            mimetype='application/json'
        )
        
        # Clean up temp file after sending
        response.call_on_close(lambda: os.unlink(temp_file))
        
        flash(f'Successfully exported {len(prompts)} prompts to JSON file', 'success')
        return response
        
    except Exception as e:
        flash(f'Error exporting prompts: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/import', methods=['GET', 'POST'])
def import_prompts():
    """Import prompts from a JSON file."""
    if request.method == 'GET':
        # Show import form
        return render_template_string(IMPORT_TEMPLATE)
    
    # Handle file upload
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('import_prompts'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('import_prompts'))
    
    if not file.filename.endswith('.json'):
        flash('Please select a JSON file', 'error')
        return redirect(url_for('import_prompts'))
    
    try:
        # Parse JSON file
        import_data = json.load(file)
        
        if 'prompts' not in import_data:
            flash('Invalid file format: missing prompts array', 'error')
            return redirect(url_for('import_prompts'))
        
        # Import prompts
        imported_count = 0
        skipped_count = 0
        
        for prompt_data in import_data['prompts']:
            try:
                # Check if prompt already exists (by name)
                existing_prompts = manager.search_prompts(prompt_data.get('name', ''))
                if existing_prompts:
                    skipped_count += 1
                    continue
                
                # Create new prompt
                manager.add_prompt(
                    name=prompt_data.get('name', 'Imported Prompt'),
                    text=prompt_data.get('text', ''),
                    category=prompt_data.get('category', 'imported')
                )
                imported_count += 1
                
            except Exception as e:
                flash(f'Error importing prompt "{prompt_data.get("name", "Unknown")}": {str(e)}', 'error')
                continue
        
        flash(f'Import completed: {imported_count} prompts imported, {skipped_count} skipped (already exist)', 'success')
        return redirect(url_for('index'))
        
    except json.JSONDecodeError:
        flash('Invalid JSON file', 'error')
        return redirect(url_for('import_prompts'))
    except Exception as e:
        flash(f'Error importing prompts: {str(e)}', 'error')
        return redirect(url_for('import_prompts'))

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

@app.route('/template-builder')
def template_builder_page():
    """Template builder page with the new UI design."""
    return render_template_string(TEMPLATE_BUILDER_HTML)

# Template Builder API Routes
@app.route('/template/parse', methods=['POST'])
def parse_template():
    """Parse template text and extract bracketed variables."""
    try:
        data = request.get_json()
        template_text = data.get('template', '')
        
        # Extract variables in brackets [variable]
        import re
        variables = re.findall(r'\[([^\]]+)\]', template_text)
        
        return json.dumps({
            'variables': variables,
            'template': template_text
        }), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/template/generate-dropdowns', methods=['POST'])
def generate_dropdowns():
    """Generate dropdown options for detected variables."""
    try:
        data = request.get_json()
        template_text = data.get('template', '')
        
        # Extract variables
        import re
        variables = re.findall(r'\[([^\]]+)\]', template_text)
        
        # Define default options for common variables
        default_options = {
            'role': ['Programmer', 'Chef', 'Soccer Coach', 'Teacher', 'Designer'],
            'what': ['Write code', 'Shop for food', 'Create tests', 'Prepare lunch', 'Plan dinner party', 'Refactor'],
            'why': ['Build better software', 'Cook delicious meals', 'Improve code quality', 'Feed my family', 'Host friends'],
            'action': ['Write code', 'Create tests', 'Refactor', 'Shop for food', 'Prepare lunch'],
            'context': ['Web development', 'Mobile app', 'Backend API', 'Kitchen', 'Restaurant']
        }
        
        dropdowns = {}
        for var in variables:
            dropdowns[var] = {
                'options': default_options.get(var, [f'Option 1 for {var}', f'Option 2 for {var}'])
            }
        
        return json.dumps({
            'dropdowns': dropdowns,
            'template': template_text
        }), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/template/update-options', methods=['POST'])
def update_options():
    """Update dropdown options based on context (selections from previous dropdowns)."""
    try:
        data = request.get_json()
        variable = data.get('variable', '')
        context = data.get('context', {})
        
        # Define context-aware options
        context_options = {
            'what': {
                'Programmer': ['Write code', 'Create tests', 'Refactor', 'Debug', 'Optimize'],
                'Chef': ['Shop for food', 'Prepare lunch', 'Plan dinner party', 'Cook meal', 'Bake dessert'],
                'Soccer Coach': ['Train players', 'Plan strategy', 'Analyze games', 'Motivate team', 'Teach skills']
            },
            'why': {
                'Write code': ['Build better software', 'Solve problems', 'Learn new skills', 'Improve efficiency'],
                'Shop for food': ['Cook delicious meals', 'Feed my family', 'Save money', 'Eat healthy'],
                'Create tests': ['Ensure quality', 'Prevent bugs', 'Build confidence', 'Document behavior']
            }
        }
        
        # Get options based on context
        if variable in context_options:
            # Find the most relevant context key
            for context_key, options in context_options[variable].items():
                if context_key in context.values():
                    return json.dumps({'options': options}), 200, {'Content-Type': 'application/json'}
        
        # Fallback to default options
        default_options = {
            'what': ['Write code', 'Shop for food', 'Create tests', 'Prepare lunch'],
            'why': ['Build better software', 'Cook delicious meals', 'Improve quality', 'Feed my family']
        }
        
        return json.dumps({'options': default_options.get(variable, [f'Option for {variable}'])}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/template/generate-final', methods=['POST'])
def generate_final_prompt():
    """Generate final prompt by replacing variables with user selections."""
    try:
        data = request.get_json()
        template_text = data.get('template', '')
        selections = data.get('selections', {})
        
        # Replace each variable with its selection
        final_prompt = template_text
        for variable, value in selections.items():
            final_prompt = final_prompt.replace(f'[{variable}]', value)
        
        return json.dumps({
            'final_prompt': final_prompt,
            'template': template_text,
            'selections': selections
        }), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/template/edit-mode', methods=['POST'])
def toggle_edit_mode():
    """Toggle edit mode for the template builder."""
    try:
        data = request.get_json()
        enabled = data.get('enabled', False)
        
        return json.dumps({
            'edit_mode': enabled
        }), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/template/generate', methods=['POST'])
def generate_template():
    """Main generate endpoint that processes template and returns dropdowns."""
    try:
        data = request.get_json()
        template_text = data.get('template', '')
        
        # Extract variables
        import re
        variables = re.findall(r'\[([^\]]+)\]', template_text)
        
        # Generate dropdowns (reuse the logic from generate_dropdowns)
        default_options = {
            'role': ['Programmer', 'Chef', 'Soccer Coach', 'Teacher', 'Designer'],
            'what': ['Write code', 'Shop for food', 'Create tests', 'Prepare lunch', 'Plan dinner party', 'Refactor'],
            'why': ['Build better software', 'Cook delicious meals', 'Improve code quality', 'Feed my family', 'Host friends'],
            'action': ['Write code', 'Create tests', 'Refactor', 'Shop for food', 'Prepare lunch'],
            'context': ['Web development', 'Mobile app', 'Backend API', 'Kitchen', 'Restaurant']
        }
        
        dropdowns = {}
        for var in variables:
            dropdowns[var] = {
                'options': default_options.get(var, [f'Option 1 for {var}', f'Option 2 for {var}'])
            }
        
        return json.dumps({
            'dropdowns': dropdowns,
            'template': template_text
        }), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@app.route('/test-combo-box')
def test_combo_box_page():
    """Test page for custom combo box component."""
    with open('test_combo_box_page.html', 'r') as f:
        return f.read()

@app.route('/test')
def test_route():
    """Simple test route to verify route registration."""
    return "Test route working!"

if __name__ == '__main__':
    print("🚀 Starting Enhanced Simple Prompt Manager Web Server...")
    print("📋 Version: 1.4 - Custom Combo Box Component Ready")
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