"""
Test option click detection to debug event handling.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestOptionClicks:
    """Test option click detection."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_option_click_detection(self):
        """
        Test if option clicks are being detected.
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
        
        # Get combo box inputs
        inputs = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-input")
        role_input = inputs[0]    # Role
        
        # Add "Programmer" to Role
        role_input.click()
        role_input.send_keys("Programmer")
        role_input.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Check if option was added
        role_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        role_texts = [opt.text for opt in role_options]
        print(f"Role options after adding Programmer: {role_texts}")
        
        # Try to click on "Programmer" option
        print("Attempting to click on Programmer option...")
        for option in role_options:
            if option.text == "Programmer":
                print(f"Found Programmer option, clicking...")
                option.click()
                time.sleep(1)
                break
        
        # Check if onSelectionChange was triggered by looking at linkage data
        result = self.driver.execute_script("""
            // Check if we can access the combo box and its callback
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                return {
                    hasCallback: !!roleCombo.onSelectionChange,
                    selectedOption: roleCombo.selectedOption,
                    selectedIndex: roleCombo.selectedIndex,
                    callbackFunction: roleCombo.onSelectionChange ? 'exists' : 'missing'
                };
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Combo box state: {result}")
        
        # Manually trigger the callback to test if it works
        test_result = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                if (roleCombo.onSelectionChange) {
                    console.log('Manually triggering callback...');
                    roleCombo.onSelectionChange('Programmer');
                    return { success: 'Callback manually triggered' };
                }
                return { error: 'No callback function' };
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Manual callback test: {test_result}")
        
        # The test passes if the callback exists
        assert result.get('hasCallback', False), "Callback not set up"
        assert result.get('selectedIndex', -1) == 1, "Option not selected"
        assert result.get('selectedOption') == 'Programmer', "Wrong option selected"
