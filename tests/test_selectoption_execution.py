"""
Test selectOption method execution to debug callback triggering.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestSelectOptionExecution:
    """Test selectOption method execution."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_selectoption_execution(self):
        """
        Test if selectOption method is being called and callback trigger code executes.
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
        
        # Check initial state
        initial_state = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                return {
                    selectedIndex: roleCombo.selectedIndex,
                    selectedOption: roleCombo.selectedOption,
                    hasCallback: !!roleCombo.onSelectionChange
                };
            }
            return { error: 'No combo boxes found' };
        """)
        print(f"Initial state: {initial_state}")
        
        # Try to click on "Programmer" option and monitor execution
        print("Attempting to click on Programmer option...")
        
        # First, let's check if we can manually call selectOption
        manual_select_result = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                const options = roleCombo.options;
                
                // Find the Programmer option (should be at index 1)
                let programmerIndex = -1;
                for (let i = 0; i < options.length; i++) {
                    if (options[i].textContent === 'Programmer') {
                        programmerIndex = i;
                        break;
                    }
                }
                
                if (programmerIndex >= 0) {
                    console.log('Manually calling selectOption with index:', programmerIndex);
                    roleCombo.selectOption(programmerIndex);
                    return {
                        success: 'selectOption called manually',
                        index: programmerIndex,
                        selectedIndex: roleCombo.selectedIndex,
                        selectedOption: roleCombo.selectedOption
                    };
                } else {
                    return { error: 'Programmer option not found' };
                }
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Manual selectOption result: {manual_select_result}")
        
        # Now try clicking the option directly
        role_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        for option in role_options:
            if option.text == "Programmer":
                print(f"Found Programmer option, clicking...")
                option.click()
                time.sleep(1)
                break
        
        # Check final state
        final_state = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                return {
                    selectedIndex: roleCombo.selectedIndex,
                    selectedOption: roleCombo.selectedOption,
                    hasCallback: !!roleCombo.onSelectionChange
                };
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Final state: {final_state}")
        
        # The test passes if we can execute selectOption and the selection state is updated
        assert manual_select_result.get('success') == 'selectOption called manually', "Manual selectOption failed"
        assert final_state.get('selectedIndex') == 1, "Option not selected after click"
        assert final_state.get('selectedOption') == 'Programmer', "Wrong option selected"
