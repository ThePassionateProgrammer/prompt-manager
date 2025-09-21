"""
Test the CORRECT linkage behavior as specified by the user.

Key Rules:
1. Linkages created on "Add..." only when parent has a selection
2. Linkages are permanent - once created, never changed  
3. Clicking parent items restores associated child linkages
4. Cascading behavior - children depend on their immediate parent
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestCorrectLinkageBehavior:
    """Test the correct linkage behavior."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_correct_linkage_creation_flow(self):
        """
        Test the correct linkage creation flow:
        1. Add "a" to [1] → No linkage (no parent selection)
        2. Select "a" in [1] → [1] = "a" selected
        3. Add "x" to [2] → Linkage: [1]="a" → [2]="x"
        4. Add "y" to [2] → Linkage: [1]="a" → [2]="x,y"
        5. Select "x" in [2] → [2] = "x" selected
        6. Add "z" to [3] → Linkage: [2]="x" → [3]="z"
        """
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
        
        print("Step 1: Add 'a' to [1] → Should create NO linkage")
        
        # Add "a" to [1]
        combo1_input.click()
        combo1_input.send_keys("a")
        combo1_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check that no linkage was created
        linkage_data = self.driver.execute_script("return window.linkageData;")
        print(f"Linkage data after adding 'a' to [1]: {linkage_data}")
        assert linkage_data == {}, "No linkage should be created when parent has no selection"
        
        print("Step 2: Select 'a' in [1]")
        
        # Select "a" in [1]
        self.driver.execute_script("""
            const option = document.querySelector('[data-value="a"]');
            if (option) option.click();
        """)
        time.sleep(1)
        
        # Verify [1] is selected
        combo1_value = combo1_input.get_attribute('value')
        assert combo1_value == "a", f"Expected [1] to be 'a', got '{combo1_value}'"
        
        print("Step 3: Add 'x' to [2] → Should create linkage [1]='a' → [2]='x'")
        
        # Add "x" to [2]
        combo2_input.click()
        combo2_input.send_keys("x")
        combo2_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check that linkage was created
        linkage_data = self.driver.execute_script("return window.linkageData;")
        print(f"Linkage data after adding 'x' to [2]: {linkage_data}")
        
        # Should have linkage: "a" -> "2": ["x"]
        assert "a" in linkage_data, "Linkage should be created for parent 'a'"
        assert "2" in linkage_data["a"], "Linkage should be created for child '2'"
        assert "x" in linkage_data["a"]["2"], "Linkage should contain 'x'"
        
        print("Step 4: Add 'y' to [2] → Should add to existing linkage")
        
        # Add "y" to [2]
        combo2_input.click()
        combo2_input.send_keys("y")
        combo2_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check that linkage was updated
        linkage_data = self.driver.execute_script("return window.linkageData;")
        print(f"Linkage data after adding 'y' to [2]: {linkage_data}")
        
        # Should have linkage: "a" -> "2": ["x", "y"]
        assert "x" in linkage_data["a"]["2"], "Linkage should still contain 'x'"
        assert "y" in linkage_data["a"]["2"], "Linkage should now contain 'y'"
        
        print("Step 5: Select 'x' in [2]")
        
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
        
        # Verify [2] is selected
        combo2_value = combo2_input.get_attribute('value')
        assert combo2_value == "x", f"Expected [2] to be 'x', got '{combo2_value}'"
        
        print("Step 6: Add 'z' to [3] → Should create linkage [2]='x' → [3]='z'")
        
        # Add "z" to [3]
        combo3_input.click()
        combo3_input.send_keys("z")
        combo3_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check that linkage was created
        linkage_data = self.driver.execute_script("return window.linkageData;")
        print(f"Linkage data after adding 'z' to [3]: {linkage_data}")
        
        # Should have linkage: "x" -> "3": ["z"]
        assert "x" in linkage_data, "Linkage should be created for parent 'x'"
        assert "3" in linkage_data["x"], "Linkage should be created for child '3'"
        assert "z" in linkage_data["x"]["3"], "Linkage should contain 'z'"
        
        print("✅ Correct linkage creation flow test passed!")
    
    def test_linkage_restoration_flow(self):
        """
        Test linkage restoration when switching parent selections:
        1. Setup: [1]="a" → [2]="x,y", [2]="x" → [3]="z"
        2. Select "b" in [1] → [2] and [3] should be cleared
        3. Add "w" to [2] → Linkage: [1]="b" → [2]="w"
        4. Select "a" in [1] → [2] should restore to "x,y", [3] cleared
        5. Select "x" in [2] → [3] should restore to "z"
        """
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
        
        # Setup initial linkages: [1]="a" → [2]="x,y", [2]="x" → [3]="z"
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
        
        # Add "x" and "y" to [2]
        combo2_input.click()
        combo2_input.send_keys("x")
        combo2_input.send_keys(Keys.RETURN)
        time.sleep(1)
        combo2_input.click()
        combo2_input.send_keys("y")
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
        
        print("Step 1: Add 'b' to [1] and select it")
        
        # Add "b" to [1] and select it
        combo1_input.click()
        combo1_input.send_keys("b")
        combo1_input.send_keys(Keys.RETURN)
        time.sleep(1)
        # Select "b" in [1] and check if callback is triggered
        self.driver.execute_script("""
            // Clear console logs
            console.clear();
            
            const options = document.querySelectorAll('[data-value="b"]');
            for (let option of options) {
                if (option.closest('.combo-box-container') === document.querySelectorAll('.combo-box-container')[0]) {
                    option.click();
                    break;
                }
            }
        """)
        time.sleep(2)  # Give more time for callback to execute
        
        # Check console logs for August 20th implementation
        logs = self.driver.get_log('browser')
        linkage_logs = [log for log in logs if 'LINKAGE CALLBACK TRIGGERED' in log['message']]
        setup_logs = [log for log in logs if 'SETTING UP LINKAGES' in log['message']]
        print(f"Linkage callback logs found: {len(linkage_logs)}")
        print(f"Setup logs found: {len(setup_logs)}")
        
        # Print all logs for debugging
        print("All console logs:")
        for log in logs:
            if any(keyword in log['message'] for keyword in ['LINKAGE', 'SETTING UP', 'linkage', 'ERROR', 'callback']):
                print(f"  {log['level']}: {log['message']}")
        
        for log in linkage_logs:
            print(f"  {log['level']}: {log['message']}")
        
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
        
        print("Step 2: Add 'w' to [2] → Should create linkage [1]='b' → [2]='w'")
        
        # Add "w" to [2]
        combo2_input.click()
        combo2_input.send_keys("w")
        combo2_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check linkage data
        linkage_data = self.driver.execute_script("return window.linkageData;")
        print(f"Linkage data after adding 'w' to [2]: {linkage_data}")
        
        # Should have linkage: "b" -> "2": ["w"]
        assert "b" in linkage_data, "Linkage should be created for parent 'b'"
        assert "2" in linkage_data["b"], "Linkage should be created for child '2'"
        assert "w" in linkage_data["b"]["2"], "Linkage should contain 'w'"
        
        print("Step 3: Select 'a' in [1] → [2] should restore to 'x,y', [3] cleared")
        
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
        
        # Check that [2] restored to "x,y"
        combo2_options = self.driver.execute_script("""
            const combo2 = document.querySelectorAll('.combo-box-container')[1];
            const options = combo2.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
        print(f"[2] options after selecting 'a': {combo2_options}")
        
        # Should have "Add...", "x", "y"
        assert "x" in combo2_options, "Should restore 'x' to [2]"
        assert "y" in combo2_options, "Should restore 'y' to [2]"
        
        print("Step 4: Select 'x' in [2] → [3] should restore to 'z'")
        
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
        
        # Check that [3] restored to "z"
        combo3_options = self.driver.execute_script("""
            const combo3 = document.querySelectorAll('.combo-box-container')[2];
            const options = combo3.querySelectorAll('.combo-box-option');
            return Array.from(options).map(opt => opt.textContent);
        """)
        print(f"[3] options after selecting 'x': {combo3_options}")
        
        # Should have "Add...", "z"
        assert "z" in combo3_options, "Should restore 'z' to [3]"
        
        print("✅ Linkage restoration flow test passed!")
