# test_template_builder.py
# 🔴 RED: Failing test for minimal template functionality

import pytest
from typing import List, Dict, Optional

# ============================================================================
# Minimal Template System
# ============================================================================

class PromptTemplate:
    """A simple template with slots that can be filled"""
    
    def __init__(self, name: str, pattern: str, slots: Dict[str, List[str]]):
        self.name = name
        self.pattern = pattern  # "As a {role}, I want to create better code."
        self.slots = slots      # {"role": ["developer", "designer", "manager"]}
    
    def get_available_slots(self) -> List[str]:
        """Get list of slot names that can be filled"""
        return list(self.slots.keys())
    
    def get_options_for_slot(self, slot_name: str) -> List[str]:
        """Get available options for a specific slot"""
        return self.slots.get(slot_name, [])
    
    def build_prompt(self, values: Dict[str, str]) -> str:
        """Build the prompt by filling in the slots"""
        try:
            return self.pattern.format(**values)
        except KeyError as e:
            raise ValueError(f"Missing required slot: {e}")
        except Exception as e:
            raise ValueError(f"Error building prompt: {e}")

class TemplateBuilder:
    """Simple builder for creating prompts from templates"""
    
    def __init__(self):
        self.templates: List[PromptTemplate] = []
    
    def add_template(self, template: PromptTemplate):
        """Add a template to the builder"""
        self.templates.append(template)
    
    def get_template_names(self) -> List[str]:
        """Get list of available template names"""
        return [template.name for template in self.templates]
    
    def get_template_by_name(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name"""
        for template in self.templates:
            if template.name == name:
                return template
        return None

# ============================================================================
# Tests
# ============================================================================

class TestTemplateBuilder:
    """Test the minimal template builder"""
    
    def test_can_create_simple_template(self):
        """Test creating a basic template with one slot"""
        # Given: A simple template
        template = PromptTemplate(
            name="User Story",
            pattern="As a {role}, I want to create better code.",
            slots={"role": ["developer", "designer", "manager"]}
        )
        
        # When: Getting available slots
        slots = template.get_available_slots()
        
        # Then: Should have one slot
        assert slots == ["role"]
        assert template.name == "User Story"
    
    def test_can_get_options_for_slot(self):
        """Test getting options for a specific slot"""
        # Given: A template with role slot
        template = PromptTemplate(
            name="User Story",
            pattern="As a {role}, I want to create better code.",
            slots={"role": ["developer", "designer", "manager"]}
        )
        
        # When: Getting options for role slot
        options = template.get_options_for_slot("role")
        
        # Then: Should return the role options
        assert options == ["developer", "designer", "manager"]
    
    def test_can_build_prompt_with_valid_values(self):
        """Test building a prompt with valid slot values"""
        # Given: A template and valid values
        template = PromptTemplate(
            name="User Story",
            pattern="As a {role}, I want to create better code.",
            slots={"role": ["developer", "designer", "manager"]}
        )
        values = {"role": "developer"}
        
        # When: Building the prompt
        result = template.build_prompt(values)
        
        # Then: Should build correctly
        assert result == "As a developer, I want to create better code."
    
    def test_build_prompt_fails_with_missing_slot(self):
        """Test that building fails when required slot is missing"""
        # Given: A template and missing values
        template = PromptTemplate(
            name="User Story",
            pattern="As a {role}, I want to create better code.",
            slots={"role": ["developer", "designer", "manager"]}
        )
        values = {}  # Missing role
        
        # When/Then: Should raise ValueError
        with pytest.raises(ValueError, match="Missing required slot"):
            template.build_prompt(values)
    
    def test_can_add_template_to_builder(self):
        """Test adding a template to the builder"""
        # Given: A template builder and template
        builder = TemplateBuilder()
        template = PromptTemplate(
            name="User Story",
            pattern="As a {role}, I want to create better code.",
            slots={"role": ["developer", "designer", "manager"]}
        )
        
        # When: Adding template to builder
        builder.add_template(template)
        
        # Then: Should be available
        assert "User Story" in builder.get_template_names()
    
    def test_can_get_template_by_name(self):
        """Test retrieving a template by name"""
        # Given: A builder with a template
        builder = TemplateBuilder()
        template = PromptTemplate(
            name="User Story",
            pattern="As a {role}, I want to create better code.",
            slots={"role": ["developer", "designer", "manager"]}
        )
        builder.add_template(template)
        
        # When: Getting template by name
        retrieved = builder.get_template_by_name("User Story")
        
        # Then: Should return the correct template
        assert retrieved is not None
        assert retrieved.name == "User Story"
        assert retrieved.pattern == "As a {role}, I want to create better code."
    
    def test_get_template_by_name_returns_none_for_missing(self):
        """Test that getting non-existent template returns None"""
        # Given: An empty builder
        builder = TemplateBuilder()
        
        # When: Getting non-existent template
        result = builder.get_template_by_name("Non-existent")
        
        # Then: Should return None
        assert result is None

    # ============================================================================
    # 🔴 RED: New failing test for multiple slots
    # ============================================================================
    
    def test_can_create_template_with_multiple_slots(self):
        """Test creating a template with multiple slots"""
        # Given: A template with multiple slots
        template = PromptTemplate(
            name="Enhanced User Story",
            pattern="As a {role}, I want to {action} so that {reason}.",
            slots={
                "role": ["developer", "designer", "manager"],
                "action": ["create", "improve", "fix", "optimize"],
                "reason": ["users benefit", "system works better", "team is efficient"]
            }
        )
        
        # When: Getting available slots
        slots = template.get_available_slots()
        
        # Then: Should have three slots
        assert len(slots) == 3
        assert "role" in slots
        assert "action" in slots
        assert "reason" in slots
    
    def test_can_build_prompt_with_multiple_slots(self):
        """Test building a prompt with multiple slot values"""
        # Given: A template with multiple slots and valid values
        template = PromptTemplate(
            name="Enhanced User Story",
            pattern="As a {role}, I want to {action} so that {reason}.",
            slots={
                "role": ["developer", "designer", "manager"],
                "action": ["create", "improve", "fix", "optimize"],
                "reason": ["users benefit", "system works better", "team is efficient"]
            }
        )
        values = {
            "role": "developer",
            "action": "create",
            "reason": "users benefit"
        }
        
        # When: Building the prompt
        result = template.build_prompt(values)
        
        # Then: Should build correctly with all slots filled
        expected = "As a developer, I want to create so that users benefit."
        assert result == expected
    
    def test_build_prompt_fails_with_partial_slots(self):
        """Test that building fails when some required slots are missing"""
        # Given: A template with multiple slots and partial values
        template = PromptTemplate(
            name="Enhanced User Story",
            pattern="As a {role}, I want to {action} so that {reason}.",
            slots={
                "role": ["developer", "designer", "manager"],
                "action": ["create", "improve", "fix", "optimize"],
                "reason": ["users benefit", "system works better", "team is efficient"]
            }
        )
        values = {
            "role": "developer",
            "action": "create"
            # Missing "reason"
        }
        
        # When/Then: Should raise ValueError for missing slot
        with pytest.raises(ValueError, match="Missing required slot"):
            template.build_prompt(values)

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 