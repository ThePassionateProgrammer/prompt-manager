# tests/test_prompt_validator.py

import pytest
from src.prompt_manager.business.prompt_validator import PromptValidator, ValidationError


class TestPromptValidator:
    def setup_method(self):
        self.validator = PromptValidator()
    
    def test_validate_prompt_creation_valid_data(self):
        """Test validation with valid prompt data."""
        is_valid, errors = self.validator.validate_prompt_creation(
            "Test Prompt", "This is test text", "test"
        )
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_prompt_creation_empty_name(self):
        """Test validation with empty name."""
        is_valid, errors = self.validator.validate_prompt_creation("", "Test text", "test")
        
        assert is_valid is False
        assert len(errors) == 1
        assert errors[0].field == "name"
        assert "cannot be empty" in errors[0].message
    
    def test_validate_prompt_creation_empty_text(self):
        """Test validation with empty text."""
        is_valid, errors = self.validator.validate_prompt_creation("Test Prompt", "", "test")
        
        assert is_valid is False
        assert len(errors) == 1
        assert errors[0].field == "text"
        assert "cannot be empty" in errors[0].message
    
    def test_validate_prompt_creation_empty_category(self):
        """Test validation with empty category."""
        is_valid, errors = self.validator.validate_prompt_creation("Test Prompt", "Test text", "")
        
        assert is_valid is False
        assert len(errors) == 1
        assert errors[0].field == "category"
        assert "cannot be empty" in errors[0].message
    
    def test_validate_prompt_creation_name_too_long(self):
        """Test validation with name exceeding maximum length."""
        long_name = "a" * (self.validator.max_name_length + 1)
        is_valid, errors = self.validator.validate_prompt_creation(long_name, "Test text", "test")
        
        assert is_valid is False
        assert len(errors) == 1
        assert errors[0].field == "name"
        assert "cannot exceed" in errors[0].message
    
    def test_validate_prompt_creation_text_too_long(self):
        """Test validation with text exceeding maximum length."""
        long_text = "a" * (self.validator.max_text_length + 1)
        is_valid, errors = self.validator.validate_prompt_creation("Test Prompt", long_text, "test")
        
        assert is_valid is False
        assert len(errors) == 1
        assert errors[0].field == "text"
        assert "cannot exceed" in errors[0].message
    
    def test_validate_prompt_creation_category_too_long(self):
        """Test validation with category exceeding maximum length."""
        long_category = "a" * (self.validator.max_category_length + 1)
        is_valid, errors = self.validator.validate_prompt_creation("Test Prompt", "Test text", long_category)
        
        assert is_valid is False
        assert len(errors) == 1
        assert errors[0].field == "category"
        assert "cannot exceed" in errors[0].message
    
    def test_validate_prompt_creation_invalid_characters_in_name(self):
        """Test validation with invalid characters in name."""
        invalid_names = ["Test<Prompt", "Test>Prompt", "Test:Prompt", "Test\"Prompt", "Test|Prompt", "Test?Prompt", "Test*Prompt"]
        
        for invalid_name in invalid_names:
            is_valid, errors = self.validator.validate_prompt_creation(invalid_name, "Test text", "test")
            
            assert is_valid is False
            assert len(errors) == 1
            assert errors[0].field == "name"
            assert "invalid characters" in errors[0].message
    
    def test_validate_prompt_creation_invalid_characters_in_category(self):
        """Test validation with invalid characters in category."""
        invalid_categories = ["test<cat", "test>cat", "test:cat", "test\"cat", "test|cat", "test?cat", "test*cat"]
        
        for invalid_category in invalid_categories:
            is_valid, errors = self.validator.validate_prompt_creation("Test Prompt", "Test text", invalid_category)
            
            assert is_valid is False
            assert len(errors) == 1
            assert errors[0].field == "category"
            assert "invalid characters" in errors[0].message
    
    def test_validate_prompt_creation_multiple_errors(self):
        """Test validation with multiple errors."""
        is_valid, errors = self.validator.validate_prompt_creation("", "", "")
        
        assert is_valid is False
        assert len(errors) == 3
        error_fields = [error.field for error in errors]
        assert "name" in error_fields
        assert "text" in error_fields
        assert "category" in error_fields
    
    def test_validate_prompt_update_valid_data(self):
        """Test validation with valid update data."""
        is_valid, errors = self.validator.validate_prompt_update(
            name="New Name", text="New text", category="new_category"
        )
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_prompt_update_partial_data(self):
        """Test validation with partial update data."""
        is_valid, errors = self.validator.validate_prompt_update(name="New Name")
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_prompt_update_empty_name(self):
        """Test validation with empty name in update."""
        is_valid, errors = self.validator.validate_prompt_update(name="")
        
        assert is_valid is False
        assert len(errors) == 1
        assert errors[0].field == "name"
        assert "cannot be empty" in errors[0].message
    
    def test_validate_prompt_update_empty_text(self):
        """Test validation with empty text in update."""
        is_valid, errors = self.validator.validate_prompt_update(text="")
        
        assert is_valid is False
        assert len(errors) == 1
        assert errors[0].field == "text"
        assert "cannot be empty" in errors[0].message
    
    def test_validate_prompt_update_empty_category(self):
        """Test validation with empty category in update."""
        is_valid, errors = self.validator.validate_prompt_update(category="")
        
        assert is_valid is False
        assert len(errors) == 1
        assert errors[0].field == "category"
        assert "cannot be empty" in errors[0].message
    
    def test_validate_prompt_update_no_fields_provided(self):
        """Test validation with no fields provided for update."""
        is_valid, errors = self.validator.validate_prompt_update()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_sanitize_name(self):
        """Test name sanitization."""
        test_cases = [
            ("Test<Prompt", "TestPrompt"),
            ("Test>Prompt", "TestPrompt"),
            ("Test:Prompt", "TestPrompt"),
            ("Test\"Prompt", "TestPrompt"),
            ("Test|Prompt", "TestPrompt"),
            ("Test?Prompt", "TestPrompt"),
            ("Test*Prompt", "TestPrompt"),
            ("Test Prompt", "Test Prompt"),  # Valid name unchanged
            ("  Test Prompt  ", "Test Prompt"),  # Whitespace trimmed
        ]
        
        for input_name, expected_output in test_cases:
            sanitized = self.validator.sanitize_name(input_name)
            assert sanitized == expected_output
    
    def test_sanitize_category(self):
        """Test category sanitization."""
        test_cases = [
            ("test<cat", "testcat"),
            ("test>cat", "testcat"),
            ("test:cat", "testcat"),
            ("test\"cat", "testcat"),
            ("test|cat", "testcat"),
            ("test?cat", "testcat"),
            ("test*cat", "testcat"),
            ("test cat", "test cat"),  # Valid category unchanged
            ("  test cat  ", "test cat"),  # Whitespace trimmed
        ]
        
        for input_category, expected_output in test_cases:
            sanitized = self.validator.sanitize_category(input_category)
            assert sanitized == expected_output
    
    def test_validation_error_dataclass(self):
        """Test ValidationError dataclass."""
        error = ValidationError("name", "Name is invalid")
        
        assert error.field == "name"
        assert error.message == "Name is invalid" 