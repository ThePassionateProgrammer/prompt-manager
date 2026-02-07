# test_prompt_builder_dom.py
# 🔴 RED: Failing test for DOM-based prompt builder

import pytest
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# ============================================================================
# DOM Structure: Composite of Decorators with Template Methods
# ============================================================================

class PromptPiece(ABC):
    """Base class for all prompt pieces - Template Method Pattern"""
    
    @abstractmethod
    def render(self) -> str:
        """Template method - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Template method - must be implemented by subclasses"""
        pass

class PromptDecorator(PromptPiece):
    """Decorator base class - can wrap other pieces"""
    
    def __init__(self, component: PromptPiece = None):
        self.component = component
    
    def render(self) -> str:
        if self.component:
            return self._decorate(self.component.render())
        return self._decorate("")
    
    @abstractmethod
    def _decorate(self, content: str) -> str:
        """Template method for decoration logic"""
        pass
    
    def validate(self) -> bool:
        if self.component:
            return self._validate_decorator() and self.component.validate()
        return self._validate_decorator()
    
    @abstractmethod
    def _validate_decorator(self) -> bool:
        """Template method for validation logic"""
        pass

class PromptComposite(PromptPiece):
    """Composite class - contains multiple pieces"""
    
    def __init__(self):
        self.pieces: List[PromptPiece] = []
    
    def add_piece(self, piece: PromptPiece):
        """Add a piece to the composite"""
        self.pieces.append(piece)
    
    def render(self) -> str:
        """Render all pieces in sequence"""
        result = []
        for piece in self.pieces:  # Polymorphic for-each loop
            if piece.validate():
                result.append(piece.render())
        return "\n\n".join(result)
    
    def validate(self) -> bool:
        """Validate all pieces"""
        for piece in self.pieces:  # Polymorphic for-each loop
            if not piece.validate():
                return False
        return True

# ============================================================================
# Concrete Implementations
# ============================================================================

class RolePiece(PromptPiece):
    """Concrete role piece"""
    
    def __init__(self, role_text: str):
        self.role_text = role_text
    
    def render(self) -> str:
        return f"You are {self.role_text}"
    
    def validate(self) -> bool:
        return bool(self.role_text and len(self.role_text.strip()) > 0)

class VoiceDecorator(PromptDecorator):
    """Decorator that adds voice/tone"""
    
    def __init__(self, voice_text: str, component: PromptPiece = None):
        super().__init__(component)
        self.voice_text = voice_text
    
    def _decorate(self, content: str) -> str:
        if content:
            return f"{content}. {self.voice_text}"
        return self.voice_text
    
    def _validate_decorator(self) -> bool:
        return bool(self.voice_text and len(self.voice_text.strip()) > 0)

class ContextDecorator(PromptDecorator):
    """Decorator that adds context"""
    
    def __init__(self, context_text: str, component: PromptPiece = None):
        super().__init__(component)
        self.context_text = context_text
    
    def _decorate(self, content: str) -> str:
        if content:
            return f"{content}\n\nContext: {self.context_text}"
        return f"Context: {self.context_text}"
    
    def _validate_decorator(self) -> bool:
        return bool(self.context_text and len(self.context_text.strip()) > 0)

class AudienceDecorator(PromptDecorator):
    """Decorator that adds audience specification"""
    
    def __init__(self, audience_text: str, component: PromptPiece = None):
        super().__init__(component)
        self.audience_text = audience_text
    
    def _decorate(self, content: str) -> str:
        if content:
            return f"{content}\n\nYour audience: {self.audience_text}"
        return f"Your audience: {self.audience_text}"
    
    def _validate_decorator(self) -> bool:
        return bool(self.audience_text and len(self.audience_text.strip()) > 0)

# ============================================================================
# Tests
# ============================================================================

class TestPromptBuilderDOM:
    """Test the DOM-based prompt builder"""
    
    def test_can_create_simple_role_piece(self):
        """Test creating a basic role piece"""
        # Given: A role piece
        role = RolePiece("a senior software developer")
        
        # When: Rendering the piece
        result = role.render()
        
        # Then: Should render correctly
        assert result == "You are a senior software developer"
        assert role.validate() is True
    
    def test_can_decorate_role_with_voice(self):
        """Test decorating a role with voice"""
        # Given: A role piece decorated with voice
        role = RolePiece("a senior software developer")
        voice_decorator = VoiceDecorator("Use technical terminology and precise language", role)
        
        # When: Rendering the decorated piece
        result = voice_decorator.render()
        
        # Then: Should combine role and voice
        expected = "You are a senior software developer. Use technical terminology and precise language"
        assert result == expected
        assert voice_decorator.validate() is True
    
    def test_can_decorate_role_with_multiple_decorators(self):
        """Test chaining multiple decorators"""
        # Given: A role with multiple decorators
        role = RolePiece("a senior software developer")
        voice_decorator = VoiceDecorator("Use technical terminology", role)
        context_decorator = ContextDecorator("You are reviewing code for best practices", voice_decorator)
        audience_decorator = AudienceDecorator("Your audience consists of developers and engineers", context_decorator)
        
        # When: Rendering the fully decorated piece
        result = audience_decorator.render()
        
        # Then: Should combine all decorators
        assert "You are a senior software developer" in result
        assert "Use technical terminology" in result
        assert "Context: You are reviewing code for best practices" in result
        assert "Your audience: Your audience consists of developers and engineers" in result
        assert audience_decorator.validate() is True
    
    def test_can_build_composite_prompt(self):
        """Test building a composite prompt with multiple pieces"""
        # Given: A composite prompt
        composite = PromptComposite()
        
        # Add different pieces
        role = RolePiece("a senior software developer")
        voice = VoiceDecorator("Use technical terminology")
        context = ContextDecorator("You are reviewing code for best practices")
        audience = AudienceDecorator("Your audience consists of developers and engineers")
        
        composite.add_piece(role)
        composite.add_piece(voice)
        composite.add_piece(context)
        composite.add_piece(audience)
        
        # When: Rendering the composite
        result = composite.render()
        
        # Then: Should render all pieces
        assert "You are a senior software developer" in result
        assert "Use technical terminology" in result
        assert "Context: You are reviewing code for best practices" in result
        assert "Your audience: Your audience consists of developers and engineers" in result
        assert composite.validate() is True
    
    def test_validation_fails_for_empty_pieces(self):
        """Test validation fails for invalid pieces"""
        # Given: An empty role piece
        empty_role = RolePiece("")
        
        # When/Then: Should fail validation
        assert empty_role.validate() is False
        
        # Given: An empty decorator
        empty_voice = VoiceDecorator("")
        
        # When/Then: Should fail validation
        assert empty_voice.validate() is False
    
    def test_composite_validation_fails_if_any_piece_invalid(self):
        """Test composite validation fails if any piece is invalid"""
        # Given: A composite with valid and invalid pieces
        composite = PromptComposite()
        
        valid_role = RolePiece("a senior developer")
        invalid_voice = VoiceDecorator("")  # Empty voice
        
        composite.add_piece(valid_role)
        composite.add_piece(invalid_voice)
        
        # When/Then: Should fail validation
        assert composite.validate() is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 