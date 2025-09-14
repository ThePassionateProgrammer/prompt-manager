#!/usr/bin/env python3
"""
Test 1: Display Mode Behavior
Test that Display mode shows "Select item..." as the first option
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class TestDisplayModeBehavior:
    
    def setup_method(self):
        """Set up Chrome driver for testing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get("file:///Users/davidbernstein/Dropbox/Dev/Python/Projects/prompt-manager/test_combo_box_standalone.html")
        
        # Wait for page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "combo1"))
        )
    
    def teardown_method(self):
        """Clean up driver"""
        self.driver.quit()
    
    def test_display_mode_shows_select_item_as_first_option(self):
        """
        Test 1: In Display mode, the first option should be "Select item..."
        This test will FAIL initially because Display mode doesn't exist yet.
        """
        # Wait for page to fully load and JavaScript to initialize
        time.sleep(5)
        
        # Try to trigger JavaScript execution by clicking the input
        combo1_input = self.driver.find_element(By.CSS_SELECTOR, "#combo1 .combo-box-input")
        combo1_input.click()
        time.sleep(1)
        
        # Find the first combo box
        combo1 = self.driver.find_element(By.ID, "combo1")
        
        # Find the first option in the dropdown
        first_option = combo1.find_element(By.CSS_SELECTOR, ".combo-box-option")
        
        # In Display mode, first option should be "Select item..."
        assert first_option.text == "Select item...", f"Expected 'Select item...', got '{first_option.text}'"
    
    def test_edit_mode_shows_add_as_first_option(self):
        """
        Test 2: In Edit mode, the first option should be "Add..."
        """
        # Wait for page to load
        time.sleep(5)
        
        # Click the mode toggle button to switch to Edit mode
        mode_toggle = self.driver.find_element(By.ID, "mode-toggle")
        mode_toggle.click()
        time.sleep(2)  # Wait for mode switch
        
        # Find the first combo box and trigger JavaScript execution
        combo1 = self.driver.find_element(By.ID, "combo1")
        combo1_input = combo1.find_element(By.CSS_SELECTOR, ".combo-box-input")
        combo1_input.click()  # Trigger focus event
        time.sleep(1)
        combo1_input.click()  # Click again to ensure JavaScript runs
        time.sleep(1)
        
        # Find the first option in the dropdown
        first_option = combo1.find_element(By.CSS_SELECTOR, ".combo-box-option")
        
        # In Edit mode, first option should be "Add..."
        assert first_option.text == "Add...", f"Expected 'Add...', got '{first_option.text}'"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
