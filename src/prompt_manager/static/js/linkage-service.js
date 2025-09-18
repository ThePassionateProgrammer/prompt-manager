/**
 * Linkage Service - Clean JavaScript interface for managing combo box linkages.
 * 
 * This service provides a clean, testable interface for managing the complex
 * linkage logic between combo boxes, separating concerns from DOM manipulation.
 */

class LinkageService {
    constructor() {
        this.linkageData = {};
        this.currentSelections = {};
        this.comboBoxes = [];
    }

    /**
     * Register combo boxes with the linkage service.
     * @param {Array} comboBoxes - Array of CustomComboBox instances
     */
    registerComboBoxes(comboBoxes) {
        this.comboBoxes = comboBoxes;
        this.setupLinkages();
    }

    /**
     * Set up linkages between combo boxes.
     * This method creates the parent-child relationships and event handlers.
     */
    setupLinkages() {
        for (let i = 0; i < this.comboBoxes.length - 1; i++) {
            const parentComboBox = this.comboBoxes[i];
            const childComboBox = this.comboBoxes[i + 1];
            
            this.setupParentChildLinkage(parentComboBox, childComboBox);
        }
    }

    /**
     * Set up linkage between a parent and child combo box.
     * @param {CustomComboBox} parentCombo - Parent combo box
     * @param {CustomComboBox} childCombo - Child combo box
     */
    setupParentChildLinkage(parentCombo, childCombo) {
        // Set up selection change handler for parent
        parentCombo.onSelectionChange = (selectedValue) => {
            this.handleParentSelectionChange(parentCombo.tag, childCombo.tag, selectedValue);
        };

        // Set up option creation handler for child
        childCombo.onOptionAdded = (newOption) => {
            this.handleChildOptionAdded(parentCombo.tag, childCombo.tag, newOption);
        };
    }

    /**
     * Handle parent selection change.
     * @param {string} parentTag - Tag of the parent combo box
     * @param {string} childTag - Tag of the child combo box
     * @param {string} selectedValue - Selected value in parent
     */
    handleParentSelectionChange(parentTag, childTag, selectedValue) {
        if (!this.isValidSelection(selectedValue)) {
            return;
        }

        // Track current selection
        this.currentSelections[parentTag] = selectedValue;

        // Clear and restore child combo box
        this.clearChildComboBox(childTag);
        this.restoreChildLinkages(parentTag, childTag);

        // Clear subsequent combo boxes
        this.clearSubsequentComboBoxes(parentTag);

        // Trigger cascading restoration
        this.triggerCascadingRestoration(parentTag, childTag);
    }

    /**
     * Handle child option addition.
     * @param {string} parentTag - Tag of the parent combo box
     * @param {string} childTag - Tag of the child combo box
     * @param {string} newOption - New option added to child
     */
    handleChildOptionAdded(parentTag, childTag, newOption) {
        if (this.currentSelections[parentTag]) {
            this.createLinkage(parentTag, childTag, newOption);
        }
    }

    /**
     * Create a linkage between parent and child.
     * @param {string} parentTag - Tag of the parent combo box
     * @param {string} childTag - Tag of the child combo box
     * @param {string} option - Option to link
     */
    createLinkage(parentTag, childTag, option) {
        if (!this.linkageData[parentTag]) {
            this.linkageData[parentTag] = {};
        }
        if (!this.linkageData[parentTag][childTag]) {
            this.linkageData[parentTag][childTag] = [];
        }
        
        if (!this.linkageData[parentTag][childTag].includes(option)) {
            this.linkageData[parentTag][childTag].push(option);
        }
    }

    /**
     * Clear child combo box options (keep first option).
     * @param {string} childTag - Tag of the child combo box
     */
    clearChildComboBox(childTag) {
        const childCombo = this.getComboBoxByTag(childTag);
        if (!childCombo) return;

        const childOptions = childCombo.dropdown.querySelectorAll('.combo-box-option');
        for (let j = childOptions.length - 1; j > 0; j--) {
            childOptions[j].remove();
        }

        // Clear selection and input
        childCombo.selectedIndex = -1;
        childCombo.selectedOption = null;
        childCombo.input.value = '';
    }

    /**
     * Restore linkages for a child combo box.
     * @param {string} parentTag - Tag of the parent combo box
     * @param {string} childTag - Tag of the child combo box
     */
    restoreChildLinkages(parentTag, childTag) {
        const childCombo = this.getComboBoxByTag(childTag);
        if (!childCombo) return;

        if (this.linkageData[parentTag] && this.linkageData[parentTag][childTag]) {
            const linkedOptions = this.linkageData[parentTag][childTag];
            linkedOptions.forEach(option => {
                childCombo.addOption(option, true, true); // Skip callback, select option
            });
        }
    }

    /**
     * Clear subsequent combo boxes.
     * @param {string} parentTag - Tag of the parent combo box
     */
    clearSubsequentComboBoxes(parentTag) {
        const parentIndex = this.getComboBoxIndex(parentTag);
        if (parentIndex === -1) return;

        for (let k = parentIndex + 2; k < this.comboBoxes.length; k++) {
            const subsequentComboBox = this.comboBoxes[k];
            const subsequentOptions = subsequentComboBox.dropdown.querySelectorAll('.combo-box-option');
            for (let l = subsequentOptions.length - 1; l > 0; l--) {
                subsequentOptions[l].remove();
            }
            subsequentComboBox.selectedIndex = -1;
            subsequentComboBox.selectedOption = null;
            subsequentComboBox.input.value = '';
        }
    }

    /**
     * Trigger cascading restoration for child's children.
     * @param {string} parentTag - Tag of the parent combo box
     * @param {string} childTag - Tag of the child combo box
     */
    triggerCascadingRestoration(parentTag, childTag) {
        const childCombo = this.getComboBoxByTag(childTag);
        if (!childCombo || !childCombo.selectedOption) return;

        if (this.linkageData[parentTag] && this.linkageData[parentTag][childTag]) {
            this.currentSelections[childTag] = childCombo.selectedOption;
            if (childCombo.onSelectionChange) {
                childCombo.onSelectionChange(childCombo.selectedOption);
            }
        }
    }

    /**
     * Get combo box by tag.
     * @param {string} tag - Tag of the combo box
     * @returns {CustomComboBox|null} The combo box or null if not found
     */
    getComboBoxByTag(tag) {
        return this.comboBoxes.find(combo => combo.tag === tag) || null;
    }

    /**
     * Get combo box index by tag.
     * @param {string} tag - Tag of the combo box
     * @returns {number} Index of the combo box or -1 if not found
     */
    getComboBoxIndex(tag) {
        return this.comboBoxes.findIndex(combo => combo.tag === tag);
    }

    /**
     * Check if a selection is valid for linkage processing.
     * @param {string} selectedValue - The selected value
     * @returns {boolean} True if valid, false otherwise
     */
    isValidSelection(selectedValue) {
        return selectedValue && 
               selectedValue !== 'Add item...' && 
               selectedValue !== 'Select item...';
    }

    /**
     * Get linkage data for debugging or persistence.
     * @returns {Object} Current linkage data
     */
    getLinkageData() {
        return JSON.parse(JSON.stringify(this.linkageData));
    }

    /**
     * Get current selections for debugging or persistence.
     * @returns {Object} Current selections
     */
    getCurrentSelections() {
        return JSON.parse(JSON.stringify(this.currentSelections));
    }

    /**
     * Set linkage data (for loading from persistence).
     * @param {Object} linkageData - Linkage data to set
     */
    setLinkageData(linkageData) {
        this.linkageData = JSON.parse(JSON.stringify(linkageData));
    }

    /**
     * Set current selections (for loading from persistence).
     * @param {Object} selections - Selections to set
     */
    setCurrentSelections(selections) {
        this.currentSelections = JSON.parse(JSON.stringify(selections));
    }
}
