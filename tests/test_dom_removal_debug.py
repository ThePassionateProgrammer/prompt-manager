"""
Debug test to check if DOM removal is working.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestDomRemovalDebug:
    """Debug DOM removal functionality."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_dom_removal_debug(self):
        """Debug if DOM removal is working."""
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
        combo2_input = inputs[1]    # [2]
        
        print("Setup: Create initial state")
        
        # Add "a" to [1] and select it
        combo1_input.click()
        combo1_input.send_keys("a")
        combo1_input.send_keys(Keys.RETURN)
        time.sleep(1)
        self.driver.execute_script("""
            const option = document.querySelector('[data-value="a"]');
            if (option) option.click();
        """)
        time.sleep(1)
        
        # Add "x" to [2]
        combo2_input.click()
        combo2_input.send_keys("x")
        combo2_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check initial state
        combo2_options = self.driver.execute_script("""
            const combo2 = document.querySelectorAll('.combo-box-container')[1];
            const options = combo2.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
        print(f"[2] options before: {combo2_options}")
        
        print("Step 1: Manually test DOM removal")
        
        # Manually test DOM removal
        removal_result = self.driver.execute_script("""
            const combo2 = document.querySelectorAll('.combo-box-container')[1];
            const childOptions = combo2.querySelectorAll('.combo-box-option');
            
            console.log('Before removal:');
            console.log('Number of options:', childOptions.length);
            Array.from(childOptions).forEach((opt, i) => {
                console.log(`Option ${i}:`, opt.textContent);
            });
            
            // Clear child combo box options (keep first option)
            for (let j = childOptions.length - 1; j > 0; j--) {
                console.log(`Removing option ${j}:`, childOptions[j].textContent);
                childOptions[j].remove();
            }
            
            // Check after removal
            const optionsAfter = combo2.querySelectorAll('.combo-box-option');
            console.log('After removal:');
            console.log('Number of options:', optionsAfter.length);
            Array.from(optionsAfter).forEach((opt, i) => {
                console.log(`Option ${i}:`, opt.textContent);
            });
            
            return {
                before_count: childOptions.length,
                after_count: optionsAfter.length,
                before_texts: Array.from(childOptions).map(opt => opt.textContent),
                after_texts: Array.from(optionsAfter).map(opt => opt.textContent)
            };
        """)
        
        print(f"Removal result: {removal_result}")
        
        # Check if removal worked
        if removal_result['after_count'] == 1 and removal_result['after_texts'] == ['Add...']:
            print("✅ DOM removal is working!")
        else:
            print("❌ DOM removal is not working!")
            print(f"Expected 1 option with 'Add...', got {removal_result['after_count']} options: {removal_result['after_texts']}")
        
        # The test passes if we can see what's happening
        assert True, "Debug test completed - check output above"
