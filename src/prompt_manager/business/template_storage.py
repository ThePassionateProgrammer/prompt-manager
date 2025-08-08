import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class TemplateStorage:
    """Manage template storage and retrieval."""
    
    def __init__(self, storage_file: Optional[str] = None):
        """
        Initialize template storage.
        
        Args:
            storage_file: Path to JSON file for storing templates
        """
        if storage_file is None:
            storage_file = Path(__file__).parent.parent.parent / "templates.json"
        
        self.storage_file = Path(storage_file)
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load templates from JSON file."""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            else:
                return {"templates": {}}
        except (json.JSONDecodeError, FileNotFoundError):
            return {"templates": {}}
    
    def _save_templates(self) -> None:
        """Save templates to JSON file."""
        try:
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_file, 'w') as f:
                json.dump(self.templates, f, indent=2)
        except Exception as e:
            raise IOError(f"Failed to save templates: {e}")
    
    def save_template(self, template_data: Dict[str, Any]) -> str:
        """
        Save a template with its state.
        
        Args:
            template_data: Template data including name, description, template string, and combo boxes
            
        Returns:
            Template ID
        """
        # Generate unique ID
        template_id = str(uuid.uuid4())
        
        # Add metadata
        template_data["id"] = template_id
        template_data["created_date"] = template_data.get("created_date", datetime.now().isoformat())
        template_data["updated_date"] = datetime.now().isoformat()
        
        # Save to storage
        self.templates["templates"][template_id] = template_data
        self._save_templates()
        
        return template_id
    
    def load_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a template by ID.
        
        Args:
            template_id: Unique template identifier
            
        Returns:
            Template data or None if not found
        """
        return self.templates["templates"].get(template_id)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all saved templates.
        
        Returns:
            List of template summaries (id, name, description, created_date)
        """
        templates = []
        for template_id, template_data in self.templates["templates"].items():
            templates.append({
                "id": template_id,
                "name": template_data.get("name", "Unnamed Template"),
                "description": template_data.get("description", ""),
                "created_date": template_data.get("created_date", ""),
                "updated_date": template_data.get("updated_date", "")
            })
        
        # Sort by updated date (newest first)
        templates.sort(key=lambda x: x.get("updated_date", ""), reverse=True)
        return templates
    
    def update_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """
        Update an existing template.
        
        Args:
            template_id: Unique template identifier
            template_data: Updated template data
            
        Returns:
            True if successful, False if template not found
        """
        if template_id not in self.templates["templates"]:
            return False
        
        # Preserve original created_date
        original_template = self.templates["templates"][template_id]
        template_data["created_date"] = original_template.get("created_date")
        template_data["updated_date"] = datetime.now().isoformat()
        template_data["id"] = template_id
        
        self.templates["templates"][template_id] = template_data
        self._save_templates()
        
        return True
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: Unique template identifier
            
        Returns:
            True if successful, False if template not found
        """
        if template_id not in self.templates["templates"]:
            return False
        
        del self.templates["templates"][template_id]
        self._save_templates()
        
        return True
    
    def template_exists(self, template_id: str) -> bool:
        """
        Check if a template exists.
        
        Args:
            template_id: Unique template identifier
            
        Returns:
            True if template exists, False otherwise
        """
        return template_id in self.templates["templates"]
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """
        Search templates by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching template summaries
        """
        query = query.lower()
        matches = []
        
        for template_id, template_data in self.templates["templates"].items():
            name = template_data.get("name", "").lower()
            description = template_data.get("description", "").lower()
            template_text = template_data.get("template", "").lower()
            
            if (query in name or 
                query in description or 
                query in template_text):
                matches.append({
                    "id": template_id,
                    "name": template_data.get("name", "Unnamed Template"),
                    "description": template_data.get("description", ""),
                    "created_date": template_data.get("created_date", ""),
                    "updated_date": template_data.get("updated_date", "")
                })
        
        return matches
