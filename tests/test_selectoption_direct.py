"""
Test direct selectOption method call to debug callback triggering.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestSelectOptionDirect:
    """Test direct selectOption method call."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_selectoption_direct(self):
        """
        Test direct selectOption method call and monitor execution.
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
        
        # Directly call selectOption and monitor execution
        result = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                const options = roleCombo.options;
                
                // Find the Programmer option (should be at index 1)
                let programmerIndex = -1;
                for (let i = 0; i < options.length; i++) {
                    if (options[i].textContent === 'Programmer') {
                        programmerIndex = i;
                        break;
                    }
                }
                
                if (programmerIndex >= 0) {
                    // Store initial state
                    const initialState = {
                        selectedIndex: roleCombo.selectedIndex,
                        selectedOption: roleCombo.selectedOption,
                        hasCallback: !!roleCombo.onSelectionChange
                    };
                    
                    // Add a flag to track if callback was triggered
                    let callbackTriggered = false;
                    const originalCallback = roleCombo.onSelectionChange;
                    roleCombo.onSelectionChange = function(value) {
                        callbackTriggered = true;
                        console.log('=== CALLBACK TRIGGERED ===', value);
                        if (originalCallback) {
                            originalCallback(value);
                        }
                    };
                    
                    console.log('=== CALLING SELECTOPTION ===');
                    console.log('Index:', programmerIndex);
                    console.log('Initial state:', initialState);
                    
                    // Call selectOption
                    roleCombo.selectOption(programmerIndex);
                    
                    console.log('=== SELECTOPTION COMPLETED ===');
                    console.log('Callback triggered:', callbackTriggered);
                    
                    return {
                        success: 'selectOption called',
                        index: programmerIndex,
                        initialState: initialState,
                        finalState: {
                            selectedIndex: roleCombo.selectedIndex,
                            selectedOption: roleCombo.selectedOption
                        },
                        callbackTriggered: callbackTriggered
                    };
                } else {
                    return { error: 'Programmer option not found' };
                }
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Direct selectOption result: {result}")
        
        # Get browser console logs
        logs = self.driver.get_log('browser')
        execution_logs = [log for log in logs if 'SELECTOPTION' in log.get('message', '') or 'CALLBACK' in log.get('message', '')]
        print(f"Execution logs: {execution_logs}")
        
        # The test passes if selectOption was called and callback was triggered
        assert result.get('success') == 'selectOption called', "selectOption not called"
        assert result.get('callbackTriggered') == True, "Callback not triggered during selectOption"
