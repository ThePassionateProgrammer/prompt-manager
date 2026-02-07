import json
import pytest
from pathlib import Path

class TestPromptPieces:
    """Acceptance tests for prompt piece management."""
    
    def test_can_load_prompt_pieces_from_json(self):
        """Test that prompt pieces can be loaded from JSON file."""
        # Given: A JSON file with prompt piece definitions
        json_path = Path("src/prompt_manager/data/prompt_pieces.json")
        
        # When: The file is loaded
        with open(json_path, 'r') as f:
            prompt_pieces = json.load(f)
        
        # Then: The structure should contain expected categories
        assert "roles" in prompt_pieces
        assert "voices" in prompt_pieces
        assert "contexts" in prompt_pieces
        assert "audiences" in prompt_pieces
        assert "formats" in prompt_pieces
    
    def test_can_access_specific_role(self):
        """Test that specific roles can be accessed and contain expected text."""
        # Given: Prompt pieces are loaded
        json_path = Path("src/prompt_manager/data/prompt_pieces.json")
        with open(json_path, 'r') as f:
            prompt_pieces = json.load(f)
        
        # When: Accessing a specific role
        senior_developer_role = prompt_pieces["roles"]["technical"]["senior_developer"]
        
        # Then: The role should contain the expected text
        assert "senior software developer" in senior_developer_role
        assert "10+ years of experience" in senior_developer_role
    
    def test_can_access_specific_voice(self):
        """Test that specific voices can be accessed."""
        # Given: Prompt pieces are loaded
        json_path = Path("src/prompt_manager/data/prompt_pieces.json")
        with open(json_path, 'r') as f:
            prompt_pieces = json.load(f)
        
        # When: Accessing a specific voice
        technical_voice = prompt_pieces["voices"]["technical"]
        
        # Then: The voice should contain the expected text
        assert "technical terminology" in technical_voice
        assert "precise language" in technical_voice
    
    def test_can_access_specific_context(self):
        """Test that specific contexts can be accessed."""
        # Given: Prompt pieces are loaded
        json_path = Path("src/prompt_manager/data/prompt_pieces.json")
        with open(json_path, 'r') as f:
            prompt_pieces = json.load(f)
        
        # When: Accessing a specific context
        code_review_context = prompt_pieces["contexts"]["code"]["review"]
        
        # Then: The context should contain the expected text
        assert "reviewing code" in code_review_context
        assert "best practices" in code_review_context
        assert "security" in code_review_context
    
    def test_all_categories_have_valid_options(self):
        """Test that all categories have valid, non-empty options."""
        # Given: Prompt pieces are loaded
        json_path = Path("src/prompt_manager/data/prompt_pieces.json")
        with open(json_path, 'r') as f:
            prompt_pieces = json.load(f)
        
        # When: Checking all categories
        categories = ["roles", "voices", "contexts", "audiences", "formats"]
        
        # Then: Each category should have options and each option should have content
        for category in categories:
            assert category in prompt_pieces
            category_data = prompt_pieces[category]
            
            if category == "roles" or category == "contexts":
                # These have subcategories
                for subcategory, options in category_data.items():
                    assert isinstance(options, dict)
                    for option_key, option_text in options.items():
                        assert isinstance(option_text, str)
                        assert len(option_text.strip()) > 0
            else:
                # These are direct key-value pairs
                for option_key, option_text in category_data.items():
                    assert isinstance(option_text, str)
                    assert len(option_text.strip()) > 0 