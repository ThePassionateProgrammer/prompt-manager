"""
Test calling selectOption manually to see if it works.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestManualSelectOption:
    """Test calling selectOption manually."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_manual_selectoption_call(self):
        """Test calling selectOption manually."""
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
        
        # Check initial state
        initial_state = self.driver.execute_script("""
            const roleCombo = window.customComboBoxes[0];
            return roleCombo ? {
                isDropdownVisible: roleCombo.isDropdownVisible,
                selectedOption: roleCombo.selectedOption,
                selectedIndex: roleCombo.selectedIndex,
                optionsCount: roleCombo.options.length
            } : null;
        """)
        print(f"Initial state: {initial_state}")
        
        print("Step 2: Manually call selectOption(1) to select 'Programmer'")
        
        # Manually call selectOption
        result = self.driver.execute_script("""
            const roleCombo = window.customComboBoxes[0];
            if (roleCombo) {
                console.log('Manually calling selectOption(1)');
                roleCombo.selectOption(1);
                console.log('selectOption call completed');
                
                return {
                    isDropdownVisible: roleCombo.isDropdownVisible,
                    selectedOption: roleCombo.selectedOption,
                    selectedIndex: roleCombo.selectedIndex,
                    inputValue: roleCombo.input.value
                };
            }
            return null;
        """)
        
        print(f"Result after manual selectOption call: {result}")
        
        # Check if dropdown is closed
        assert result['isDropdownVisible'] is False, f"Dropdown should be closed, got {result['isDropdownVisible']}"
        assert result['selectedOption'] == "Programmer", f"Selected option should be 'Programmer', got {result['selectedOption']}"
        assert result['selectedIndex'] == 1, f"Selected index should be 1, got {result['selectedIndex']}"
        assert result['inputValue'] == "Programmer", f"Input value should be 'Programmer', got {result['inputValue']}"
