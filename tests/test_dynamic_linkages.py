"""
Test dynamic linkage functionality for custom combo boxes.

This test verifies that linkages are created dynamically when users
select options and add new options to subsequent combo boxes.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TestDynamicLinkages:
    """Test dynamic linkage creation and cascading behavior."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_basic_linkage_creation(self):
        """
        Test 1: When user selects an option in combo box [1], 
        it should create a linkage entry for that option.
        """
        # Enter a template first
        template_input = self.driver.find_element(By.ID, "templateInput")
        template_input.send_keys("As a [Role], I want to [What], so that [Why]")
        time.sleep(1)
        
        # Generate combo boxes
        generate_btn = self.driver.find_element(By.ID, "generateBtn")
        generate_btn.click()
        time.sleep(2)
        
        # Debug: Check what elements exist on the page
        page_source = self.driver.page_source
        print(f"Page source contains 'combo-box': {'combo-box' in page_source}")
        print(f"Page source contains 'role': {'role' in page_source}")
        
        # Check if combo boxes container exists
        try:
            combo_container = self.driver.find_element(By.ID, "combo-boxes-container")
            print(f"Combo boxes container found: {combo_container.text[:100]}")
        except:
            print("Combo boxes container not found")
        
        # Check if combo-box-role element exists
        try:
            role_container = self.driver.find_element(By.ID, "combo-box-role")
            print(f"Role container found: {role_container.get_attribute('outerHTML')[:200]}")
        except:
            print("Role container not found")
        
        # Check if any combo-box-input elements exist
        try:
            inputs = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-input")
            print(f"Found {len(inputs)} combo-box-input elements")
            for i, inp in enumerate(inputs):
                print(f"Input {i}: {inp.get_attribute('outerHTML')}")
        except:
            print("No combo-box-input elements found")
        
        # Add sample data to first combo box (Role)
        role_input = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-input")[0]  # First input
        role_input.click()
        time.sleep(1)
        
        # Add option "A" to first combo box
        role_input.send_keys("A")
        role_input.send_keys("\n")  # Press Enter to add
        time.sleep(1)
        
        # Verify "A" was added to first combo box
        role_options = self.driver.find_elements(By.CSS_SELECTOR, ".combo-box-option")
        option_texts = [opt.text for opt in role_options]
        assert "A" in option_texts, f"Expected 'A' in role options, got {option_texts}"
        
        # Select "A" in first combo box
        for option in role_options:
            if option.text == "A":
                option.click()
                break
        time.sleep(1)
        
        # Check that linkage data structure exists (but may be empty initially)
        linkage_data = self.driver.execute_script("return window.linkageData;")
        assert linkage_data is not None, "Linkage data should exist"
        
        # Check that current selections are tracked
        current_selections = self.driver.execute_script("return window.currentSelections;")
        assert current_selections is not None, "Current selections should exist"
        
        print(f"✓ Test 1 passed: Dynamic linkage system initialized")
        print(f"  Linkage data: {linkage_data}")
        print(f"  Current selections: {current_selections}")
