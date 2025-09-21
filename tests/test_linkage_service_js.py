"""
Unit tests for the JavaScript LinkageService.

These tests use a headless browser to test the JavaScript service in isolation.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


class TestLinkageServiceJS:
    """Test the JavaScript LinkageService class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.driver = webdriver.Chrome()
        
        # Create a simple test page with the LinkageService
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>LinkageService Test</title>
        </head>
        <body>
            <script src="/static/js/linkage-service.js"></script>
            <script>
                // Mock CustomComboBox class for testing
                class MockCustomComboBox {
                    constructor(tag) {
                        this.tag = tag;
                        this.selectedOption = null;
                        this.selectedIndex = -1;
                        this.dropdown = {
                            querySelectorAll: () => []
                        };
                        this.input = { value: '' };
                        this.onSelectionChange = null;
                        this.onOptionAdded = null;
                    }
                    
                    addOption(option, skipCallback = false, selectOption = true) {
                        // Mock implementation
                        if (selectOption) {
                            this.selectedOption = option;
                        }
                        if (this.onOptionAdded && !skipCallback) {
                            this.onOptionAdded(option);
                        }
                    }
                }
                
                // Create test instance
                window.linkageService = new LinkageService();
                window.mockComboBoxes = [
                    new MockCustomComboBox('Role'),
                    new MockCustomComboBox('What'),
                    new MockCustomComboBox('Why')
                ];
            </script>
        </body>
        </html>
        """
        
        # Write test HTML to a temporary file
        with open('/tmp/linkage_service_test.html', 'w') as f:
            f.write(test_html)
        
        self.driver.get(f'file:///tmp/linkage_service_test.html')
        time.sleep(1)
    
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_linkage_service_initialization(self):
        """Test that LinkageService initializes correctly."""
        result = self.driver.execute_script("""
            return {
                hasLinkageService: typeof window.linkageService !== 'undefined',
                hasMockComboBoxes: typeof window.mockComboBoxes !== 'undefined',
                mockComboBoxCount: window.mockComboBoxes ? window.mockComboBoxes.length : 0
            };
        """)
        
        assert result['hasLinkageService'] is True
        assert result['hasMockComboBoxes'] is True
        assert result['mockComboBoxCount'] == 3
    
    def test_register_combo_boxes(self):
        """Test registering combo boxes with the service."""
        result = self.driver.execute_script("""
            window.linkageService.registerComboBoxes(window.mockComboBoxes);
            return {
                comboBoxCount: window.linkageService.comboBoxes.length,
                firstTag: window.linkageService.comboBoxes[0].tag,
                lastTag: window.linkageService.comboBoxes[2].tag
            };
        """)
        
        assert result['comboBoxCount'] == 3
        assert result['firstTag'] == 'Role'
        assert result['lastTag'] == 'Why'
    
    def test_create_linkage(self):
        """Test creating linkages between combo boxes."""
        result = self.driver.execute_script("""
            window.linkageService.registerComboBoxes(window.mockComboBoxes);
            
            // Create a linkage
            window.linkageService.createLinkage('Role', 'What', 'Write Code');
            window.linkageService.createLinkage('Role', 'What', 'Test Code');
            
            return {
                linkageData: window.linkageService.getLinkageData(),
                hasRoleLinkage: 'Role' in window.linkageService.linkageData,
                hasWhatLinkage: window.linkageService.linkageData['Role'] && 'What' in window.linkageService.linkageData['Role'],
                linkedOptions: window.linkageService.linkageData['Role']['What']
            };
        """)
        
        assert result['hasRoleLinkage'] is True
        assert result['hasWhatLinkage'] is True
        assert 'Write Code' in result['linkedOptions']
        assert 'Test Code' in result['linkedOptions']
        assert len(result['linkedOptions']) == 2
    
    def test_parent_selection_change(self):
        """Test handling parent selection changes."""
        result = self.driver.execute_script("""
            window.linkageService.registerComboBoxes(window.mockComboBoxes);
            
            // Create linkages first
            window.linkageService.createLinkage('Role', 'What', 'Write Code');
            window.linkageService.createLinkage('Role', 'What', 'Test Code');
            
            // Set up a mock child combo box with options
            const whatCombo = window.mockComboBoxes[1];
            whatCombo.dropdown = {
                querySelectorAll: () => [
                    { remove: () => {} }, // First option (Add...)
                    { remove: () => {} }, // Write Code option
                    { remove: () => {} }  // Test Code option
                ]
            };
            
            // Simulate parent selection change
            window.linkageService.handleParentSelectionChange('Role', 'What', 'Programmer');
            
            return {
                currentSelections: window.linkageService.getCurrentSelections(),
                hasRoleSelection: 'Role' in window.linkageService.currentSelections,
                roleSelection: window.linkageService.currentSelections['Role']
            };
        """)
        
        assert result['hasRoleSelection'] is True
        assert result['roleSelection'] == 'Programmer'
    
    def test_child_option_added(self):
        """Test handling child option additions."""
        result = self.driver.execute_script("""
            window.linkageService.registerComboBoxes(window.mockComboBoxes);
            
            // Set current selection for parent
            window.linkageService.currentSelections['Role'] = 'Programmer';
            
            // Simulate child option addition
            window.linkageService.handleChildOptionAdded('Role', 'What', 'Write Code');
            
            return {
                linkageData: window.linkageService.getLinkageData(),
                hasLinkage: 'Role' in window.linkageService.linkageData && 
                           'What' in window.linkageService.linkageData['Role'],
                linkedOptions: window.linkageService.linkageData['Role']['What']
            };
        """)
        
        assert result['hasLinkage'] is True
        assert 'Write Code' in result['linkedOptions']
    
    def test_is_valid_selection(self):
        """Test selection validation logic."""
        result = self.driver.execute_script("""
            return {
                validProgrammer: window.linkageService.isValidSelection('Programmer'),
                invalidAddItem: window.linkageService.isValidSelection('Add item...'),
                invalidSelectItem: window.linkageService.isValidSelection('Select item...'),
                invalidEmpty: window.linkageService.isValidSelection(''),
                invalidNull: window.linkageService.isValidSelection(null)
            };
        """)
        
        assert result['validProgrammer'] is True
        assert result['invalidAddItem'] is False
        assert result['invalidSelectItem'] is False
        assert result['invalidEmpty'] is False
        assert result['invalidNull'] is False
    
    def test_get_combo_box_by_tag(self):
        """Test getting combo boxes by tag."""
        result = self.driver.execute_script("""
            window.linkageService.registerComboBoxes(window.mockComboBoxes);
            
            return {
                roleCombo: window.linkageService.getComboBoxByTag('Role') ? window.linkageService.getComboBoxByTag('Role').tag : null,
                whatCombo: window.linkageService.getComboBoxByTag('What') ? window.linkageService.getComboBoxByTag('What').tag : null,
                nonExistent: window.linkageService.getComboBoxByTag('NonExistent')
            };
        """)
        
        assert result['roleCombo'] == 'Role'
        assert result['whatCombo'] == 'What'
        assert result['nonExistent'] is None
    
    def test_data_persistence(self):
        """Test data persistence methods."""
        result = self.driver.execute_script("""
            window.linkageService.registerComboBoxes(window.mockComboBoxes);
            
            // Create some test data
            window.linkageService.createLinkage('Role', 'What', 'Write Code');
            window.linkageService.currentSelections['Role'] = 'Programmer';
            
            // Get data
            const linkageData = window.linkageService.getLinkageData();
            const selections = window.linkageService.getCurrentSelections();
            
            // Clear and restore
            window.linkageService.linkageData = {};
            window.linkageService.currentSelections = {};
            
            window.linkageService.setLinkageData(linkageData);
            window.linkageService.setCurrentSelections(selections);
            
            return {
                restoredLinkageData: window.linkageService.getLinkageData(),
                restoredSelections: window.linkageService.getCurrentSelections(),
                hasWriteCode: window.linkageService.linkageData['Role']['What'].includes('Write Code'),
                hasProgrammer: window.linkageService.currentSelections['Role'] === 'Programmer'
            };
        """)
        
        assert result['hasWriteCode'] is True
        assert result['hasProgrammer'] is True
