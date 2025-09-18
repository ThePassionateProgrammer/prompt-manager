"""
Test linkage restoration functionality.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


class TestLinkageRestoration:
    """Test that linkages are properly restored when switching between parent options."""
    
    def setup_method(self):
        """Set up the test environment."""
        self.driver = webdriver.Chrome()
        self.driver.get("http://localhost:8000/template-builder")
        time.sleep(3)  # Wait for page to load
        
    def teardown_method(self):
        """Clean up after each test."""
        self.driver.quit()
    
    def test_linkage_restoration_workflow(self):
        """
        Test the complete workflow: create linkages for A, create linkages for B, 
        then switch back to A and verify A's linkages are restored.
        """
        # Enter a template first
        template_input = self.driver.find_element(By.ID, "templateInput")
        template_input.send_keys("As a [Role], I want to [What], so that [Why]")
        time.sleep(1)
        
        # Generate combo boxes
        generate_btn = self.driver.find_element(By.ID, "generateBtn")
        generate_btn.click()
        time.sleep(2)
        
        # Test the complete linkage restoration workflow
        result = self.driver.execute_script("""
            // Get the combo boxes
            const comboBoxes = window.customComboBoxes;
            const roleCombo = comboBoxes[0];  // Role combo box
            const whatCombo = comboBoxes[1];  // What combo box
            
            // Step 1: Add option "A" to role combo box and select it
            roleCombo.addOption("A");
            roleCombo.setSelectedValue("A");
            
            // Step 2: Add options "A1", "A2" to what combo box (create linkages for A)
            whatCombo.addOption("A1");
            whatCombo.addOption("A2");
            
            // Step 3: Add option "B" to role combo box and select it
            roleCombo.addOption("B");
            roleCombo.setSelectedValue("B");
            
            // Step 4: Add options "B1", "B2" to what combo box (create linkages for B)
            whatCombo.addOption("B1");
            whatCombo.addOption("B2");
            
            // Step 5: Switch back to "A" and check if A's linkages are restored
            roleCombo.setSelectedValue("A");
            
            // Get current state
            const currentSelections = window.currentSelections;
            const linkageData = window.linkageData;
            const whatOptions = whatCombo.options.map(opt => opt.textContent);
            
            return {
                currentSelections: currentSelections,
                linkageData: linkageData,
                whatOptions: whatOptions,
                roleOptions: roleCombo.options.map(opt => opt.textContent)
            };
        """)
        
        print(f"Test result: {result}")
        
        # Verify linkage data contains both A and B linkages
        assert "A" in result["linkageData"], f"Expected 'A' in linkage data, got {result['linkageData']}"
        assert "B" in result["linkageData"], f"Expected 'B' in linkage data, got {result['linkageData']}"
        assert "What" in result["linkageData"]["A"], f"Expected 'What' linkage for 'A', got {result['linkageData']['A']}"
        assert "What" in result["linkageData"]["B"], f"Expected 'What' linkage for 'B', got {result['linkageData']['B']}"
        
        # Verify A's linkages contain A1 and A2
        assert "A1" in result["linkageData"]["A"]["What"], f"Expected 'A1' in A's linkages, got {result['linkageData']['A']['What']}"
        assert "A2" in result["linkageData"]["A"]["What"], f"Expected 'A2' in A's linkages, got {result['linkageData']['A']['What']}"
        
        # Verify B's linkages contain B1 and B2
        assert "B1" in result["linkageData"]["B"]["What"], f"Expected 'B1' in B's linkages, got {result['linkageData']['B']['What']}"
        assert "B2" in result["linkageData"]["B"]["What"], f"Expected 'B2' in B's linkages, got {result['linkageData']['B']['What']}"
        
        # Verify current selection is A
        assert result["currentSelections"]["Role"] == "A", f"Expected Role selection to be 'A', got {result['currentSelections']['Role']}"
        
        # CRITICAL: Verify that when we switch back to A, the What combo box shows A1 and A2
        assert "A1" in result["whatOptions"], f"Expected 'A1' in what options when A is selected, got {result['whatOptions']}"
        assert "A2" in result["whatOptions"], f"Expected 'A2' in what options when A is selected, got {result['whatOptions']}"
        
        # Verify B1 and B2 are NOT shown when A is selected
        assert "B1" not in result["whatOptions"], f"Expected 'B1' NOT in what options when A is selected, got {result['whatOptions']}"
        assert "B2" not in result["whatOptions"], f"Expected 'B2' NOT in what options when A is selected, got {result['whatOptions']}"
        
        print("✓ Linkage restoration test passed!")
        print(f"  Role options: {result['roleOptions']}")
        print(f"  What options when A selected: {result['whatOptions']}")
        print(f"  Current selections: {result['currentSelections']}")
        print(f"  Linkage data: {result['linkageData']}")
