/**
 * Template Storage Manager
 * Handles JSON local storage for template data and hierarchical linkages
 */

class TemplateStorage {
    constructor() {
        this.storageKey = 'prompt_manager_templates';
    }
    
    /**
     * Save template data to local storage
     * @param {string} templateId - Unique identifier for the template
     * @param {Object} templateData - Template data including combo box options and linkages
     */
    saveTemplate(templateId, templateData) {
        const templates = this.getAllTemplates();
        templates[templateId] = {
            ...templateData,
            lastModified: new Date().toISOString()
        };
        localStorage.setItem(this.storageKey, JSON.stringify(templates));
    }
    
    /**
     * Load template data from local storage
     * @param {string} templateId - Unique identifier for the template
     * @returns {Object|null} Template data or null if not found
     */
    loadTemplate(templateId) {
        const templates = this.getAllTemplates();
        return templates[templateId] || null;
    }
    
    /**
     * Get all templates from local storage
     * @returns {Object} All templates
     */
    getAllTemplates() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : {};
        } catch (error) {
            console.error('Error loading templates from storage:', error);
            return {};
        }
    }
    
    /**
     * Delete template from local storage
     * @param {string} templateId - Unique identifier for the template
     */
    deleteTemplate(templateId) {
        const templates = this.getAllTemplates();
        delete templates[templateId];
        localStorage.setItem(this.storageKey, JSON.stringify(templates));
    }
    
    /**
     * Generate unique template ID from template text
     * @param {string} templateText - The template text
     * @returns {string} Unique template ID
     */
    generateTemplateId(templateText) {
        // Simple hash function for template ID
        let hash = 0;
        for (let i = 0; i < templateText.length; i++) {
            const char = templateText.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return 'template_' + Math.abs(hash).toString(36);
    }
}

/**
 * Template Data Structure
 * 
 * Example JSON structure:
 * {
 *   "template_abc123": {
 *     "templateText": "As a [Role], I want to [What], so that I can [Why]",
 *     "comboBoxes": [
 *       {
 *         "tag": "Role",
 *         "index": 0,
 *         "options": ["Developer", "Designer", "Manager"],
 *         "linkages": {
 *           "Developer": ["Fix bugs", "Write tests", "Deploy code"],
 *           "Designer": ["Create mockups", "User research", "Prototype"],
 *           "Manager": ["Plan sprints", "Review work", "Team meetings"]
 *         }
 *       },
 *       {
 *         "tag": "What",
 *         "index": 1,
 *         "options": ["Fix bugs", "Write tests", "Deploy code"],
 *         "linkages": {
 *           "Fix bugs": ["Save time", "Improve quality", "Reduce errors"],
 *           "Write tests": ["Prevent regressions", "Document behavior", "Enable refactoring"],
 *           "Deploy code": ["Deliver features", "Update production", "Rollback if needed"]
 *         }
 *       },
 *       {
 *         "tag": "Why",
 *         "index": 2,
 *         "options": ["Save time", "Improve quality", "Reduce errors"],
 *         "linkages": {}
 *       }
 *     ],
 *     "lastModified": "2025-09-14T14:30:00.000Z"
 *   }
 * }
 */

class TemplateDataManager {
    constructor() {
        this.storage = new TemplateStorage();
        this.currentTemplateId = null;
        this.currentData = null;
    }
    
    /**
     * Initialize template data from template text
     * @param {string} templateText - The template text with tags
     * @returns {Object} Template data structure
     */
    initializeTemplate(templateText) {
        const tags = this.extractTags(templateText);
        const templateId = this.storage.generateTemplateId(templateText);
        
        const templateData = {
            templateText: templateText,
            comboBoxes: tags.map((tag, index) => ({
                tag: tag,
                index: index,
                options: [],
                linkages: {}
            })),
            lastModified: new Date().toISOString()
        };
        
        this.currentTemplateId = templateId;
        this.currentData = templateData;
        return templateData;
    }
    
    /**
     * Extract tags from template text
     * @param {string} templateText - Template text with [Tag] format
     * @returns {Array} Array of tag names
     */
    extractTags(templateText) {
        const tagRegex = /\[([^\]]+)\]/g;
        const tags = [];
        let match;
        
        while ((match = tagRegex.exec(templateText)) !== null) {
            const tag = match[1].trim();
            if (!tags.includes(tag)) {
                tags.push(tag);
            }
        }
        
        return tags;
    }
    
    /**
     * Update combo box options
     * @param {number} comboBoxIndex - Index of the combo box
     * @param {Array} options - New options array
     */
    updateComboBoxOptions(comboBoxIndex, options) {
        if (!this.currentData || !this.currentData.comboBoxes[comboBoxIndex]) {
            return;
        }
        
        this.currentData.comboBoxes[comboBoxIndex].options = [...options];
        this.currentData.lastModified = new Date().toISOString();
    }
    
    /**
     * Update linkages for a combo box
     * @param {number} comboBoxIndex - Index of the combo box
     * @param {string} sourceOption - The option that triggers the linkage
     * @param {Array} linkedOptions - Options for the next combo box
     */
    updateLinkages(comboBoxIndex, sourceOption, linkedOptions) {
        if (!this.currentData || !this.currentData.comboBoxes[comboBoxIndex]) {
            return;
        }
        
        const comboBox = this.currentData.comboBoxes[comboBoxIndex];
        comboBox.linkages[sourceOption] = [...linkedOptions];
        this.currentData.lastModified = new Date().toISOString();
    }
    
    /**
     * Get linked options for a combo box
     * @param {number} comboBoxIndex - Index of the combo box
     * @param {string} sourceOption - The option that triggers the linkage
     * @returns {Array} Linked options or empty array
     */
    getLinkedOptions(comboBoxIndex, sourceOption) {
        if (!this.currentData || !this.currentData.comboBoxes[comboBoxIndex]) {
            return [];
        }
        
        const comboBox = this.currentData.comboBoxes[comboBoxIndex];
        return comboBox.linkages[sourceOption] || [];
    }
    
    /**
     * Save current template data
     */
    saveCurrentTemplate() {
        if (this.currentTemplateId && this.currentData) {
            this.storage.saveTemplate(this.currentTemplateId, this.currentData);
        }
    }
    
    /**
     * Load template data
     * @param {string} templateId - Template ID to load
     */
    loadTemplate(templateId) {
        const templateData = this.storage.loadTemplate(templateId);
        if (templateData) {
            this.currentTemplateId = templateId;
            this.currentData = templateData;
        }
        return templateData;
    }
    
    /**
     * Get current template data
     * @returns {Object|null} Current template data
     */
    getCurrentTemplate() {
        return this.currentData;
    }
    
    /**
     * Get current template ID
     * @returns {string|null} Current template ID
     */
    getCurrentTemplateId() {
        return this.currentTemplateId;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TemplateStorage, TemplateDataManager };
}

