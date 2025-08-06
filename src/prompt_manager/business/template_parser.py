import re
from typing import List


class TemplateParser:
    """Parse template strings to extract tags and manage template operations."""
    
    def extract_tags(self, template: str) -> List[str]:
        """
        Extract unique tags from a template string.
        
        Args:
            template: Template string containing tags in brackets [TagName]
            
        Returns:
            List of unique tag names in order of appearance
        """
        if not template:
            return []
        
        # Find all tags in brackets, handling whitespace
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, template)
        
        # Clean up whitespace and get unique tags in order
        tags = []
        seen = set()
        
        for match in matches:
            tag = match.strip()
            if tag and tag not in seen:
                tags.append(tag)
                seen.add(tag)
        
        return tags 