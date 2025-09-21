"""
Test the new LinkageManagerV2 implementation.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestLinkageManagerV2:
    """Test the new LinkageManagerV2 implementation."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_linkage_manager_v2_basic_functionality(self):
        """Test basic LinkageManagerV2 functionality."""
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
        
        print("Step 1: Check if LinkageManagerV2 is already initialized")
        
        # Check if LinkageManagerV2 is already initialized by the Template Builder
        init_result = self.driver.execute_script("""
            // Check if LinkageManagerV2 is already initialized
            if (window.linkageManagerV2) {
                return {
                    success: true,
                    comboBoxCount: window.customComboBoxes.length,
                    tags: window.customComboBoxes.map(combo => combo.tag),
                    debugInfo: window.linkageManagerV2.getDebugInfo()
                };
            } else {
                return {
                    success: false,
                    error: 'LinkageManagerV2 not initialized by Template Builder'
                };
            }
        """)
        
        print(f"LinkageManagerV2 status: {init_result}")
        assert init_result['success'], f"LinkageManagerV2 should be initialized by Template Builder, got {init_result}"
        
        print("Step 2: Test linkage creation flow")
        
        # Get combo box inputs
        inputs = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-input")
        combo1_input = inputs[0]    # [1]
        combo2_input = inputs[1]    # [2]
        combo3_input = inputs[2]    # [3]
        
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
        
        # Check that no linkage was created yet
        linkage_data = self.driver.execute_script("return window.linkageManagerV2.getDebugInfo().linkageData;")
        print(f"Linkage data after adding 'a' to [1]: {linkage_data}")
        assert linkage_data == {}, "No linkage should be created when parent has no selection"
        
        # Add "x" to [2] - this should create a linkage
        combo2_input.click()
        combo2_input.send_keys("x")
        combo2_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check that linkage was created
        linkage_data = self.driver.execute_script("return window.linkageManagerV2.getDebugInfo().linkageData;")
        print(f"Linkage data after adding 'x' to [2]: {linkage_data}")
        
        # Should have linkage: "a" -> "2": ["x"]
        assert "a" in linkage_data, "Linkage should be created for parent 'a'"
        assert "2" in linkage_data["a"], "Linkage should be created for child '2'"
        assert "x" in linkage_data["a"]["2"], "Linkage should contain 'x'"
        
        print("Step 3: Test linkage restoration")
        
        # Add "b" to [1] and select it
        combo1_input.click()
        combo1_input.send_keys("b")
        combo1_input.send_keys(Keys.RETURN)
        time.sleep(1)
        self.driver.execute_script("""
            const options = document.querySelectorAll('[data-value="b"]');
            for (let option of options) {
                if (option.closest('.combo-box-container') === document.querySelectorAll('.combo-box-container')[0]) {
                    option.click();
                    break;
                }
            }
        """)
        time.sleep(1)
        
        # Check that [2] and [3] are cleared
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
        
        print(f"[2] options after selecting 'b': {combo2_options}")
        print(f"[3] options after selecting 'b': {combo3_options}")
        
        # Should only have "Add..." option
        assert combo2_options == ["Add..."], f"Expected [2] to be cleared, got {combo2_options}"
        assert combo3_options == ["Add..."], f"Expected [3] to be cleared, got {combo3_options}"
        
        print("Step 4: Test linkage restoration when switching back")
        
        # Select "a" in [1] - should restore [2] linkage
        self.driver.execute_script("""
            const options = document.querySelectorAll('[data-value="a"]');
            for (let option of options) {
                if (option.closest('.combo-box-container') === document.querySelectorAll('.combo-box-container')[0]) {
                    option.click();
                    break;
                }
            }
        """)
        time.sleep(1)
        
        # Check that [2] is restored
        combo2_options = self.driver.execute_script("""
            const combo2 = document.querySelectorAll('.combo-box-container')[1];
            const options = combo2.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
        
        print(f"[2] options after selecting 'a': {combo2_options}")
        
        # Should have "Add..." and "x"
        assert "Add..." in combo2_options, "[2] should have 'Add...' option"
        assert "x" in combo2_options, "[2] should restore 'x' option"
        
        print("✅ LinkageManagerV2 basic functionality test passed!")
    
    def test_linkage_manager_v2_cascading_behavior(self):
        """Test cascading linkage behavior."""
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
        
        # Initialize LinkageManagerV2
        self.driver.execute_script("""
            window.linkageManagerV2 = new LinkageManagerV2();
            const comboBoxes = window.customComboBoxes;
            const tags = ['1', '2', '3'];
            window.linkageManagerV2.registerComboBoxes(comboBoxes, tags);
        """)
        time.sleep(1)
        
        # Get combo box inputs
        inputs = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-input")
        combo1_input = inputs[0]    # [1]
        combo2_input = inputs[1]    # [2]
        combo3_input = inputs[2]    # [3]
        
        print("Setup: Create 3-level linkage [1]='a' → [2]='x' → [3]='z'")
        
        # Create 3-level linkage: [1]="a" → [2]="x" → [3]="z"
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
        
        # Add "x" to [2] and select it
        combo2_input.click()
        combo2_input.send_keys("x")
        combo2_input.send_keys(Keys.RETURN)
        time.sleep(1)
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
        
        # Check linkage data
        linkage_data = self.driver.execute_script("return window.linkageManagerV2.getDebugInfo().linkageData;")
        print(f"Linkage data after setup: {linkage_data}")
        
        # Should have linkages: "a" → "2": ["x"], "x" → "3": ["z"]
        assert "a" in linkage_data, "Should have linkage for 'a'"
        assert "2" in linkage_data["a"], "Should have linkage 'a' → '2'"
        assert "x" in linkage_data["a"]["2"], "Should have 'x' in linkage 'a' → '2'"
        assert "x" in linkage_data, "Should have linkage for 'x'"
        assert "3" in linkage_data["x"], "Should have linkage 'x' → '3'"
        assert "z" in linkage_data["x"]["3"], "Should have 'z' in linkage 'x' → '3'"
        
        print("Step 1: Switch [1] to 'b' - should clear [2] and [3]")
        
        # Add "b" to [1] and select it
        combo1_input.click()
        combo1_input.send_keys("b")
        combo1_input.send_keys(Keys.RETURN)
        time.sleep(1)
        self.driver.execute_script("""
            const options = document.querySelectorAll('[data-value="b"]');
            for (let option of options) {
                if (option.closest('.combo-box-container') === document.querySelectorAll('.combo-box-container')[0]) {
                    option.click();
                    break;
                }
            }
        """)
        time.sleep(1)
        
        # Check that [2] and [3] are cleared
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
        
        print(f"[2] options after selecting 'b': {combo2_options}")
        print(f"[3] options after selecting 'b': {combo3_options}")
        
        assert combo2_options == ["Add..."], f"Expected [2] to be cleared, got {combo2_options}"
        assert combo3_options == ["Add..."], f"Expected [3] to be cleared, got {combo3_options}"
        
        print("Step 2: Switch back to [1]='a' - should restore [2]='x'")
        
        # Select "a" in [1]
        self.driver.execute_script("""
            const options = document.querySelectorAll('[data-value="a"]');
            for (let option of options) {
                if (option.closest('.combo-box-container') === document.querySelectorAll('.combo-box-container')[0]) {
                    option.click();
                    break;
                }
            }
        """)
        time.sleep(1)
        
        # Check that [2] is restored
        combo2_options = self.driver.execute_script("""
            const combo2 = document.querySelectorAll('.combo-box-container')[1];
            const options = combo2.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
        
        print(f"[2] options after selecting 'a': {combo2_options}")
        
        assert "Add..." in combo2_options, "[2] should have 'Add...' option"
        assert "x" in combo2_options, "[2] should restore 'x' option"
        
        print("Step 3: Select [2]='x' - should restore [3]='z'")
        
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
        
        # Check that [3] is restored
        combo3_options = self.driver.execute_script("""
            const combo3 = document.querySelectorAll('.combo-box-container')[2];
            const options = combo3.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
        
        print(f"[3] options after selecting 'x': {combo3_options}")
        
        assert "Add..." in combo3_options, "[3] should have 'Add...' option"
        assert "z" in combo3_options, "[3] should restore 'z' option"
        
        print("✅ LinkageManagerV2 cascading behavior test passed!")
