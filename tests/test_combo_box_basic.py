"""
Test basic combo box functionality to debug initialization issues.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TestComboBoxBasic:
    """Test basic combo box functionality."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_combo_box_initialization(self):
        """
        Test that combo boxes are properly initialized as CustomComboBox objects.
        """
        # Enter a template first
        template_input = self.driver.find_element(By.ID, "templateInput")
        template_input.send_keys("As a [Role], I want to [What], so that [Why]")
        time.sleep(1)
        
        # Generate combo boxes
        generate_btn = self.driver.find_element(By.ID, "generateBtn")
        generate_btn.click()
        time.sleep(2)
        
        # Check if combo boxes are initialized by looking for CustomComboBox instances
        combo_box_count = self.driver.execute_script("return window.customComboBoxes ? window.customComboBoxes.length : 0;")
        print(f"CustomComboBox instances found: {combo_box_count}")
        
        # Check if we can access the combo box methods
        if combo_box_count > 0:
            # Try to call a method on the first combo box
            try:
                result = self.driver.execute_script("""
                    if (window.customComboBoxes && window.customComboBoxes.length > 0) {
                        window.customComboBoxes[0].showDropdown();
                        return 'showDropdown() method works';
                    }
                    return 'No combo boxes found';
                """)
                print(f"✓ {result}")
            except Exception as e:
                print(f"✗ showDropdown() failed: {e}")
        else:
            print("✗ No CustomComboBox instances found")
            
        # Check browser console for errors
        logs = self.driver.get_log('browser')
        for log in logs:
            print(f"Browser log: {log['level']} - {log['message']}")
        
        # This test should pass if combo boxes are properly initialized
        assert combo_box_count > 0, f"Should have at least one combo box, got {combo_box_count}"
