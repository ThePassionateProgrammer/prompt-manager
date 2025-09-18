"""
Test option selection to debug why clicking 'Programmer' selects 'ProgrammerManager'.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestOptionSelectionDebug:
    """Test option selection debugging."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_option_selection_debug(self):
        """
        Test option selection to debug the Programmer vs ProgrammerManager issue.
        """
        # Enter a template first
        template_input = self.driver.find_element(By.ID, "templateInput")
        template_input.send_keys("As a [Role], I want to [What].")
        time.sleep(1)
        
        # Generate combo boxes
        generate_btn = self.driver.find_element(By.ID, "generateBtn")
        generate_btn.click()
        time.sleep(2)
        
        # Switch to Edit Mode
        edit_mode_btn = self.driver.find_element(By.ID, "editModeBtn")
        edit_mode_btn.click()
        time.sleep(1)
        
        # Get combo box input
        inputs = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-input")
        role_input = inputs[0]    # Role
        
        # Add "Programmer" to Role
        role_input.click()
        role_input.send_keys("Programmer")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Add "Manager" to Role (this might create "ProgrammerManager")
        role_input.click()
        role_input.send_keys("Manager")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check what options we have
        role_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        option_texts = [opt.text for opt in role_options]
        print(f"Available options: {option_texts}")
        
        # Check the internal state of the combo box
        combo_state = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                const options = roleCombo.options;
                const optionDetails = options.map((opt, index) => ({
                    index: index,
                    text: opt.textContent,
                    value: opt.dataset.value
                }));
                return {
                    selectedIndex: roleCombo.selectedIndex,
                    selectedOption: roleCombo.selectedOption,
                    options: optionDetails
                };
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Combo box state: {combo_state}")
        
        # Try to click on "Programmer" and see what happens
        print("Attempting to click on 'Programmer'...")
        for i, option in enumerate(role_options):
            if option.text == "Programmer":
                print(f"Found 'Programmer' at index {i}, clicking...")
                
                # Check state before click
                before_state = self.driver.execute_script("""
                    const comboBoxes = window.customComboBoxes;
                    if (comboBoxes && comboBoxes.length > 0) {
                        const roleCombo = comboBoxes[0];
                        return {
                            selectedIndex: roleCombo.selectedIndex,
                            selectedOption: roleCombo.selectedOption
                        };
                    }
                    return { error: 'No combo boxes found' };
                """)
                print(f"Before click: {before_state}")
                
                option.click()
                time.sleep(1)
                
                # Check state after click
                after_state = self.driver.execute_script("""
                    const comboBoxes = window.customComboBoxes;
                    if (comboBoxes && comboBoxes.length > 0) {
                        const roleCombo = comboBoxes[0];
                        return {
                            selectedIndex: roleCombo.selectedIndex,
                            selectedOption: roleCombo.selectedOption
                        };
                    }
                    return { error: 'No combo boxes found' };
                """)
                print(f"After click: {after_state}")
                
                break
        
        # The test passes if we can identify the issue
        assert len(option_texts) > 0, "No options found"
        assert "Programmer" in option_texts, "Programmer option not found"
