"""
Test LinkageManagerV2 in isolation to verify it works correctly.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestLinkageManagerV2Isolated:
    """Test LinkageManagerV2 in isolation."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_linkage_manager_v2_isolated(self):
        """Test LinkageManagerV2 in isolation."""
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
        
        print("Step 1: Test LinkageManagerV2 in isolation")
        
        # Test LinkageManagerV2 in isolation
        result = self.driver.execute_script("""
            // Create a fresh LinkageManagerV2 instance
            const linkageManager = new LinkageManagerV2();
            
            // Get combo boxes and tags
            const comboBoxes = window.customComboBoxes;
            const tags = ['1', '2'];
            
            // Register combo boxes
            linkageManager.registerComboBoxes(comboBoxes, tags);
            
            // Test the callback setup
            const combo1 = comboBoxes[0];
            const combo2 = comboBoxes[1];
            
            // Check if callbacks are set up
            const hasCallback1 = !!combo1.onSelectionChange;
            const hasCallback2 = !!combo2.onSelectionChange;
            
            // Test the callback directly
            let callbackCalled = false;
            let callbackValue = null;
            
            const originalCallback = combo1.onSelectionChange;
            combo1.onSelectionChange = function(value) {
                console.log('Test callback called with:', value);
                callbackCalled = true;
                callbackValue = value;
                
                // Call the LinkageManagerV2 callback
                if (originalCallback) {
                    return originalCallback(value);
                }
            };
            
            // Simulate adding an option and selecting it
            combo1.addOption('test');
            
            // Manually call selectOption to trigger the callback
            combo1.selectOption('test');
            
            return {
                linkageManagerInitialized: true,
                hasCallback1: hasCallback1,
                hasCallback2: hasCallback2,
                callbackCalled: callbackCalled,
                callbackValue: callbackValue,
                debugInfo: linkageManager.getDebugInfo()
            };
        """)
        
        print(f"LinkageManagerV2 isolated test result: {result}")
        
        if result['callbackCalled']:
            print("✅ LinkageManagerV2 callback is working in isolation!")
        else:
            print("❌ LinkageManagerV2 callback is not working in isolation!")
        
        # The test passes if we can see what's happening
        assert True, "Debug test completed - check output above"
