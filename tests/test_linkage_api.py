"""
Test dynamic linkage functionality using the CustomComboBox API directly.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


class TestLinkageAPI:
    """Test linkage functionality using direct API calls."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_dynamic_linkage_creation_via_api(self):
        """
        Test dynamic linkage creation using the CustomComboBox API directly.
        """
        # Enter a template first
        template_input = self.driver.find_element(By.ID, "templateInput")
        template_input.send_keys("As a [Role], I want to [What], so that [Why]")
        time.sleep(1)
        
        # Generate combo boxes
        generate_btn = self.driver.find_element(By.ID, "generateBtn")
        generate_btn.click()
        time.sleep(2)
        
        # Verify combo boxes are initialized
        combo_box_count = self.driver.execute_script("return window.customComboBoxes ? window.customComboBoxes.length : 0;")
        assert combo_box_count == 3, f"Expected 3 combo boxes, got {combo_box_count}"
        
        # Test the dynamic linkage system
        result = self.driver.execute_script("""
            // Get the combo boxes
            const comboBoxes = window.customComboBoxes;
            const roleCombo = comboBoxes[0];  // Role combo box
            const whatCombo = comboBoxes[1];  // What combo box
            
            // Add option "A" to role combo box
            roleCombo.addOption("A");
            
            // Select "A" in role combo box
            roleCombo.setSelectedValue("A");
            
            // Check if current selections are tracked
            const currentSelections = window.currentSelections;
            
            // Add option "A1" to what combo box (should create linkage)
            whatCombo.addOption("A1");
            
            // Check if linkage was created
            const linkageData = window.linkageData;
            
            return {
                roleOptions: roleCombo.options.map(opt => opt.textContent),
                whatOptions: whatCombo.options.map(opt => opt.textContent),
                currentSelections: currentSelections,
                linkageData: linkageData
            };
        """)
        
        print(f"Test result: {result}")
        
        # Verify the role combo box has "A"
        assert "A" in result["roleOptions"], f"Expected 'A' in role options, got {result['roleOptions']}"
        
        # Verify the what combo box has "A1"
        assert "A1" in result["whatOptions"], f"Expected 'A1' in what options, got {result['whatOptions']}"
        
        # Verify current selections are tracked
        assert "Role" in result["currentSelections"], f"Expected 'Role' in current selections, got {result['currentSelections']}"
        assert result["currentSelections"]["Role"] == "A", f"Expected Role selection to be 'A', got {result['currentSelections']['Role']}"
        
        # Verify linkage was created
        assert "A" in result["linkageData"], f"Expected 'A' in linkage data, got {result['linkageData']}"
        assert "What" in result["linkageData"]["A"], f"Expected 'What' linkage for 'A', got {result['linkageData']['A']}"
        assert "A1" in result["linkageData"]["A"]["What"], f"Expected 'A1' in linkage, got {result['linkageData']['A']['What']}"
        
        print("✓ Dynamic linkage creation test passed!")
        print(f"  Role options: {result['roleOptions']}")
        print(f"  What options: {result['whatOptions']}")
        print(f"  Current selections: {result['currentSelections']}")
        print(f"  Linkage data: {result['linkageData']}")
