import pytest
from pathlib import Path
from src.prompt_manager.business.prompt_builder import PromptBuilder

class TestPromptBuilder:
    """Tests for the PromptBuilder class."""
    
    def test_can_initialize_with_default_pieces_file(self):
        """Test that PromptBuilder can initialize with default pieces file."""
        # Given: A PromptBuilder instance
        builder = PromptBuilder()
        
        # Then: It should have loaded the pieces data
        assert builder.pieces_data is not None
        assert "roles" in builder.pieces_data
        assert "voices" in builder.pieces_data
    
    def test_can_get_available_roles(self):
        """Test that available roles can be retrieved."""
        # Given: A PromptBuilder instance
        builder = PromptBuilder()
        
        # When: Getting available roles
        roles = builder.get_available_roles()
        
        # Then: Should return the roles structure
        assert isinstance(roles, dict)
        assert "technical" in roles
        assert "creative" in roles
        assert "business" in roles
        assert "educational" in roles
    
    def test_can_get_specific_role_text(self):
        """Test that specific role text can be retrieved."""
        # Given: A PromptBuilder instance
        builder = PromptBuilder()
        
        # When: Getting a specific role text
        role_text = builder.get_role_text("technical", "senior_developer")
        
        # Then: Should return the expected text
        assert "senior software developer" in role_text
        assert "10+ years of experience" in role_text
    
    def test_can_get_specific_voice_text(self):
        """Test that specific voice text can be retrieved."""
        # Given: A PromptBuilder instance
        builder = PromptBuilder()
        
        # When: Getting a specific voice text
        voice_text = builder.get_voice_text("technical")
        
        # Then: Should return the expected text
        assert "technical terminology" in voice_text
        assert "precise language" in voice_text
    
    def test_can_build_prompt_with_role_only(self):
        """Test that a prompt can be built with just a role."""
        # Given: A PromptBuilder instance
        builder = PromptBuilder()
        
        # When: Building a prompt with just a role
        result = builder.build_prompt(
            role_category="technical",
            role="senior_developer"
        )
        
        # Then: Should return the role text
        assert "senior software developer" in result["prompt"]
        assert "10+ years of experience" in result["prompt"]
        assert result["model"] == "gpt-4-turbo"
        assert result["temperature"] == 0.7
    
    def test_can_build_prompt_with_multiple_pieces(self):
        """Test that a prompt can be built with multiple pieces."""
        # Given: A PromptBuilder instance
        builder = PromptBuilder()
        
        # When: Building a prompt with multiple pieces
        result = builder.build_prompt(
            role_category="technical",
            role="code_reviewer",
            voice="technical",
            context_category="code",
            context="review"
        )
        
        # Then: Should combine all pieces
        assert "expert code reviewer" in result["prompt"]
        assert "technical terminology" in result["prompt"]
        assert "reviewing code" in result["prompt"]
        assert "model" in result
        assert "temperature" in result
    
    def test_can_build_prompt_with_custom_text(self):
        """Test that a prompt can be built with custom text."""
        # Given: A PromptBuilder instance
        builder = PromptBuilder()
        
        # When: Building a prompt with custom text
        result = builder.build_prompt(
            role_category="technical",
            role="senior_developer",
            custom_text="Please review this Python code for best practices."
        )
        
        # Then: Should include both role and custom text
        assert "senior software developer" in result["prompt"]
        assert "Please review this Python code for best practices." in result["prompt"]
        assert "model" in result
        assert "temperature" in result
    
    def test_build_prompt_returns_empty_string_when_no_pieces(self):
        """Test that build_prompt returns empty string when no pieces provided."""
        # Given: A PromptBuilder instance
        builder = PromptBuilder()
        
        # When: Building a prompt with no pieces
        result = builder.build_prompt()
        
        # Then: Should return empty string in prompt field
        assert result["prompt"] == ""
        assert "model" in result
        assert "temperature" in result
    
    def test_raises_error_for_invalid_role_category(self):
        """Test that error is raised for invalid role category."""
        # Given: A PromptBuilder instance
        builder = PromptBuilder()
        
        # When/Then: Should raise ValueError for invalid category
        with pytest.raises(ValueError, match="Role category 'invalid' not found"):
            builder.get_role_text("invalid", "senior_developer")
    
    def test_raises_error_for_invalid_role(self):
        """Test that error is raised for invalid role."""
        # Given: A PromptBuilder instance
        builder = PromptBuilder()
        
        # When/Then: Should raise ValueError for invalid role
        with pytest.raises(ValueError, match="Role 'invalid' not found in category 'technical'"):
            builder.get_role_text("technical", "invalid")
    
    def test_raises_error_for_invalid_voice(self):
        """Test that error is raised for invalid voice."""
        # Given: A PromptBuilder instance
        builder = PromptBuilder()
        
        # When/Then: Should raise ValueError for invalid voice
        with pytest.raises(ValueError, match="Voice 'invalid' not found"):
            builder.get_voice_text("invalid") 