#!/usr/bin/env python3
"""
Test the working version to verify it actually works.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os

def test_working_version():
    """Test that the working version actually works."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Get the absolute path to the working version
        test_file_path = os.path.abspath("test_combo_box_standalone.html")
        driver.get(f"file://{test_file_path}")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "combo1"))
        )
        
        # Wait for JavaScript to initialize
        time.sleep(3)
        
        # Check that we start in Display mode
        mode_status = driver.find_element(By.ID, "mode-status")
        print(f"Mode status: {mode_status.text}")
        assert "Display mode" in mode_status.text
        
        # Check first combo box first option
        combo1 = driver.find_element(By.ID, "combo1")
        first_option = combo1.find_element(By.CSS_SELECTOR, ".combo-box-option")
        print(f"First option text: '{first_option.text}'")
        print(f"First option HTML: {first_option.get_attribute('outerHTML')}")
        assert first_option.text == "Select item..."
        
        # Check placeholder
        input1 = combo1.find_element(By.CSS_SELECTOR, ".combo-box-input")
        print(f"Placeholder: '{input1.get_attribute('placeholder')}'")
        assert input1.get_attribute("placeholder") == "Select item..."
        
        print("✅ Working version test PASSED")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    test_working_version()
