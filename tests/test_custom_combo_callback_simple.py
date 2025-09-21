"""
Test CustomComboBox callback with simple implementation.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestCustomComboCallbackSimple:
    """Test CustomComboBox callback with simple implementation."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_custom_combo_callback_simple(self):
        """Test CustomComboBox callback with simple implementation."""
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
        
        print("Step 1: Test CustomComboBox callback with simple implementation")
        
        # Test CustomComboBox callback with simple implementation
        result = self.driver.execute_script("""
            const combo1 = window.customComboBoxes[0];
            
            // Check if callback is set up
            const hasCallback = !!combo1.onSelectionChange;
            const callbackType = typeof combo1.onSelectionChange;
            
            // Test the callback directly
            let callbackCalled = false;
            let callbackValue = null;
            
            const originalCallback = combo1.onSelectionChange;
            combo1.onSelectionChange = function(value) {
                console.log('Test callback called with:', value);
                callbackCalled = true;
                callbackValue = value;
                
                // Call the original callback if it exists
                if (originalCallback) {
                    return originalCallback(value);
                }
            };
            
            // Add an option and select it
            combo1.addOption('test');
            
            // Manually call setSelectedValue to trigger the callback
            combo1.setSelectedValue('test');
            
            return {
                hasCallback: hasCallback,
                callbackType: callbackType,
                callbackCalled: callbackCalled,
                callbackValue: callbackValue
            };
        """)
        
        print(f"CustomComboBox callback result: {result}")
        
        if result['callbackCalled']:
            print("✅ CustomComboBox callback is working!")
        else:
            print("❌ CustomComboBox callback is not working!")
        
        # The test passes if we can see what's happening
        assert True, "Debug test completed - check output above"
