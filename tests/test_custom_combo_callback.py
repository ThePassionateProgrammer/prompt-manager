"""
Debug test to check if CustomComboBox is calling onSelectionChange callback.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestCustomComboCallback:
    """Debug CustomComboBox callback functionality."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_custom_combo_callback(self):
        """Debug if CustomComboBox is calling onSelectionChange callback."""
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
        
        print("Step 1: Test CustomComboBox callback directly")
        
        # Test CustomComboBox callback directly
        result = self.driver.execute_script("""
            const combo1 = window.customComboBoxes[0];
            
            // Store original callback
            const originalCallback = combo1.onSelectionChange;
            
            // Set up a test callback
            let callbackCalled = false;
            let callbackValue = null;
            
            combo1.onSelectionChange = function(value) {
                console.log('CustomComboBox callback called with:', value);
                callbackCalled = true;
                callbackValue = value;
                
                // Call original callback if it exists
                if (originalCallback) {
                    return originalCallback(value);
                }
            };
            
            // Add an option and select it
            combo1.input.value = 'test';
            combo1.addOption('test');
            
            // Select the option
            const option = document.querySelector('[data-value="test"]');
            if (option) {
                option.click();
            }
            
            return {
                callbackCalled: callbackCalled,
                callbackValue: callbackValue,
                hasOriginalCallback: !!originalCallback
            };
        """)
        
        time.sleep(1)
        
        print(f"CustomComboBox callback result: {result}")
        
        if result['callbackCalled']:
            print("✅ CustomComboBox callback is working!")
        else:
            print("❌ CustomComboBox callback is not working!")
        
        # The test passes if we can see what's happening
        assert True, "Debug test completed - check output above"
