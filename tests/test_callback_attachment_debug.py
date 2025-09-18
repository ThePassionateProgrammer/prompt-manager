"""
Test callback attachment to debug why callbacks aren't being triggered when clicking options.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestCallbackAttachmentDebug:
    """Test callback attachment debugging."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_callback_attachment_debug(self):
        """
        Test callback attachment to debug the issue.
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
        
        # Test callback attachment and execution
        result = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                
                // Check callback attachment
                const callbackInfo = {
                    hasCallback: !!roleCombo.onSelectionChange,
                    callbackType: typeof roleCombo.onSelectionChange,
                    callbackFunction: roleCombo.onSelectionChange ? 'exists' : 'missing'
                };
                
                // Monitor callback execution during selectOption
                let callbackExecuted = false;
                let callbackError = null;
                
                const originalCallback = roleCombo.onSelectionChange;
                if (originalCallback) {
                    roleCombo.onSelectionChange = function(value) {
                        callbackExecuted = true;
                        console.log('=== CALLBACK EXECUTED IN TEST ===', value);
                        try {
                            originalCallback(value);
                        } catch (error) {
                            callbackError = error.message;
                            console.error('=== CALLBACK ERROR IN TEST ===', error);
                        }
                    };
                }
                
                // Test direct selectOption call
                console.log('=== TESTING DIRECT SELECTOPTION ===');
                roleCombo.selectOption(1); // Should select Programmer
                
                const directCallResult = {
                    callbackExecuted: callbackExecuted,
                    callbackError: callbackError,
                    selectedOption: roleCombo.selectedOption
                };
                
                // Reset for click test
                callbackExecuted = false;
                callbackError = null;
                
                // Test clicking on option
                const options = roleCombo.options;
                let programmerOption = null;
                for (let i = 0; i < options.length; i++) {
                    if (options[i].textContent === 'Programmer') {
                        programmerOption = options[i];
                        break;
                    }
                }
                
                if (programmerOption) {
                    console.log('=== TESTING CLICK ON OPTION ===');
                    programmerOption.click();
                }
                
                const clickResult = {
                    callbackExecuted: callbackExecuted,
                    callbackError: callbackError,
                    selectedOption: roleCombo.selectedOption
                };
                
                return {
                    callbackInfo: callbackInfo,
                    directCallResult: directCallResult,
                    clickResult: clickResult
                };
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Callback attachment debug result: {result}")
        
        # The test passes if we can see what's happening with the callbacks
        assert result.get('callbackInfo', {}).get('hasCallback') == True, "No callback attached"
        
        # Check direct call result
        directResult = result.get('directCallResult', {})
        if directResult.get('callbackExecuted'):
            print("✅ Callback executed during direct selectOption call")
        else:
            print("❌ Callback NOT executed during direct selectOption call")
            
        # Check click result
        clickResult = result.get('clickResult', {})
        if clickResult.get('callbackExecuted'):
            print("✅ Callback executed during option click")
        else:
            print("❌ Callback NOT executed during option click")
            
        # Check for errors
        if directResult.get('callbackError'):
            print(f"❌ Direct call callback error: {directResult.get('callbackError')}")
        if clickResult.get('callbackError'):
            print(f"❌ Click callback error: {clickResult.get('callbackError')}")
