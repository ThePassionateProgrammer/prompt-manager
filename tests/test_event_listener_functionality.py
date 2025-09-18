"""
Test event listener functionality to debug why clicking options doesn't trigger selectOption.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class TestEventListenerFunctionality:
    """Test event listener functionality."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_event_listener_functionality(self):
        """
        Test event listener functionality to debug the issue.
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
        
        # Test event listener functionality
        result = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            if (comboBoxes && comboBoxes.length > 0) {
                const roleCombo = comboBoxes[0];
                const options = roleCombo.options;
                
                // Find the Programmer option
                let programmerOption = null;
                for (let i = 0; i < options.length; i++) {
                    if (options[i].textContent === 'Programmer') {
                        programmerOption = options[i];
                        break;
                    }
                }
                
                if (programmerOption) {
                    // Monitor selectOption calls
                    let selectOptionCalled = false;
                    let selectOptionIndex = -1;
                    
                    const originalSelectOption = roleCombo.selectOption.bind(roleCombo);
                    roleCombo.selectOption = function(index) {
                        selectOptionCalled = true;
                        selectOptionIndex = index;
                        console.log('=== SELECTOPTION CALLED ===', index);
                        return originalSelectOption(index);
                    };
                    
                    console.log('=== TESTING EVENT LISTENER FUNCTIONALITY ===');
                    console.log('Programmer option:', programmerOption);
                    console.log('Programmer option has click listener:', programmerOption.onclick !== null);
                    
                    // Store initial state
                    const initialState = {
                        selectedIndex: roleCombo.selectedIndex,
                        selectedOption: roleCombo.selectedOption
                    };
                    
                    // Manually trigger the click event
                    console.log('Manually triggering click event...');
                    programmerOption.click();
                    
                    // Store final state
                    const finalState = {
                        selectedIndex: roleCombo.selectedIndex,
                        selectedOption: roleCombo.selectedOption
                    };
                    
                    return {
                        success: 'Event test completed',
                        programmerOption: programmerOption.textContent,
                        selectOptionCalled: selectOptionCalled,
                        selectOptionIndex: selectOptionIndex,
                        initialState: initialState,
                        finalState: finalState
                    };
                } else {
                    return { error: 'Programmer option not found' };
                }
            }
            return { error: 'No combo boxes found' };
        """)
        
        print(f"Event listener functionality result: {result}")
        
        # The test passes if we can see what's happening with the event listeners
        assert result.get('success') == 'Event test completed', "Event test failed"
        
        # Check if selectOption was called
        if result.get('selectOptionCalled'):
            print(f"✅ selectOption was called with index: {result.get('selectOptionIndex')}")
        else:
            print("❌ selectOption was NOT called when clicking option")
            
        # Verify selection state
        assert result.get('finalState', {}).get('selectedOption') == 'Programmer', "Wrong option selected"
