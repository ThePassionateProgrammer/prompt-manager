# test_template_approvals.py
# 🟢 GREEN: Approvals tests for data-driven template aspects

import pytest
from approvaltests import verify
from test_template_builder import PromptTemplate, TemplateBuilder
import json

# ============================================================================
# Data-Driven Template Tests (Approvals)
# ============================================================================

class TestTemplateApprovals:
    """Test data-driven aspects using Approvals Testing"""
    
    def test_template_definitions_are_consistent(self):
        """Test that all template definitions follow consistent structure"""
        # Given: A collection of template definitions
        templates = [
            {
                "name": "User Story",
                "pattern": "As a {role}, I want to {action} so that {reason}.",
                "slots": {
                    "role": ["developer", "designer", "manager"],
                    "action": ["create", "improve", "fix", "optimize"],
                    "reason": ["users benefit", "system works better", "team is efficient"]
                }
            },
            {
                "name": "Code Review",
                "pattern": "Review this code as a {role} with focus on {aspect}.",
                "slots": {
                    "role": ["senior developer", "junior developer", "architect"],
                    "aspect": ["security", "performance", "readability", "best practices"]
                }
            },
            {
                "name": "Bug Report",
                "pattern": "As a {reporter}, I found a bug in {component} that {description}.",
                "slots": {
                    "reporter": ["developer", "tester", "user"],
                    "component": ["frontend", "backend", "database", "API"],
                    "description": ["causes crashes", "shows wrong data", "is too slow", "doesn't work"]
                }
            },
            {
                "name": "Feature Request",
                "pattern": "I would like to add {feature} to {component} because {benefit}.",
                "slots": {
                    "feature": ["search functionality", "export feature", "user authentication", "dark mode"],
                    "component": ["the main app", "the dashboard", "the settings page", "the API"],
                    "benefit": ["users can find things faster", "data can be shared easily", "accounts are secure", "it's easier on the eyes"]
                }
            }
        ]
        
        # When: Converting to JSON for approval
        template_json = json.dumps(templates, indent=2)
        
        # Then: Verify the structure is consistent (approval test)
        verify(template_json)
    
    def test_generated_prompts_from_templates(self):
        """Test that generated prompts from templates are consistent"""
        # Given: Templates and sample values
        builder = TemplateBuilder()
        
        user_story = PromptTemplate(
            name="User Story",
            pattern="As a {role}, I want to {action} so that {reason}.",
            slots={
                "role": ["developer", "designer", "manager"],
                "action": ["create", "improve", "fix", "optimize"],
                "reason": ["users benefit", "system works better", "team is efficient"]
            }
        )
        
        code_review = PromptTemplate(
            name="Code Review",
            pattern="Review this code as a {role} with focus on {aspect}.",
            slots={
                "role": ["senior developer", "junior developer", "architect"],
                "aspect": ["security", "performance", "readability", "best practices"]
            }
        )
        
        builder.add_template(user_story)
        builder.add_template(code_review)
        
        # When: Generating prompts with sample values
        generated_prompts = []
        
        # Test User Story variations
        user_story_values = [
            {"role": "developer", "action": "create", "reason": "users benefit"},
            {"role": "designer", "action": "improve", "reason": "system works better"},
            {"role": "manager", "action": "optimize", "reason": "team is efficient"}
        ]
        
        for values in user_story_values:
            prompt = user_story.build_prompt(values)
            generated_prompts.append(f"User Story: {prompt}")
        
        # Test Code Review variations
        code_review_values = [
            {"role": "senior developer", "aspect": "security"},
            {"role": "junior developer", "aspect": "readability"},
            {"role": "architect", "aspect": "best practices"}
        ]
        
        for values in code_review_values:
            prompt = code_review.build_prompt(values)
            generated_prompts.append(f"Code Review: {prompt}")
        
        # Then: Verify generated prompts (approval test)
        verify("\n".join(generated_prompts))
    
    def test_template_slot_combinations(self):
        """Test all possible slot combinations for a template"""
        # Given: A template with multiple slots
        template = PromptTemplate(
            name="User Story",
            pattern="As a {role}, I want to {action} so that {reason}.",
            slots={
                "role": ["developer", "designer"],
                "action": ["create", "improve"],
                "reason": ["users benefit", "system works better"]
            }
        )
        
        # When: Generating all possible combinations
        combinations = []
        for role in template.get_options_for_slot("role"):
            for action in template.get_options_for_slot("action"):
                for reason in template.get_options_for_slot("reason"):
                    values = {"role": role, "action": action, "reason": reason}
                    prompt = template.build_prompt(values)
                    combinations.append(f"{role} + {action} + {reason} = {prompt}")
        
        # Then: Verify all combinations (approval test)
        verify("\n".join(combinations))

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 