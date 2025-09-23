"""
Comprehensive test suite for LinkageManager v3.0
Tests the enhanced functionality with GUID template IDs and tag-based identification
"""

import pytest
import json
import os
from pathlib import Path


class TestLinkageManagerV3Structure:
    """Test the enhanced LinkageManager v3.0 structure"""
    
    def test_linkage_manager_v3_file_exists(self):
        """Test that the LinkageManager v3.0 JavaScript file exists"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        assert js_file.exists(), "LinkageManager v3.0 JavaScript file not found"
    
    def test_linkage_manager_v3_class_name(self):
        """Test that the class is named LinkageManager (not LinkageManagerV2)"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should contain the new class name
        assert "class LinkageManager" in content, "Should be named LinkageManager"
        assert "class LinkageManagerV2" not in content, "Should not be LinkageManagerV2"
    
    def test_guid_generation_method(self):
        """Test that GUID generation method exists"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should have GUID generation
        guid_elements = [
            "generateTemplateId(",
            "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx",
            "Math.random()",
            "toString(16)"
        ]
        
        for element in guid_elements:
            assert element in content, f"Missing GUID generation element: {element}"
    
    def test_template_initialization_method(self):
        """Test that template initialization method exists"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should have template initialization
        init_elements = [
            "initializeTemplate(",
            "templateText",
            "tags",
            "this.linkageData[templateId]",
            "this.currentSelections[templateId]",
            "this.comboBoxes[templateId]",
            "this.comboBoxTags[templateId]"
        ]
        
        for element in init_elements:
            assert element in content, f"Missing template initialization element: {element}"
    
    def test_enhanced_data_structure(self):
        """Test that the enhanced data structure is properly defined"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should have enhanced data structure
        data_structure_elements = [
            "this.linkageData = {}",
            "this.currentSelections = {}",
            "this.comboBoxes = {}",
            "this.comboBoxTags = {}",
            "this.currentTemplateId = null"
        ]
        
        for element in data_structure_elements:
            assert element in content, f"Missing enhanced data structure element: {element}"


class TestLinkageManagerV3Methods:
    """Test the new methods in LinkageManager v3.0"""
    
    def test_register_combo_boxes_method(self):
        """Test that registerComboBoxes method exists with new signature"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should have registerComboBoxes with templateId parameter
        register_elements = [
            "registerComboBoxes(",
            "templateId",
            "comboBoxes",
            "this.comboBoxes[templateId] = comboBoxes",
            "setupEventHandlers(templateId)"
        ]
        
        for element in register_elements:
            assert element in content, f"Missing registerComboBoxes element: {element}"
    
    def test_template_storage_methods(self):
        """Test that template storage methods exist"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should have template storage methods
        storage_elements = [
            "saveToTemplateStorage(",
            "loadFromTemplateStorage(",
            "getTemplateLinkageData(",
            "setTemplateLinkageData(",
            "clearTemplateData("
        ]
        
        for element in storage_elements:
            assert element in content, f"Missing template storage method: {element}"
    
    def test_enhanced_linkage_creation(self):
        """Test that linkage creation uses the new structure"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should have enhanced linkage creation
        creation_elements = [
            "createLinkage(templateId, parentTag, parentValue, childTag, optionValue)",
            "this.linkageData[templateId][parentTag][parentValue][childTag]",
            "this.linkageData[templateId][parentTag][parentValue][childTag].push"
        ]
        
        for element in creation_elements:
            assert element in content, f"Missing enhanced linkage creation element: {element}"
    
    def test_enhanced_linkage_restoration(self):
        """Test that linkage restoration uses the new structure"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should have enhanced linkage restoration
        restoration_elements = [
            "restoreChildLinkages(templateId, parentValue, childTag)",
            "this.comboBoxes[templateId]",
            "this.currentSelections[templateId]",
            "this.comboBoxTags[templateId]"
        ]
        
        for element in restoration_elements:
            assert element in content, f"Missing enhanced linkage restoration element: {element}"


class TestLinkageManagerV3DataFormat:
    """Test the enhanced data format for linkages"""
    
    def test_linkage_data_format_v3(self):
        """Test that linkage data uses the new format with template IDs"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should use the new data format
        # Format: {templateId: {parentTag: {parentValue: {childTag: [options]}}}}
        format_elements = [
            "this.linkageData[templateId][parentTag][parentValue][childTag]",
            "this.linkageData[templateId] = {}",
            "this.linkageData[templateId][parentTag] = {}",
            "this.linkageData[templateId][parentTag][parentValue] = {}"
        ]
        
        for element in format_elements:
            assert element in content, f"Missing v3 data format element: {element}"
    
    def test_current_selections_format_v3(self):
        """Test that current selections use the new format with template IDs"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should use the new current selections format
        # Format: {templateId: {tag: selectedValue}}
        format_elements = [
            "this.currentSelections[templateId][tag]",
            "this.currentSelections[templateId][parentTag] = selectedValue",
            "this.currentSelections[templateId] = {}"
        ]
        
        for element in format_elements:
            assert element in content, f"Missing v3 current selections format element: {element}"
    
    def test_combo_boxes_format_v3(self):
        """Test that combo boxes use the new format with template IDs"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should use the new combo boxes format
        # Format: {templateId: {tag: CustomComboBox}}
        format_elements = [
            "this.comboBoxes[templateId] = {}",
            "this.comboBoxes[templateId] = comboBoxes",
            "const comboBoxes = this.comboBoxes[templateId]"
        ]
        
        for element in format_elements:
            assert element in content, f"Missing v3 combo boxes format element: {element}"


class TestLinkageManagerV3BusinessRules:
    """Test the enhanced business rules for linkages"""
    
    def test_template_isolation(self):
        """Test that linkages are isolated by template ID"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should isolate data by template ID
        isolation_elements = [
            "templateId",
            "this.linkageData[templateId]",
            "this.currentSelections[templateId]",
            "this.comboBoxes[templateId]"
        ]
        
        for element in isolation_elements:
            assert element in content, f"Missing template isolation element: {element}"
    
    def test_tag_based_identification(self):
        """Test that combo boxes are identified by tag names"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should use tag-based identification
        tag_elements = [
            "parentTag",
            "childTag",
            "comboBoxes[parentTag]",
            "comboBoxes[childTag]",
            "this.comboBoxTags[templateId]"
        ]
        
        for element in tag_elements:
            assert element in content, f"Missing tag-based identification element: {element}"
    
    def test_enhanced_linkage_creation_rule(self):
        """Test that linkages are created with template context"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should create linkages with template context
        creation_elements = [
            "handleChildOptionAdded(templateId, parentTag, childTag, newOptionValue)",
            "this.currentSelections[templateId][parentTag]",
            "createLinkage(templateId, parentTag, parentSelection, childTag, newOptionValue)"
        ]
        
        for element in creation_elements:
            assert element in content, f"Missing enhanced linkage creation rule element: {element}"
    
    def test_enhanced_linkage_restoration_rule(self):
        """Test that linkages are restored with template context"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should restore linkages with template context
        restoration_elements = [
            "handleParentSelectionChange(templateId, parentTag, childTag, selectedValue)",
            "this.currentSelections[templateId][parentTag] = selectedValue",
            "clearSubsequentComboBoxes(templateId, parentTag)"
        ]
        
        for element in restoration_elements:
            assert element in content, f"Missing enhanced linkage restoration rule element: {element}"


class TestLinkageManagerV3TemplateIntegration:
    """Test template storage integration"""
    
    def test_template_storage_integration(self):
        """Test that template storage integration methods exist"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should have template storage integration
        integration_elements = [
            "getTemplateLinkageData(",
            "setTemplateLinkageData(",
            "templateData = {",
            "linkageData: this.linkageData[templateId]",
            "currentSelections: this.currentSelections[templateId]"
        ]
        
        for element in integration_elements:
            assert element in content, f"Missing template storage integration element: {element}"
    
    def test_local_storage_with_template_id(self):
        """Test that localStorage uses template ID for isolation"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should use template ID in localStorage keys
        storage_elements = [
            "localStorage.setItem(`linkageData_${templateId}`",
            "localStorage.getItem(`linkageData_${templateId}`",
            "localStorage.removeItem(`linkageData_${templateId}`)"
        ]
        
        for element in storage_elements:
            assert element in content, f"Missing localStorage with template ID element: {element}"


class TestLinkageManagerV3ErrorHandling:
    """Test error handling in LinkageManager v3.0"""
    
    def test_enhanced_error_handling(self):
        """Test that error handling exists for template operations"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should have error handling for template operations
        error_elements = [
            "try {",
            "catch (error) {",
            "console.error",
            "Error loading linkage data"
        ]
        
        for element in error_elements:
            assert element in content, f"Missing enhanced error handling element: {element}"
    
    def test_template_id_validation(self):
        """Test that template ID validation exists"""
        js_file = Path("src/prompt_manager/static/js/linkage-manager-v3.js")
        content = js_file.read_text()
        
        # Should validate template ID in operations
        validation_elements = [
            "if (!this.linkageData[templateId])",
            "this.linkageData[templateId] = {}",
            "this.currentSelections[templateId] = {}"
        ]
        
        for element in validation_elements:
            assert element in content, f"Missing template ID validation element: {element}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
