# test_nested_template_builder.py
# 🔴 RED: Failing test for nested template dependencies

import pytest
from typing import List, Dict, Optional

# ============================================================================
# Nested Template System
# ============================================================================

class NestedPromptTemplate:
    """A template with nested dependencies between variables"""
    
    def __init__(self, name: str, pattern: str, variables: Dict[str, any]):
        self.name = name
        self.pattern = pattern  # "As a [role], I want to [what], so I can [why]"
        self.variables = variables  # {"role": ["dev", "manager"], "what": {"dev": [...], "manager": [...]}}
    
    def get_available_variables(self) -> List[str]:
        """Get list of variable names that can be filled"""
        return list(self.variables.keys())
    
    def get_options_for_variable(self, variable_name: str, context: Dict[str, str] = None) -> List[str]:
        """Get available options for a specific variable, considering dependencies"""
        if variable_name not in self.variables:
            return []
        
        variable_def = self.variables[variable_name]
        
        # If it's a simple list, return all options
        if isinstance(variable_def, list):
            return variable_def
        
        # If it's a nested dict, filter based on context
        if isinstance(variable_def, dict) and context:
            # Find the first dependency that matches
            for dep_var, dep_value in context.items():
                # Check if this variable depends on the context variable
                if dep_value in variable_def:
                    return variable_def[dep_value]
            # If no context matches, return empty list
            return []
        
        # If it's a nested dict but no context, return all options
        if isinstance(variable_def, dict):
            all_options = []
            for key, options in variable_def.items():
                if isinstance(options, list):
                    all_options.extend(options)
            return all_options
        
        # Fallback: return all options from nested structure
        all_options = []
        if isinstance(variable_def, dict):
            for key, options in variable_def.items():
                if isinstance(options, list):
                    all_options.extend(options)
                elif isinstance(options, dict):
                    for sub_options in options.values():
                        if isinstance(sub_options, list):
                            all_options.extend(sub_options)
        return all_options

# ============================================================================
# Tests
# ============================================================================

class TestNestedTemplateBuilder:
    """Test the nested template builder with dependencies"""
    
    def test_can_create_nested_template(self):
        """Test creating a template with nested dependencies"""
        # Given: A template with nested dependencies
        template = NestedPromptTemplate(
            name="User Story",
            pattern="As a [role], I want to [what], so I can [why]",
            variables={
                "role": ["developer", "manager", "designer"],
                "what": {
                    "developer": ["write code", "debug", "optimize"],
                    "manager": ["approve", "coordinate", "plan"],
                    "designer": ["create mockups", "improve UX", "design"]
                },
                "why": ["users benefit", "system works better", "team is efficient"]
            }
        )
        
        # When: Getting available variables
        variables = template.get_available_variables()
        
        # Then: Should have the expected variables
        assert variables == ["role", "what", "why"]
        assert template.name == "User Story"
    
    def test_can_get_options_for_independent_variable(self):
        """Test getting options for a variable with no dependencies"""
        # Given: A template with role variable (independent)
        template = NestedPromptTemplate(
            name="User Story",
            pattern="As a [role], I want to [what], so I can [why]",
            variables={
                "role": ["developer", "manager", "designer"],
                "what": {
                    "developer": ["write code", "debug", "optimize"],
                    "manager": ["approve", "coordinate", "plan"],
                    "designer": ["create mockups", "improve UX", "design"]
                }
            }
        )
        
        # When: Getting options for role (no dependencies)
        options = template.get_options_for_variable("role")
        
        # Then: Should return all role options
        assert options == ["developer", "manager", "designer"]
    
    def test_can_get_options_for_dependent_variable(self):
        """Test getting options for a variable with dependencies"""
        # Given: A template with what variable (depends on role)
        template = NestedPromptTemplate(
            name="User Story",
            pattern="As a [role], I want to [what], so I can [why]",
            variables={
                "role": ["developer", "manager", "designer"],
                "what": {
                    "developer": ["write code", "debug", "optimize"],
                    "manager": ["approve", "coordinate", "plan"],
                    "designer": ["create mockups", "improve UX", "design"]
                }
            }
        )
        
        # When: Getting options for what with developer context
        options = template.get_options_for_variable("what", {"role": "developer"})
        
        # Then: Should return only developer options
        assert options == ["write code", "debug", "optimize"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 