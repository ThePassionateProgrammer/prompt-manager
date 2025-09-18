"""
Test the selection flow: clicking/Enter should select item, close dropdown, and update downstream.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestSelectionFlow:
    """Test the complete selection flow behavior."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_click_selection_flow(self):
        """
        Test that clicking on an item selects it, closes dropdown, and updates downstream.
        """
        # Enter a template first
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
        role_input = inputs[0]    # Role
        
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
        
        # Click on the Programmer option using JavaScript (Selenium click has issues)
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
    
    def test_enter_selection_flow(self):
        """
        Test that pressing Enter on a highlighted item selects it, closes dropdown, and updates downstream.
        """
        # Enter a template first
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
        role_input = inputs[0]    # Role
        
        print("Step 1: Add 'Programmer' to Role combo box")
        
        # Add "Programmer" to Role
        role_input.click()
        role_input.send_keys("Programmer")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        print("Step 2: Use arrow keys to highlight 'Programmer' and press Enter")
        
        # Use arrow keys to navigate to the Programmer option
        role_input.send_keys(Keys.ARROW_DOWN)  # This should highlight the first option (Add...)
        role_input.send_keys(Keys.ARROW_DOWN)  # This should highlight Programmer
        time.sleep(0.5)
        
        # Check highlighted state
        highlighted_state = self.driver.execute_script("""
            const roleCombo = window.customComboBoxes[0];
            return roleCombo ? {
                highlightedIndex: roleCombo.highlightedIndex,
                dropdownVisible: roleCombo.isDropdownVisible
            } : null;
        """)
        
        print(f"Highlighted state before Enter: {highlighted_state}")
        
        # Press Enter to select the highlighted option
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check final state
        role_value = role_input.get_attribute('value')
        print(f"Role input value after Enter: '{role_value}'")
        
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
        
        print(f"Dropdown visible after Enter: {dropdown_visible}")
        print(f"Selection state after Enter: {selection_state}")
        
        # Assertions
        assert role_value == "Programmer", f"Expected 'Programmer', got '{role_value}'"
        assert dropdown_visible is False, "Dropdown should be closed after Enter selection"
        assert selection_state['selectedOption'] == "Programmer", "Selected option should be 'Programmer'"
        assert selection_state['selectedIndex'] >= 0, "Selected index should be valid"
    
    def test_downstream_update_on_selection(self):
        """
        Test that selecting an item in a parent combo box updates downstream combo boxes.
        """
        # Enter a template first
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
        role_input = inputs[0]    # Role
        what_input = inputs[1]    # What
        
        print("Step 1: Create Programmer -> Write Code linkage")
        
        # Add "Programmer" to Role and select it
        role_input.click()
        role_input.send_keys("Programmer")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Select Programmer using JavaScript
        self.driver.execute_script("""
            const programmerOption = document.querySelector('[data-value="Programmer"]');
            if (programmerOption) {
                programmerOption.click();
            }
        """)
        time.sleep(1)
        
        # Add "Write Code" to What combo box
        what_input.click()
        what_input.send_keys("Write Code")
        what_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        print("Step 2: Add Manager and switch to it")
        
        # Add "Manager" to Role
        role_input.click()
        role_input.send_keys("Manager")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Select Manager using JavaScript
        self.driver.execute_script("""
            const managerOption = document.querySelector('[data-value="Manager"]');
            if (managerOption) {
                managerOption.click();
            }
        """)
        time.sleep(1)
        
        print("Step 3: Switch back to Programmer and verify Write Code is restored")
        
        # Select Programmer again using JavaScript
        self.driver.execute_script("""
            const programmerOption = document.querySelector('[data-value="Programmer"]');
            if (programmerOption) {
                programmerOption.click();
            }
        """)
        time.sleep(1)
        
        # Check that Write Code is restored in What combo box
        what_options_after_programmer = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 1) {
                const whatCombo = comboBoxes[1];
                return Array.from(whatCombo.dropdown.querySelectorAll('.combo-box-option')).map(opt => opt.textContent);
            }
            return [];
        """)
        
        print(f"What options after switching back to Programmer: {what_options_after_programmer}")
        
        # Verify Write Code is restored
        assert "Write Code" in what_options_after_programmer, f"Expected 'Write Code' to be restored, got {what_options_after_programmer}"
        
        # Verify dropdowns are closed after selection
        dropdown_states = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            return comboBoxes ? comboBoxes.map(combo => ({
                tag: combo.tag,
                dropdownVisible: combo.isDropdownVisible
            })) : [];
        """)
        
        print(f"Dropdown states after selection: {dropdown_states}")
        
        # All dropdowns should be closed
        for state in dropdown_states:
            assert state['dropdownVisible'] is False, f"Dropdown for {state['tag']} should be closed"
