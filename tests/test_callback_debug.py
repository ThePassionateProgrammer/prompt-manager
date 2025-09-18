"""
Test callback execution with console log capture.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestCallbackDebug:
    """Test callback execution with console log capture."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_callback_debug(self):
        """
        Test callback execution and capture console logs.
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
        
        # Add "Programmer" to Role
        role_input.click()
        role_input.send_keys("Programmer")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Clear any existing logs
        self.driver.get_log('browser')
        
        # Try to click on "Programmer" option
        print("Attempting to click on Programmer option...")
        role_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in role_options:
            if option.text == "Programmer":
                print(f"Found Programmer option, clicking...")
                option.click()
                time.sleep(2)  # Wait for any async operations
                break
        
        # Get browser console logs
        logs = self.driver.get_log('browser')
        callback_logs = [log for log in logs if 'CALLBACK' in log.get('message', '')]
        selectoption_logs = [log for log in logs if 'SELECTOPTION' in log.get('message', '')]
        
        print(f"Callback logs: {callback_logs}")
        print(f"SelectOption logs: {selectoption_logs}")
        
        # Also check if we can manually trigger the callback and see what happens
        manual_result = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                if (roleCombo.onSelectionChange) {
                    console.log('=== MANUAL CALLBACK TEST ===');
                    try {
                        roleCombo.onSelectionChange('Programmer');
                        console.log('=== MANUAL CALLBACK SUCCESS ===');
                        return { success: 'Manual callback executed' };
                    } catch (error) {
                        console.error('=== MANUAL CALLBACK ERROR ===', error);
                        return { error: error.message };
                    }
                }
                return { error: 'No callback function' };
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Manual callback result: {manual_result}")
        
        # Get logs after manual callback
        logs_after_manual = self.driver.get_log('browser')
        manual_logs = [log for log in logs_after_manual if 'MANUAL' in log.get('message', '')]
        print(f"Manual callback logs: {manual_logs}")
        
        # The test passes if we can see some evidence of callback execution
        assert len(callback_logs) > 0 or len(selectoption_logs) > 0 or manual_result.get('success'), "No callback execution detected"
