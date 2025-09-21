"""
Debug test to check if the clearing logic in the callback is working.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestClearingLogicDebug:
    """Debug clearing logic in callback."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_clearing_logic_debug(self):
        """Debug if the clearing logic in the callback is working."""
        # Enter template
        template_input = self.driver.find_element(By.ID, "templateInput")
        template_input.send_keys("[1][2][3]")
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
        combo3_input = inputs[2]    # [3]
        
        print("Setup: Create initial linkages")
        
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
        
        # Select "x" in [2]
        self.driver.execute_script("""
            const options = document.querySelectorAll('[data-value="x"]');
            for (let option of options) {
                if (option.closest('.combo-box-container') === document.querySelectorAll('.combo-box-container')[1]) {
                    option.click();
                    break;
                }
            }
        """)
        time.sleep(1)
        
        # Add "z" to [3]
        combo3_input.click()
        combo3_input.send_keys("z")
        combo3_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check initial state
        print("Initial state:")
        combo2_options = self.driver.execute_script("""
            const combo2 = document.querySelectorAll('.combo-box-container')[1];
            const options = combo2.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
        combo3_options = self.driver.execute_script("""
            const combo3 = document.querySelectorAll('.combo-box-container')[2];
            const options = combo3.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
        print(f"[2] options: {combo2_options}")
        print(f"[3] options: {combo3_options}")
        
        # Check linkage data
        linkage_data = self.driver.execute_script("return window.linkageData;")
        print(f"Linkage data: {linkage_data}")
        
        print("Step 1: Add 'b' to [1] and select it")
        
        # Add "b" to [1] and select it
        combo1_input.click()
        combo1_input.send_keys("b")
        combo1_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Select "b" in [1] and monitor the clearing process
        result = self.driver.execute_script("""
            // Store the options before selection
            const combo2_before = document.querySelectorAll('.combo-box-container')[1];
            const combo2_options_before = combo2_before.querySelectorAll('.combo-box-option');
            const combo2_options_before_text = Array.from(combo2_options_before).map(opt => opt.textContent);
            
            const combo3_before = document.querySelectorAll('.combo-box-container')[2];
            const combo3_options_before = combo3_before.querySelectorAll('.combo-box-option');
            const combo3_options_before_text = Array.from(combo3_options_before).map(opt => opt.textContent);
            
            // Select "b" in [1]
            const options = document.querySelectorAll('[data-value="b"]');
            for (let option of options) {
                if (option.closest('.combo-box-container') === document.querySelectorAll('.combo-box-container')[0]) {
                    option.click();
                    break;
                }
            }
            
            // Wait a moment for the callback to execute
            setTimeout(() => {
                // Store the options after selection
                const combo2_after = document.querySelectorAll('.combo-box-container')[1];
                const combo2_options_after = combo2_after.querySelectorAll('.combo-box-option');
                const combo2_options_after_text = Array.from(combo2_options_after).map(opt => opt.textContent);
                
                const combo3_after = document.querySelectorAll('.combo-box-container')[2];
                const combo3_options_after = combo3_after.querySelectorAll('.combo-box-option');
                const combo3_options_after_text = Array.from(combo3_options_after).map(opt => opt.textContent);
                
                window.clearing_result = {
                    combo2_before: combo2_options_before_text,
                    combo2_after: combo2_options_after_text,
                    combo3_before: combo3_options_before_text,
                    combo3_after: combo3_options_after_text
                };
            }, 100);
            
            return {
                combo2_before: combo2_options_before_text,
                combo3_before: combo3_options_before_text
            };
        """)
        
        time.sleep(2)  # Wait for the callback to execute
        
        # Get the clearing result
        clearing_result = self.driver.execute_script("return window.clearing_result;")
        print(f"Clearing result: {clearing_result}")
        
        # Check if clearing worked
        combo2_cleared = clearing_result['combo2_after'] == ['Add...']
        combo3_cleared = clearing_result['combo3_after'] == ['Add...']
        
        print(f"[2] cleared: {combo2_cleared}")
        print(f"[3] cleared: {combo3_cleared}")
        
        if not combo2_cleared or not combo3_cleared:
            print("❌ Clearing logic is not working!")
            print(f"Expected [2] to be ['Add...'], got {clearing_result['combo2_after']}")
            print(f"Expected [3] to be ['Add...'], got {clearing_result['combo3_after']}")
        else:
            print("✅ Clearing logic is working!")
        
        # The test passes if we can see what's happening
        assert True, "Debug test completed - check output above"
