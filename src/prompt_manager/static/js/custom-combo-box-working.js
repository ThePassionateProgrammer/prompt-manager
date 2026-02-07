/**
 * CustomComboBox Component - Working Version
 * Extracted directly from test_combo_box_standalone.html
 * 
 * Features:
 * - Edit Mode: Add, edit, delete items
 * - Display Mode: Read-only selection
 * - State Pattern implementation
 * - Hierarchical linkages support
 */

// CustomComboBox v2.0 - Production Ready
// Complete implementation with Add, Update, Delete functionality
// Date: December 2024

// State Pattern Implementation
class EditModeState {
    constructor(comboBox) {
        this.comboBox = comboBox;
    }
    
    getFirstOptionText() {
        return 'Add...';
    }
    
    getPlaceholderText() {
        return 'Type to add...';
    }
    
    handleEnter(entryText) {
        if (this.comboBox.selectedIndex >= 0) {
            // Item is selected - update or delete
            if (entryText === '') {
                // Remove selected option
                this.comboBox.removeOption(this.comboBox.selectedOption);
                // Keep dropdown open after deletion
                this.comboBox.showDropdown();
            } else {
                // Replace selected option
                this.comboBox.replaceOption(this.comboBox.selectedOption, entryText);
                // Close dropdown after replacement
                this.comboBox.hideDropdown();
            }
        } else {
            // No item selected - default to add behavior
            if (entryText !== '') {
                // Add option without selecting it, but allow callbacks for linkage creation
                this.comboBox.addOption(entryText, false, false);
                // Clear input field
                this.comboBox.input.value = '';
                // Keep dropdown open after adding
                this.comboBox.showDropdown();
            } else {
                // No text entered - close dropdown
                this.comboBox.hideDropdown();
            }
        }
    }
}

class DisplayModeState {
    constructor(comboBox) {
        this.comboBox = comboBox;
    }
    
    getFirstOptionText() {
        return 'Select item...';
    }
    
    getPlaceholderText() {
        return 'Select item...';
    }
    
    handleEnter(entryText) {
        // In Display mode, only allow selection
        if (this.comboBox.selectedIndex >= 0 && this.comboBox.selectedOption !== 'Select item...') {
            this.comboBox.input.value = this.comboBox.selectedOption;
            // Close dropdown after selection in Display mode
            this.comboBox.hideDropdown();
        } else {
            // No valid selection - keep dropdown open
            this.comboBox.showDropdown();
        }
    }
}

class CustomComboBox {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        
        this.input = this.container.querySelector('.combo-box-input');
        this.dropdown = this.container.querySelector('.combo-box-dropdown');
        this.arrow = this.container.querySelector('.combo-box-arrow');
        this.options = Array.from(this.dropdown.querySelectorAll('.combo-box-option'));
        
        this.selectedIndex = -1;
        this.selectedOption = null;
        this.highlightedIndex = -1;
        this.isDropdownVisible = false;
        this.isEditMode = false;
        this.originalText = null;
        this.isUpdating = false;
        this.newText = null;
        
        // Initialize with Display mode state
        this.setState(new DisplayModeState(this));
        
        this.setupEventListeners();
        this.updateOptions();
    }
    
    setState(newState) {
        this.currentState = newState;
        this.updateMode();
    }
    
    setupEventListeners() {
        // Focus events - always show dropdown
        this.input.addEventListener('focus', () => this.showDropdown());
        
        // Blur events - exit edit mode if active
        this.input.addEventListener('blur', () => {
            if (this.isEditMode) {
                this.exitEditMode(false); // Apply changes on focus loss
            }
        });
        
        // Key events
        this.input.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Input events - handle typing
        this.input.addEventListener('input', (e) => {
            // Don't clear selection when typing in edit mode - keep item highlighted
            if (this.isEditMode) {
                // Update stored text when typing in edit mode
                this.newText = this.input.value;
                // Keep the selection highlighted while editing (even when text is cleared)
                return;
            }
            
            // Special case: If we have a selected option and user is deleting/clearing the text,
            // keep the selection so Enter can delete the item
            if (this.selectedOption && this.input.value === '') {
                // Keep the selection highlighted so Enter will delete the item
                return;
            }
            
            // Only clear selection if not in edit mode and input doesn't match selected option
            if (this.selectedOption && this.input.value !== this.selectedOption) {
                this.selectedOption = null;
                this.selectedIndex = -1;
                this.updateSelection();
            }
        });
        
        // Handle click on input field for edit mode
        this.input.addEventListener('click', (e) => {
            // If there's a selected option and user clicks on input, enter edit mode
            if (this.selectedOption && this.input.value === this.selectedOption) {
                this.enterEditMode();
            }
        });
        
        // Arrow click - only way to close dropdown
        this.arrow.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        });
        
        // Option clicks
        this.options.forEach((option, index) => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                // If clicking on already selected option, enter edit mode
                if (this.selectedOption && option.dataset.value === this.selectedOption) {
                    this.enterEditMode();
                } else {
                    // Otherwise, select the option normally
                    this.selectOption(index);
                }
            });
            option.addEventListener('mouseenter', () => this.highlightOption(index));
        });
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                this.hideDropdown();
            }
        });
    }
    
    handleKeyDown(e) {
        switch(e.key) {
            case 'Enter':
                e.preventDefault();
                this.handleEnter();
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.navigateDown();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.navigateUp();
                break;
            case 'Escape':
                e.preventDefault();
                if (this.isEditMode) {
                    this.exitEditMode(true); // true = revert
                } else {
                    this.hideDropdown();
                }
                break;
            case 'Delete':
                // In edit mode, Delete key should only clear text, not selection
                if (this.isEditMode) {
                    // Update stored text when deleting in edit mode
                    this.newText = this.input.value;
                }
                // Let default Delete behavior work (don't preventDefault)
                break;
            case 'Tab':
                // Let default tab behavior work
                break;
        }
    }
    
    handleEnter() {
        const entryText = this.input.value.trim();
        
        // Priority 1: If in edit mode, check if user is trying to add new item vs edit existing
        if (this.isEditMode) {
            // If the input text is different from the original text, treat as adding new item
            if (entryText !== this.originalText && entryText !== '') {
                // User is adding a new item, not editing the existing one
                this.exitEditMode(true); // Revert the edit mode
                this.currentState.handleEnter(entryText); // Add the new item
                return;
            } else {
                // User is editing the existing item
                this.exitEditMode(false); // Apply changes
                return;
            }
        }
        
        // Priority 2: If there's a highlighted option, select it
        if (this.highlightedIndex >= 0 && this.highlightedIndex < this.options.length) {
            this.selectOption(this.highlightedIndex);
            return;
        }
        
        // Priority 3: Use state-specific Enter handling
        this.currentState.handleEnter(entryText);
    }
    
    enterEditMode() {
        this.isEditMode = true;
        this.originalText = this.input.value;
        this.newText = this.input.value; // Store the initial text
        
        // Keep dropdown open
        this.showDropdown();
        
        // Move cursor to end of text
        setTimeout(() => {
            const length = this.input.value.length;
            this.input.setSelectionRange(length, length);
        }, 10);
    }
    
    exitEditMode(revert = false) {
        if (!this.isEditMode) return;
        
        this.isEditMode = false;
        
        if (revert) {
            // Revert to original text
            this.input.value = this.originalText;
        } else {
            // Apply changes - update the selected option
            const newText = this.newText && this.newText.trim() !== '' ? this.newText.trim() : this.input.value.trim();
            const oldValue = this.originalText;
            
            if (newText === '') {
                // Delete the option if text is empty
                this.removeOption(oldValue);
            } else if (newText !== oldValue) {
                // Update the option with new text (only if different)
                this.replaceOption(oldValue, newText);
            }
            // If newText === oldValue, no change needed
        }
        
        this.originalText = null;
        this.newText = null;
    }
    
    navigateDown() {
        if (!this.isDropdownVisible) {
            this.showDropdown();
        }
        
        this.highlightedIndex = Math.min(this.highlightedIndex + 1, this.options.length - 1);
        this.updateHighlight();
    }
    
    navigateUp() {
        if (!this.isDropdownVisible) {
            this.showDropdown();
        }
        
        this.highlightedIndex = Math.max(this.highlightedIndex - 1, 0);
        this.updateHighlight();
    }
    
    selectOption(index) {
        if (index < 0 || index >= this.options.length) return;
        
        const option = this.options[index];
        if (option.dataset.value === 'Add...') {
            // Handle Add... like a button - always works
            const entryText = this.input.value.trim();
            if (entryText !== '') {
                this.addOption(entryText);
                this.input.value = ''; // Clear input field to prevent duplicate adds
            }
            // Keep dropdown open and focus on input
            this.showDropdown();
            setTimeout(() => this.input.focus(), 10);
            return;
        }
        
        // If in edit mode, apply changes before selecting new option
        if (this.isEditMode) {
            this.exitEditMode(false); // Apply changes
        }
        
        // Select the option
        const previousSelection = this.selectedOption;
        this.selectedIndex = index;
        this.selectedOption = option.dataset.value;
        this.input.value = option.dataset.value;
        this.updateSelection();
        
        // Trigger selection change callback (even if same option selected)
        if (this.onSelectionChange && typeof this.onSelectionChange === 'function') {
            try {
                this.onSelectionChange(this.selectedOption);
            } catch (error) {
                console.error('Callback error:', error);
            }
        }
        
        // Close dropdown after selection
        this.hideDropdown();
        
        // Select all text in input field
        this.input.select();
    }
    
    highlightOption(index) {
        this.highlightedIndex = index;
        this.updateHighlight();
    }
    
    showDropdown() {
        this.dropdown.classList.add('show');
        this.arrow.classList.add('up');
        this.isDropdownVisible = true;
        
        // Update selection highlighting when dropdown is shown
        this.updateSelection();
        
        // Clear any previous highlighting
        this.highlightedIndex = -1;
        this.updateHighlight();
    }
    
    hideDropdown() {
        this.dropdown.classList.remove('show');
        this.arrow.classList.remove('up');
        this.isDropdownVisible = false;
        this.highlightedIndex = -1;
        this.updateHighlight();
    }
    
    toggleDropdown() {
        if (this.isDropdownVisible) {
            this.hideDropdown();
        } else {
            this.showDropdown();
        }
    }
    
    updateHighlight() {
        this.options.forEach((option, index) => {
            option.classList.toggle('highlighted', index === this.highlightedIndex);
        });
    }
    
    updateSelection() {
        this.options.forEach((option, index) => {
            const isSelected = index === this.selectedIndex;
            option.classList.toggle('selected', isSelected);
            if (isSelected) {
                option.style.backgroundColor = '#555';
                option.style.color = 'white';
                option.style.fontWeight = 'bold';
            } else {
                option.style.backgroundColor = '';
                option.style.color = '';
                option.style.fontWeight = '';
            }
        });
    }
    
    addOption(value, skipCallback = false, selectNewOption = true) {
        // Add new option after "Add..." or "Select item..." option (index 0)
        const firstOption = this.options[0];
        const newOption = document.createElement('div');
        newOption.className = 'combo-box-option';
        newOption.dataset.value = value;
        newOption.textContent = value;
        
        // Insert the new option into DOM first
        firstOption.parentNode.insertBefore(newOption, firstOption.nextSibling);
        this.options = Array.from(this.dropdown.querySelectorAll('.combo-box-option'));
        
        // Add event listeners with correct index - use DOM position to determine index
        newOption.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            // Calculate the correct index dynamically based on DOM position
            const allOptions = Array.from(this.dropdown.querySelectorAll('.combo-box-option'));
            const clickedIndex = allOptions.indexOf(newOption);
            this.selectOption(clickedIndex);
        });
        newOption.addEventListener('mouseenter', () => {
            // Calculate the correct index dynamically based on DOM position
            const allOptions = Array.from(this.dropdown.querySelectorAll('.combo-box-option'));
            const hoverIndex = allOptions.indexOf(newOption);
            this.highlightOption(hoverIndex);
        });
        
        // Select the newly added option only if requested (it's at index 1)
        if (selectNewOption) {
            this.selectedIndex = 1;
            this.selectedOption = value;
            this.input.value = value; // Set the input field value to show the selection
            this.updateSelection();
            
            // Trigger selection change callback
            if (this.onSelectionChange && typeof this.onSelectionChange === 'function') {
                this.onSelectionChange(this.selectedOption);
            }
        }
        
        // Trigger option added callback (only in addOption, not selectOption, and only if not skipping)
        if (!skipCallback && this.onOptionAdded && typeof this.onOptionAdded === 'function') {
            this.onOptionAdded(value); // Use the value parameter instead of selectedOption
        }
        
        // Clear any previous highlighting
        this.highlightedIndex = -1;
        this.updateHighlight();
    }
    
    replaceOption(oldValue, newValue) {
        // Find the option by value instead of index
        const option = this.options.find(opt => opt.textContent === oldValue);
        if (!option) return;
        
        // Set updating flag to prevent interference
        this.isUpdating = true;
        
        // Temporarily disable callbacks to prevent interference
        const originalSelectionCallback = this.onSelectionChange;
        const originalOptionAddedCallback = this.onOptionAdded;
        this.onSelectionChange = null;
        this.onOptionAdded = null;
        
        // Update the existing option in place
        option.textContent = newValue;
        option.dataset.value = newValue;
        
        // Update the selected option value
        this.selectedOption = newValue;
        
        // Ensure the input field shows the new value
        this.input.value = newValue;
        
        // Refresh the options array
        this.options = Array.from(this.dropdown.querySelectorAll('.combo-box-option'));
        
        // Update selection highlighting
        this.updateSelection();
        
        // Clear any previous highlighting
        this.highlightedIndex = -1;
        this.updateHighlight();
        
        // Re-enable the callbacks after a delay to ensure all updates are complete
        setTimeout(() => {
            this.onSelectionChange = originalSelectionCallback;
            this.onOptionAdded = originalOptionAddedCallback;
            this.isUpdating = false;
        }, 500);
    }
    
    removeOption(value) {
        // Find and remove the option by value
        const option = this.options.find(opt => opt.textContent === value);
        if (option && option.dataset.value !== 'Add...' && option.dataset.value !== 'Select item...') {
            option.remove();
            this.options = Array.from(this.dropdown.querySelectorAll('.combo-box-option'));
            
            // Clear selection if we removed the currently selected option
            if (this.selectedOption === value) {
                this.selectedIndex = -1;
                this.selectedOption = null;
                this.updateSelection();
            }
            
            // Clear any previous highlighting
            this.highlightedIndex = -1;
            this.updateHighlight();
        }
    }
    
    updateOptions() {
        this.updateSelection();
    }
    
    updateMode() {
        // Update the first option and placeholder based on current state
        if (this.options.length > 0) {
            this.options[0].textContent = this.currentState.getFirstOptionText();
            this.options[0].dataset.value = this.currentState.getFirstOptionText();
            this.input.placeholder = this.currentState.getPlaceholderText();
        }
    }
    
    // Public API methods for integration
    getOptions() {
        return this.options
            .filter(option => option.dataset.value !== 'Add...' && option.dataset.value !== 'Select item...')
            .map(option => option.dataset.value);
    }
    
    setOptions(options) {
        // Clear existing options (except first one)
        this.options.slice(1).forEach(option => option.remove());
        
        // Add new options
        options.forEach(option => this.addOption(option));
        
        this.options = Array.from(this.dropdown.querySelectorAll('.combo-box-option'));
    }
    
    getSelectedValue() {
        return this.selectedOption;
    }
    
    setSelectedValue(value) {
        const option = this.options.find(opt => opt.dataset.value === value);
        if (option) {
            this.selectOption(this.options.indexOf(option));
        }
    }
    
    setMode(mode) {
        this.setState(mode === 'edit' ? new EditModeState(this) : new DisplayModeState(this));
    }
    
    getMode() {
        return this.currentState instanceof EditModeState ? 'edit' : 'display';
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CustomComboBox, EditModeState, DisplayModeState };
}
