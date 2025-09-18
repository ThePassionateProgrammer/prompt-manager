"""
Test the full workflow with manual callback triggering.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestManualCallbackWorkflow:
    """Test the full workflow with manual callback triggering."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_manual_callback_workflow(self):
        """
        Test the full workflow: create linkages, then manually trigger callback to restore.
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
        
        # Check linkage data after creating Programmer linkages
        result1 = self.driver.execute_script("""
            return {
                linkageData: window.linkageData,
                currentSelections: window.currentSelections
            };
        """)
        print(f"After Programmer setup: {result1}")
        
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
        
        # Check what options after switching to Manager
        what_options_after_manager = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        what_texts_after_manager = [opt.text for opt in what_options_after_manager]
        print(f"What options after Manager: {what_texts_after_manager}")
        
        print("Step 3: Manually trigger callback to restore Programmer linkages")
        
        # Manually trigger the callback for Role combo box
        manual_result = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                if (roleCombo.onSelectionChange) {
                    console.log('Manually triggering callback for Programmer...');
                    roleCombo.onSelectionChange('Programmer');
                    
                    // Check what options after manual restoration
                    const whatOptions = document.querySelectorAll('.combo-box-option');
                    const whatTexts = Array.from(whatOptions).map(opt => opt.textContent);
                    
                    return {
                        success: 'Callback manually triggered',
                        whatOptions: whatTexts,
                        linkageData: window.linkageData,
                        currentSelections: window.currentSelections
                    };
                }
                return { error: 'No callback function' };
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Manual callback result: {manual_result}")
        
        # Verify that Write Code is restored when manually triggering the callback
        assert "Write Code" in manual_result["whatOptions"], f"Expected 'Write Code' to be restored, got {manual_result['whatOptions']}"
        
        print("✓ Manual callback workflow works!")
