"""
Debug test to understand why dropdown isn't closing after selection.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestDebugDropdown:
    """Debug test for dropdown behavior."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_debug_dropdown_behavior(self):
        """Debug the dropdown behavior step by step."""
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
        
        print("Step 1: Add 'Programmer' to Role combo box")
        
        # Add "Programmer" to Role
        role_input.click()
        role_input.send_keys("Programmer")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check dropdown state before clicking
        state_before = self.driver.execute_script("""
            const roleCombo = window.customComboBoxes[0];
            return roleCombo ? {
                isDropdownVisible: roleCombo.isDropdownVisible,
                selectedOption: roleCombo.selectedOption,
                selectedIndex: roleCombo.selectedIndex
            } : null;
        """)
        print(f"State before clicking option: {state_before}")
        
        # Get the Programmer option
        role_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        programmer_option = None
        for option in role_options:
            if option.text == "Programmer":
                programmer_option = option
                break
        
        assert programmer_option is not None, "Programmer option should be available"
        
        print("Step 2: Click on 'Programmer' option and monitor console")
        
        # Click on the Programmer option
        programmer_option.click()
        time.sleep(1)  # Give time for events to process
        
        # Check state immediately after click
        state_immediate = self.driver.execute_script("""
            const roleCombo = window.customComboBoxes[0];
            return roleCombo ? {
                isDropdownVisible: roleCombo.isDropdownVisible,
                selectedOption: roleCombo.selectedOption,
                selectedIndex: roleCombo.selectedIndex
            } : null;
        """)
        print(f"State immediately after click: {state_immediate}")
        
        time.sleep(2)  # Give more time for any delayed events
        
        # Check dropdown state after clicking
        state_after = self.driver.execute_script("""
            const roleCombo = window.customComboBoxes[0];
            return roleCombo ? {
                isDropdownVisible: roleCombo.isDropdownVisible,
                selectedOption: roleCombo.selectedOption,
                selectedIndex: roleCombo.selectedIndex
            } : null;
        """)
        print(f"State after clicking option: {state_after}")
        
        # Get console logs
        logs = self.driver.get_log('browser')
        print("Browser console logs:")
        for log in logs:
            print(f"  {log['level']}: {log['message']}")
        
        # Also try to get console logs via JavaScript
        js_logs = self.driver.execute_script("""
            // Try to get console logs if available
            return window.console && window.console.logs ? window.console.logs : 'No console logs available';
        """)
        print(f"JavaScript console logs: {js_logs}")
        
        # The test passes if we can see the debug output
        assert True, "Debug test completed - check console output above"
