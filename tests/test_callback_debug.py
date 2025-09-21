"""
Debug test to check if the onSelectionChange callback is working.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestCallbackDebug:
    """Debug callback functionality."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_callback_debug(self):
        """Debug if the onSelectionChange callback is working."""
        # Enter template
        template_input = self.driver.find_element(By.ID, "templateInput")
        template_input.send_keys("[1][2]")
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
        combo1_input = inputs[0]    # [1]
        
        print("Step 1: Check if callback is set up")
        
        # Check if callback is set up
        callback_info = self.driver.execute_script("""
            const combo1 = window.customComboBoxes[0];
            return {
                hasCallback: !!combo1.onSelectionChange,
                callbackType: typeof combo1.onSelectionChange,
                callbackFunction: combo1.onSelectionChange ? combo1.onSelectionChange.toString().substring(0, 100) : null
            };
        """)
        print(f"Callback info: {callback_info}")
        
        # Add "a" to [1] and select it
        combo1_input.click()
        combo1_input.send_keys("a")
        combo1_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        print("Step 2: Select 'a' and check if callback is triggered")
        
        # Select "a" in [1] and monitor for callback
        result = self.driver.execute_script("""
            // Add a flag to track if callback was called
            window.callbackCalled = false;
            window.callbackValue = null;
            
            // Store original callback
            const originalCallback = window.customComboBoxes[0].onSelectionChange;
            
            // Wrap the callback to track calls
            window.customComboBoxes[0].onSelectionChange = function(value) {
                console.log('Callback wrapper called with:', value);
                window.callbackCalled = true;
                window.callbackValue = value;
                if (originalCallback) {
                    return originalCallback(value);
                }
            };
            
            // Select the option
            const option = document.querySelector('[data-value="a"]');
            if (option) {
                option.click();
            }
            
            return {
                callbackWasCalled: window.callbackCalled,
                callbackValue: window.callbackValue
            };
        """)
        time.sleep(1)
        
        print(f"Callback result: {result}")
        
        # Check if callback was called
        assert result['callbackWasCalled'], f"Callback should have been called, got {result}"
        assert result['callbackValue'] == 'a', f"Callback should have been called with 'a', got {result['callbackValue']}"
        
        print("✅ Callback is working correctly!")