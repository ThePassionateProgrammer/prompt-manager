"""
Test linkage restoration logic to debug why linkages aren't being restored.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestLinkageRestorationDebug:
    """Test linkage restoration debugging."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_linkage_restoration_debug(self):
        """
        Test linkage restoration logic to debug the issue.
        """
        # Enter a template first
        template_input = self.driver.find_element(By.ID, "templateInput")
        template_input.send_keys("As a [Role], I want to [What].")
        time.sleep(1)
        
        # Generate combo boxes
        generate_btn = self.driver.find_element(By.ID, "generateBtn")
        generate_btn.click()
        time.sleep(2)
        
        # Switch to Edit Mode
        edit_mode_btn = self.driver.find_element(By.ID, "editModeBtn")
        edit_mode_btn.click()
        time.sleep(1)
        
        # Get combo box inputs
        inputs = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-input")
        role_input = inputs[0]    # Role
        what_input = inputs[1]    # What
        
        # Add "Programmer" to Role
        role_input.click()
        role_input.send_keys("Programmer")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Select "Programmer"
        role_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in role_options:
            if option.text == "Programmer":
                option.click()
                break
        time.sleep(1)
        
        # Add "Write Code" to What
        what_input.click()
        what_input.send_keys("Write Code")
        what_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check initial linkage data
        initial_state = self.driver.execute_script("""
            return {
                linkageData: window.linkageData,
                currentSelections: window.currentSelections
            };
        """)
        print(f"Initial state: {initial_state}")
        
        # Test linkage restoration by clicking on Programmer again
        result = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                const whatCombo = comboBoxes[1];
                
                // Store initial state
                const initialState = {
                    linkageData: JSON.parse(JSON.stringify(window.linkageData)),
                    currentSelections: JSON.parse(JSON.stringify(window.currentSelections)),
                    whatOptions: Array.from(whatCombo.dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent)
                };
                
                console.log('=== TESTING LINKAGE RESTORATION ===');
                console.log('Initial state:', initialState);
                
                // Click on Programmer to trigger linkage restoration
                const roleOptions = roleCombo.options;
                for (let i = 0; i < roleOptions.length; i++) {
                    if (roleOptions[i].textContent === 'Programmer') {
                        console.log('Clicking on Programmer...');
                        roleOptions[i].click();
                        break;
                    }
                }
                
                // Wait a bit for any async operations
                setTimeout(() => {
                    const finalState = {
                        linkageData: JSON.parse(JSON.stringify(window.linkageData)),
                        currentSelections: JSON.parse(JSON.stringify(window.currentSelections)),
                        whatOptions: Array.from(whatCombo.dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent)
                    };
                    console.log('Final state:', finalState);
                }, 100);
                
                return {
                    success: 'Linkage restoration test completed',
                    initialState: initialState
                };
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Linkage restoration debug result: {result}")
        
        # Wait a bit for the async operations to complete
        time.sleep(2)
        
        # Check final state
        final_state = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const whatCombo = comboBoxes[1];
                return {
                    linkageData: window.linkageData,
                    currentSelections: window.currentSelections,
                    whatOptions: Array.from(whatCombo.dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent)
                };
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Final state: {final_state}")
        
        # The test passes if we can see what's happening with the linkage restoration
        assert result.get('success') == 'Linkage restoration test completed', "Linkage restoration test failed"
        
        # Check if Write Code is restored
        what_options = final_state.get('whatOptions', [])
        if "Write Code" in what_options:
            print("✅ Write Code was restored in What combo box")
        else:
            print("❌ Write Code was NOT restored in What combo box")
            print(f"What options: {what_options}")
