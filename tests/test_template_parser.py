import pytest
from prompt_manager.business.template_parser import TemplateParser


class TestTemplateParser:
    """Test template parsing functionality."""
    
    def test_extract_tags_from_simple_template(self):
        """Test extracting tags from a simple template."""
        parser = TemplateParser()
        template = "As a [Role], I want to [What], so that I can [Why]"
        
        tags = parser.extract_tags(template)
        
        assert tags == ["Role", "What", "Why"]
    
    def test_extract_tags_from_template_with_no_tags(self):
        """Test extracting tags from template with no tags."""
        parser = TemplateParser()
        template = "This is a simple prompt with no tags"
        
        tags = parser.extract_tags(template)
        
        assert tags == []
    
    def test_extract_tags_from_template_with_duplicate_tags(self):
        """Test extracting tags when same tag appears multiple times."""
        parser = TemplateParser()
        template = "As a [Role], I want to [What], so that I can [Why]. The [Role] will benefit from this."
        
        tags = parser.extract_tags(template)
        
        assert tags == ["Role", "What", "Why"]
    
    def test_extract_tags_with_whitespace(self):
        """Test extracting tags with various whitespace patterns."""
        parser = TemplateParser()
        template = "As a [ Role ], I want to [ What ], so that I can [ Why ]"
        
        tags = parser.extract_tags(template)
        
        assert tags == ["Role", "What", "Why"]
    
    def test_generate_combo_boxes_from_template(self):
        """Test generating combo box data from a template."""
        parser = TemplateParser()
        template = "As a [Role], I want to [What], so that I can [Why]"
        
        combo_boxes = parser.generate_combo_boxes(template)
        
        assert len(combo_boxes) == 3
        assert combo_boxes[0]["tag"] == "Role"
        assert combo_boxes[1]["tag"] == "What"
        assert combo_boxes[2]["tag"] == "Why"
        assert combo_boxes[0]["enabled"] == True
        assert combo_boxes[1]["enabled"] == False  # Disabled until Role is selected
        assert combo_boxes[2]["enabled"] == False  # Disabled until What is selected 