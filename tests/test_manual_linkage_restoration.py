"""
Test manual linkage restoration to verify the logic works.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestManualLinkageRestoration:
    """Test manual linkage restoration."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_manual_linkage_restoration(self):
        """
        Test manual linkage restoration by directly calling the callback.
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
        
        print("Step 1: Create Programmer -> Write Code linkages")
        
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
        
        # Check linkage data
        result1 = self.driver.execute_script("""
            return {
                linkageData: window.linkageData,
                currentSelections: window.currentSelections
            };
        """)
        print(f"After Programmer setup: {result1}")
        
        print("Step 2: Manually trigger linkage restoration")
        
        # Manually call the onSelectionChange callback for Role combo box
        result2 = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            const roleCombo = comboBoxes[0];
            
            // Manually trigger the callback
            if (roleCombo.onSelectionChange) {
                roleCombo.onSelectionChange('Programmer');
            }
            
            // Check what options after manual restoration
            const whatOptions = document.querySelectorAll('.combo-box-option');
            const whatTexts = Array.from(whatOptions).map(opt => opt.textContent);
            
            return {
                whatOptions: whatTexts,
                linkageData: window.linkageData,
                currentSelections: window.currentSelections
            };
        """)
        
        print(f"After manual restoration: {result2}")
        
        # Verify that Write Code is restored
        assert "Write Code" in result2["whatOptions"], f"Expected 'Write Code' to be restored, got {result2['whatOptions']}"
        
        print("✓ Manual linkage restoration works!")
