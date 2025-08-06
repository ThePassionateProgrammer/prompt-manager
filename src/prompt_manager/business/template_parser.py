import re
from typing import List, Dict, Any


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
    
    def generate_combo_boxes(self, template: str) -> List[Dict[str, Any]]:
        """
        Generate combo box data structures from a template.
        
        Args:
            template: Template string containing tags in brackets [TagName]
            
        Returns:
            List of combo box configurations with tag names and enabled states
        """
        tags = self.extract_tags(template)
        combo_boxes = []
        
        for i, tag in enumerate(tags):
            combo_box = {
                "tag": tag,
                "enabled": i == 0,  # Only first combo box is enabled initially
                "index": i,
                "value": "",  # Empty initial value
                "options": []  # Will be populated from component data later
            }
            combo_boxes.append(combo_box)
        
        return combo_boxes 