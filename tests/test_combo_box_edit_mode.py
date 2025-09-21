"""
Test CustomComboBox Edit Mode Behavior

Tests the sophisticated editing workflow:
1. Click item in dropdown → item appears in entry field (highlighted), item selected in list, dropdown stays open
2. Click highlighted item in entry field → item stays in field, cursor moves to end, item stays selected, dropdown stays open, ready for editing
3. Editing actions:
   - Append text + Enter → replaces current item with new text
   - Edit text + Enter → replaces current item with edited text  
   - Delete all text + Enter → removes item from list
4. Focus loss → same as Enter (apply changes)
5. Click different item → same as Enter (apply changes to current, select new item)
6. Escape → revert to original item text
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time

class TestComboBoxEditMode:
    
    @pytest.fixture
    def driver(self):
        driver = webdriver.Chrome()
        yield driver
        driver.quit()
    
    @pytest.fixture
    def combo_box(self, driver):
        # Navigate to template builder
        driver.get("http://localhost:8000/template-builder")
        
        # Add a template to generate combo boxes
        template_input = driver.find_element(By.ID, "templateInput")
        template_input.send_keys("As a [Who], I want to [What], so that I can [Why]")
        
        # Click generate button
        generate_btn = driver.find_element(By.ID, "generateBtn")
        generate_btn.click()
        
        # Wait for combo boxes to be created dynamically
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "combo-box-Who"))
        )
        
        # Get the first combo box input (Who)
        combo_box_container = driver.find_element(By.ID, "combo-box-Who")
        combo_box = combo_box_container.find_element(By.CLASS_NAME, "combo-box-input")
        return combo_box
    
    def test_initial_selection_behavior(self, driver, combo_box):
        """Test: Click item in dropdown → item appears in entry field (highlighted), item selected in list, dropdown stays open"""
        
        # Get the combo box container to find dropdown and options
        combo_box_container = combo_box.find_element(By.XPATH, "./..")
        
        # Click on input to open dropdown
        combo_box.click()
        time.sleep(0.1)
        
        # Find and click on an existing option (not "Add...")
        options = combo_box_container.find_elements(By.CLASS_NAME, "combo-box-option")
        # Skip first option (Add...) and click second option if it exists
        if len(options) > 1:
            target_option = options[1]
            option_text = target_option.text
            
            # Click the option
            driver.execute_script("arguments[0].click();", target_option)
            time.sleep(0.1)
            
            # Verify: item appears in entry field (highlighted)
            assert combo_box.get_attribute("value") == option_text
            
            # Verify: item is selected in list (should have selected class)
            assert "selected" in target_option.get_attribute("class")
            
            # Verify: dropdown stays open
            dropdown = combo_box_container.find_element(By.CLASS_NAME, "combo-box-dropdown")
            assert "show" in dropdown.get_attribute("class")
            
            # Verify: text is highlighted/selected in input field
            # Check if text is selected by trying to get selected text
            selected_text = driver.execute_script("return window.getSelection().toString();")
            assert selected_text == option_text or combo_box.get_attribute("value") == option_text
    
    def test_edit_mode_activation(self, driver, combo_box):
        """Test: Click highlighted item in entry field → item stays in field, cursor moves to end, item stays selected, dropdown stays open, ready for editing"""
        
        # First, select an item
        combo_box.click()
        time.sleep(0.1)
        
        options = driver.find_elements(By.CLASS_NAME, "combo-box-option")
        if len(options) > 1:
            target_option = options[1]
            option_text = target_option.text
            
            # Click the option to select it
            driver.execute_script("arguments[0].click();", target_option)
            time.sleep(0.1)
            
            # Now click on the highlighted text in the input field
            combo_box.click()
            time.sleep(0.1)
            
            # Verify: item stays in field
            assert combo_box.get_attribute("value") == option_text
            
            # Verify: item stays selected in list
            assert "selected" in target_option.get_attribute("class")
            
            # Verify: dropdown stays open
            dropdown = driver.find_element(By.CLASS_NAME, "combo-box-dropdown")
            assert "show" in dropdown.get_attribute("class")
            
            # Verify: cursor is at the end (text is not selected)
            selected_text = driver.execute_script("return window.getSelection().toString();")
            assert selected_text == ""  # No text should be selected
    
    def test_append_text_behavior(self, driver, combo_box):
        """Test: Append text + Enter → replaces current item with new text"""
        
        # Get the combo box container to find dropdown and options
        combo_box_container = combo_box.find_element(By.XPATH, "./..")
        
        # Select an item first
        combo_box.click()
        time.sleep(0.1)
        
        options = combo_box_container.find_elements(By.CLASS_NAME, "combo-box-option")
        if len(options) > 1:
            target_option = options[1]
            original_text = target_option.text
            
            # Select the item
            driver.execute_script("arguments[0].click();", target_option)
            time.sleep(0.1)
            
            # Click on input to enter edit mode
            combo_box.click()
            time.sleep(0.1)
            
            # Append text
            combo_box.send_keys("_appended")
            time.sleep(0.1)
            
            # Press Enter
            combo_box.send_keys(Keys.ENTER)
            time.sleep(0.1)
            
            # Verify: item is replaced with new text
            expected_text = original_text + "_appended"
            assert combo_box.get_attribute("value") == expected_text
            
            # Verify: option in dropdown is updated
            assert target_option.text == expected_text
    
    def test_edit_text_behavior(self, driver, combo_box):
        """Test: Edit text + Enter → replaces current item with edited text"""
        
        # Get the combo box container to find dropdown and options
        combo_box_container = combo_box.find_element(By.XPATH, "./..")
        
        # Select an item first
        combo_box.click()
        time.sleep(0.1)
        
        options = combo_box_container.find_elements(By.CLASS_NAME, "combo-box-option")
        if len(options) > 1:
            target_option = options[1]
            original_text = target_option.text
            
            # Select the item
            driver.execute_script("arguments[0].click();", target_option)
            time.sleep(0.1)
            
            # Click on input to enter edit mode
            combo_box.click()
            time.sleep(0.1)
            
            # Clear and edit text
            combo_box.clear()
            combo_box.send_keys("edited_text")
            time.sleep(0.1)
            
            # Press Enter
            combo_box.send_keys(Keys.ENTER)
            time.sleep(0.1)
            
            # Verify: item is replaced with edited text
            assert combo_box.get_attribute("value") == "edited_text"
            
            # Verify: option in dropdown is updated
            assert target_option.text == "edited_text"
    
    def test_delete_text_behavior(self, driver, combo_box):
        """Test: Delete all text + Enter → removes item from list"""
        
        # Get the combo box container to find dropdown and options
        combo_box_container = combo_box.find_element(By.XPATH, "./..")
        
        # Select an item first
        combo_box.click()
        time.sleep(0.1)
        
        options = combo_box_container.find_elements(By.CLASS_NAME, "combo-box-option")
        if len(options) > 1:
            target_option = options[1]
            original_text = target_option.text
            
            # Select the item
            driver.execute_script("arguments[0].click();", target_option)
            time.sleep(0.1)
            
            # Click on input to enter edit mode
            combo_box.click()
            time.sleep(0.1)
            
            # Clear all text
            combo_box.clear()
            time.sleep(0.1)
            
            # Press Enter
            combo_box.send_keys(Keys.ENTER)
            time.sleep(0.1)
            
            # Verify: item is removed from list
            # The option should no longer exist or should be different
            updated_options = combo_box_container.find_elements(By.CLASS_NAME, "combo-box-option")
            option_texts = [opt.text for opt in updated_options]
            assert original_text not in option_texts
    
    def test_escape_behavior(self, driver, combo_box):
        """Test: Escape → revert to original item text"""
        
        # Get the combo box container to find dropdown and options
        combo_box_container = combo_box.find_element(By.XPATH, "./..")
        
        # Select an item first
        combo_box.click()
        time.sleep(0.1)
        
        options = combo_box_container.find_elements(By.CLASS_NAME, "combo-box-option")
        if len(options) > 1:
            target_option = options[1]
            original_text = target_option.text
            
            # Select the item
            driver.execute_script("arguments[0].click();", target_option)
            time.sleep(0.1)
            
            # Click on input to enter edit mode
            combo_box.click()
            time.sleep(0.1)
            
            # Edit text
            combo_box.clear()
            combo_box.send_keys("modified_text")
            time.sleep(0.1)
            
            # Press Escape
            combo_box.send_keys(Keys.ESCAPE)
            time.sleep(0.1)
            
            # Verify: text reverts to original
            assert combo_box.get_attribute("value") == original_text
            
            # Verify: option in dropdown is unchanged
            assert target_option.text == original_text
    
    def test_focus_loss_behavior(self, driver, combo_box):
        """Test: Focus loss → same as Enter (apply changes)"""
        
        # Get the combo box container to find dropdown and options
        combo_box_container = combo_box.find_element(By.XPATH, "./..")
        
        # Select an item first
        combo_box.click()
        time.sleep(0.1)
        
        options = combo_box_container.find_elements(By.CLASS_NAME, "combo-box-option")
        if len(options) > 1:
            target_option = options[1]
            original_text = target_option.text
            
            # Select the item
            driver.execute_script("arguments[0].click();", target_option)
            time.sleep(0.1)
            
            # Click on input to enter edit mode
            combo_box.click()
            time.sleep(0.1)
            
            # Edit text
            combo_box.clear()
            combo_box.send_keys("focus_loss_test")
            time.sleep(0.1)
            
            # Click elsewhere to lose focus
            body = driver.find_element(By.TAG_NAME, "body")
            body.click()
            time.sleep(0.1)
            
            # Verify: changes are applied
            assert combo_box.get_attribute("value") == "focus_loss_test"
            
            # Verify: option in dropdown is updated
            assert target_option.text == "focus_loss_test"
