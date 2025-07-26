import uuid
from typing import Dict, List, Optional
from .prompt import Prompt
from .storage import StorageManager


class PromptManager:
    def __init__(self, storage_file: str = "prompts.json"):
        self.storage = StorageManager(storage_file)
        self.prompts: Dict[str, Prompt] = {}
        self.load_prompts()
    
    def load_prompts(self):
        """Load prompts from storage."""
        self.prompts = self.storage.load_prompts()
    
    def save_prompts(self) -> bool:
        """Save prompts to storage."""
        return self.storage.save_prompts(self.prompts)
    
    def add_prompt(self, name: str, text: str, category: str = "general") -> str:
        """Add a new prompt and return its GUID."""
        prompt_id = str(uuid.uuid4())
        prompt = Prompt(name, text, category)
        prompt.id = prompt_id
        self.prompts[prompt_id] = prompt
        self.save_prompts()
        return prompt_id
    
    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Get a prompt by its GUID."""
        return self.prompts.get(prompt_id)
    
    def get_prompt_by_name(self, name: str) -> Optional[Prompt]:
        """Get a prompt by its name (returns first match)."""
        for prompt in self.prompts.values():
            if prompt.name == name:
                return prompt
        return None
    
    def list_prompts(self, category: Optional[str] = None) -> List[Prompt]:
        """List all prompts, optionally filtered by category."""
        if category is None:
            return list(self.prompts.values())
        return [prompt for prompt in self.prompts.values() if prompt.category == category]
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt by its GUID. Returns True if deleted, False if not found."""
        if prompt_id in self.prompts:
            del self.prompts[prompt_id]
            self.save_prompts()
            return True
        return False
    
    def update_prompt(self, prompt_id: str, name: Optional[str] = None, 
                     text: Optional[str] = None, category: Optional[str] = None) -> bool:
        """Update a prompt's attributes. Returns True if updated, False if not found."""
        if prompt_id not in self.prompts:
            return False
        
        prompt = self.prompts[prompt_id]
        if name is not None:
            prompt.name = name
        if text is not None:
            prompt.update_text(text)
        if category is not None:
            prompt.category = category
        
        self.save_prompts()
        return True
    
    def search_prompts(self, query: str) -> List[Prompt]:
        """Search prompts by name or text content."""
        query_lower = query.lower()
        results = []
        for prompt in self.prompts.values():
            if (query_lower in prompt.name.lower() or 
                query_lower in prompt.text.lower()):
                results.append(prompt)
        return results 