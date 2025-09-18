#!/usr/bin/env python3
"""
Unit tests for the CustomComboBox component.
Tests the component in isolation to ensure it works correctly.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import os

class TestCustomComboBoxComponent:
    """Test suite for the CustomComboBox component."""
    
    def setup_method(self):
        """Set up Chrome driver for testing."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Get the absolute path to the test file
        test_file_path = os.path.abspath("test_component_integration.html")
        self.driver.get(f"file://{test_file_path}")
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "combo1"))
        )
        
        # Wait for JavaScript to initialize
        time.sleep(2)
    
    def teardown_method(self):
        """Clean up driver."""
        self.driver.quit()
    
    def test_component_initialization(self):
        """Test that the component initializes correctly."""
        # Check that all combo boxes are present
        combo1 = self.driver.find_element(By.ID, "combo1")
        combo2 = self.driver.find_element(By.ID, "combo2")
        combo3 = self.driver.find_element(By.ID, "combo3")
        
        assert combo1 is not None
        assert combo2 is not None
        assert combo3 is not None
        
        # Check that inputs are present
        input1 = combo1.find_element(By.CSS_SELECTOR, ".combo-box-input")
        input2 = combo2.find_element(By.CSS_SELECTOR, ".combo-box-input")
        input3 = combo3.find_element(By.CSS_SELECTOR, ".combo-box-input")
        
        assert input1 is not None
        assert input2 is not None
        assert input3 is not None
    
    def test_display_mode_initialization(self):
        """Test that component starts in Display mode."""
        # Check mode status
        mode_status = self.driver.find_element(By.ID, "mode-status")
        assert "Display Mode" in mode_status.text
        
        # Check first combo box first option
        combo1 = self.driver.find_element(By.ID, "combo1")
        first_option = combo1.find_element(By.CSS_SELECTOR, ".combo-box-option")
        print(f"First option text: '{first_option.text}'")
        print(f"First option HTML: {first_option.get_attribute('outerHTML')}")
        assert first_option.text == "Select item..."
        
        # Check placeholder
        input1 = combo1.find_element(By.CSS_SELECTOR, ".combo-box-input")
        assert input1.get_attribute("placeholder") == "Select item..."
    
    def test_edit_mode_switching(self):
        """Test switching to Edit mode."""
        # Click mode toggle
        mode_toggle = self.driver.find_element(By.ID, "mode-toggle")
        mode_toggle.click()
        time.sleep(1)
        
        # Check mode status
        mode_status = self.driver.find_element(By.ID, "mode-status")
        assert "Edit Mode" in mode_status.text
        
        # Check first combo box first option
        combo1 = self.driver.find_element(By.ID, "combo1")
        first_option = combo1.find_element(By.CSS_SELECTOR, ".combo-box-option")
        assert first_option.text == "Add..."
        
        # Check placeholder
        input1 = combo1.find_element(By.CSS_SELECTOR, ".combo-box-input")
        assert input1.get_attribute("placeholder") == "Type to add..."
    
    def test_display_mode_switching(self):
        """Test switching back to Display mode."""
        # First switch to Edit mode
        mode_toggle = self.driver.find_element(By.ID, "mode-toggle")
        mode_toggle.click()
        time.sleep(1)
        
        # Then switch back to Display mode
        mode_toggle.click()
        time.sleep(1)
        
        # Check mode status
        mode_status = self.driver.find_element(By.ID, "mode-status")
        assert "Display Mode" in mode_status.text
        
        # Check first combo box first option
        combo1 = self.driver.find_element(By.ID, "combo1")
        first_option = combo1.find_element(By.CSS_SELECTOR, ".combo-box-option")
        assert first_option.text == "Select item..."
    
    def test_dropdown_visibility(self):
        """Test dropdown show/hide functionality."""
        combo1 = self.driver.find_element(By.ID, "combo1")
        input1 = combo1.find_element(By.CSS_SELECTOR, ".combo-box-input")
        dropdown1 = combo1.find_element(By.CSS_SELECTOR, ".combo-box-dropdown")
        
        # Initially hidden
        assert dropdown1.get_attribute("class") == "combo-box-dropdown"
        
        # Click input to show dropdown
        input1.click()
        time.sleep(0.5)
        
        # Should now have 'show' class
        assert "show" in dropdown1.get_attribute("class")
    
    def test_add_option_in_edit_mode(self):
        """Test adding a new option in Edit mode."""
        # Switch to Edit mode
        mode_toggle = self.driver.find_element(By.ID, "mode-toggle")
        mode_toggle.click()
        time.sleep(1)
        
        # Get combo box elements
        combo1 = self.driver.find_element(By.ID, "combo1")
        input1 = combo1.find_element(By.CSS_SELECTOR, ".combo-box-input")
        
        # Type new option and press Enter
        input1.clear()
        input1.send_keys("Test Role")
        input1.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check that option was added
        options = combo1.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        option_texts = [option.text for option in options]
        assert "Test Role" in option_texts
    
    def test_edit_option_in_edit_mode(self):
        """Test editing an existing option in Edit mode."""
        # Switch to Edit mode
        mode_toggle = self.driver.find_element(By.ID, "mode-toggle")
        mode_toggle.click()
        time.sleep(1)
        
        # Add an option first
        combo1 = self.driver.find_element(By.ID, "combo1")
        input1 = combo1.find_element(By.CSS_SELECTOR, ".combo-box-input")
        
        input1.clear()
        input1.send_keys("Original Role")
        input1.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Select the option (click on it)
        options = combo1.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in options:
            if option.text == "Original Role":
                option.click()
                break
        time.sleep(0.5)
        
        # Edit the option
        input1.clear()
        input1.send_keys("Edited Role")
        input1.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check that option was updated
        options = combo1.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        option_texts = [option.text for option in options]
        assert "Edited Role" in option_texts
        assert "Original Role" not in option_texts
    
    def test_delete_option_in_edit_mode(self):
        """Test deleting an option in Edit mode."""
        # Switch to Edit mode
        mode_toggle = self.driver.find_element(By.ID, "mode-toggle")
        mode_toggle.click()
        time.sleep(1)
        
        # Add an option first
        combo1 = self.driver.find_element(By.ID, "combo1")
        input1 = combo1.find_element(By.CSS_SELECTOR, ".combo-box-input")
        
        input1.clear()
        input1.send_keys("Role to Delete")
        input1.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Select the option
        options = combo1.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in options:
            if option.text == "Role to Delete":
                option.click()
                break
        time.sleep(0.5)
        
        # Delete the option (clear field and press Enter)
        input1.clear()
        input1.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check that option was deleted
        options = combo1.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        option_texts = [option.text for option in options]
        assert "Role to Delete" not in option_texts
    
    def test_selection_in_display_mode(self):
        """Test that selection works in Display mode."""
        # Ensure we're in Display mode
        mode_status = self.driver.find_element(By.ID, "mode-status")
        if "Edit Mode" in mode_status.text:
            mode_toggle = self.driver.find_element(By.ID, "mode-toggle")
            mode_toggle.click()
            time.sleep(1)
        
        # Add some options first (in Edit mode)
        mode_toggle = self.driver.find_element(By.ID, "mode-toggle")
        mode_toggle.click()
        time.sleep(1)
        
        combo1 = self.driver.find_element(By.ID, "combo1")
        input1 = combo1.find_element(By.CSS_SELECTOR, ".combo-box-input")
        
        input1.clear()
        input1.send_keys("Selectable Role")
        input1.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Switch back to Display mode
        mode_toggle.click()
        time.sleep(1)
        
        # Try to select the option
        options = combo1.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in options:
            if option.text == "Selectable Role":
                option.click()
                break
        time.sleep(0.5)
        
        # Check that option was selected
        assert input1.get_attribute("value") == "Selectable Role"
    
    def test_hierarchical_linkages(self):
        """Test that hierarchical linkages work correctly."""
        # Switch to Edit mode to add options
        mode_toggle = self.driver.find_element(By.ID, "mode-toggle")
        mode_toggle.click()
        time.sleep(1)
        
        # Add a role
        combo1 = self.driver.find_element(By.ID, "combo1")
        input1 = combo1.find_element(By.CSS_SELECTOR, ".combo-box-input")
        
        input1.clear()
        input1.send_keys("Developer")
        input1.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Select the role
        options = combo1.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in options:
            if option.text == "Developer":
                option.click()
                break
        time.sleep(1)
        
        # Check that action options were populated
        combo2 = self.driver.find_element(By.ID, "combo2")
        options2 = combo2.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        option_texts2 = [option.text for option in options2]
        
        # Should have the linked options
        assert "Fix bugs" in option_texts2
        assert "Write tests" in option_texts2
        assert "Deploy code" in option_texts2
    
    def test_template_generation(self):
        """Test that template generation works with selections."""
        # Add and select options
        mode_toggle = self.driver.find_element(By.ID, "mode-toggle")
        mode_toggle.click()
        time.sleep(1)
        
        # Add role
        combo1 = self.driver.find_element(By.ID, "combo1")
        input1 = combo1.find_element(By.CSS_SELECTOR, ".combo-box-input")
        input1.clear()
        input1.send_keys("Developer")
        input1.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Select role
        options = combo1.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in options:
            if option.text == "Developer":
                option.click()
                break
        time.sleep(1)
        
        # Select action
        combo2 = self.driver.find_element(By.ID, "combo2")
        options2 = combo2.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in options2:
            if option.text == "Fix bugs":
                option.click()
                break
        time.sleep(1)
        
        # Select goal
        combo3 = self.driver.find_element(By.ID, "combo3")
        options3 = combo3.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in options3:
            if option.text == "Save time":
                option.click()
                break
        time.sleep(1)
        
        # Check generated prompt
        generated_prompt = self.driver.find_element(By.ID, "generated-prompt")
        expected_text = "As a Developer, I want to Fix bugs, so that I can Save time"
        assert expected_text in generated_prompt.text

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
