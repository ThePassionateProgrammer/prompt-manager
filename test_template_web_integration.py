# test_template_web_integration.py
# 🔴 RED: Failing test for web integration of template builder

import pytest
from unittest.mock import patch, MagicMock
from test_template_builder import PromptTemplate, TemplateBuilder

# ============================================================================
# Web Integration Test
# ============================================================================

class TestTemplateWebIntegration:
    """Test integrating template builder with web interface"""
    
    def test_can_get_template_data_for_web_dropdown(self):
        """Test getting template data formatted for web dropdowns"""
        # Given: A template builder with templates
        builder = TemplateBuilder()
        
        # Add some templates
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
        
        # When: Getting template data for web interface
        template_data = []
        for template in builder.templates:
            template_data.append({
                "name": template.name,
                "pattern": template.pattern,
                "slots": template.slots
            })
        
        # Then: Should have formatted data for web
        assert len(template_data) == 2
        assert template_data[0]["name"] == "User Story"
        assert template_data[1]["name"] == "Code Review"
        assert "role" in template_data[0]["slots"]
        assert "action" in template_data[0]["slots"]
        assert "reason" in template_data[0]["slots"]
    
    def test_can_build_prompt_from_web_form_data(self):
        """Test building prompt from web form submission"""
        # Given: A template and web form data
        template = PromptTemplate(
            name="User Story",
            pattern="As a {role}, I want to {action} so that {reason}.",
            slots={
                "role": ["developer", "designer", "manager"],
                "action": ["create", "improve", "fix", "optimize"],
                "reason": ["users benefit", "system works better", "team is efficient"]
            }
        )
        
        # Simulate web form data
        web_form_data = {
            "template_name": "User Story",
            "role": "developer",
            "action": "create",
            "reason": "users benefit"
        }
        
        # When: Building prompt from web data
        slot_values = {
            "role": web_form_data["role"],
            "action": web_form_data["action"],
            "reason": web_form_data["reason"]
        }
        result = template.build_prompt(slot_values)
        
        # Then: Should build correctly
        expected = "As a developer, I want to create so that users benefit."
        assert result == expected
    
    def test_web_form_validation_fails_with_missing_slots(self):
        """Test that web form validation fails with missing required slots"""
        # Given: A template and incomplete web form data
        template = PromptTemplate(
            name="User Story",
            pattern="As a {role}, I want to {action} so that {reason}.",
            slots={
                "role": ["developer", "designer", "manager"],
                "action": ["create", "improve", "fix", "optimize"],
                "reason": ["users benefit", "system works better", "team is efficient"]
            }
        )
        
        # Simulate incomplete web form data
        web_form_data = {
            "template_name": "User Story",
            "role": "developer",
            "action": "create"
            # Missing "reason"
        }
        
        # When: Building prompt from incomplete data
        slot_values = {
            "role": web_form_data["role"],
            "action": web_form_data["action"]
            # Missing reason
        }
        
        # Then: Should raise ValueError
        with pytest.raises(ValueError, match="Missing required slot"):
            template.build_prompt(slot_values)
    
    def test_can_get_template_options_for_web_dropdowns(self):
        """Test getting template options formatted for web dropdowns"""
        # Given: A template
        template = PromptTemplate(
            name="User Story",
            pattern="As a {role}, I want to {action} so that {reason}.",
            slots={
                "role": ["developer", "designer", "manager"],
                "action": ["create", "improve", "fix", "optimize"],
                "reason": ["users benefit", "system works better", "team is efficient"]
            }
        )
        
        # When: Getting options for web dropdowns
        web_options = {}
        for slot_name in template.get_available_slots():
            web_options[slot_name] = template.get_options_for_slot(slot_name)
        
        # Then: Should have options for each slot
        assert "role" in web_options
        assert "action" in web_options
        assert "reason" in web_options
        assert web_options["role"] == ["developer", "designer", "manager"]
        assert web_options["action"] == ["create", "improve", "fix", "optimize"]
        assert web_options["reason"] == ["users benefit", "system works better", "team is efficient"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 