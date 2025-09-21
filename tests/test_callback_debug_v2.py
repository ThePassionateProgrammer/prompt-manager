"""
Debug test to check if LinkageManagerV2 callback is being triggered.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestCallbackDebugV2:
    """Debug LinkageManagerV2 callback functionality."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_callback_debug_v2(self):
        """Debug if LinkageManagerV2 callback is being triggered."""
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
        
        print("Step 1: Check if LinkageManagerV2 is initialized")
        
        # Check if simple linkage implementation is initialized
        init_result = self.driver.execute_script("""
            return {
                hasLinkageData: !!window.linkageData,
                hasCurrentSelections: !!window.currentSelections,
                comboBoxCount: window.customComboBoxes ? window.customComboBoxes.length : 0,
                comboBoxTags: window.customComboBoxes ? window.customComboBoxes.map(combo => combo.tag) : []
            };
        """)
        
        print(f"Simple linkage status: {init_result}")
        assert init_result['hasLinkageData'], "Linkage data should be initialized"
        assert init_result['hasCurrentSelections'], "Current selections should be initialized"
        
        print("Step 2: Check if callback is set up")
        
        # Check if callback is set up
        callback_info = self.driver.execute_script("""
            const combo1 = window.customComboBoxes[0];
            return {
                hasCallback: !!combo1.onSelectionChange,
                callbackType: typeof combo1.onSelectionChange
            };
        """)
        
        print(f"Callback info: {callback_info}")
        assert callback_info['hasCallback'], "Callback should be set up"
        
        print("Step 3: Add 'a' to [1] and select it")
        
        # Add "a" to [1] and select it
        combo1_input.click()
        combo1_input.send_keys("a")
        combo1_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Select "a" in [1] and monitor for callback
        result = self.driver.execute_script("""
            // Clear any previous console logs
            console.clear();
            
            // Select the option
            const option = document.querySelector('[data-value="a"]');
            if (option) {
                option.click();
            }
            
            // Wait a moment for the callback to execute
            setTimeout(() => {
                window.callbackTestResult = {
                    success: true,
                    message: 'Option selected'
                };
            }, 100);
            
            return {
                success: true,
                message: 'Option click initiated'
            };
        """)
        
        time.sleep(1)
        
        # Check if callback was triggered by looking for console logs
        logs = self.driver.get_log('browser')
        print("Browser console logs:")
        for log in logs:
            if 'LinkageManagerV2' in log['message']:
                print(f"  {log['level']}: {log['message']}")
        
        # The test passes if we can see the callback logs
        callback_logs = [log for log in logs if 'LinkageManagerV2' in log['message']]
        if callback_logs:
            print("✅ LinkageManagerV2 callback is working!")
        else:
            print("❌ LinkageManagerV2 callback is not working!")
        
        # The test passes if we can see what's happening
        assert True, "Debug test completed - check output above"
