"""
Test event listener setup to debug the indexing issue.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestEventListenerDebug:
    """Test event listener setup debugging."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_event_listener_debug(self):
        """
        Test event listener setup to debug the indexing issue.
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
        
        # Get combo box input
        inputs = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-input")
        role_input = inputs[0]    # Role
        
        # Clear any existing logs
        self.driver.get_log('browser')
        
        # Add "Programmer" to Role
        role_input.click()
        role_input.send_keys("Programmer")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Add "Manager" to Role
        role_input.click()
        role_input.send_keys("Manager")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Get logs after adding options
        logs_after_add = self.driver.get_log('browser')
        add_logs = [log for log in logs_after_add if 'Adding option' in log.get('message', '')]
        print(f"Add option logs: {add_logs}")
        
        # Now try to click on "Programmer" and capture logs
        role_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in role_options:
            if option.text == "Programmer":
                print(f"Clicking on 'Programmer'...")
                option.click()
                time.sleep(1)
                break
        
        # Get logs after clicking
        logs_after_click = self.driver.get_log('browser')
        click_logs = [log for log in logs_after_click if 'Option clicked' in log.get('message', '')]
        print(f"Click logs: {click_logs}")
        
        # Check final state
        final_state = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                return {
                    selectedIndex: roleCombo.selectedIndex,
                    selectedOption: roleCombo.selectedOption
                };
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Final state: {final_state}")
        
        # The test passes if we can see the debug logs
        assert len(add_logs) > 0 or len(click_logs) > 0, "No debug logs captured"
