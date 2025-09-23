"""
TemplateService - Integration layer for template management.

This module provides a high-level service that combines TemplateManager
business logic with TemplateStorage persistence.
"""

from typing import Dict, List, Any
from .template_manager import TemplateManager
from .template_storage import TemplateStorage


class TemplateService:
    """High-level service for template management with persistence."""
    
    def __init__(self, storage_file_path: str):
        """
        Initialize the TemplateService.
        
        Args:
            storage_file_path: Path to the JSON file for storing templates
        """
        self.template_manager = TemplateManager()
        self.template_storage = TemplateStorage(storage_file_path)
    
    def save_template(self, name: str, description: str, template_text: str,
                     combo_box_values: Dict[str, List[str]], 
                     linkage_data: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
        """
        Save a template with validation and persistence.
        
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
        # Create template using business logic
        template_data = self.template_manager.create_template(
            name=name,
            description=description,
            template_text=template_text,
            combo_box_values=combo_box_values,
            linkage_data=linkage_data
        )
        
        # Persist to storage
        self.template_storage.save_template(template_data)
        
        return template_data
    
    def load_template(self, name: str) -> Dict[str, Any]:
        """
        Load a template by name.
        
        Args:
            name: Template name
            
        Returns:
            Template data dictionary
            
        Raises:
            ValueError: If template is not found
        """
        return self.template_storage.load_template(name)
    
    def list_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        List all templates.
        
        Returns:
            Dictionary of template name -> template data
        """
        return self.template_storage.list_templates()
    
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
        # Load existing template
        existing_template = self.template_storage.load_template(name)
        
        # Update using business logic
        updated_template = self.template_manager.update_template(name, **kwargs)
        
        # Persist changes
        self.template_storage.save_template(updated_template)
        
        return updated_template
    
    def delete_template(self, name: str) -> bool:
        """
        Delete a template.
        
        Args:
            name: Template name
            
        Returns:
            True if deleted, False if not found
        """
        # Delete from business logic
        result = self.template_manager.delete_template(name)
        
        # Delete from storage
        if result:
            self.template_storage.delete_template(name)
        
        return result
    
    def template_exists(self, name: str) -> bool:
        """
        Check if a template exists.
        
        Args:
            name: Template name
            
        Returns:
            True if template exists, False otherwise
        """
        return self.template_storage.template_exists(name)
    
    def get_template_count(self) -> int:
        """
        Get the number of templates.
        
        Returns:
            Number of templates
        """
        return self.template_storage.get_template_count()
    
    def validate_template_text(self, template_text: str) -> bool:
        """
        Validate template text without saving.
        
        Args:
            template_text: The template text to validate
            
        Returns:
            True if valid, False otherwise
        """
        return self.template_manager.validate_template_text(template_text)
