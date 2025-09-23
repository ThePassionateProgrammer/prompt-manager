"""
TemplateManager - Business logic for managing prompt templates.

This module handles the business logic for creating, validating, and managing
prompt templates with their associated combo box values and linkage data.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import re


class TemplateManager:
    """Manages prompt templates with their associated data."""
    
    def __init__(self):
        """Initialize the TemplateManager."""
        self._templates: Dict[str, Dict[str, Any]] = {}
    
    def create_template(self, name: str, description: str, template_text: str, 
                       combo_box_values: Dict[str, List[str]], 
                       linkage_data: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
        """
        Create a new template with the given data.
        
        Args:
            name: Unique template name
            description: Template description
            template_text: The template text with [tags]
            combo_box_values: Dictionary of tag -> list of values
            linkage_data: Dictionary of parent -> child linkages
            
        Returns:
            Dictionary containing the created template data
            
        Raises:
            ValueError: If template name is not unique or template text is invalid
        """
        if name in self._templates:
            raise ValueError("Template name must be unique")
        
        if not self.validate_template_text(template_text):
            raise ValueError("Template text contains malformed tags")
        
        now = datetime.utcnow().isoformat()
        
        template_data = {
            "name": name,
            "description": description,
            "template_text": template_text,
            "combo_box_values": combo_box_values,
            "linkage_data": linkage_data,
            "created_at": now,
            "updated_at": now
        }
        
        self._templates[name] = template_data
        return template_data
    
    def validate_template_text(self, template_text: str) -> bool:
        """
        Validate that template text has well-formed tags.
        
        Args:
            template_text: The template text to validate
            
        Returns:
            True if all tags are well-formed, False otherwise
        """
        # Find all [tags] in the template
        tag_pattern = r'\[([^\]]*)\]'
        tags = re.findall(tag_pattern, template_text)
        
        # Check that all [ and ] are properly paired
        open_brackets = template_text.count('[')
        close_brackets = template_text.count(']')
        
        if open_brackets != close_brackets:
            return False
        
        # Check that all tags are non-empty
        for tag in tags:
            if not tag.strip():
                return False
        
        return True
    
    def get_template(self, name: str) -> Dict[str, Any]:
        """
        Get a template by name.
        
        Args:
            name: Template name
            
        Returns:
            Template data dictionary
            
        Raises:
            ValueError: If template is not found
        """
        if name not in self._templates:
            raise ValueError("Template not found")
        
        return self._templates[name]
    
    def list_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        List all templates.
        
        Returns:
            Dictionary of template name -> template data
        """
        return self._templates.copy()
    
    def update_template(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Update an existing template.
        
        Args:
            name: Template name
            **kwargs: Fields to update
            
        Returns:
            Updated template data
            
        Raises:
            ValueError: If template is not found or validation fails
        """
        if name not in self._templates:
            raise ValueError("Template not found")
        
        # Validate template_text if it's being updated
        if 'template_text' in kwargs:
            if not self.validate_template_text(kwargs['template_text']):
                raise ValueError("Template text contains malformed tags")
        
        # Update the template
        template = self._templates[name]
        for key, value in kwargs.items():
            if key in template:
                template[key] = value
        
        template['updated_at'] = datetime.utcnow().isoformat()
        return template
    
    def delete_template(self, name: str) -> bool:
        """
        Delete a template.
        
        Args:
            name: Template name
            
        Returns:
            True if deleted, False if not found
        """
        if name in self._templates:
            del self._templates[name]
            return True
        return False
