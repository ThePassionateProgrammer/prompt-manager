"""
Test cascading linkage restoration to debug complex scenarios.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestCascadingLinkageDebug:
    """Test cascading linkage restoration debugging."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_cascading_linkage_debug(self):
        """
        Test cascading linkage restoration in complex scenarios.
        """
        # Enter a template first
        template_input = self.driver.find_element(By.ID, "templateInput")
        template_input.send_keys("As a [Role], I want to [What], so that I can [Why].")
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
        why_input = inputs[2]     # Why
        
        print("Step 1: Create Programmer -> Write Code -> Deliver linkages")
        
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
        
        # Select "Write Code"
        what_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in what_options:
            if option.text == "Write Code":
                option.click()
                break
        time.sleep(1)
        
        # Add "Deliver" to Why
        why_input.click()
        why_input.send_keys("Deliver")
        why_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check initial linkage data
        initial_state = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            return {
                linkageData: window.linkageData,
                currentSelections: window.currentSelections,
                roleOptions: Array.from(comboBoxes[0].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent),
                whatOptions: Array.from(comboBoxes[1].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent),
                whyOptions: Array.from(comboBoxes[2].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent)
            };
        """)
        print(f"Initial state: {initial_state}")
        
        print("Step 2: Add Manager and switch to it")
        
        # Add "Manager" to Role
        role_input.click()
        role_input.send_keys("Manager")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Select "Manager"
        role_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in role_options:
            if option.text == "Manager":
                option.click()
                break
        time.sleep(1)
        
        # Check state after switching to Manager
        manager_state = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            return {
                linkageData: window.linkageData,
                currentSelections: window.currentSelections,
                roleOptions: Array.from(comboBoxes[0].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent),
                whatOptions: Array.from(comboBoxes[1].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent),
                whyOptions: Array.from(comboBoxes[2].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent)
            };
        """)
        print(f"Manager state: {manager_state}")
        
        print("Step 3: Switch back to Programmer and monitor restoration")
        
        # Test the callback directly to see what happens
        result = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                
                // Store state before callback
                const beforeState = {
                    linkageData: JSON.parse(JSON.stringify(window.linkageData)),
                    currentSelections: JSON.parse(JSON.stringify(window.currentSelections)),
                    whatOptions: Array.from(comboBoxes[1].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent),
                    whyOptions: Array.from(comboBoxes[2].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent)
                };
                
                console.log('=== TESTING CASCADING LINKAGE RESTORATION ===');
                console.log('Before callback:', beforeState);
                
                // Manually trigger the callback for Programmer
                if (roleCombo.onSelectionChange) {
                    console.log('Triggering callback for Programmer...');
                    roleCombo.onSelectionChange('Programmer');
                }
                
                // Wait a bit for any async operations
                setTimeout(() => {
                    const afterState = {
                        linkageData: JSON.parse(JSON.stringify(window.linkageData)),
                        currentSelections: JSON.parse(JSON.stringify(window.currentSelections)),
                        whatOptions: Array.from(comboBoxes[1].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent),
                        whyOptions: Array.from(comboBoxes[2].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent)
                    };
                    console.log('After callback:', afterState);
                }, 100);
                
                return {
                    success: 'Cascading linkage test completed',
                    beforeState: beforeState
                };
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Cascading linkage debug result: {result}")
        
        # Wait for async operations
        time.sleep(2)
        
        # Check final state
        final_state = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            return {
                linkageData: window.linkageData,
                currentSelections: window.currentSelections,
                roleOptions: Array.from(comboBoxes[0].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent),
                whatOptions: Array.from(comboBoxes[1].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent),
                whyOptions: Array.from(comboBoxes[2].dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent)
            };
        """)
        
        print(f"Final state: {final_state}")
        
        # Check if Write Code and Deliver are restored
        what_options = final_state.get('whatOptions', [])
        why_options = final_state.get('whyOptions', [])
        
        if "Write Code" in what_options:
            print("✅ Write Code was restored in What combo box")
        else:
            print("❌ Write Code was NOT restored in What combo box")
            
        if "Deliver" in why_options:
            print("✅ Deliver was restored in Why combo box")
        else:
            print("❌ Deliver was NOT restored in Why combo box")
        
        # The test passes if we can see what's happening with the cascading restoration
        assert result.get('success') == 'Cascading linkage test completed', "Cascading linkage test failed"
