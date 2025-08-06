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