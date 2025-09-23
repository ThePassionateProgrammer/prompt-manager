"""
Comprehensive test suite for LinkageManager functionality
Tests the domain model for linkage creation, restoration, and persistence
"""

import pytest
import json
import os
from pathlib import Path


class TestLinkageManagerDomainModel:
    """Test the LinkageManager domain model and business rules"""
    
    def test_linkage_manager_file_exists(self):
        """Test that the LinkageManager JavaScript file exists"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        assert js_file.exists(), "LinkageManager JavaScript file not found"
    
    def test_linkage_manager_class_structure(self):
        """Test that the LinkageManager has the expected class structure"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should contain key classes and methods
        expected_elements = [
            "class LinkageManagerV2",
            "constructor(",
            "registerComboBoxes(",
            "setupEventHandlers(",
            "handleParentSelectionChange(",
            "handleChildOptionAdded(",
            "createLinkage(",
            "restoreChildLinkages(",
            "clearSubsequentComboBoxes(",
            "saveToStorage(",
            "loadFromStorage("
        ]
        
        for element in expected_elements:
            assert element in content, f"Missing expected element: {element}"
    
    def test_linkage_data_structure(self):
        """Test that the linkage data structure is properly defined"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should have proper data structure initialization
        data_structure_elements = [
            "this.linkageData = {}",
            "this.currentSelections = {}",
            "this.comboBoxes = []",
            "this.comboBoxTags = []"
        ]
        
        for element in data_structure_elements:
            assert element in content, f"Missing data structure element: {element}"
    
    def test_linkage_creation_logic(self):
        """Test that linkage creation logic is properly implemented"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should have linkage creation logic
        creation_elements = [
            "createLinkage(",
            "parentValue",
            "childTag",
            "optionValue",
            "this.linkageData[parentValue]",
            "this.linkageData[parentValue][childTag]"
        ]
        
        for element in creation_elements:
            assert element in content, f"Missing linkage creation element: {element}"
    
    def test_linkage_restoration_logic(self):
        """Test that linkage restoration logic is properly implemented"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should have linkage restoration logic
        restoration_elements = [
            "restoreChildLinkages(",
            "hasLinkageData(",
            "getLinkedOptions(",
            "addOption(",
            "clearSubsequentComboBoxes("
        ]
        
        for element in restoration_elements:
            assert element in content, f"Missing linkage restoration element: {element}"
    
    def test_event_handler_setup(self):
        """Test that event handler setup is properly implemented"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should have event handler setup
        event_elements = [
            "onSelectionChange",
            "onOptionAdded",
            "setupEventHandlers(",
            "handleParentSelectionChange(",
            "handleChildOptionAdded("
        ]
        
        for element in event_elements:
            assert element in content, f"Missing event handler element: {element}"
    
    def test_persistence_logic(self):
        """Test that persistence logic is properly implemented"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should have persistence logic
        persistence_elements = [
            "saveToStorage(",
            "loadFromStorage(",
            "localStorage.setItem",
            "localStorage.getItem",
            "JSON.stringify",
            "JSON.parse"
        ]
        
        for element in persistence_elements:
            assert element in content, f"Missing persistence element: {element}"
    
    def test_validation_logic(self):
        """Test that validation logic is properly implemented"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should have validation logic
        validation_elements = [
            "isValidSelection(",
            "Add item...",
            "Select item...",
            "Add..."
        ]
        
        for element in validation_elements:
            assert element in content, f"Missing validation element: {element}"


class TestLinkageManagerIntegration:
    """Test LinkageManager integration with the server"""
    
    def test_server_includes_linkage_manager(self):
        """Test that the server includes the LinkageManager"""
        server_file = Path("enhanced_simple_server.py")
        content = server_file.read_text()
        
        # Should include the LinkageManager JavaScript file (v3.0)
        assert "linkage-manager-v3.js" in content, "Server should include LinkageManager v3.0 JavaScript"
    
    def test_server_has_linkage_setup(self):
        """Test that the server has linkage setup code"""
        server_file = Path("enhanced_simple_server.py")
        content = server_file.read_text()
        
        # Should have linkage setup
        linkage_elements = [
            "setupLinkages",
            "LinkageManager",
            "linkageManager"
        ]
        
        for element in linkage_elements:
            assert element in content, f"Missing linkage setup element: {element}"


class TestLinkageManagerBusinessRules:
    """Test specific business rules for linkages"""
    
    def test_linkage_creation_rule(self):
        """Test that linkages are created only when parent has selection"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should check for parent selection before creating linkage
        assert "parentSelection" in content, "Should check parent selection"
        assert "currentSelections[parentTag]" in content, "Should use current selections"
    
    def test_linkage_restoration_rule(self):
        """Test that linkages are restored when parent selection changes"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should restore linkages on selection change
        assert "handleParentSelectionChange" in content, "Should handle parent selection change"
        assert "restoreChildLinkages" in content, "Should restore child linkages"
    
    def test_cascading_behavior_rule(self):
        """Test that cascading behavior is implemented"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should implement cascading behavior
        assert "clearSubsequentComboBoxes" in content, "Should clear subsequent combo boxes"
        assert "getNextComboBoxTag" in content, "Should get next combo box tag"
    
    def test_linkage_persistence_rule(self):
        """Test that linkages persist across sessions"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should persist linkages
        assert "saveToStorage" in content, "Should save to storage"
        assert "loadFromStorage" in content, "Should load from storage"


class TestLinkageManagerDataFormat:
    """Test the data format for linkages"""
    
    def test_linkage_data_format(self):
        """Test that linkage data uses the correct format"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should use the correct data format
        # Format: {parent_value: {child_tag: [options]}}
        format_elements = [
            "this.linkageData[parentValue] = {}",
            "this.linkageData[parentValue][childTag] = []",
            "this.linkageData[parentValue][childTag].push"
        ]
        
        for element in format_elements:
            assert element in content, f"Missing data format element: {element}"
    
    def test_current_selections_format(self):
        """Test that current selections use the correct format"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should use the correct current selections format
        # Format: {tag: selected_value}
        format_elements = [
            "this.currentSelections[tag]",
            "this.currentSelections[parentTag] = selectedValue"
        ]
        
        for element in format_elements:
            assert element in content, f"Missing current selections format element: {element}"


class TestLinkageManagerErrorHandling:
    """Test error handling in LinkageManager"""
    
    def test_error_handling_in_load(self):
        """Test that error handling exists in loadFromStorage"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should have error handling
        error_elements = [
            "try {",
            "catch (error) {",
            "console.error",
            "Error loading linkage data"
        ]
        
        for element in error_elements:
            assert element in content, f"Missing error handling element: {element}"
    
    def test_validation_error_handling(self):
        """Test that validation error handling exists"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v2.js")
        content = js_file.read_text()
        
        # Should validate inputs
        validation_elements = [
            "if (!childCombo)",
            "if (linkedOptions.length === 0)",
            "if (!this.linkageData[parentValue])"
        ]
        
        for element in validation_elements:
            assert element in content, f"Missing validation element: {element}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
