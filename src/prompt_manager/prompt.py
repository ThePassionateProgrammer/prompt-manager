# src/prompt_manager/prompt.py

from datetime import datetime

class Prompt:
    def __init__(self, name: str, text: str, category: str = "general"):
        self.name = name
        self.text = text
        self.category = category
        self.created_at = datetime.now()
        self.modified_at = self.created_at
        self.id = None  # Will be set by PromptManager

    def update_text(self, new_text: str):
        self.text = new_text
        self.modified_at = datetime.now()

    def __str__(self):
        return f"Prompt(name={self.name}, category={self.category})"
    
    def to_dict(self):
        """Convert prompt to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'text': self.text,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create prompt from dictionary (for JSON deserialization)."""
        prompt = cls(data['name'], data['text'], data['category'])
        prompt.id = data['id']
        prompt.created_at = datetime.fromisoformat(data['created_at'])
        prompt.modified_at = datetime.fromisoformat(data['modified_at'])
        return prompt