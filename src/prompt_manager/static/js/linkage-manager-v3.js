/**
 * LinkageManager v3.0 - Enhanced with Template Integration
 * 
 * Core Rules:
 * 1. Linkages created when user adds entry to child combo box (presses Enter)
 * 2. Linkages displayed when parent dropdown closes (goes up)
 * 3. Hierarchical structure - only upstream linkages (parent → child)
 * 4. Empty lists show only "Add..." when no linkages exist
 * 5. Linkages persist with template data, survive page refresh
 * 
 * Data Structure:
 * - Template ID: GUID for each template
 * - Combo Box ID: Tag name (e.g., "Role", "Action")
 * - Linkage Format: {templateId: {parentTag: {parentValue: [childValues]}}}
 */

class LinkageManager {
    constructor() {
        this.linkageData = {}; // {templateId: {parentTag: {parentValue: [childValues]}}}
        this.currentSelections = {}; // {templateId: {tag: selectedValue}}
        this.comboBoxes = {}; // {templateId: {tag: CustomComboBox}}
        this.comboBoxTags = {}; // {templateId: [orderedTags]}
        this.currentTemplateId = null;
    }

    /**
     * Generate a GUID for template identification
     */
    generateTemplateId() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    /**
     * Initialize linkages for a template
     * @param {string} templateText - The template text
     * @param {Array} tags - Ordered array of combo box tags
     * @returns {string} - Template ID
     */
    initializeTemplate(templateText, tags) {
        const templateId = this.generateTemplateId();
        
        // Initialize data structures for this template
        this.linkageData[templateId] = {};
        this.currentSelections[templateId] = {};
        this.comboBoxes[templateId] = {};
        this.comboBoxTags[templateId] = tags;
        
        // Initialize current selections for all combo boxes
        tags.forEach(tag => {
            this.currentSelections[templateId][tag] = null;
        });
        
        this.currentTemplateId = templateId;
        return templateId;
    }

    /**
     * Register combo boxes for a template
     * @param {string} templateId - Template ID
     * @param {Object} comboBoxes - Object with tag as key, CustomComboBox as value
     */
    registerComboBoxes(templateId, comboBoxes) {
        this.comboBoxes[templateId] = comboBoxes;
        this.setupEventHandlers(templateId);
    }

    /**
     * Setup event handlers for all combo boxes in a template
     * @param {string} templateId - Template ID
     */
    setupEventHandlers(templateId) {
        console.log('=== LinkageManager v3.0: setupEventHandlers ===');
        console.log('templateId:', templateId);
        
        const tags = this.comboBoxTags[templateId];
        const comboBoxes = this.comboBoxes[templateId];
        console.log('tags:', tags);
        console.log('comboBoxes:', Object.keys(comboBoxes));
        
        // Setup parent-child linkages
        for (let i = 0; i < tags.length - 1; i++) {
            const parentTag = tags[i];
            const childTag = tags[i + 1];
            const parentCombo = comboBoxes[parentTag];
            const childCombo = comboBoxes[childTag];
            
            console.log(`Setting up linkage: ${parentTag} -> ${childTag}`);
            console.log('parentCombo exists:', !!parentCombo);
            console.log('childCombo exists:', !!childCombo);
            
            if (parentCombo && childCombo) {
                // Setup parent selection change handler
                parentCombo.onSelectionChange = (selectedValue) => {
                    console.log(`Parent ${parentTag} selection changed to: ${selectedValue}`);
                    this.handleParentSelectionChange(templateId, parentTag, childTag, selectedValue);
                };
                
                // Setup child option added handler
                childCombo.onOptionAdded = (newOptionValue) => {
                    console.log(`Child ${childTag} option added: ${newOptionValue}`);
                    this.handleChildOptionAdded(templateId, parentTag, childTag, newOptionValue);
                };
                
                console.log('Event handlers set up successfully');
            } else {
                console.log('Missing combo boxes for linkage setup');
            }
        }
    }

    /**
     * Handle parent selection change - restore or clear child linkages
     * @param {string} templateId - Template ID
     * @param {string} parentTag - Parent combo box tag
     * @param {string} childTag - Child combo box tag
     * @param {string} selectedValue - Selected value
     */
    handleParentSelectionChange(templateId, parentTag, childTag, selectedValue) {
        console.log('=== LinkageManager v3.0: handleParentSelectionChange ===');
        console.log('templateId:', templateId);
        console.log('parentTag:', parentTag);
        console.log('childTag:', childTag);
        console.log('selectedValue:', selectedValue);
        
        // Update current selection
        this.currentSelections[templateId][parentTag] = selectedValue;
        console.log('Updated current selection for', parentTag, ':', selectedValue);
        
        // Clear all subsequent combo boxes (children, grandchildren, etc.)
        this.clearSubsequentComboBoxes(templateId, parentTag);
        
        // Restore linkages for the child if they exist
        console.log('Checking for linkage data:', templateId, selectedValue, childTag);
        console.log('hasLinkageData result:', this.hasLinkageData(templateId, selectedValue, childTag));
        
        if (this.hasLinkageData(templateId, selectedValue, childTag)) {
            console.log('Restoring child linkages for:', selectedValue, '->', childTag);
            this.restoreChildLinkages(templateId, selectedValue, childTag);
        } else {
            console.log('No linkage data found for:', selectedValue, '->', childTag);
        }
        
        // Save to template storage
        this.saveToTemplateStorage(templateId);
    }

    /**
     * Handle child option added - create linkage if parent has selection
     * @param {string} templateId - Template ID
     * @param {string} parentTag - Parent combo box tag
     * @param {string} childTag - Child combo box tag
     * @param {string} newOptionValue - New option value
     */
    handleChildOptionAdded(templateId, parentTag, childTag, newOptionValue) {
        console.log('=== LinkageManager v3.0: handleChildOptionAdded ===');
        console.log('templateId:', templateId);
        console.log('parentTag:', parentTag);
        console.log('childTag:', childTag);
        console.log('newOptionValue:', newOptionValue);
        
        const parentSelection = this.currentSelections[templateId][parentTag];
        console.log('parentSelection:', parentSelection);
        console.log('isValidSelection:', this.isValidSelection(parentSelection));
        
        if (parentSelection && this.isValidSelection(parentSelection)) {
            console.log('Creating linkage:', parentSelection, '->', childTag, ':', newOptionValue);
            this.createLinkage(templateId, parentTag, parentSelection, childTag, newOptionValue);
            this.saveToTemplateStorage(templateId);
            console.log('Linkage created and saved');
        } else {
            console.log('No valid parent selection, skipping linkage creation');
        }
    }

    /**
     * Clear all combo boxes that come after the specified parent
     * @param {string} templateId - Template ID
     * @param {string} parentTag - Parent tag
     */
    clearSubsequentComboBoxes(templateId, parentTag) {
        const tags = this.comboBoxTags[templateId];
        const comboBoxes = this.comboBoxes[templateId];
        const parentIndex = tags.indexOf(parentTag);
        
        if (parentIndex === -1) return;
        
        // Clear all subsequent combo boxes
        for (let i = parentIndex + 1; i < tags.length; i++) {
            const tag = tags[i];
            const combo = comboBoxes[tag];
            
            if (combo) {
                // Clear options (keep first option)
                this.clearComboBoxOptions(combo);
                
                // Clear selection
                combo.selectedIndex = -1;
                combo.selectedOption = null;
                combo.input.value = '';
                
                // Clear current selection
                this.currentSelections[templateId][tag] = null;
            }
        }
    }

    /**
     * Clear combo box options (keep first option)
     * @param {CustomComboBox} comboBox - Combo box to clear
     */
    clearComboBoxOptions(comboBox) {
        const options = comboBox.dropdown.querySelectorAll('.combo-box-option');
        
        for (let i = options.length - 1; i > 0; i--) {
            options[i].remove();
        }
        
        // Update the options array
        comboBox.options = Array.from(comboBox.dropdown.querySelectorAll('.combo-box-option'));
    }

    /**
     * Restore child linkages for a specific parent selection
     * @param {string} templateId - Template ID
     * @param {string} parentValue - Parent value
     * @param {string} childTag - Child tag
     */
    restoreChildLinkages(templateId, parentValue, childTag) {
        console.log('=== LinkageManager v3.0: restoreChildLinkages ===');
        console.log('templateId:', templateId);
        console.log('parentValue:', parentValue);
        console.log('childTag:', childTag);
        
        const comboBoxes = this.comboBoxes[templateId];
        const childCombo = comboBoxes[childTag];
        
        console.log('childCombo exists:', !!childCombo);
        
        if (!childCombo) return;
        
        const linkedOptions = this.getLinkedOptions(templateId, parentValue, childTag);
        console.log('linkedOptions:', linkedOptions);
        
        if (linkedOptions.length === 0) {
            console.log('No linked options found');
            return;
        }
        
        // Add linked options to child combo box
        linkedOptions.forEach(option => {
            console.log('Adding option to child combo:', option);
            childCombo.addOption(option, true, false); // Skip callback, don't auto-select
        });
        
        console.log('Options added successfully');
        
        // Recursively restore linkages for the child's children
        const childSelection = this.currentSelections[templateId][childTag];
        if (childSelection && this.isValidSelection(childSelection)) {
            const tags = this.comboBoxTags[templateId];
            const childIndex = tags.indexOf(childTag);
            const nextChildTag = childIndex < tags.length - 1 ? tags[childIndex + 1] : null;
            
            if (nextChildTag && this.hasLinkageData(templateId, childSelection, nextChildTag)) {
                this.restoreChildLinkages(templateId, childSelection, nextChildTag);
            }
        }
    }

    /**
     * Create a linkage between parent and child
     * @param {string} templateId - Template ID
     * @param {string} parentTag - Parent tag
     * @param {string} parentValue - Parent value
     * @param {string} childTag - Child tag
     * @param {string} optionValue - Option value
     */
    createLinkage(templateId, parentTag, parentValue, childTag, optionValue) {
        console.log('=== LinkageManager v3.0: createLinkage ===');
        console.log('templateId:', templateId);
        console.log('parentTag:', parentTag);
        console.log('parentValue:', parentValue);
        console.log('childTag:', childTag);
        console.log('optionValue:', optionValue);
        console.log('Before createLinkage - linkageData:', this.linkageData);
        
        if (!this.linkageData[templateId]) {
            this.linkageData[templateId] = {};
            console.log('Created templateId entry');
        }
        if (!this.linkageData[templateId][parentValue]) {
            this.linkageData[templateId][parentValue] = {};
            console.log('Created parentValue entry');
        }
        if (!this.linkageData[templateId][parentValue][childTag]) {
            this.linkageData[templateId][parentValue][childTag] = [];
            console.log('Created childTag array');
        }
        
        // Add option if not already present
        if (!this.linkageData[templateId][parentValue][childTag].includes(optionValue)) {
            this.linkageData[templateId][parentValue][childTag].push(optionValue);
            console.log('Added option to array');
        } else {
            console.log('Option already exists in array');
        }
        
        console.log('After createLinkage - linkageData:', this.linkageData);
        console.log('Final structure:', this.linkageData[templateId][parentValue][childTag]);
    }

    /**
     * Check if linkage data exists for parent-child pair
     * @param {string} templateId - Template ID
     * @param {string} parentValue - Parent value
     * @param {string} childTag - Child tag
     * @returns {boolean}
     */
    hasLinkageData(templateId, parentValue, childTag) {
        console.log('=== LinkageManager v3.0: hasLinkageData ===');
        console.log('templateId:', templateId);
        console.log('parentValue:', parentValue);
        console.log('childTag:', childTag);
        console.log('this.linkageData:', this.linkageData);
        console.log('this.linkageData[templateId]:', this.linkageData[templateId]);
        console.log('this.linkageData[templateId][parentValue]:', this.linkageData[templateId] ? this.linkageData[templateId][parentValue] : 'N/A');
        console.log('this.linkageData[templateId][parentValue][childTag]:', this.linkageData[templateId] && this.linkageData[templateId][parentValue] ? this.linkageData[templateId][parentValue][childTag] : 'N/A');
        
        const result = this.linkageData[templateId] && 
               this.linkageData[templateId][parentValue] &&
               this.linkageData[templateId][parentValue][childTag] && 
               this.linkageData[templateId][parentValue][childTag].length > 0;
        
        console.log('hasLinkageData result:', result);
        return result;
    }

    /**
     * Get linked options for parent-child pair
     * @param {string} templateId - Template ID
     * @param {string} parentValue - Parent value
     * @param {string} childTag - Child tag
     * @returns {Array}
     */
    getLinkedOptions(templateId, parentValue, childTag) {
        console.log('=== LinkageManager v3.0: getLinkedOptions ===');
        console.log('templateId:', templateId);
        console.log('parentValue:', parentValue);
        console.log('childTag:', childTag);
        console.log('linkageData structure:', this.linkageData);
        
        if (this.hasLinkageData(templateId, parentValue, childTag)) {
            const options = this.linkageData[templateId][parentValue][childTag];
            console.log('Found linked options:', options);
            return options;
        }
        console.log('No linkage data found');
        return [];
    }

    /**
     * Check if a selection value is valid (not placeholder text)
     * @param {string} value - Value to check
     * @returns {boolean}
     */
    isValidSelection(value) {
        return value && 
               value !== 'Add item...' && 
               value !== 'Select item...' && 
               value !== 'Add...';
    }

    /**
     * Save linkage data to template storage
     * @param {string} templateId - Template ID
     */
    saveToTemplateStorage(templateId) {
        // This will be integrated with the template storage system
        // For now, save to localStorage with template ID
        const templateData = {
            linkageData: this.linkageData[templateId] || {},
            currentSelections: this.currentSelections[templateId] || {}
        };
        
        localStorage.setItem(`linkageData_${templateId}`, JSON.stringify(templateData));
    }

    /**
     * Load linkage data from template storage
     * @param {string} templateId - Template ID
     */
    loadFromTemplateStorage(templateId) {
        try {
            const storedData = localStorage.getItem(`linkageData_${templateId}`);
            
            if (storedData) {
                const templateData = JSON.parse(storedData);
                this.linkageData[templateId] = templateData.linkageData || {};
                this.currentSelections[templateId] = templateData.currentSelections || {};
            }
        } catch (error) {
            console.error('Error loading linkage data from storage:', error);
            this.linkageData[templateId] = {};
            this.currentSelections[templateId] = {};
        }
    }

    /**
     * Get linkage data for template storage integration
     * @param {string} templateId - Template ID
     * @returns {Object}
     */
    getTemplateLinkageData(templateId) {
        return {
            linkageData: this.linkageData[templateId] || {},
            currentSelections: this.currentSelections[templateId] || {}
        };
    }

    /**
     * Set linkage data from template storage
     * @param {string} templateId - Template ID
     * @param {Object} data - Linkage data
     */
    setTemplateLinkageData(templateId, data) {
        this.linkageData[templateId] = data.linkageData || {};
        this.currentSelections[templateId] = data.currentSelections || {};
    }

    /**
     * Clear all linkage data for a template
     * @param {string} templateId - Template ID
     */
    clearTemplateData(templateId) {
        delete this.linkageData[templateId];
        delete this.currentSelections[templateId];
        delete this.comboBoxes[templateId];
        delete this.comboBoxTags[templateId];
        
        localStorage.removeItem(`linkageData_${templateId}`);
    }

    /**
     * Get debug information for a template
     * @param {string} templateId - Template ID
     * @returns {Object}
     */
    getDebugInfo(templateId) {
        return {
            templateId: templateId,
            linkageData: this.linkageData[templateId] || {},
            currentSelections: this.currentSelections[templateId] || {},
            comboBoxTags: this.comboBoxTags[templateId] || [],
            comboBoxCount: Object.keys(this.comboBoxes[templateId] || {}).length
        };
    }
}

// Make it globally available
window.LinkageManager = LinkageManager;
