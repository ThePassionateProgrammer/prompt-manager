import json
import os
from typing import Dict, List
from .prompt import Prompt


class StorageManager:
    def __init__(self, file_path: str = "prompts.json"):
        self.file_path = file_path
    
    def save_prompts(self, prompts: Dict[str, Prompt]) -> bool:
        """Save prompts to JSON file. Returns True on success, False on error."""
        try:
            data = {
                'prompts': {
                    prompt_id: prompt.to_dict() 
                    for prompt_id, prompt in prompts.items()
                }
            }
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving prompts: {e}")
            return False
    
    def load_prompts(self) -> Dict[str, Prompt]:
        """Load prompts from JSON file. Returns empty dict if file doesn't exist or error."""
        if not os.path.exists(self.file_path):
            return {}
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            prompts = {}
            for prompt_id, prompt_data in data.get('prompts', {}).items():
                prompt = Prompt.from_dict(prompt_data)
                prompts[prompt_id] = prompt
            
            return prompts
        except Exception as e:
            print(f"Error loading prompts: {e}")
            return {}
    
    def file_exists(self) -> bool:
        """Check if the storage file exists."""
        return os.path.exists(self.file_path)
    
    def delete_file(self) -> bool:
        """Delete the storage file. Returns True on success, False on error."""
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False 