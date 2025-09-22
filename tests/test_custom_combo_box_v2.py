"""
Comprehensive test suite for CustomComboBox v2.0
Tests all functionality: Add, Update, Delete, Edit Mode, Selection, and Linkages
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


@pytest.fixture
def combo_box_page():
    """Setup browser and navigate to template builder page"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("http://localhost:8000/template-builder")
    
    # Wait for page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "combo-box-container"))
    )
    
    yield driver
    driver.quit()


class TestCustomComboBoxCoreFunctionality:
    """Test core combo box functionality"""
    
    def test_initial_state(self, combo_box_page):
        """Test initial state of combo box"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Should have "Add..." option initially
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        assert len(options) == 1
        assert options[0].text == 'Add...'
        
        # Input should be empty
        assert input_field.get_attribute('value') == ''
        
        # Dropdown should be hidden initially
        assert 'show' not in dropdown.get_attribute('class')
    
    def test_add_new_item(self, combo_box_page):
        """Test adding a new item to the combo box"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Type new item and press Enter
        input_field.click()
        input_field.send_keys('Developer')
        input_field.send_keys(Keys.RETURN)
        
        # Should add the item to the dropdown
        time.sleep(0.5)
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        option_texts = [opt.text for opt in options if opt.text not in ['Add...']]
        
        assert len(option_texts) == 1
        assert 'Developer' in option_texts
    
    def test_select_existing_item(self, combo_box_page):
        """Test selecting an existing item"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add an item first
        input_field.click()
        input_field.send_keys('Manager')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        # Click on the item to select it
        manager_option = dropdown.find_element(By.XPATH, "//div[text()='Manager']")
        manager_option.click()
        
        # Input field should show the selected item
        assert input_field.get_attribute('value') == 'Manager'
        
        # Item should be highlighted in dropdown
        selected_options = dropdown.find_elements(By.CSS_SELECTOR, '.combo-box-option.selected')
        assert len(selected_options) == 1
        assert selected_options[0].text == 'Manager'


class TestEditModeFunctionality:
    """Test edit mode functionality"""
    
    def test_enter_edit_mode_on_selected_item(self, combo_box_page):
        """Test entering edit mode by clicking on selected item"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add and select an item
        input_field.click()
        input_field.send_keys('Designer')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        designer_option = dropdown.find_element(By.XPATH, "//div[text()='Designer']")
        designer_option.click()
        
        # Click on the selected item again to enter edit mode
        designer_option.click()
        
        # Should enter edit mode - dropdown should stay open
        assert 'show' in dropdown.get_attribute('class')
        
        # Cursor should be at end of text
        cursor_position = driver.execute_script("return arguments[0].selectionStart", input_field)
        assert cursor_position == len('Designer')
    
    def test_edit_mode_update_item(self, combo_box_page):
        """Test updating an item in edit mode"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add and select an item
        input_field.click()
        input_field.send_keys('Tester')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        tester_option = dropdown.find_element(By.XPATH, "//div[text()='Tester']")
        tester_option.click()
        
        # Click on selected item to enter edit mode
        tester_option.click()
        
        # Edit the text
        input_field.send_keys('_Senior')
        input_field.send_keys(Keys.RETURN)
        
        # Should update the item in the dropdown
        time.sleep(0.5)
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        option_texts = [opt.text for opt in options if opt.text not in ['Add...']]
        
        assert len(option_texts) == 1
        assert option_texts[0] == 'Tester_Senior'
        
        # Should not have the old item
        assert 'Tester' not in option_texts
    
    def test_edit_mode_escape_reverts_changes(self, combo_box_page):
        """Test that Escape key reverts changes in edit mode"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add and select an item
        input_field.click()
        input_field.send_keys('Analyst')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        analyst_option = dropdown.find_element(By.XPATH, "//div[text()='Analyst']")
        analyst_option.click()
        
        # Click on selected item to enter edit mode
        analyst_option.click()
        
        # Edit the text
        input_field.send_keys('_Lead')
        
        # Press Escape to revert
        input_field.send_keys(Keys.ESCAPE)
        
        # Should revert to original text
        assert input_field.get_attribute('value') == 'Analyst'
        
        # Original item should still be in dropdown
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        option_texts = [opt.text for opt in options if opt.text not in ['Add...']]
        assert 'Analyst' in option_texts
        assert 'Analyst_Lead' not in option_texts


class TestDeleteFunctionality:
    """Test delete functionality"""
    
    def test_delete_selected_item_by_clearing_text(self, combo_box_page):
        """Test deleting an item by clearing text and pressing Enter"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add an item first
        input_field.click()
        input_field.send_keys('Consultant')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        # Click on the item to select it
        consultant_option = dropdown.find_element(By.XPATH, "//div[text()='Consultant']")
        consultant_option.click()
        
        # Clear the text and press Enter
        input_field.send_keys(Keys.CONTROL + 'a')  # Select all
        input_field.send_keys(Keys.DELETE)  # Delete
        input_field.send_keys(Keys.RETURN)
        
        # Should delete the item from dropdown
        time.sleep(0.5)
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        option_texts = [opt.text for opt in options if opt.text not in ['Add...']]
        
        assert len(option_texts) == 0
    
    def test_delete_with_multiple_items(self, combo_box_page):
        """Test deleting an item when multiple items exist"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add multiple items
        items = ['Architect', 'Lead', 'Junior']
        for item in items:
            input_field.click()
            input_field.send_keys(item)
            input_field.send_keys(Keys.RETURN)
            time.sleep(0.3)
        
        # Click on 'Lead' to select it
        lead_option = dropdown.find_element(By.XPATH, "//div[text()='Lead']")
        lead_option.click()
        
        # Clear the text and press Enter to delete
        input_field.send_keys(Keys.CONTROL + 'a')  # Select all
        input_field.send_keys(Keys.DELETE)  # Delete
        input_field.send_keys(Keys.RETURN)
        
        # Should only delete 'Lead'
        time.sleep(0.5)
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        option_texts = [opt.text for opt in options if opt.text not in ['Add...']]
        
        expected_texts = ['Architect', 'Junior']
        assert len(option_texts) == 2
        
        for expected in expected_texts:
            assert expected in option_texts
        
        assert 'Lead' not in option_texts
    
    def test_delete_key_preserves_selection(self, combo_box_page):
        """Test that Delete key preserves selection for delete on Enter"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add an item
        input_field.click()
        input_field.send_keys('Specialist')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        # Click on the item to select it
        specialist_option = dropdown.find_element(By.XPATH, "//div[text()='Specialist']")
        specialist_option.click()
        
        # Press Delete key to clear text
        input_field.send_keys(Keys.DELETE)
        
        # Item should still be highlighted in dropdown
        selected_options = dropdown.find_elements(By.CSS_SELECTOR, '.combo-box-option.selected')
        assert len(selected_options) == 1
        assert selected_options[0].text == 'Specialist'
        
        # Press Enter to delete
        input_field.send_keys(Keys.RETURN)
        
        # Should delete the item
        time.sleep(0.5)
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        option_texts = [opt.text for opt in options if opt.text not in ['Add...']]
        assert len(option_texts) == 0


class TestSelectionPersistence:
    """Test selection persistence during editing"""
    
    def test_selection_persists_while_typing(self, combo_box_page):
        """Test that selection persists while typing in edit mode"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add and select an item
        input_field.click()
        input_field.send_keys('Coordinator')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        coordinator_option = dropdown.find_element(By.XPATH, "//div[text()='Coordinator']")
        coordinator_option.click()
        
        # Click on selected item to enter edit mode
        coordinator_option.click()
        
        # Type some text
        input_field.send_keys('_Senior')
        
        # Item should still be highlighted in dropdown
        selected_options = dropdown.find_elements(By.CSS_SELECTOR, '.combo-box-option.selected')
        assert len(selected_options) == 1
        assert selected_options[0].text == 'Coordinator'
    
    def test_selection_persists_while_deleting(self, combo_box_page):
        """Test that selection persists while deleting in edit mode"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add and select an item
        input_field.click()
        input_field.send_keys('Supervisor')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        supervisor_option = dropdown.find_element(By.XPATH, "//div[text()='Supervisor']")
        supervisor_option.click()
        
        # Click on selected item to enter edit mode
        supervisor_option.click()
        
        # Delete some text
        input_field.send_keys(Keys.CONTROL + 'a')  # Select all
        input_field.send_keys(Keys.DELETE)  # Delete all
        
        # Item should still be highlighted in dropdown
        selected_options = dropdown.find_elements(By.CSS_SELECTOR, '.combo-box-option.selected')
        assert len(selected_options) == 1
        assert selected_options[0].text == 'Supervisor'


class TestKeyboardNavigation:
    """Test keyboard navigation"""
    
    def test_arrow_keys_navigation(self, combo_box_page):
        """Test arrow key navigation in dropdown"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add multiple items
        items = ['Item1', 'Item2', 'Item3']
        for item in items:
            input_field.click()
            input_field.send_keys(item)
            input_field.send_keys(Keys.RETURN)
            time.sleep(0.3)
        
        # Click to open dropdown
        input_field.click()
        
        # Navigate with arrow keys
        input_field.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.1)
        
        # Should highlight first option
        highlighted_options = dropdown.find_elements(By.CSS_SELECTOR, '.combo-box-option.highlighted')
        assert len(highlighted_options) == 1
        
        # Navigate down more
        input_field.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.1)
        input_field.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.1)
        
        # Navigate up
        input_field.send_keys(Keys.ARROW_UP)
        time.sleep(0.1)
        
        # Should have highlighted option
        highlighted_options = dropdown.find_elements(By.CSS_SELECTOR, '.combo-box-option.highlighted')
        assert len(highlighted_options) == 1
    
    def test_enter_selects_highlighted_option(self, combo_box_page):
        """Test that Enter selects the highlighted option"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add an item
        input_field.click()
        input_field.send_keys('SelectableItem')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        # Clear input and open dropdown
        input_field.clear()
        input_field.click()
        
        # Navigate to the item and select it
        input_field.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.1)
        input_field.send_keys(Keys.RETURN)
        
        # Should select the item
        assert input_field.get_attribute('value') == 'SelectableItem'
        
        # Item should be selected in dropdown
        selected_options = dropdown.find_elements(By.CSS_SELECTOR, '.combo-box-option.selected')
        assert len(selected_options) == 1
        assert selected_options[0].text == 'SelectableItem'


class TestFocusAndBlur:
    """Test focus and blur behavior"""
    
    def test_focus_loss_applies_changes(self, combo_box_page):
        """Test that losing focus applies changes in edit mode"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add and select an item
        input_field.click()
        input_field.send_keys('FocusTest')
        input_field.send_keys(Keys.RETURN)
        time.sleep(0.5)
        
        focus_option = dropdown.find_element(By.XPATH, "//div[text()='FocusTest']")
        focus_option.click()
        
        # Click on selected item to enter edit mode
        focus_option.click()
        
        # Edit the text
        input_field.send_keys('_Updated')
        
        # Click outside to lose focus
        driver.find_element(By.TAG_NAME, 'body').click()
        
        # Should apply changes
        time.sleep(0.5)
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        option_texts = [opt.text for opt in options if opt.text not in ['Add...']]
        
        assert len(option_texts) == 1
        assert option_texts[0] == 'FocusTest_Updated'
    
    def test_click_different_item_while_editing(self, combo_box_page):
        """Test clicking different item while editing applies changes"""
        driver = combo_box_page
        who_combo = driver.find_element(By.ID, 'combo-box-1')
        input_field = who_combo.find_element(By.CLASS_NAME, 'combo-box-input')
        dropdown = who_combo.find_element(By.CLASS_NAME, 'combo-box-dropdown')
        
        # Add multiple items
        items = ['FirstItem', 'SecondItem']
        for item in items:
            input_field.click()
            input_field.send_keys(item)
            input_field.send_keys(Keys.RETURN)
            time.sleep(0.3)
        
        # Click on first item to select it
        first_option = dropdown.find_element(By.XPATH, "//div[text()='FirstItem']")
        first_option.click()
        
        # Click on selected item to enter edit mode
        first_option.click()
        
        # Edit the text
        input_field.send_keys('_Modified')
        
        # Click on second item
        second_option = dropdown.find_element(By.XPATH, "//div[text()='SecondItem']")
        second_option.click()
        
        # Should apply changes to first item and select second item
        time.sleep(0.5)
        options = dropdown.find_elements(By.CLASS_NAME, 'combo-box-option')
        option_texts = [opt.text for opt in options if opt.text not in ['Add...']]
        
        assert 'FirstItem_Modified' in option_texts
        assert 'SecondItem' in option_texts
        assert input_field.get_attribute('value') == 'SecondItem'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
