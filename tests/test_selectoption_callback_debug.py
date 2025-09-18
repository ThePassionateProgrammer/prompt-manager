"""
Test selectOption method callback triggering to debug why callbacks aren't being triggered.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestSelectOptionCallbackDebug:
    """Test selectOption method callback triggering."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_selectoption_callback_debug(self):
        """
        Test selectOption method callback triggering to debug the issue.
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
        
        # Test the selectOption method directly with callback monitoring
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
                    // Monitor callback execution
                    let callbackExecuted = false;
                    let callbackError = null;
                    
                    const originalCallback = roleCombo.onSelectionChange;
                    roleCombo.onSelectionChange = function(value) {
                        callbackExecuted = true;
                        console.log('=== CALLBACK EXECUTED ===', value);
                        if (originalCallback) {
                            try {
                                originalCallback(value);
                            } catch (error) {
                                callbackError = error.message;
                                console.error('=== CALLBACK ERROR ===', error);
                            }
                        }
                    };
                    
                    console.log('=== TESTING SELECTOPTION WITH CALLBACK MONITORING ===');
                    console.log('Programmer index:', programmerIndex);
                    console.log('Callback function exists:', !!roleCombo.onSelectionChange);
                    console.log('Callback function:', roleCombo.onSelectionChange);
                    
                    // Store initial state
                    const initialState = {
                        selectedIndex: roleCombo.selectedIndex,
                        selectedOption: roleCombo.selectedOption
                    };
                    
                    // Call selectOption
                    roleCombo.selectOption(programmerIndex);
                    
                    // Store final state
                    const finalState = {
                        selectedIndex: roleCombo.selectedIndex,
                        selectedOption: roleCombo.selectedOption
                    };
                    
                    return {
                        success: 'selectOption called',
                        programmerIndex: programmerIndex,
                        hasCallback: !!originalCallback,
                        callbackExecuted: callbackExecuted,
                        callbackError: callbackError,
                        initialState: initialState,
                        finalState: finalState
                    };
                } else {
                    return { error: 'Programmer option not found' };
                }
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"SelectOption callback debug result: {result}")
        
        # The test passes if we can see what's happening with the callback
        assert result.get('success') == 'selectOption called', "selectOption not called"
        assert result.get('hasCallback') == True, "No callback function attached"
        
        # Check if callback was executed
        if result.get('callbackExecuted'):
            print("✅ Callback was executed successfully")
        else:
            print("❌ Callback was NOT executed")
            
        # Check for callback errors
        if result.get('callbackError'):
            print(f"❌ Callback error: {result.get('callbackError')}")
        
        # Verify selection state
        assert result.get('finalState', {}).get('selectedOption') == 'Programmer', "Wrong option selected"
