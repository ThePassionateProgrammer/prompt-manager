"""
Test selectOption method to debug the index issue.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestSelectOptionDebug:
    """Test selectOption method debugging."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_selectoption_debug(self):
        """
        Test selectOption method to debug the index issue.
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
        
        # Add "Manager" to Role
        role_input.click()
        role_input.send_keys("Manager")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Test direct selectOption calls
        result = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                const options = roleCombo.options;
                
                console.log('=== TESTING SELECTOPTION ===');
                console.log('Available options:', options.map((opt, i) => ({index: i, text: opt.textContent})));
                
                // Test selecting index 1 (Manager)
                console.log('Testing selectOption(1) - should select Manager');
                roleCombo.selectOption(1);
                const state1 = {
                    selectedIndex: roleCombo.selectedIndex,
                    selectedOption: roleCombo.selectedOption
                };
                console.log('After selectOption(1):', state1);
                
                // Test selecting index 2 (Programmer)
                console.log('Testing selectOption(2) - should select Programmer');
                roleCombo.selectOption(2);
                const state2 = {
                    selectedIndex: roleCombo.selectedIndex,
                    selectedOption: roleCombo.selectedOption
                };
                console.log('After selectOption(2):', state2);
                
                return {
                    options: options.map((opt, i) => ({index: i, text: opt.textContent})),
                    state1: state1,
                    state2: state2
                };
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"SelectOption test result: {result}")
        
        # Get browser console logs
        logs = self.driver.get_log('browser')
        selectoption_logs = [log for log in logs if 'SELECTOPTION' in log.get('message', '') or 'selectOption' in log.get('message', '')]
        print(f"SelectOption logs: {selectoption_logs}")
        
        # The test passes if we can see the direct selectOption calls working
        assert result.get('state1', {}).get('selectedOption') == 'Manager', f"Expected Manager, got {result.get('state1')}"
        assert result.get('state2', {}).get('selectedOption') == 'Programmer', f"Expected Programmer, got {result.get('state2')}"
