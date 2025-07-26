from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ValidationError:
    field: str
    message: str


class PromptValidator:
    """Business rules for prompt validation."""
    
    def __init__(self):
        self.min_name_length = 1
        self.max_name_length = 100
        self.min_text_length = 1
        self.max_text_length = 10000
        self.max_category_length = 50
    
    def validate_prompt_creation(self, name: str, text: str, category: str = "general") -> Tuple[bool, List[ValidationError]]:
        """Validate prompt creation data."""
        errors = []
        
        # Validate name
        name_errors = self._validate_name(name)
        errors.extend(name_errors)
        
        # Validate text
        text_errors = self._validate_text(text)
        errors.extend(text_errors)
        
        # Validate category
        category_errors = self._validate_category(category)
        errors.extend(category_errors)
        
        return len(errors) == 0, errors
    
    def validate_prompt_update(self, name: Optional[str] = None, 
                             text: Optional[str] = None, 
                             category: Optional[str] = None) -> Tuple[bool, List[ValidationError]]:
        """Validate prompt update data (only validates provided fields)."""
        errors = []
        
        if name is not None:
            name_errors = self._validate_name(name)
            errors.extend(name_errors)
        
        if text is not None:
            text_errors = self._validate_text(text)
            errors.extend(text_errors)
        
        if category is not None:
            category_errors = self._validate_category(category)
            errors.extend(category_errors)
        
        return len(errors) == 0, errors
    
    def _validate_name(self, name: str) -> List[ValidationError]:
        """Validate prompt name."""
        errors = []
        
        if not name:
            errors.append(ValidationError("name", "Name cannot be empty"))
            return errors
        
        if len(name) < self.min_name_length:
            errors.append(ValidationError("name", f"Name must be at least {self.min_name_length} character(s)"))
        
        if len(name) > self.max_name_length:
            errors.append(ValidationError("name", f"Name cannot exceed {self.max_name_length} characters"))
        
        # Check for invalid characters
        if any(char in name for char in ['<', '>', ':', '"', '|', '?', '*']):
            errors.append(ValidationError("name", "Name contains invalid characters"))
        
        return errors
    
    def _validate_text(self, text: str) -> List[ValidationError]:
        """Validate prompt text."""
        errors = []
        
        if not text:
            errors.append(ValidationError("text", "Text cannot be empty"))
            return errors
        
        if len(text) < self.min_text_length:
            errors.append(ValidationError("text", f"Text must be at least {self.min_text_length} character(s)"))
        
        if len(text) > self.max_text_length:
            errors.append(ValidationError("text", f"Text cannot exceed {self.max_text_length} characters"))
        
        return errors
    
    def _validate_category(self, category: str) -> List[ValidationError]:
        """Validate prompt category."""
        errors = []
        
        if not category:
            errors.append(ValidationError("category", "Category cannot be empty"))
            return errors
        
        if len(category) > self.max_category_length:
            errors.append(ValidationError("category", f"Category cannot exceed {self.max_category_length} characters"))
        
        # Check for invalid characters
        if any(char in category for char in ['<', '>', ':', '"', '|', '?', '*']):
            errors.append(ValidationError("category", "Category contains invalid characters"))
        
        return errors
    
    def sanitize_name(self, name: str) -> str:
        """Sanitize prompt name by removing invalid characters."""
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            name = name.replace(char, '')
        return name.strip()
    
    def sanitize_category(self, category: str) -> str:
        """Sanitize prompt category by removing invalid characters."""
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            category = category.replace(char, '')
        return category.strip() 