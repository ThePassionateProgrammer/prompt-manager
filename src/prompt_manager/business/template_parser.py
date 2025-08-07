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
                "options": [],  # Will be populated from component data later
                "is_custom": False  # Track if user entered custom text
            }
            combo_boxes.append(combo_box)
        
        return combo_boxes
    
    def update_cascading_selections(self, combo_boxes: List[Dict[str, Any]], 
                                  changed_index: int) -> List[Dict[str, Any]]:
        """
        Update combo boxes when a selection changes, resetting downstream selections.
        
        Args:
            combo_boxes: List of combo box configurations
            changed_index: Index of the combo box that was changed
            
        Returns:
            Updated combo boxes with downstream selections reset
        """
        # Reset all combo boxes downstream from the changed one
        for i in range(changed_index + 1, len(combo_boxes)):
            combo_boxes[i]["value"] = ""
            combo_boxes[i]["enabled"] = False
            combo_boxes[i]["options"] = []
            combo_boxes[i]["is_custom"] = False
        
        # Enable the next combo box if there is one
        if changed_index + 1 < len(combo_boxes):
            combo_boxes[changed_index + 1]["enabled"] = True
        
        return combo_boxes
    
    def generate_prompt_from_selections(self, template: str, combo_boxes: List[Dict[str, Any]]) -> str:
        """
        Generate the final prompt by replacing tags with selected values.
        
        Args:
            template: Original template string with tags
            combo_boxes: List of combo box configurations with selected values
            
        Returns:
            Final prompt with tags replaced by selections
        """
        result = template
        
        # Replace each tag with its selected value
        for combo_box in combo_boxes:
            tag = combo_box["tag"]
            value = combo_box.get("value", "")
            
            # Replace the tag in the template
            tag_pattern = f"[{tag}]"
            result = result.replace(tag_pattern, value)
        
        return result 