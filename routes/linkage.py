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
                <div class="alert alert-info mb-0">
                    <strong>Custom Combo Box Version:</strong> <span id="combo-box-version">Loading...</span>
                </div>
                <div>
                <button id="saveTemplateBtn" class="btn btn-outline-light me-2">
                    <i class="fas fa-save me-1"></i>Save Template
                </button>
                <button id="saveAsTemplateBtn" class="btn btn-outline-light me-2">
                    <i class="fas fa-save me-1"></i>Save As...
                </button>
                <button id="loadTemplateBtn" class="btn btn-outline-light me-2">
                    <i class="fas fa-folder-open me-1"></i>Load Template
                </button>
                    <button id="testModeBtn" class="btn btn-outline-light me-2">
                        <i class="fas fa-vial me-1"></i>Test Mode
                    </button>
                    <button id="editModeBtn" class="btn btn-outline-light me-2">
                        <i class="fas fa-edit me-1"></i>Edit Mode
                    </button>
                    <a href="/dashboard" class="btn btn-outline-light">
                        <i class="fas fa-arrow-left me-1"></i>Back to Dashboard
                    </a>
                </div>
            </div>
        </div>

        <!-- Test Panel (Hidden by default) -->
        <div id="testPanel" class="bg-warning text-dark p-3" style="display: none;">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <h5 class="mb-3"><i class="fas fa-vial me-2"></i>Test Panel</h5>
                        <div class="d-flex gap-2 flex-wrap">
                            <button id="addSampleDataBtn" class="btn btn-sm btn-outline-dark">
                                <i class="fas fa-plus me-1"></i>Add Sample Data
                            </button>
                            <button id="resetComboBoxesBtn" class="btn btn-sm btn-outline-dark">
                                <i class="fas fa-undo me-1"></i>Reset
                            </button>
                            <button id="runTestsBtn" class="btn btn-sm btn-outline-dark">
                                <i class="fas fa-play me-1"></i>Run Tests
                            </button>
                            <button id="testLinkagesBtn" class="btn btn-sm btn-outline-dark">
                                <i class="fas fa-link me-1"></i>Test Linkages
                            </button>
                        </div>
                        <div id="testResults" class="mt-3" style="display: none;">
                            <h6>Test Results:</h6>
                            <div id="testOutput" class="bg-light p-2 rounded"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Top Panel - Dropdowns Area -->
        <div class="top-panel">
            <div class="container-fluid">
                <div class="row">
                    <div class="col-12">
                        <h4 class="mb-3"><i class="fas fa-list me-2"></i>Template Variables</h4>
                        <div id="combo-boxes-container">
                            <div class="text-center text-muted py-5">
                                <i class="fas fa-arrow-down fa-2x mb-3"></i>
                                <p>Enter a template below and click "Generate" to create combo boxes</p>
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

    <!-- Include Custom Combo Box Component -->
    <link rel="stylesheet" href="/static/css/custom-combo-box.css">
    <script src="/static/js/custom-combo-box-working.js?v=2.5&t=1734567910&cache=bust"></script>
    <script src="/static/js/template-storage.js"></script>
        <script src="/static/js/linkage-manager-v3.js?v=3.1&t=1734567908&cache=bust"></script>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Display version information
        document.getElementById('combo-box-version').textContent = 'ComboBox v2.5 | LinkageManager v3.1';
        
        // Template Builder State - Old Layout with CustomComboBox
        let currentTemplate = "";
        let customComboBoxes = [];
        window.customComboBoxes = customComboBoxes;  // Make globally accessible
        let isEditMode = false;
        let templateManager = new TemplateDataManager();
        
        // Dynamic Linkage Data Structure
        window.linkageData = {};  // Will be populated dynamically as user creates linkages
        
        // Track current selections for linkage creation
        window.currentSelections = {};  // Maps combo box tag to currently selected value

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            setupEventListeners();
        });
        
        // Debug function to test template loading manually
        window.debugLoadTemplate = function(templateName) {
            console.log('=== MANUAL DEBUG LOAD ===');
            console.log('Loading template:', templateName);
            
            fetch(`/api/templates/load/${encodeURIComponent(templateName)}`)
            .then(response => response.json())
            .then(data => {
                console.log('API Response:', data);
                if (data.success) {
                    const template = data.template;
                    console.log('Template data:', template);
                    
                    // Test combo box generation
                    document.getElementById('templateInput').value = template.template_text;
                    generateCustomComboBoxes();
                    
                    setTimeout(() => {
                        console.log('=== AFTER COMBO BOX GENERATION ===');
                        console.log('customComboBoxes:', window.customComboBoxes);
                        console.log('customComboBoxes length:', window.customComboBoxes ? window.customComboBoxes.length : 'undefined');
                        
                        if (window.customComboBoxes) {
                            window.customComboBoxes.forEach((combo, index) => {
                                console.log(`Combo ${index}:`, combo);
                                console.log(`Combo ${index} tag:`, combo.tag);
                                console.log(`Combo ${index} options:`, combo.options);
                                console.log(`Combo ${index} dropdown HTML:`, combo.dropdown.innerHTML);
                            });
                        }
                        
                        // Now test the actual loading logic
                        console.log('=== TESTING LOADING LOGIC ===');
                        console.log('template.combo_box_values:', template.combo_box_values);
                        
                        if (window.customComboBoxes && template.combo_box_values) {
                            window.customComboBoxes.forEach(combo => {
                                console.log('Processing combo box for tag:', combo.tag);
                                if (combo.tag && template.combo_box_values[combo.tag]) {
                                    const values = template.combo_box_values[combo.tag];
                                    console.log('Values for', combo.tag, ':', values);
                                    
                                    // Simply add saved options to existing combo box
                                    values.forEach(value => {
                                        console.log('Adding value:', value);
                                        // Check if option already exists to avoid duplicates
                                        const existingOption = combo.dropdown.querySelector(`[data-value="${value}"]`);
                                        if (!existingOption) {
                                            console.log('Option does not exist, adding:', value);
                                            combo.addOption(value, false, false); // Add without selecting, skip callback
                                        } else {
                                            console.log('Option already exists:', value);
                                        }
                                    });
                                } else {
                                    console.log('No values found for tag:', combo.tag);
                                }
                            });
                        } else {
                            console.log('Missing customComboBoxes or combo_box_values');
                        }
                    }, 1000);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        };

        // Global variable to track current template name
        let currentTemplateName = null;
        
        function setupEventListeners() {
            // Template persistence
            document.getElementById('saveTemplateBtn').addEventListener('click', saveTemplate);
            document.getElementById('saveAsTemplateBtn').addEventListener('click', saveAsTemplate);
            document.getElementById('loadTemplateBtn').addEventListener('click', loadTemplate);
            
            // Edit mode toggle
            document.getElementById('editModeBtn').addEventListener('click', toggleEditMode);
            
            // Test mode toggle
            document.getElementById('testModeBtn').addEventListener('click', toggleTestMode);
            
            // Generate combo boxes
            document.getElementById('generateBtn').addEventListener('click', generateCustomComboBoxes);
            
            // Test panel buttons
            document.getElementById('addSampleDataBtn').addEventListener('click', addSampleData);
            document.getElementById('resetComboBoxesBtn').addEventListener('click', resetComboBoxes);
            document.getElementById('runTestsBtn').addEventListener('click', runBasicTests);
            document.getElementById('testLinkagesBtn').addEventListener('click', testLinkages);
        }

        function toggleEditMode() {
            isEditMode = !isEditMode;
            updateEditModeButton();
            
            // Update all custom combo boxes to new mode
            customComboBoxes.forEach(comboBox => {
                comboBox.setMode(isEditMode ? 'edit' : 'display');
            });
        }

        function updateEditModeButton() {
            const button = document.getElementById('editModeBtn');
            if (isEditMode) {
                button.innerHTML = '<i class="fas fa-check me-1"></i>Edit Mode Active';
                button.classList.remove('btn-outline-light');
                button.classList.add('btn-warning');
                document.getElementById('combo-boxes-container').classList.add('edit-mode-active');
            } else {
                button.innerHTML = '<i class="fas fa-edit me-1"></i>Edit Mode';
                button.classList.remove('btn-warning');
                button.classList.add('btn-outline-light');
                document.getElementById('combo-boxes-container').classList.remove('edit-mode-active');
            }
        }

        function generateCustomComboBoxes() {
            const template = document.getElementById('templateInput').value.trim();
            
            if (!template) {
                alert('Please enter a template');
                return;
            }
            
            try {
                // Initialize template data
                const templateData = templateManager.initializeTemplate(template);
                const tags = templateManager.extractTags(template);
                
                // Clear existing combo boxes
                customComboBoxes = [];
                window.customComboBoxes = customComboBoxes;  // Update global reference
                
                // Create custom combo boxes
                const container = document.getElementById('combo-boxes-container');
                container.innerHTML = '';
                
                tags.forEach((tag, index) => {
                    // Create combo box container
                    const comboBoxContainer = document.createElement('div');
                    comboBoxContainer.className = 'mb-4';
                    comboBoxContainer.innerHTML = `
                        <div class="dropdown-label mb-2">${tag.charAt(0).toUpperCase() + tag.slice(1)}</div>
                        <div id="combo-box-${tag}" class="combo-box-container">
                            <input type="text" class="combo-box-input" placeholder="Type to add...">
                            <div class="combo-box-arrow"></div>
                            <div class="combo-box-dropdown">
                                <div class="combo-box-option" data-value="Select item...">Select item...</div>
                            </div>
                        </div>
                    `;
                    
                    container.appendChild(comboBoxContainer);
                    
                    // Create CustomComboBox instance (after HTML is in DOM)
                    console.log('Creating CustomComboBox for tag:', tag);
                    const comboBox = new CustomComboBox(`combo-box-${tag}`);
                    console.log('CustomComboBox created:', comboBox);
                    
                    // Set the tag name for this combo box
                    comboBox.tag = tag;
                    
                    // Set the initial mode
                    comboBox.setMode(isEditMode ? 'edit' : 'display');
                    
                    customComboBoxes.push(comboBox);
                });
                
                // Set up linkages between combo boxes using working August 20th implementation
                console.log('About to call setupLinkages()');
                setupLinkages();
                console.log('setupLinkages() completed');
                
            } catch (error) {
                console.error('Error in generateCustomComboBoxes:', error);
                alert('Error: ' + error.message);
                return;
            }
        }

        // Global LinkageManager instance
        let linkageManager = null;
        let currentTemplateId = null;

        function setupLinkages() {
            console.log('=== SETTING UP LINKAGES (LinkageManager v3.0) ===');
            console.log('Number of combo boxes:', customComboBoxes.length);
            
            // Get template text and tags
            const templateText = document.getElementById('templateInput').value;
            const tags = customComboBoxes.map(combo => combo.tag);
            
            // Initialize LinkageManager
            linkageManager = new LinkageManager();
            window.linkageManager = linkageManager; // Make it globally accessible
            currentTemplateId = linkageManager.initializeTemplate(templateText, tags);
            console.log('Initialized template with ID:', currentTemplateId);
            
            // Create combo boxes object with tag as key
            const comboBoxesByTag = {};
            customComboBoxes.forEach(combo => {
                comboBoxesByTag[combo.tag] = combo;
            });
            
            // Register combo boxes with LinkageManager
            linkageManager.registerComboBoxes(currentTemplateId, comboBoxesByTag);
            
            // Load existing linkage data if available
            linkageManager.loadFromTemplateStorage(currentTemplateId);
            
            console.log('LinkageManager setup completed');
        }

        // Test Panel Functions
        function toggleTestMode() {
            const testPanel = document.getElementById('testPanel');
            const testModeBtn = document.getElementById('testModeBtn');
            
            if (testPanel.style.display === 'none') {
                testPanel.style.display = 'block';
                testModeBtn.innerHTML = '<i class="fas fa-vial me-1"></i>Test Mode: ON';
                testModeBtn.classList.remove('btn-outline-light');
                testModeBtn.classList.add('btn-warning');
            } else {
                testPanel.style.display = 'none';
                testModeBtn.innerHTML = '<i class="fas fa-vial me-1"></i>Test Mode';
                testModeBtn.classList.remove('btn-warning');
                testModeBtn.classList.add('btn-outline-light');
            }
        }

        function addSampleData() {
            if (customComboBoxes.length === 0) {
                alert('Please generate combo boxes first');
                return;
            }
            
            // Add sample data to each combo box
            const sampleData = {
                'Role': ['Developer', 'Designer', 'Manager', 'Tester'],
                'What': ['Fix bugs', 'Add features', 'Improve performance', 'Refactor code'],
                'Why': ['Save time', 'Improve quality', 'Reduce errors', 'Enhance user experience'],
                '1': ['Option 1A', 'Option 1B', 'Option 1C'],
                '2': ['Option 2A', 'Option 2B', 'Option 2C'],
                '3': ['Option 3A', 'Option 3B', 'Option 3C']
            };
            
            customComboBoxes.forEach(comboBox => {
                const tag = comboBox.tag;
                const options = sampleData[tag] || ['Sample Option 1', 'Sample Option 2', 'Sample Option 3'];
                options.forEach(option => {
                    comboBox.addOption(option);
                });
            });
            
            showTestResult('Sample data added to all combo boxes');
        }

        function resetComboBoxes() {
            customComboBoxes.forEach(comboBox => {
                // Clear all options except the first one (Add item... or Select item...)
                const options = comboBox.dropdown.querySelectorAll('.combo-box-option');
                for (let i = options.length - 1; i > 0; i--) {
                    options[i].remove();
                }
                comboBox.selectedIndex = -1;
                comboBox.selectedOption = null;
                comboBox.input.value = '';
            });
            
            showTestResult('All combo boxes reset');
        }

        function runBasicTests() {
            const results = [];
            
            // Test 1: Check if combo boxes exist
            if (customComboBoxes.length > 0) {
                results.push('✓ Combo boxes created successfully');
            } else {
                results.push('✗ No combo boxes found');
            }
            
            // Test 2: Check Edit/Display mode switching
            const originalMode = isEditMode;
            toggleEditMode();
            const newMode = isEditMode;
            toggleEditMode(); // Switch back
            
            if (originalMode !== newMode) {
                results.push('✓ Edit/Display mode switching works');
            } else {
                results.push('✗ Edit/Display mode switching failed');
            }
            
            // Test 3: Check if combo boxes have required elements
            let allHaveElements = true;
            customComboBoxes.forEach(comboBox => {
                if (!comboBox.input || !comboBox.dropdown || !comboBox.arrow) {
                    allHaveElements = false;
                }
            });
            
            if (allHaveElements) {
                results.push('✓ All combo boxes have required elements');
            } else {
                results.push('✗ Some combo boxes missing required elements');
            }
            
            showTestResult(results.join('<br>'));
        }

        function testLinkages() {
            const results = [];
            
            // Test 1: Check if we have at least 2 combo boxes for linkage testing
            if (customComboBoxes.length < 2) {
                results.push('✗ Need at least 2 combo boxes for linkage testing');
                showTestResult(results.join('<br>'));
                return;
            }
            
            // Test 2: Verify LinkageManager exists
            if (!linkageManager) {
                results.push('✗ LinkageManager not found');
                results.push('🔧 Need to initialize LinkageManager');
            } else {
                results.push('✓ LinkageManager exists');
            }
            
            // Test 3: Verify template ID exists
            if (!currentTemplateId) {
                results.push('✗ Template ID not found');
                results.push('🔧 Need to initialize template');
            } else {
                results.push(`✓ Template ID: ${currentTemplateId}`);
            }
            
            // Test 4: Check if combo boxes have linkage setup
            let linkageSetupCount = 0;
            customComboBoxes.forEach((comboBox, index) => {
                if (comboBox.onSelectionChange && typeof comboBox.onSelectionChange === 'function') {
                    linkageSetupCount++;
                }
            });
            
            if (linkageSetupCount > 0) {
                results.push(`✓ ${linkageSetupCount} combo boxes have linkage setup`);
            } else {
                results.push('✗ No combo boxes have linkage setup');
                results.push('🔧 Need to implement onSelectionChange handlers');
            }
            
            // Test 5: Get debug info from LinkageManager
            if (linkageManager && currentTemplateId) {
                const debugInfo = linkageManager.getDebugInfo(currentTemplateId);
                results.push(`✓ Debug Info: ${JSON.stringify(debugInfo, null, 2)}`);
            }
            
            // Test 6: Test actual linkage behavior
            try {
                const firstComboBox = customComboBoxes[0];
                const secondComboBox = customComboBoxes[1];
                
                // Simulate selecting an item in the first combo box
                const testSelection = 'Developer';
                firstComboBox.selectOption(1); // Select first real option (index 1, after "Add item...")
                
                // Check if second combo box options changed
                const secondOptions = secondComboBox.dropdown.querySelectorAll('.combo-box-option');
                const secondOptionTexts = Array.from(secondOptions).map(option => option.textContent);
                
                if (secondOptionTexts.length > 1) {
                    results.push('✓ Second combo box has options');
                    results.push(`📋 Second combo box options: ${secondOptionTexts.slice(1).join(', ')}`);
                } else {
                    results.push('✗ Second combo box has no options after selection');
                    results.push('🔧 Linkage not working - options should update based on selection');
                }
                
            } catch (error) {
                results.push(`✗ Error testing linkage: ${error.message}`);
            }
            
            showTestResult(results.join('<br>'));
        }

        function showTestResult(message) {
            const testResults = document.getElementById('testResults');
            const testOutput = document.getElementById('testOutput');
            testOutput.innerHTML = message;
            testResults.style.display = 'block';
        }

        // Save Prompt Button
        document.getElementById('savePromptBtn').addEventListener('click', function() {
            const finalPrompt = document.getElementById('finalPromptText').textContent;
            if (!finalPrompt) {
                alert('No prompt to save');
                return;
            }
            
            // Create a name for the prompt
            const promptName = `Template: ${Object.keys(customComboBoxes.map(cb => cb.tag)).join(' → ')}`;
            
            // Save to prompts
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
        
        // Template Persistence Functions
        function saveAsTemplate() {
            saveTemplate(true); // true = force new name
        }
        
        function saveTemplate(forceNewName = false) {
            console.log('=== SAVE TEMPLATE FUNCTION CALLED ===');
            
            const templateText = document.getElementById('templateInput').value.trim();
            console.log('Template text:', templateText);
            
            if (!templateText) {
                alert('Please enter a template text first');
                return;
            }
            
            let templateName = currentTemplateName;
            let templateDescription = '';
            
            // If no current template name or forcing new name, prompt for name
            if (!templateName || forceNewName) {
                templateName = prompt('Enter a name for this template:');
                if (!templateName) return;
                
                templateDescription = prompt('Enter a description for this template (optional):') || '';
            }
            
            console.log('Template name:', templateName);
            console.log('Template description:', templateDescription);
            
            // Collect combo box values and linkage data
            const comboBoxValues = {};
            const linkageData = {};
            
            // Get current combo box values
            if (window.customComboBoxes) {
                console.log('Found', window.customComboBoxes.length, 'combo boxes');
                window.customComboBoxes.forEach(combo => {
                    if (combo.tag) {
                        const values = combo.options.slice(1).map(option => option.dataset.value);
                        comboBoxValues[combo.tag] = values;
                        console.log('Combo box', combo.tag, 'values:', values);
                    }
                });
            } else {
                console.log('No custom combo boxes found');
            }
            
            // Get linkage data if available
            if (window.linkageManager) {
                const templateId = window.linkageManager.getCurrentTemplateId();
                if (templateId) {
                    Object.assign(linkageData, window.linkageManager.collectLinkageDataForStorage(templateId));
                    console.log('Linkage data:', linkageData);
                }
            } else {
                console.log('No linkage manager found');
            }
            
            // Save template
            const templateData = {
                name: templateName,
                description: templateDescription,
                template_text: templateText,
                combo_box_values: comboBoxValues,
                linkage_data: linkageData
            };
            
            console.log('Sending template data:', templateData);
            
            fetch('/api/templates/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(templateData)
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                if (data.success) {
                    // Update current template name
                    currentTemplateName = templateName;
                    alert('Template saved successfully!');
                } else {
                    alert('Error saving template: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                alert('Error saving template: ' + error);
            });
        }
        
        function loadTemplate() {
            // First, get list of available templates
            fetch('/api/templates/list')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const templates = data.templates;
                    const templateNames = Object.keys(templates);
                    
                    if (templateNames.length === 0) {
                        alert('No saved templates found');
                        return;
                    }
                    
                    // Build template list HTML
                    let templateListHtml = '';
                    templateNames.forEach(name => {
                        const template = templates[name];
                        const description = template.description || 'No description';
                        const createdDate = template.created_at ? new Date(template.created_at).toLocaleDateString() : 'Unknown';
                        templateListHtml += `
                            <div class="template-item" data-template-name="${name}" style="padding: 10px; border: 1px solid #ddd; margin: 5px 0; cursor: pointer; border-radius: 4px; transition: background-color 0.2s;">
                                <h6 style="margin: 0; color: #007bff;">${name}</h6>
                                <small style="color: #666;">${description}</small><br>
                                <small style="color: #999;">Created: ${createdDate}</small>
                            </div>
                        `;
                    });
                    
                    // Show modal with template list
                    const modalHtml = `
                        <div class="modal fade" id="loadTemplateModal" tabindex="-1" aria-labelledby="loadTemplateModalLabel" aria-hidden="true">
                            <div class="modal-dialog">
                                <div class="modal-content">
                                    <div class="modal-header">
                                        <h5 class="modal-title" id="loadTemplateModalLabel">Load Template</h5>
                                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                    </div>
                                    <div class="modal-body">
                                        <p>Select a template to load:</p>
                                        <div id="templateList">
                                            ${templateListHtml}
                                        </div>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    // Remove existing modal if any
                    const existingModal = document.getElementById('loadTemplateModal');
                    if (existingModal) {
                        existingModal.remove();
                    }
                    
                    // Add modal to page
                    document.body.insertAdjacentHTML('beforeend', modalHtml);
                    
                    // Add click handlers to template items
                    document.querySelectorAll('.template-item').forEach(item => {
                        item.addEventListener('click', function() {
                            const templateName = this.getAttribute('data-template-name');
                            loadSpecificTemplate(templateName);
                            // Close modal
                            const modal = bootstrap.Modal.getInstance(document.getElementById('loadTemplateModal'));
                            if (modal) {
                                modal.hide();
                            }
                        });
                        
                        // Add hover effects
                        item.addEventListener('mouseenter', function() {
                            this.style.backgroundColor = '#f8f9fa';
                        });
                        item.addEventListener('mouseleave', function() {
                            this.style.backgroundColor = '';
                        });
                    });
                    
                    // Show modal
                    const modal = new bootstrap.Modal(document.getElementById('loadTemplateModal'));
                    modal.show();
                } else {
                    alert('Error loading templates: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error loading templates: ' + error);
            });
        }
        
        function loadSpecificTemplate(templateName) {
            fetch(`/api/templates/load/${encodeURIComponent(templateName)}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const template = data.template;
                    
                    // Load template text
                    document.getElementById('templateInput').value = template.template_text;
                    
                    // Generate combo boxes
                    generateCustomComboBoxes();
                    
                    // Wait for combo boxes to be created, then load values
                    setTimeout(() => {
                        console.log('=== LOADING TEMPLATE VALUES ===');
                        console.log('customComboBoxes:', window.customComboBoxes);
                        console.log('template.combo_box_values:', template.combo_box_values);
                        
                        // Load combo box values
                        if (window.customComboBoxes && template.combo_box_values) {
                            console.log('=== LOADING COMBO BOX VALUES ===');
                            console.log('customComboBoxes:', window.customComboBoxes);
                            console.log('template.combo_box_values:', template.combo_box_values);
                            
                            window.customComboBoxes.forEach((combo, index) => {
                                console.log(`=== Processing combo ${index} ===`);
                                console.log('combo.tag:', combo.tag);
                                console.log('template.combo_box_values[combo.tag]:', template.combo_box_values[combo.tag]);
                                
                                if (combo.tag && template.combo_box_values[combo.tag]) {
                                    const values = template.combo_box_values[combo.tag];
                                    console.log('Values for', combo.tag, ':', values);
                                    console.log('Values length:', values.length);
                                    
                                    // Simply add saved options to existing combo box
                                    values.forEach((value, valueIndex) => {
                                        console.log(`Adding value ${valueIndex}:`, value);
                                        // Check if option already exists to avoid duplicates
                                        const existingOption = combo.dropdown.querySelector(`[data-value="${value}"]`);
                                        if (!existingOption) {
                                            console.log('Option does not exist, adding:', value);
                                            try {
                                                combo.addOption(value, true, false); // Add without selecting, skip callback to prevent linkage interference
                                                console.log('Successfully added option:', value);
                                                console.log('Dropdown HTML after adding:', combo.dropdown.innerHTML);
                                                console.log('Options array length:', combo.options.length);
                                                console.log('Dropdown visible:', combo.dropdown.style.display);
                                                console.log('Dropdown class list:', combo.dropdown.classList.toString());
                                            } catch (error) {
                                                console.error('Error adding option:', value, error);
                                            }
                                        } else {
                                            console.log('Option already exists:', value);
                                        }
                                    });
                                } else {
                                    console.log('No values found for tag:', combo.tag);
                                }
                            });
                        } else {
                            console.log('Missing customComboBoxes or combo_box_values');
                        }
                        
                        // Load linkage data if available
                        if (window.linkageManager && template.linkage_data) {
                            console.log('=== LOADING LINKAGE DATA ===');
                            console.log('template.linkage_data:', template.linkage_data);
                            
                            // Get the current template ID from LinkageManager
                            const templateId = window.linkageManager.getCurrentTemplateId();
                            if (templateId) {
                                console.log('Restoring linkage data for template ID:', templateId);
                                
                                // Restore linkage data to LinkageManager
                                window.linkageManager.linkageData[templateId] = template.linkage_data;
                                
                                console.log('Linkage data restored:', window.linkageManager.linkageData[templateId]);
                            } else {
                                console.log('No current template ID found');
                            }
                        } else {
                            console.log('No linkage data to restore or LinkageManager not available');
                        }
                        
        // Final summary of all combo boxes
        console.log('=== FINAL COMBO BOX SUMMARY ===');
        window.customComboBoxes.forEach((combo, index) => {
            console.log(`Combo ${index} (${combo.tag}):`);
            console.log(`  - Options count: ${combo.options.length}`);
            console.log(`  - Dropdown HTML: ${combo.dropdown.innerHTML}`);
            console.log(`  - Dropdown visible: ${combo.dropdown.style.display}`);
            console.log(`  - Options array:`, combo.options.map(opt => opt.dataset.value));
        });
        
        // Add a test function to manually check dropdown contents
        window.testDropdown = function(tag) {
            const combo = window.customComboBoxes.find(c => c.tag === tag);
            if (combo) {
                console.log(`=== TESTING DROPDOWN FOR ${tag} ===`);
                console.log('Options array length:', combo.options.length);
                console.log('Options array:', combo.options.map(opt => opt.dataset.value));
                console.log('DOM query result:', Array.from(combo.dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.dataset.value));
                console.log('Dropdown HTML:', combo.dropdown.innerHTML);
            } else {
                console.log('Combo box not found for tag:', tag);
            }
        };
        
        // Add a function to force refresh options array
        window.refreshOptions = function(tag) {
            const combo = window.customComboBoxes.find(c => c.tag === tag);
            if (combo) {
                console.log(`=== REFRESHING OPTIONS FOR ${tag} ===`);
                console.log('Before refresh:', combo.options.map(opt => opt.dataset.value));
                combo.options = Array.from(combo.dropdown.querySelectorAll('.combo-box-option'));
                console.log('After refresh:', combo.options.map(opt => opt.dataset.value));
            }
        };
                        
                        // Note: Linkage data is restored in the main loading section above
                        
                        // Update current template name
                        currentTemplateName = templateName;
                        
                        alert('Template loaded successfully!');
                    }, 500);
                } else {
                    alert('Error loading template: ' + data.error);
                }
            })
            .catch(error => {
                alert('Error loading template: ' + error);
            });
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

# Additional Template Builder API Routes - Episode 5 Complete Integration
@linkage_bp.route('/template/parse', methods=['POST'])
def parse_template():
    """Parse template text and extract bracketed variables."""
    try:
        data = request.get_json()
        template_text = data.get('template', '')
        import re
        variables = re.findall(r'\[([^\]]+)\]', template_text)
        return json.dumps({'variables': variables, 'template': template_text}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/template/generate-dropdowns', methods=['POST'])
def generate_dropdowns():
    """Generate dropdown options for detected variables."""
    try:
        data = request.get_json()
        template_text = data.get('template', '')
        import re
        variables = re.findall(r'\[([^\]]+)\]', template_text)
        default_options = {
            'role': ['Programmer', 'Chef', 'Soccer Coach', 'Teacher', 'Designer'],
            'what': ['Write code', 'Shop for food', 'Create tests', 'Prepare lunch', 'Plan dinner party', 'Refactor'],
            'why': ['Build better software', 'Cook delicious meals', 'Improve code quality', 'Feed my family', 'Host friends'],
            'action': ['Write code', 'Create tests', 'Refactor', 'Shop for food', 'Prepare lunch'],
            'context': ['Web development', 'Mobile app', 'Backend API', 'Kitchen', 'Restaurant']
        }
        dropdowns = {}
        for var in variables:
            dropdowns[var] = {'options': default_options.get(var, [f'Option 1 for {var}', f'Option 2 for {var}'])}
        return json.dumps({'dropdowns': dropdowns, 'template': template_text}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/template/update-options', methods=['POST'])
def update_options():
    """Update dropdown options based on context."""
    try:
        data = request.get_json()
        variable = data.get('variable', '')
        context = data.get('context', {})
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
        if variable in context_options:
            for context_key, options in context_options[variable].items():
                if context_key in context.values():
                    return json.dumps({'options': options}), 200, {'Content-Type': 'application/json'}
        default_options = {'what': ['Write code', 'Shop for food', 'Create tests', 'Prepare lunch'], 'why': ['Build better software', 'Cook delicious meals', 'Improve quality', 'Feed my family']}
        return json.dumps({'options': default_options.get(variable, [f'Option for {variable}'])}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/template/generate-final', methods=['POST'])
def generate_template_final_prompt():
    """Generate final prompt by replacing variables with user selections."""
    try:
        data = request.get_json()
        template_text = data.get('template', '')
        selections = data.get('selections', {})
        final_prompt = template_text
        for variable, value in selections.items():
            final_prompt = final_prompt.replace(f'[{variable}]', value)
        return json.dumps({'final_prompt': final_prompt, 'template': template_text, 'selections': selections}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/template/edit-mode', methods=['POST'])
def toggle_edit_mode():
    """Toggle edit mode for the template builder."""
    try:
        data = request.get_json()
        enabled = data.get('enabled', False)
        return json.dumps({'edit_mode': enabled}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/template/generate', methods=['POST'])
def generate_template():
    """Main generate endpoint that processes template and returns dropdowns."""
    from flask import current_app
    try:
        data = request.get_json()
        template_text = data.get('template', '')
        edit_mode = data.get('edit_mode', False)
        import re
        variables = re.findall(r'\[([^\]]+)\]', template_text)
        
        if edit_mode:
            custom_combo_integration = current_app.config['CUSTOM_COMBO_INTEGRATION']
            custom_result = custom_combo_integration.create_template_with_custom_combo_boxes(template_text)
            dropdowns = {}
            for combo_box in custom_result["combo_boxes"]:
                tag = combo_box["tag"]
                dropdowns[tag] = {
                    "options": combo_box["options"] if combo_box["options"] else [f"Option 1 for {tag}", f"Option 2 for {tag}"],
                    "enabled": combo_box["enabled"],
                    "value": combo_box["value"],
                    "is_custom": True
                }
        else:
            default_options = {
                'role': ['Programmer', 'Chef', 'Soccer Coach', 'Teacher', 'Designer'],
                'what': ['Write code', 'Shop for food', 'Create tests', 'Prepare lunch', 'Plan dinner party', 'Refactor'],
                'why': ['Build better software', 'Cook delicious meals', 'Improve code quality', 'Feed my family', 'Host friends'],
                'action': ['Write code', 'Create tests', 'Refactor', 'Shop for food', 'Prepare lunch'],
                'context': ['Web development', 'Mobile app', 'Backend API', 'Kitchen', 'Restaurant']
            }
            dropdowns = {}
            for var in variables:
                dropdowns[var] = {'options': default_options.get(var.lower(), [f'Option 1 for {var}', f'Option 2 for {var}'])}
        
        return json.dumps({'dropdowns': dropdowns, 'template': template_text, 'edit_mode': edit_mode}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/api/custom-combo-box/create-template', methods=['POST'])
def create_template_with_custom_combo_boxes():
    """Create a template with custom combo boxes."""
    from flask import current_app
    try:
        data = request.get_json()
        if not data or 'template' not in data:
            return json.dumps({'error': 'Template is required'}), 400, {'Content-Type': 'application/json'}
        template = data['template']
        custom_combo_integration = current_app.config['CUSTOM_COMBO_INTEGRATION']
        result = custom_combo_integration.create_template_with_custom_combo_boxes(template)
        return json.dumps(result), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/api/custom-combo-box/handle-change', methods=['POST'])
def handle_custom_combo_box_change():
    """Handle a combo box change and update cascading state."""
    from flask import current_app
    try:
        data = request.get_json()
        if not data or 'combo_box_id' not in data or 'new_value' not in data or 'combo_boxes' not in data:
            return json.dumps({'error': 'combo_box_id, new_value, and combo_boxes are required'}), 400, {'Content-Type': 'application/json'}
        combo_box_id = data['combo_box_id']
        new_value = data['new_value']
        combo_boxes = data['combo_boxes']
        custom_combo_integration = current_app.config['CUSTOM_COMBO_INTEGRATION']
        updated_combo_boxes = custom_combo_integration.handle_combo_box_change(combo_box_id, new_value, combo_boxes)
        return json.dumps({'combo_boxes': updated_combo_boxes}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/api/custom-combo-box/generate-prompt', methods=['POST'])
def generate_custom_combo_box_prompt():
    """Generate final prompt from template and combo box selections."""
    from flask import current_app
    try:
        data = request.get_json()
        if not data or 'template' not in data or 'combo_boxes' not in data:
            return json.dumps({'error': 'template and combo_boxes are required'}), 400, {'Content-Type': 'application/json'}
        template = data['template']
        combo_boxes = data['combo_boxes']
        custom_combo_integration = current_app.config['CUSTOM_COMBO_INTEGRATION']
        final_prompt = custom_combo_integration.generate_final_prompt(template, combo_boxes)
        return json.dumps({'final_prompt': final_prompt}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/api/custom-combo-box/validate-template', methods=['POST'])
def validate_custom_combo_box_template():
    """Validate a template."""
    from flask import current_app
    try:
        data = request.get_json()
        if not data or 'template' not in data:
            return json.dumps({'error': 'template is required'}), 400, {'Content-Type': 'application/json'}
        template = data['template']
        custom_combo_integration = current_app.config['CUSTOM_COMBO_INTEGRATION']
        validation = custom_combo_integration.validate_template(template)
        return json.dumps(validation), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/api/custom-combo-box/available-templates', methods=['GET'])
def get_available_templates():
    """Get list of available templates."""
    from flask import current_app
    try:
        custom_combo_integration = current_app.config['CUSTOM_COMBO_INTEGRATION']
        templates = custom_combo_integration.get_available_templates()
        return json.dumps({'templates': templates}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/api/custom-combo-box/export-config', methods=['POST'])
def export_template_config():
    """Export template configuration."""
    from flask import current_app
    try:
        data = request.get_json()
        if not data or 'template' not in data or 'combo_boxes' not in data:
            return json.dumps({'error': 'template and combo_boxes are required'}), 400, {'Content-Type': 'application/json'}
        template = data['template']
        combo_boxes = data['combo_boxes']
        custom_combo_integration = current_app.config['CUSTOM_COMBO_INTEGRATION']
        config = custom_combo_integration.export_template_config(template, combo_boxes)
        return json.dumps(config), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/api/custom-combo-box/import-config', methods=['POST'])
def import_template_config():
    """Import template configuration."""
    from flask import current_app
    try:
        data = request.get_json()
        if not data:
            return json.dumps({'error': 'config data is required'}), 400, {'Content-Type': 'application/json'}
        custom_combo_integration = current_app.config['CUSTOM_COMBO_INTEGRATION']
        result = custom_combo_integration.import_template_config(data)
        return json.dumps(result), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        return json.dumps({'error': str(e)}), 500, {'Content-Type': 'application/json'}

@linkage_bp.route('/custom-combo-box-builder')
def custom_combo_box_builder():
    """Serve the custom combo box builder interface."""
    with open('src/prompt_manager/templates/custom_combo_box_builder.html', 'r') as f:
        return f.read()
