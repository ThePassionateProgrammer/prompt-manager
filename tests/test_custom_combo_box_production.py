"""
Production Tests for CustomComboBox Component

Tests the core functionality of the CustomComboBox component:
- Edit mode behavior (add, edit, delete items)
- Display mode behavior (selection only)
- State transitions and persistence
- Enter key priority handling (critical bug fix)
- Option replacement without duplicates

These tests validate the production-ready functionality.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time


class TestCustomComboBoxProduction:
    """Test suite for production CustomComboBox functionality"""
    
    @pytest.fixture
    def driver(self):
        """Set up Chrome driver for testing"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    @pytest.fixture
    def combo_box_page(self, driver):
        """Load the template builder page with combo boxes"""
        driver.get('http://localhost:8000/template-builder')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'combo-box-Who'))
        )
        return driver
    
    def test_edit_mode_enter_priority_fix(self, combo_box_page):
        """
        Test the critical bug fix: Enter key priority in edit mode
        
        This test validates the fix for the duplicate options bug where
        handleEnter was prioritizing highlighted options over edit mode.
        
        Steps:
        1. Add an item to the combo box
        2. Click the item to enter edit mode
        3. Type new text and hit Enter
        4. Verify only the new text appears (no duplicates)
        """
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-Who')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Step 1: Add initial item
        input_field.click()
        input_field.send_keys('Developer')
        input_field.send_keys(Keys.RETURN)
        
        # Wait for item to be added
        time.sleep(0.5)
        
        # Step 2: Click on the item to enter edit mode
        developer_option = dropdown.find_element(By.XPATH, "//div[text()='Developer']")
        developer_option.click()
        
        # Step 3: Edit the text and hit Enter
        input_field.send_keys('_Senior')
        input_field.send_keys(Keys.RETURN)
        
        # Step 4: Verify only one item exists (no duplicates)
        time.sleep(0.5)
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        option_texts = [opt.text for opt in options if opt.text not in ['Add...']]
        
        # Should have exactly one option: "Developer_Senior"
        assert len(option_texts) == 1, f"Expected 1 option, got {len(option_texts)}: {option_texts}"
        assert option_texts[0] == 'Developer_Senior', f"Expected 'Developer_Senior', got '{option_texts[0]}'"
    
    def test_edit_mode_delete_item(self, combo_box_page):
        """Test deleting an item by clearing text and hitting Enter"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-Who')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add an item first
        input_field.click()
        input_field.send_keys('Manager')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        # Click on the item to enter edit mode
        manager_option = dropdown.find_element(By.XPATH, "//div[text()='Manager']")
        manager_option.click()
        
        # Clear the text and hit Enter to delete
        input_field.send_keys(Keys.CONTROL + 'a')  # Select all
        input_field.send_keys(Keys.DELETE)  # Delete
        input_field.send_keys(Keys.RETURN)
        
        # Verify item was deleted
        time.sleep(0.5)
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        option_texts = [opt.text for opt in options if opt.text not in ['Add...']]
        
        assert len(option_texts) == 0, f"Expected 0 options, got {len(option_texts)}: {option_texts}"
    
    def test_escape_key_reverts_changes(self, combo_box_page):
        """Test that Escape key reverts changes in edit mode"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-Who')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add an item first
        input_field.click()
        input_field.send_keys('Designer')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        # Click on the item to enter edit mode
        designer_option = dropdown.find_element(By.XPATH, "//div[text()='Designer']")
        designer_option.click()
        
        # Edit the text
        input_field.send_keys('_Senior')
        
        # Hit Escape to revert
        input_field.send_keys(Keys.ESCAPE)
        
        # Verify original text is restored
        assert input_field.get_attribute('value') == 'Designer'
        
        # Verify dropdown still shows original item
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        option_texts = [opt.text for opt in options if opt.text not in ['Add...']]
        assert 'Designer' in option_texts
        assert 'Designer_Senior' not in option_texts
    
    def test_selection_persistence_during_edit(self, combo_box_page):
        """Test that item stays highlighted while editing"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-Who')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add an item first
        input_field.click()
        input_field.send_keys('Analyst')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        # Click on the item to enter edit mode
        analyst_option = dropdown.find_element(By.XPATH, "//div[text()='Analyst']")
        analyst_option.click()
        
        # Start typing - item should remain highlighted
        input_field.send_keys('_Senior')
        
        # Verify the item is still highlighted/selected
        time.sleep(0.1)
        selected_options = dropdown.find_elements(By.CSS_SELECTOR, '.combo-box-option.selected')
        assert len(selected_options) == 1
        assert selected_options[0].text == 'Analyst'
    
    def test_multiple_items_edit_workflow(self, combo_box_page):
        """Test editing multiple items in sequence"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-Who')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add multiple items
        items = ['Developer', 'Manager', 'Designer']
        for item in items:
            input_field.click()
            input_field.send_keys(item)
            input_field.send_keys(Keys.RETURN)
            time.sleep(0.3)
        
        # Edit each item
        for i, item in enumerate(items):
            # Click on the item to edit
            option = dropdown.find_element(By.XPATH, f"//div[text()='{item}']")
            option.click()
            
            # Edit the text
            input_field.send_keys('_Senior')
            input_field.send_keys(Keys.RETURN)
            time.sleep(0.3)
        
        # Verify all items were updated correctly
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        option_texts = [opt.text for opt in options if opt.text not in ['Add...']]
        
        expected_texts = ['Developer_Senior', 'Manager_Senior', 'Designer_Senior']
        assert len(option_texts) == 3, f"Expected 3 options, got {len(option_texts)}: {option_texts}"
        
        for expected in expected_texts:
            assert expected in option_texts, f"Expected '{expected}' in {option_texts}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
