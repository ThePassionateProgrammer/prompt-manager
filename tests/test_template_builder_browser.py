"""
Test the actual Template Builder browser functionality.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestTemplateBuilderBrowser:
    """Test the actual Template Builder browser functionality."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_template_builder_basic_functionality(self):
        """Test basic Template Builder functionality."""
        print("Testing Template Builder basic functionality...")
        
        # Enter a template
        template_input = self.driver.find_element(By.ID, "templateInput")
        template_input.send_keys("As a [Role], I want to [What], so that I can [Why].")
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
        assert len(inputs) >= 3, f"Expected at least 3 combo box inputs, got {len(inputs)}"
        
        role_input = inputs[0]    # Role
        what_input = inputs[1]    # What
        why_input = inputs[2]     # Why
        
        print("Step 1: Add 'Programmer' to Role combo box")
        
        # Add "Programmer" to Role
        role_input.click()
        role_input.send_keys("Programmer")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check that dropdown is open and "Programmer" is available
        role_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        programmer_option = None
        for option in role_options:
            if option.text == "Programmer":
                programmer_option = option
                break
        
        assert programmer_option is not None, "Programmer option should be available"
        
        print("Step 2: Click on 'Programmer' option")
        
        # Click on the Programmer option using JavaScript (same as our working tests)
        self.driver.execute_script("""
            const programmerOption = document.querySelector('[data-value="Programmer"]');
            if (programmerOption) {
                programmerOption.click();
            }
        """)
        time.sleep(1)
        
        # Check that:
        # 1. Role input shows "Programmer"
        # 2. Dropdown is closed
        # 3. Selection is made
        
        role_value = role_input.get_attribute('value')
        print(f"Role input value after click: '{role_value}'")
        
        # Check dropdown visibility
        dropdown_visible = self.driver.execute_script("""
            const roleCombo = window.customComboBoxes[0];
            return roleCombo ? roleCombo.isDropdownVisible : false;
        """)
        
        # Check selection state
        selection_state = self.driver.execute_script("""
            const roleCombo = window.customComboBoxes[0];
            return roleCombo ? {
                selectedOption: roleCombo.selectedOption,
                selectedIndex: roleCombo.selectedIndex
            } : null;
        """)
        
        print(f"Dropdown visible after click: {dropdown_visible}")
        print(f"Selection state after click: {selection_state}")
        
        # Assertions
        assert role_value == "Programmer", f"Expected 'Programmer', got '{role_value}'"
        assert dropdown_visible is False, "Dropdown should be closed after selection"
        assert selection_state['selectedOption'] == "Programmer", "Selected option should be 'Programmer'"
        assert selection_state['selectedIndex'] >= 0, "Selected index should be valid"
        
        print("Step 3: Test Enter key selection")
        
        # Add "Write Code" to What combo box
        what_input.click()
        what_input.send_keys("Write Code")
        what_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Use arrow keys to highlight and press Enter
        what_input.send_keys(Keys.ARROW_DOWN)
        what_input.send_keys(Keys.ARROW_DOWN)  # Should highlight "Write Code"
        time.sleep(0.5)
        
        # Press Enter to select
        what_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check What combo box state
        what_value = what_input.get_attribute('value')
        what_dropdown_visible = self.driver.execute_script("""
            const whatCombo = window.customComboBoxes[1];
            return whatCombo ? whatCombo.isDropdownVisible : false;
        """)
        
        print(f"What input value after Enter: '{what_value}'")
        print(f"What dropdown visible after Enter: {what_dropdown_visible}")
        
        # Assertions
        assert what_value == "Write Code", f"Expected 'Write Code', got '{what_value}'"
        assert what_dropdown_visible is False, "What dropdown should be closed after Enter selection"
        
        print("✅ Template Builder basic functionality test passed!")
