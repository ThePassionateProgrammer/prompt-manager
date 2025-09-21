"""
Debug test to understand why linkage restoration isn't working.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestDebugLinkageRestoration:
    """Debug linkage restoration issue."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_debug_linkage_restoration(self):
        """Debug why linkage restoration isn't working."""
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
        combo1_options = self.driver.execute_script("""
            const combo1 = document.querySelectorAll('.combo-box-container')[0];
            const options = combo1.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
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
        print(f"[1] options: {combo1_options}")
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
        
        # Check state before selecting "b"
        print("Before selecting 'b':")
        combo2_options_before = self.driver.execute_script("""
            const combo2 = document.querySelectorAll('.combo-box-container')[1];
            const options = combo2.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
        combo3_options_before = self.driver.execute_script("""
            const combo3 = document.querySelectorAll('.combo-box-container')[2];
            const options = combo3.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
        print(f"[2] options before: {combo2_options_before}")
        print(f"[3] options before: {combo3_options_before}")
        
        # Select "b" in [1]
        self.driver.execute_script("""
            const options = document.querySelectorAll('[data-value="b"]');
            for (let option of options) {
                if (option.closest('.combo-box-container') === document.querySelectorAll('.combo-box-container')[0]) {
                    option.click();
                    break;
                }
            }
        """)
        time.sleep(2)  # Give more time for the callback to execute
        
        # Check state after selecting "b"
        print("After selecting 'b':")
        combo2_options_after = self.driver.execute_script("""
            const combo2 = document.querySelectorAll('.combo-box-container')[1];
            const options = combo2.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
        combo3_options_after = self.driver.execute_script("""
            const combo3 = document.querySelectorAll('.combo-box-container')[2];
            const options = combo3.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
        print(f"[2] options after: {combo2_options_after}")
        print(f"[3] options after: {combo3_options_after}")
        
        # Check if callback was triggered
        callback_triggered = self.driver.execute_script("""
            // Check if there are any console logs about linkage callbacks
            return window.console && window.console.logs ? window.console.logs : 'No console logs available';
        """)
        print(f"Console logs: {callback_triggered}")
        
        # The test passes if we can see what's happening
        assert True, "Debug test completed - check output above"
