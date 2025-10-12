"""
Linkage System Routes - Template Builder with Custom Combo Boxes

This module contains the working linkage system for template building.
"""

from flask import Blueprint, request, render_template_string, json
from src.prompt_manager.template_service import TemplateService

# Create blueprint
linkage_bp = Blueprint('linkage', __name__)

# Get the TEMPLATE_BUILDER_HTML from the original file
TEMPLATE_BUILDER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Template Builder - Prompt Manager</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .version-info {
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }
        .template-input {
            width: 100%;
            height: 120px;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            font-family: 'Courier New', monospace;
            margin-bottom: 20px;
            resize: vertical;
        }
        .template-input:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }
        .controls {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s;
        }
        .btn-primary {
            background-color: #007bff;
            color: white;
        }
        .btn-primary:hover {
            background-color: #0056b3;
        }
        .btn-success {
            background-color: #28a745;
            color: white;
        }
        .btn-success:hover {
            background-color: #1e7e34;
        }
        .btn-secondary {
            background-color: #6c757d;
            color: white;
        }
        .btn-secondary:hover {
            background-color: #545b62;
        }
        .dropdown-container {
            display: flex;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        .dropdown-wrapper {
            flex: 1;
            min-width: 200px;
        }
        .dropdown-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #333;
        }
        .custom-combo-box {
            position: relative;
            width: 100%;
        }
        .combo-input {
            width: 100%;
            padding: 12px 40px 12px 15px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            background: white;
            cursor: pointer;
        }
        .combo-input:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }
        .combo-arrow {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            pointer-events: none;
            color: #666;
        }
        .combo-dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 2px solid #ddd;
            border-top: none;
            border-radius: 0 0 6px 6px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        }
        .combo-option {
            padding: 12px 15px;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
        }
        .combo-option:hover {
            background-color: #f8f9fa;
        }
        .combo-option:last-child {
            border-bottom: none;
        }
        .combo-option.add-new {
            background-color: #e3f2fd;
            color: #1976d2;
            font-weight: 500;
        }
        .combo-option.add-new:hover {
            background-color: #bbdefb;
        }
        .generated-prompt {
            background-color: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
        }
        .generated-prompt h4 {
            margin-top: 0;
            color: #495057;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .save-section {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
        }
        .save-form {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }
        .save-input {
            flex: 1;
            min-width: 200px;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        .save-input:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }
        .status-message {
            padding: 12px 20px;
            border-radius: 6px;
            margin-top: 15px;
            font-weight: 500;
        }
        .status-success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status-error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .load-section {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }
        .template-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .template-item {
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .template-item:hover {
            border-color: #007bff;
            background-color: #f8f9fa;
        }
        .template-name {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        .template-description {
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Template Builder</h1>
            <p>Create dynamic prompts with custom combo boxes and linkages</p>
            <div class="version-info">ComboBox v2.5 | LinkageManager v3.1</div>
        </div>

        <div>
            <label for="templateInput" style="display: block; margin-bottom: 10px; font-weight: 500;">
                Template Text (use [variable] for dynamic content):
            </label>
            <textarea 
                id="templateInput" 
                class="template-input" 
                placeholder="Enter your template here, e.g.: As a [role], I want to [what] so that [why]."
            >As a [role], I want to [what] so that [why].</textarea>
        </div>

        <div class="controls">
            <button class="btn btn-primary" onclick="parseTemplate()">Parse Template</button>
            <button class="btn btn-success" onclick="generateTemplate()">Generate Template</button>
            <button class="btn btn-secondary" onclick="clearAll()">Clear All</button>
        </div>

        <div id="dropdownContainer" class="dropdown-container">
            <!-- Dynamic dropdowns will be generated here -->
        </div>

        <div id="generatedPrompt" class="generated-prompt" style="display: none;">
            <h4>Generated Prompt:</h4>
            <div id="promptContent"></div>
        </div>

        <div class="save-section">
            <h3>💾 Save Template</h3>
            <div class="save-form">
                <input type="text" id="templateName" class="save-input" placeholder="Template name" required>
                <input type="text" id="templateDescription" class="save-input" placeholder="Template description" required>
                <button class="btn btn-success" onclick="saveTemplate()">Save Template</button>
            </div>
            <div id="saveStatus"></div>
        </div>

        <div class="load-section">
            <h3>📂 Load Template</h3>
            <button class="btn btn-secondary" onclick="loadTemplates()">Refresh Template List</button>
            <div id="templateList" class="template-list">
                <!-- Saved templates will be loaded here -->
            </div>
        </div>
    </div>

    <!-- JavaScript files with cache busting -->
    <script src="/static/js/custom-combo-box-working.js?v=2.5&t=20241220&cache=bust"></script>
    <script src="/static/js/linkage-manager-v3.js?v=3.1&t=20241220&cache=bust"></script>
    
    <script>
        let linkageManager = null;
        let currentTemplateId = null;

        // Initialize the application
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Template Builder initialized');
            setupLinkages();
        });

        function setupLinkages() {
            console.log('=== SETTING UP LINKAGES (LinkageManager v3.1) ===');
            
            // Initialize LinkageManager
            linkageManager = new LinkageManager();
            
            // Make it globally accessible
            window.linkageManager = linkageManager;
            
            console.log('LinkageManager setup completed');
        }

        function parseTemplate() {
            const templateText = document.getElementById('templateInput').value;
            console.log('Parsing template:', templateText);
            
            // Extract variables in brackets [variable]
            const variables = templateText.match(/\\[([^\\]]+)\\]/g);
            if (!variables) {
                alert('No variables found in template. Use [variable] format.');
                return;
            }
            
            // Clean up variable names
            const cleanVariables = variables.map(v => v.replace(/[\\[\\]]/g, ''));
            console.log('Found variables:', cleanVariables);
            
            // Generate dropdowns
            generateDropdowns(cleanVariables);
        }

        function generateDropdowns(variables) {
            const container = document.getElementById('dropdownContainer');
            container.innerHTML = '';
            
            // Generate unique template ID
            currentTemplateId = 'template_' + Date.now();
            
            // Initialize template in LinkageManager
            linkageManager.initializeTemplate(currentTemplateId, variables.length);
            
            variables.forEach((variable, index) => {
                const tag = index + 1; // Use 1-based indexing for tags
                
                const dropdownWrapper = document.createElement('div');
                dropdownWrapper.className = 'dropdown-wrapper';
                dropdownWrapper.innerHTML = `
                    <label class="dropdown-label">${variable}</label>
                    <div class="custom-combo-box" id="combo-${tag}">
                        <input type="text" class="combo-input" placeholder="Select or add ${variable}..." readonly>
                        <span class="combo-arrow">▼</span>
                        <div class="combo-dropdown"></div>
                    </div>
                `;
                
                container.appendChild(dropdownWrapper);
                
                // Initialize CustomComboBox
                const comboElement = document.getElementById(`combo-${tag}`);
                const comboBox = new CustomComboBox(comboElement);
                
                // Add some default options
                const defaultOptions = getDefaultOptions(variable);
                defaultOptions.forEach(option => {
                    comboBox.addOption(option, option);
                });
                
                console.log(`CustomComboBox created for tag: ${tag}`);
            });
            
            console.log('Dropdowns generated for variables:', variables);
        }

        function getDefaultOptions(variable) {
            const optionsMap = {
                'role': ['Programmer', 'Chef', 'Soccer Coach', 'Teacher', 'Designer'],
                'what': ['Write code', 'Shop for food', 'Create tests', 'Prepare lunch', 'Plan dinner party'],
                'why': ['Build better software', 'Cook delicious meals', 'Improve code quality', 'Feed my family', 'Host friends'],
                'action': ['Write code', 'Create tests', 'Refactor', 'Shop for food', 'Prepare lunch'],
                'context': ['Web development', 'Mobile app', 'Backend API', 'Kitchen', 'Restaurant']
            };
            
            return optionsMap[variable] || [`Option 1 for ${variable}`, `Option 2 for ${variable}`];
        }

        function generateTemplate() {
            if (!currentTemplateId) {
                alert('Please parse template first to generate dropdowns.');
                return;
            }
            
            const templateText = document.getElementById('templateInput').value;
            const variables = templateText.match(/\\[([^\\]]+)\\]/g);
            
            if (!variables) {
                alert('No variables found in template.');
                return;
            }
            
            let generatedText = templateText;
            
            // Replace variables with current selections
            variables.forEach((variable, index) => {
                const tag = index + 1;
                const comboElement = document.getElementById(`combo-${tag}`);
                if (comboElement) {
                    const comboInput = comboElement.querySelector('.combo-input');
                    const selectedValue = comboInput.value || `[${variable.replace(/[\\[\\]]/g, '')}]`;
                    generatedText = generatedText.replace(variable, selectedValue);
                }
            });
            
            // Display generated prompt
            document.getElementById('promptContent').textContent = generatedText;
            document.getElementById('generatedPrompt').style.display = 'block';
        }

        function clearAll() {
            document.getElementById('templateInput').value = '';
            document.getElementById('dropdownContainer').innerHTML = '';
            document.getElementById('generatedPrompt').style.display = 'none';
            document.getElementById('saveStatus').innerHTML = '';
            document.getElementById('templateList').innerHTML = '';
            currentTemplateId = null;
            linkageManager = null;
            setupLinkages();
        }

        function saveTemplate() {
            const name = document.getElementById('templateName').value.trim();
            const description = document.getElementById('templateDescription').value.trim();
            const templateText = document.getElementById('templateInput').value.trim();
            
            if (!name || !description || !templateText) {
                showSaveStatus('Please fill in all fields.', 'error');
                return;
            }
            
            if (!currentTemplateId) {
                showSaveStatus('Please generate template first.', 'error');
                return;
            }
            
            console.log('=== SAVE TEMPLATE FUNCTION CALLED ===');
            console.log('Template text:', templateText);
            console.log('Template name:', name);
            console.log('Template description:', description);
            
            // Collect combo box values
            const comboBoxValues = {};
            const comboBoxes = document.querySelectorAll('.custom-combo-box');
            comboBoxes.forEach((combo, index) => {
                const tag = index + 1;
                const input = combo.querySelector('.combo-input');
                const dropdown = combo.querySelector('.combo-dropdown');
                const options = Array.from(dropdown.querySelectorAll('.combo-option')).map(opt => opt.textContent);
                
                comboBoxValues[tag] = {
                    value: input.value || '',
                    options: options
                };
            });
            
            console.log('Found', comboBoxes.length, 'combo boxes');
            Object.keys(comboBoxValues).forEach(tag => {
                console.log(`Combo box ${tag} values:`, comboBoxValues[tag].options);
            });
            
            // Collect linkage data
            const linkageData = {};
            Object.assign(linkageData, window.linkageManager.collectLinkageDataForStorage(currentTemplateId));
            
            console.log('Linkage data collected:', linkageData);
            
            const templateData = {
                name: name,
                description: description,
                template_text: templateText,
                combo_box_values: comboBoxValues,
                linkage_data: linkageData
            };
            
            fetch('/api/templates/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(templateData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showSaveStatus('Template saved successfully!', 'success');
                    document.getElementById('templateName').value = '';
                    document.getElementById('templateDescription').value = '';
                    loadTemplates(); // Refresh template list
                } else {
                    showSaveStatus('Error saving template: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showSaveStatus('Error saving template: ' + error.message, 'error');
            });
        }

        function showSaveStatus(message, type) {
            const statusDiv = document.getElementById('saveStatus');
            statusDiv.innerHTML = `<div class="status-message status-${type}">${message}</div>`;
        }

        function loadTemplates() {
            fetch('/api/templates/list')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayTemplates(data.templates);
                } else {
                    console.error('Error loading templates:', data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }

        function displayTemplates(templates) {
            const container = document.getElementById('templateList');
            
            if (!templates || templates.length === 0) {
                container.innerHTML = '<p style="color: #666; text-align: center; padding: 20px;">No saved templates found.</p>';
                return;
            }
            
            container.innerHTML = templates.map(template => `
                <div class="template-item" onclick="loadTemplate('${template.name}')">
                    <div class="template-name">${template.name}</div>
                    <div class="template-description">${template.description}</div>
                </div>
            `).join('');
        }

        function loadTemplate(templateName) {
            fetch(`/api/templates/load/${encodeURIComponent(templateName)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadSpecificTemplate(data.template);
                } else {
                    alert('Error loading template: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading template: ' + error.message);
            });
        }

        function loadSpecificTemplate(template) {
            console.log('Loading template:', template);
            
            // Set template text
            document.getElementById('templateInput').value = template.template_text || '';
            
            // Parse template to generate dropdowns
            parseTemplate();
            
            // Wait a moment for dropdowns to be created, then populate them
            setTimeout(() => {
                populateTemplateData(template);
            }, 100);
        }

        function populateTemplateData(template) {
            console.log('Populating template data:', template);
            
            // Restore combo box values
            if (template.combo_box_values) {
                Object.keys(template.combo_box_values).forEach(tag => {
                    const comboElement = document.getElementById(`combo-${tag}`);
                    if (comboElement) {
                        const comboData = template.combo_box_values[tag];
                        const input = comboElement.querySelector('.combo-input');
                        const dropdown = comboElement.querySelector('.combo-dropdown');
                        
                        // Clear existing options
                        dropdown.innerHTML = '';
                        
                        // Add options from saved data
                        if (comboData.options) {
                            comboData.options.forEach(option => {
                                const optionElement = document.createElement('div');
                                optionElement.className = 'combo-option';
                                optionElement.textContent = option;
                                optionElement.onclick = () => selectOption(comboElement, option);
                                dropdown.appendChild(optionElement);
                            });
                        }
                        
                        // Set selected value
                        if (comboData.value) {
                            input.value = comboData.value;
                        }
                    }
                });
            }
            
            // Restore linkage data
            if (template.linkage_data && window.linkageManager) {
                window.linkageManager.linkageData[currentTemplateId] = template.linkage_data;
                console.log('Linkage data restored for template:', currentTemplateId);
            }
            
            // Generate the final prompt
            generateTemplate();
        }

        function selectOption(comboElement, value) {
            const input = comboElement.querySelector('.combo-input');
            const dropdown = comboElement.querySelector('.combo-dropdown');
            
            input.value = value;
            dropdown.style.display = 'none';
        }
    </script>
</body>
</html>
"""

@linkage_bp.route('/template-builder')
def template_builder_page():
    """Template builder page with CustomComboBox integration."""
    return render_template_string(TEMPLATE_BUILDER_HTML)

@linkage_bp.route('/api/templates/save', methods=['POST'])
def save_template():
    """Save a template to persistent storage."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'description', 'template_text', 'combo_box_values', 'linkage_data']
        for field in required_fields:
            if field not in data:
                return json.dumps({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Get template service from app context
        template_service = TemplateService('templates/templates.json')
        
        # Save template
        template_service.save_template(
            name=data['name'],
            description=data['description'],
            template_text=data['template_text'],
            combo_box_values=data['combo_box_values'],
            linkage_data=data['linkage_data']
        )
        
        return json.dumps({
            "success": True,
            "message": "Template saved successfully"
        }), 200
        
    except ValueError as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500

@linkage_bp.route('/api/templates/load/<template_name>', methods=['GET'])
def load_template(template_name):
    """Load a template by name."""
    try:
        template_service = TemplateService('templates/templates.json')
        template = template_service.load_template(template_name)
        
        return json.dumps({
            "success": True,
            "template": template
        }), 200
        
    except ValueError as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }), 404
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500

@linkage_bp.route('/api/templates/list', methods=['GET'])
def list_templates():
    """List all saved templates."""
    try:
        template_service = TemplateService('templates/templates.json')
        templates = template_service.list_templates()
        
        return json.dumps({
            "success": True,
            "templates": templates
        }), 200
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500

@linkage_bp.route('/api/templates/delete/<template_name>', methods=['DELETE'])
def delete_template(template_name):
    """Delete a template by name."""
    try:
        template_service = TemplateService('templates/templates.json')
        
        if not template_service.template_exists(template_name):
            return json.dumps({
                "success": False,
                "error": "Template not found"
            }), 404
        
        template_service.delete_template(template_name)
        
        return json.dumps({
            "success": True,
            "message": "Template deleted successfully"
        }), 200
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500

@linkage_bp.route('/api/templates/exists/<template_name>', methods=['GET'])
def template_exists(template_name):
    """Check if a template exists."""
    try:
        template_service = TemplateService('templates/templates.json')
        exists = template_service.template_exists(template_name)
        
        return json.dumps({
            "success": True,
            "exists": exists
        }), 200
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }), 500

# Template Builder API Routes - Restored from Episode 5
@linkage_bp.route('/template/parse', methods=['POST'])
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
