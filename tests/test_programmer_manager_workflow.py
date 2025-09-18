"""
Test the exact workflow described by the user:
1. Create Programmer -> Write Code -> Deliver linkages
2. Switch to Manager (clears other combo boxes - correct)
3. Switch back to Programmer (should restore Write Code -> Deliver - currently broken)
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestProgrammerManagerWorkflow:
    """Test the exact user workflow that's failing."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_programmer_manager_linkage_workflow(self):
        """
        Test the exact workflow: Programmer -> Write Code -> Deliver, 
        then Manager, then back to Programmer.
        """
        # Enter the exact template from user
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
        
        print("Step 2: Switch to Manager (should clear other combo boxes)")
        
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
        
        print("Step 3: Switch back to Programmer (should restore Write Code -> Deliver)")
        
        # Select "Programmer" again
        role_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in role_options:
            if option.text == "Programmer":
                option.click()
                break
        time.sleep(1)
        
        # Check what options after switching back to Programmer
        what_options_after_programmer = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        what_texts_after_programmer = [opt.text for opt in what_options_after_programmer]
        print(f"What options after Programmer: {what_texts_after_programmer}")
        
        # Check final linkage data
        result2 = self.driver.execute_script("""
            return {
                linkageData: window.linkageData,
                currentSelections: window.currentSelections
            };
        """)
        print(f"Final state: {result2}")
        
        # Verify that Write Code is restored when switching back to Programmer
        assert "Write Code" in what_texts_after_programmer, f"Expected 'Write Code' to be restored, got {what_texts_after_programmer}"
        
        print("✓ Programmer linkage restoration test completed")
