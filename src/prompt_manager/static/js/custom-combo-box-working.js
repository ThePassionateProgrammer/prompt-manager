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
            } else {
                // Replace selected option
                this.comboBox.replaceOption(this.comboBox.selectedOption, entryText);
            }
        } else {
            // No item selected - default to add behavior
            if (entryText !== '') {
                this.comboBox.addOption(entryText);
                this.comboBox.input.value = '';
            }
        }
        
        // Always keep dropdown open
        this.comboBox.showDropdown();
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
        }
        this.comboBox.showDropdown();
    }
}

class CustomComboBox {
    constructor(containerId) {
        console.log('CustomComboBox constructor called with:', containerId);
        this.container = document.getElementById(containerId);
        console.log('Container found:', this.container);
        
        this.input = this.container.querySelector('.combo-box-input');
        this.dropdown = this.container.querySelector('.combo-box-dropdown');
        this.arrow = this.container.querySelector('.combo-box-arrow');
        this.options = Array.from(this.dropdown.querySelectorAll('.combo-box-option'));
        
        console.log('Elements found:', {
            input: this.input,
            dropdown: this.dropdown,
            arrow: this.arrow,
            options: this.options
        });
        
        this.selectedIndex = -1;
        this.selectedOption = null;
        this.highlightedIndex = -1;
        this.isDropdownVisible = false;
        
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
        
        // Key events
        this.input.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
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
                this.selectOption(index);
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
                this.hideDropdown();
                break;
            case 'Tab':
                // Let default tab behavior work
                break;
        }
    }
    
    handleEnter() {
        const entryText = this.input.value.trim();
        this.currentState.handleEnter(entryText);
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
        
        // Select the option
        this.selectedIndex = index;
        this.selectedOption = option.dataset.value;
        this.input.value = option.dataset.value;
        this.updateSelection();
        
        // Trigger selection change callback
        if (this.onSelectionChange && typeof this.onSelectionChange === 'function') {
            this.onSelectionChange(this.selectedOption);
        }
        
        // Keep dropdown open and focus on input
        this.showDropdown();
        setTimeout(() => this.input.focus(), 10);
        
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
    
    addOption(value, skipCallback = false) {
        // Add new option after "Add..." or "Select item..." option (index 0)
        const firstOption = this.options[0];
        const newOption = document.createElement('div');
        newOption.className = 'combo-box-option';
        newOption.dataset.value = value;
        newOption.textContent = value;
        
        // Add event listeners
        newOption.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.selectOption(this.options.indexOf(newOption));
        });
        newOption.addEventListener('mouseenter', () => this.highlightOption(this.options.indexOf(newOption)));
        
        firstOption.parentNode.insertBefore(newOption, firstOption.nextSibling);
        this.options = Array.from(this.dropdown.querySelectorAll('.combo-box-option'));
        
        // Select the newly added option (it's at index 1)
        this.selectedIndex = 1;
        this.selectedOption = value;
        this.updateSelection();
        
        // Trigger selection change callback
        if (this.onSelectionChange && typeof this.onSelectionChange === 'function') {
            this.onSelectionChange(this.selectedOption);
        }
        
        // Trigger option added callback (only in addOption, not selectOption, and only if not skipping)
        if (!skipCallback && this.onOptionAdded && typeof this.onOptionAdded === 'function') {
            this.onOptionAdded(this.selectedOption);
        }
        
        // Clear any previous highlighting
        this.highlightedIndex = -1;
        this.updateHighlight();
    }
    
    replaceOption(oldValue, newValue) {
        // Find the option by current selected index instead of value
        if (this.selectedIndex >= 0 && this.selectedIndex < this.options.length) {
            const option = this.options[this.selectedIndex];
            option.dataset.value = newValue;
            option.textContent = newValue;
            this.selectedOption = newValue;
            this.updateSelection();
            
            // Clear any previous highlighting
            this.highlightedIndex = -1;
            this.updateHighlight();
        }
    }
    
    removeOption(value) {
        // Remove the currently selected option by index
        if (this.selectedIndex >= 0 && this.selectedIndex < this.options.length) {
            const option = this.options[this.selectedIndex];
            if (option.dataset.value !== 'Add...' && option.dataset.value !== 'Select item...') {
                option.remove();
                this.options = Array.from(this.dropdown.querySelectorAll('.combo-box-option'));
                
                // Clear selection
                this.selectedIndex = -1;
                this.selectedOption = null;
                this.updateSelection();
                
                // Clear any previous highlighting
                this.highlightedIndex = -1;
                this.updateHighlight();
            }
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
