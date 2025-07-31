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
    
    def test_cascading_dependencies_work_correctly(self):
        """Test that cascading dependencies work (role affects what, what affects how)"""
        # Given: A template with cascading dependencies
        template = NestedPromptTemplate(
            name="Complex User Story",
            pattern="As a [role], I want to [what], so I can [why] using [how]",
            variables={
                "role": ["developer", "manager", "designer"],
                "what": {
                    "developer": ["write code", "debug", "optimize"],
                    "manager": ["approve", "coordinate", "plan"],
                    "designer": ["create mockups", "improve UX", "design"]
                },
                "why": ["users benefit", "system works better", "team is efficient"],
                "how": {
                    "write code": ["using TDD", "with pair programming", "following SOLID"],
                    "debug": ["with logging", "using debugger", "with unit tests"],
                    "approve": ["after review", "with stakeholder input", "based on metrics"],
                    "create mockups": ["in Figma", "with user feedback", "iteratively"]
                }
            }
        )
        
        # When: Getting options for how with developer + write code context
        options = template.get_options_for_variable("how", {"role": "developer", "what": "write code"})
        
        # Then: Should return only write code options
        assert options == ["using TDD", "with pair programming", "following SOLID"]
    
    def test_empty_context_returns_all_options(self):
        """Test that empty context returns all options for nested variables"""
        # Given: A template with nested variables
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
        
        # When: Getting options for what with no context
        options = template.get_options_for_variable("what")
        
        # Then: Should return all options from all roles
        expected = ["write code", "debug", "optimize", "approve", "coordinate", "plan", "create mockups", "improve UX", "design"]
        assert sorted(options) == sorted(expected)
    
    def test_invalid_context_returns_empty_list(self):
        """Test that invalid context returns empty list for dependent variables"""
        # Given: A template with nested variables
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
        
        # When: Getting options for what with invalid role context
        options = template.get_options_for_variable("what", {"role": "invalid_role"})
        
        # Then: Should return empty list
        assert options == []
    
    def test_missing_variable_returns_empty_list(self):
        """Test that missing variable returns empty list"""
        # Given: A template
        template = NestedPromptTemplate(
            name="User Story",
            pattern="As a [role], I want to [what], so I can [why]",
            variables={
                "role": ["developer", "manager", "designer"],
                "what": {
                    "developer": ["write code", "debug", "optimize"],
                    "manager": ["approve", "coordinate", "plan"]
                }
            }
        )
        
        # When: Getting options for non-existent variable
        options = template.get_options_for_variable("non_existent")
        
        # Then: Should return empty list
        assert options == []
    
    def test_mixed_independent_and_dependent_variables(self):
        """Test template with both independent and dependent variables"""
        # Given: A template with mixed variable types
        template = NestedPromptTemplate(
            name="Mixed Template",
            pattern="As a [role], I want to [what] in [environment]",
            variables={
                "role": ["developer", "manager"],  # Independent
                "what": {
                    "developer": ["write code", "debug"],
                    "manager": ["approve", "coordinate"]
                },  # Dependent
                "environment": ["production", "staging", "development"]  # Independent
            }
        )
        
        # When: Getting options for independent variables
        role_options = template.get_options_for_variable("role")
        env_options = template.get_options_for_variable("environment")
        
        # Then: Should return all options
        assert role_options == ["developer", "manager"]
        assert env_options == ["production", "staging", "development"]
        
        # When: Getting options for dependent variable with context
        what_options = template.get_options_for_variable("what", {"role": "developer"})
        
        # Then: Should return only developer options
        assert what_options == ["write code", "debug"]
    
    def test_deep_nested_dependencies(self):
        """Test deeply nested dependencies (3+ levels)"""
        # Given: A template with deep nesting
        template = NestedPromptTemplate(
            name="Deep Nested Template",
            pattern="As a [role], I want to [what] using [tool] in [environment]",
            variables={
                "role": ["developer", "designer"],
                "what": {
                    "developer": ["write code", "debug"],
                    "designer": ["create mockups", "improve UX"]
                },
                "tool": {
                    "write code": ["VS Code", "IntelliJ", "Vim"],
                    "debug": ["Chrome DevTools", "VS Code debugger", "logging"],
                    "create mockups": ["Figma", "Sketch", "Adobe XD"],
                    "improve UX": ["user testing", "analytics", "feedback"]
                },
                "environment": ["production", "staging", "development"]
            }
        )
        
        # When: Getting options for tool with developer + write code context
        tool_options = template.get_options_for_variable("tool", {"role": "developer", "what": "write code"})
        
        # Then: Should return only write code tool options
        assert tool_options == ["VS Code", "IntelliJ", "Vim"]
        
        # When: Getting options for tool with designer + create mockups context
        tool_options = template.get_options_for_variable("tool", {"role": "designer", "what": "create mockups"})
        
        # Then: Should return only create mockups tool options
        assert tool_options == ["Figma", "Sketch", "Adobe XD"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 