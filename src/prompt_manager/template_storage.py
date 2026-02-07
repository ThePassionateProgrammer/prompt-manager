"""
TemplateStorage - Persistence layer for prompt templates.

This module handles saving and loading prompt templates to/from JSON files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List


class TemplateStorage:
    """Handles persistence of prompt templates to JSON files."""
    
    def __init__(self, file_path: str):
        """
        Initialize the TemplateStorage.
        
        Args:
            file_path: Path to the JSON file for storing templates
        """
        self.file_path = Path(file_path)
        self._ensure_directory_exists()
    
    def _ensure_directory_exists(self):
        """Ensure the directory for the storage file exists."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_templates_file(self) -> Dict[str, Any]:
        """
        Load templates from the JSON file.
        
        Returns:
            Dictionary of template data
            
        Raises:
            ValueError: If the file is corrupted or cannot be read
        """
        if not self.file_path.exists():
            return {}
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise ValueError("Corrupted template file")
        except Exception as e:
            raise ValueError(f"Error reading template file: {str(e)}")
    
    def _save_templates_file(self, templates: Dict[str, Any]):
        """
        Save templates to the JSON file.
        
        Args:
            templates: Dictionary of template data to save
        """
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)
    
    def save_template(self, template_data: Dict[str, Any]):
        """
        Save a template to the storage file.
        
        Args:
            template_data: Template data dictionary
        """
        templates = self._load_templates_file()
        templates[template_data["name"]] = template_data
        self._save_templates_file(templates)
    
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
        templates = self._load_templates_file()
        if name not in templates:
            raise ValueError("Template not found")
        
        return templates[name]
    
    def list_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        List all templates in the storage file.
        
        Returns:
            Dictionary of template name -> template data
        """
        return self._load_templates_file()
    
    def delete_template(self, name: str) -> bool:
        """
        Delete a template from the storage file.
        
        Args:
            name: Template name
            
        Returns:
            True if deleted, False if not found
        """
        templates = self._load_templates_file()
        if name not in templates:
            return False
        
        del templates[name]
        self._save_templates_file(templates)
        return True
    
    def template_exists(self, name: str) -> bool:
        """
        Check if a template exists in the storage file.
        
        Args:
            name: Template name
            
        Returns:
            True if template exists, False otherwise
        """
        templates = self._load_templates_file()
        return name in templates
    
    def get_template_count(self) -> int:
        """
        Get the number of templates in the storage file.
        
        Returns:
            Number of templates
        """
        templates = self._load_templates_file()
        return len(templates)
