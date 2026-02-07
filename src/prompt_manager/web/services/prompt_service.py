"""
Prompt Service

Handles prompt CRUD operations, search, and validation.
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from src.prompt_manager.prompt_manager import PromptManager


class PromptService:
    """Service for prompt operations."""
    
    def __init__(self):
        self.prompt_manager = PromptManager()
    
    def get_all_prompts(self) -> List[Dict]:
        """Get all prompts."""
        return self.prompt_manager.get_all_prompts()
    
    def search_prompts(self, query: str) -> List[Dict]:
        """Search prompts by query."""
        if not query:
            return self.get_all_prompts()
        
        all_prompts = self.get_all_prompts()
        query_lower = query.lower()
        
        filtered_prompts = []
        for prompt in all_prompts:
            if (query_lower in prompt.get('name', '').lower() or 
                query_lower in prompt.get('text', '').lower() or
                query_lower in prompt.get('category', '').lower()):
                filtered_prompts.append(prompt)
        
        return filtered_prompts
    
    def create_prompt(self, name: str, text: str, category: str) -> Tuple[bool, str]:
        """Create a new prompt."""
        if not name or not text:
            return False, "Name and text are required"
        
        if len(name) > 100:
            return False, "Name must be 100 characters or less"
        
        if len(text) > 5000:
            return False, "Text must be 5000 characters or less"
        
        try:
            self.prompt_manager.add_prompt(name, text, category)
            return True, "Prompt created successfully"
        except Exception as e:
            return False, f"Error creating prompt: {str(e)}"
    
    def update_prompt(self, prompt_id: str, name: str, text: str, category: str) -> Tuple[bool, str]:
        """Update an existing prompt."""
        if not prompt_id or not name or not text:
            return False, "Prompt ID, name, and text are required"
        
        if len(name) > 100:
            return False, "Name must be 100 characters or less"
        
        if len(text) > 5000:
            return False, "Text must be 5000 characters or less"
        
        try:
            # Get existing prompt to preserve other fields
            all_prompts = self.get_all_prompts()
            existing_prompt = None
            for prompt in all_prompts:
                if prompt.get('id') == prompt_id:
                    existing_prompt = prompt
                    break
            
            if not existing_prompt:
                return False, "Prompt not found"
            
            # Update fields
            existing_prompt['name'] = name
            existing_prompt['text'] = text
            existing_prompt['category'] = category
            existing_prompt['modified_at'] = datetime.now().isoformat()
            
            # Save updated prompts
            self.prompt_manager.save_prompts(all_prompts)
            return True, "Prompt updated successfully"
        except Exception as e:
            return False, f"Error updating prompt: {str(e)}"
    
    def delete_prompt(self, prompt_id: str) -> Tuple[bool, str]:
        """Delete a prompt."""
        if not prompt_id:
            return False, "Prompt ID is required"
        
        try:
            all_prompts = self.get_all_prompts()
            updated_prompts = [p for p in all_prompts if p.get('id') != prompt_id]
            
            if len(updated_prompts) == len(all_prompts):
                return False, "Prompt not found"
            
            self.prompt_manager.save_prompts(updated_prompts)
            return True, "Prompt deleted successfully"
        except Exception as e:
            return False, f"Error deleting prompt: {str(e)}"
    
    def get_prompt_by_id(self, prompt_id: str) -> Optional[Dict]:
        """Get a prompt by ID."""
        all_prompts = self.get_all_prompts()
        for prompt in all_prompts:
            if prompt.get('id') == prompt_id:
                return prompt
        return None
    
    def export_prompts(self) -> str:
        """Export all prompts as JSON."""
        prompts = self.get_all_prompts()
        return json.dumps(prompts, indent=2)
    
    def import_prompts(self, json_data: str) -> Tuple[bool, str]:
        """Import prompts from JSON."""
        try:
            prompts = json.loads(json_data)
            if not isinstance(prompts, list):
                return False, "Invalid format: expected list of prompts"
            
            # Validate each prompt
            for prompt in prompts:
                if not isinstance(prompt, dict):
                    return False, "Invalid prompt format"
                if 'name' not in prompt or 'text' not in prompt:
                    return False, "Prompt missing required fields"
            
            # Import prompts
            self.prompt_manager.save_prompts(prompts)
            return True, f"Successfully imported {len(prompts)} prompts"
        except json.JSONDecodeError:
            return False, "Invalid JSON format"
        except Exception as e:
            return False, f"Error importing prompts: {str(e)}"
    
    def get_categories(self) -> List[str]:
        """Get all unique categories."""
        prompts = self.get_all_prompts()
        categories = set()
        for prompt in prompts:
            category = prompt.get('category', 'Uncategorized')
            if category:
                categories.add(category)
        return sorted(list(categories))
