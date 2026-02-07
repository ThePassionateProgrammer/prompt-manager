/**
 * Clean Linkage Manager - Fresh Implementation
 * 
 * Core Rules:
 * 1. Linkages created on "Add..." only when parent has a selection
 * 2. Linkages are permanent - once created, never changed
 * 3. Clicking parent items restores associated child linkages
 * 4. Cascading behavior - children depend on their immediate parent
 * 5. Linkages persist in localStorage
 */

class LinkageManagerV2 {
    constructor() {
        this.linkageData = {}; // {parent_value: {child_tag: [options]}}
        this.currentSelections = {}; // {tag: selected_value}
        this.comboBoxes = []; // Array of CustomComboBox instances
        this.comboBoxTags = []; // Ordered list of combo box tags
        
        this.loadFromStorage();
    }

    /**
     * Register combo boxes and their tags
     */
    registerComboBoxes(comboBoxes, tags) {
        this.comboBoxes = comboBoxes;
        this.comboBoxTags = tags;
        
        // Initialize current selections for all combo boxes
        tags.forEach(tag => {
            if (!(tag in this.currentSelections)) {
                this.currentSelections[tag] = null;
            }
        });
        
        this.setupEventHandlers();
    }

    /**
     * Setup event handlers for all combo boxes
     */
    setupEventHandlers() {
        // Setup parent-child linkages
        for (let i = 0; i < this.comboBoxes.length - 1; i++) {
            const parentCombo = this.comboBoxes[i];
            const childCombo = this.comboBoxes[i + 1];
            const parentTag = this.comboBoxTags[i];
            const childTag = this.comboBoxTags[i + 1];
            
            // Setup parent selection change handler
            parentCombo.onSelectionChange = (selectedValue) => {
                this.handleParentSelectionChange(parentTag, childTag, selectedValue);
            };
            
            // Setup child option added handler
            childCombo.onOptionAdded = (newOptionValue) => {
                this.handleChildOptionAdded(parentTag, childTag, newOptionValue);
            };
        }
    }

    /**
     * Handle parent selection change - restore or clear child linkages
     */
    handleParentSelectionChange(parentTag, childTag, selectedValue) {
        console.log(`LinkageManagerV2: Parent '${parentTag}' selected '${selectedValue}'`);
        console.log(`LinkageManagerV2: Callback triggered for ${parentTag} -> ${childTag}`);
        
        // Update current selection
        this.currentSelections[parentTag] = selectedValue;
        
        // Clear all subsequent combo boxes (children, grandchildren, etc.)
        this.clearSubsequentComboBoxes(parentTag);
        
        // Restore linkages for the child if they exist
        if (this.hasLinkageData(selectedValue, childTag)) {
            this.restoreChildLinkages(selectedValue, childTag);
        }
        
        this.saveToStorage();
    }

    /**
     * Handle child option added - create linkage if parent has selection
     */
    handleChildOptionAdded(parentTag, childTag, newOptionValue) {
        const parentSelection = this.currentSelections[parentTag];
        
        if (parentSelection && this.isValidSelection(parentSelection)) {
            console.log(`LinkageManagerV2: Creating linkage ${parentSelection} -> ${childTag}: ${newOptionValue}`);
            this.createLinkage(parentSelection, childTag, newOptionValue);
            this.saveToStorage();
        } else {
            console.log(`LinkageManagerV2: No parent selection, skipping linkage creation`);
        }
    }

    /**
     * Clear all combo boxes that come after the specified parent
     */
    clearSubsequentComboBoxes(parentTag) {
        const parentIndex = this.comboBoxTags.indexOf(parentTag);
        if (parentIndex === -1) return;
        
        // Clear all subsequent combo boxes
        for (let i = parentIndex + 1; i < this.comboBoxes.length; i++) {
            const combo = this.comboBoxes[i];
            const tag = this.comboBoxTags[i];
            
            // Clear options (keep first option)
            this.clearComboBoxOptions(combo);
            
            // Clear selection
            combo.selectedIndex = -1;
            combo.selectedOption = null;
            combo.input.value = '';
            
            // Clear current selection
            this.currentSelections[tag] = null;
            
            console.log(`LinkageManagerV2: Cleared combo box '${tag}'`);
        }
    }

    /**
     * Clear combo box options (keep first option)
     */
    clearComboBoxOptions(comboBox) {
        console.log('LinkageManagerV2: Clearing combo box options');
        const options = comboBox.dropdown.querySelectorAll('.combo-box-option');
        console.log(`LinkageManagerV2: Found ${options.length} options to clear`);
        
        for (let i = options.length - 1; i > 0; i--) {
            console.log(`LinkageManagerV2: Removing option ${i}: ${options[i].textContent}`);
            options[i].remove();
        }
        
        // Update the options array
        comboBox.options = Array.from(comboBox.dropdown.querySelectorAll('.combo-box-option'));
        console.log(`LinkageManagerV2: After clearing, ${comboBox.options.length} options remain`);
    }

    /**
     * Restore child linkages for a specific parent selection
     */
    restoreChildLinkages(parentValue, childTag) {
        const childCombo = this.getComboBoxByTag(childTag);
        if (!childCombo) return;
        
        const linkedOptions = this.getLinkedOptions(parentValue, childTag);
        if (linkedOptions.length === 0) return;
        
        console.log(`LinkageManagerV2: Restoring ${linkedOptions.length} options for ${childTag}`);
        
        // Add linked options to child combo box
        linkedOptions.forEach(option => {
            childCombo.addOption(option, true, false); // Skip callback, don't auto-select
        });
        
        // Recursively restore linkages for the child's children
        // Find the child's current selection and restore its linkages
        const childSelection = this.currentSelections[childTag];
        if (childSelection && this.isValidSelection(childSelection)) {
            const nextChildTag = this.getNextComboBoxTag(childTag);
            if (nextChildTag && this.hasLinkageData(childSelection, nextChildTag)) {
                this.restoreChildLinkages(childSelection, nextChildTag);
            }
        }
    }

    /**
     * Create a linkage between parent and child
     */
    createLinkage(parentValue, childTag, optionValue) {
        if (!this.linkageData[parentValue]) {
            this.linkageData[parentValue] = {};
        }
        if (!this.linkageData[parentValue][childTag]) {
            this.linkageData[parentValue][childTag] = [];
        }
        
        // Add option if not already present
        if (!this.linkageData[parentValue][childTag].includes(optionValue)) {
            this.linkageData[parentValue][childTag].push(optionValue);
        }
    }

    /**
     * Check if linkage data exists for parent-child pair
     */
    hasLinkageData(parentValue, childTag) {
        return this.linkageData[parentValue] && 
               this.linkageData[parentValue][childTag] && 
               this.linkageData[parentValue][childTag].length > 0;
    }

    /**
     * Get linked options for parent-child pair
     */
    getLinkedOptions(parentValue, childTag) {
        if (this.hasLinkageData(parentValue, childTag)) {
            return this.linkageData[parentValue][childTag];
        }
        return [];
    }

    /**
     * Get combo box by tag
     */
    getComboBoxByTag(tag) {
        const index = this.comboBoxTags.indexOf(tag);
        return index !== -1 ? this.comboBoxes[index] : null;
    }

    /**
     * Get next combo box tag after the specified tag
     */
    getNextComboBoxTag(currentTag) {
        const index = this.comboBoxTags.indexOf(currentTag);
        return index !== -1 && index < this.comboBoxTags.length - 1 
            ? this.comboBoxTags[index + 1] 
            : null;
    }

    /**
     * Check if a selection value is valid (not placeholder text)
     */
    isValidSelection(value) {
        return value && 
               value !== 'Add item...' && 
               value !== 'Select item...' && 
               value !== 'Add...';
    }

    /**
     * Save linkage data to localStorage
     */
    saveToStorage() {
        localStorage.setItem('linkageDataV2', JSON.stringify(this.linkageData));
        localStorage.setItem('currentSelectionsV2', JSON.stringify(this.currentSelections));
    }

    /**
     * Load linkage data from localStorage
     */
    loadFromStorage() {
        try {
            const storedLinkageData = localStorage.getItem('linkageDataV2');
            const storedCurrentSelections = localStorage.getItem('currentSelectionsV2');
            
            if (storedLinkageData) {
                this.linkageData = JSON.parse(storedLinkageData);
            }
            if (storedCurrentSelections) {
                this.currentSelections = JSON.parse(storedCurrentSelections);
            }
        } catch (error) {
            console.error('Error loading linkage data from storage:', error);
            this.linkageData = {};
            this.currentSelections = {};
        }
    }

    /**
     * Clear all linkage data
     */
    clearAllData() {
        this.linkageData = {};
        this.currentSelections = {};
        localStorage.removeItem('linkageDataV2');
        localStorage.removeItem('currentSelectionsV2');
        
        // Clear all combo boxes
        this.comboBoxes.forEach(combo => {
            this.clearComboBoxOptions(combo);
            combo.selectedIndex = -1;
            combo.selectedOption = null;
            combo.input.value = '';
        });
    }

    /**
     * Get debug information
     */
    getDebugInfo() {
        return {
            linkageData: this.linkageData,
            currentSelections: this.currentSelections,
            comboBoxTags: this.comboBoxTags,
            comboBoxCount: this.comboBoxes.length
        };
    }
}

// Make it globally available
window.LinkageManagerV2 = LinkageManagerV2;
