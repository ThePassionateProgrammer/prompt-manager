"""
Test clicking on options more directly.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time


class TestDirectOptionClick:
    """Test clicking on options more directly."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_direct_option_click(self):
        """Test clicking on options using different methods."""
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
                optionsCount: roleCombo.options.length,
                optionsText: roleCombo.options.map(opt => opt.textContent)
            } : null;
        """)
        print(f"Initial state: {initial_state}")
        
        print("Step 2: Try different ways to click on the Programmer option")
        
        # Method 1: Find by text content
        role_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        programmer_option_by_text = None
        for option in role_options:
            if option.text == "Programmer":
                programmer_option_by_text = option
                break
        
        print(f"Found Programmer option by text: {programmer_option_by_text is not None}")
        if programmer_option_by_text:
            print(f"Option visible to Selenium: {programmer_option_by_text.is_displayed()}")
            print(f"Option location: {programmer_option_by_text.location}")
        
        # Method 2: Find by data-value attribute
        programmer_option_by_data = self.driver.find_element(By.CSS_SELECTOR, "[data-value='Programmer']")
        print(f"Found Programmer option by data-value: {programmer_option_by_data is not None}")
        if programmer_option_by_data:
            print(f"Option visible to Selenium: {programmer_option_by_data.is_displayed()}")
            print(f"Option location: {programmer_option_by_data.location}")
        
        # Check dropdown CSS classes
        dropdown_info = self.driver.execute_script("""
            const dropdown = document.querySelector('.combo-box-dropdown');
            return {
                className: dropdown.className,
                hasShowClass: dropdown.classList.contains('show'),
                computedStyle: {
                    display: window.getComputedStyle(dropdown).display,
                    visibility: window.getComputedStyle(dropdown).visibility,
                    opacity: window.getComputedStyle(dropdown).opacity
                }
            };
        """)
        print(f"Dropdown info: {dropdown_info}")
        
        # Method 3: Use JavaScript to click
        print("Step 3: Use JavaScript to trigger click event")
        js_result = self.driver.execute_script("""
            const programmerOption = document.querySelector('[data-value="Programmer"]');
            if (programmerOption) {
                console.log('Found programmer option:', programmerOption);
                console.log('Option text:', programmerOption.textContent);
                console.log('Option visible:', programmerOption.offsetParent !== null);
                
                // Try to trigger click event
                programmerOption.click();
                
                return {
                    success: true,
                    optionText: programmerOption.textContent,
                    optionVisible: programmerOption.offsetParent !== null
                };
            }
            return { success: false };
        """)
        print(f"JavaScript click result: {js_result}")
        
        # Check state after JavaScript click
        state_after_js = self.driver.execute_script("""
            const roleCombo = window.customComboBoxes[0];
            return roleCombo ? {
                isDropdownVisible: roleCombo.isDropdownVisible,
                selectedOption: roleCombo.selectedOption,
                selectedIndex: roleCombo.selectedIndex,
                inputValue: roleCombo.input.value
            } : null;
        """)
        print(f"State after JavaScript click: {state_after_js}")
        
        # The test passes if we can see what's happening
        assert True, "Direct option click test completed - check output above"
