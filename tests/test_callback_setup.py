"""
Test that onSelectionChange callbacks are properly set up.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


class TestCallbackSetup:
    """Test that callbacks are properly set up."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_callback_setup(self):
        """
        Test that onSelectionChange callbacks are properly set up.
        """
        # Enter a template first
        template_input = self.driver.find_element(By.ID, "templateInput")
        template_input.send_keys("As a [Role], I want to [What], so that I can [Why].")
        time.sleep(1)
        
        # Generate combo boxes
        generate_btn = self.driver.find_element(By.ID, "generateBtn")
        generate_btn.click()
        time.sleep(2)
        
        # Check if callbacks are set up
        result = self.driver.execute_script("""
            const comboBoxes = window.customComboBoxes;
            return {
                comboBoxCount: comboBoxes.length,
                firstComboHasCallback: comboBoxes[0] && typeof comboBoxes[0].onSelectionChange === 'function',
                secondComboHasCallback: comboBoxes[1] && typeof comboBoxes[1].onSelectionChange === 'function',
                thirdComboHasCallback: comboBoxes[2] && typeof comboBoxes[2].onSelectionChange === 'function'
            };
        """)
        
        print(f"Callback setup result: {result}")
        
        # All combo boxes should have callbacks
        assert result["comboBoxCount"] == 3, f"Expected 3 combo boxes, got {result['comboBoxCount']}"
        assert result["firstComboHasCallback"], "First combo box should have onSelectionChange callback"
        assert result["secondComboHasCallback"], "Second combo box should have onSelectionChange callback"
        assert result["thirdComboHasCallback"], "Third combo box should have onSelectionChange callback"
        
        print("✓ All callbacks are properly set up")
