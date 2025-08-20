import pytest
import json
from unittest.mock import patch, MagicMock
from src.prompt_manager.web import PromptManagerWeb

class TestCascadingIntegration:
    """Test integration of cascading combo boxes into template builder."""
    
    @pytest.fixture
    def web_app(self):
        """Create a test web app instance."""
        return PromptManagerWeb()
    
    def test_template_builder_uses_cascading_combo_boxes(self, web_app):
        """Test that template builder generates cascading combo boxes instead of simple dropdowns."""
        # Given: A template with cascading variables
        template = "As a [Role], I want to [What], so that [Why]"
        
        # When: Generating combo boxes for the template
        with patch.object(web_app, '_api_request') as mock_api:
            mock_api.return_value = {
                'combo_boxes': [
                    {'tag': 'Role', 'enabled': True, 'options': ['Manager', 'Programmer', 'Fitness Coach']},
                    {'tag': 'What', 'enabled': False, 'options': []},
                    {'tag': 'Why', 'enabled': False, 'options': []}
                ]
            }
            
            result = web_app.generate_template_combo_boxes(template)
        
        # Then: Should return cascading combo box structure
        assert 'combo_boxes' in result
        assert len(result['combo_boxes']) == 3
        
        # Verify first combo box is enabled
        assert result['combo_boxes'][0]['enabled'] == True
        assert result['combo_boxes'][0]['tag'] == 'Role'
        
        # Verify downstream combo boxes are disabled initially
        assert result['combo_boxes'][1]['enabled'] == False
        assert result['combo_boxes'][2]['enabled'] == False
    
    def test_cascading_relationships_are_loaded(self, web_app):
        """Test that cascading relationships are loaded from configuration."""
        # Given: Cascading relationship configuration
        relationships = {
            "Manager": {
                "Review Status": ["Evaluate Next Actions", "Review Performance"],
                "File Compliance Report": ["Keep higher-ups informed", "Meet our standards"]
            },
            "Programmer": {
                "Code Review": ["Keep Code Clean", "Propagate Good Practices"],
                "Test Plan": ["Ensure Quality", "Prevent Bugs"]
            }
        }
        
        # When: Loading relationships into template builder
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(relationships)
            
            result = web_app.load_cascading_relationships()
        
        # Then: Should return the relationship structure
        assert 'Manager' in result
        assert 'Programmer' in result
        assert 'Review Status' in result['Manager']
        assert 'Code Review' in result['Programmer']
    
    def test_template_builder_generates_cascading_options(self, web_app):
        """Test that selecting a role generates appropriate what options."""
        # Given: A role selection
        role = "Manager"
        
        # When: Getting what options for the role
        with patch.object(web_app, 'load_cascading_relationships') as mock_load:
            mock_load.return_value = {
                "Manager": {
                    "Review Status": ["Evaluate Next Actions", "Review Performance"],
                    "File Compliance Report": ["Keep higher-ups informed", "Meet our standards"]
                }
            }
            
            what_options = web_app.get_what_options_for_role(role)
        
        # Then: Should return the what options for Manager
        assert "Review Status" in what_options
        assert "File Compliance Report" in what_options
        assert len(what_options) == 2
    
    def test_cascading_state_persistence(self, web_app):
        """Test that cascading selections are persisted and restored."""
        # Given: A user's selection state
        state = {
            "Manager": {
                "selected": "Review Status",
                "Review Status": {
                    "selected": "Evaluate Next Actions"
                }
            }
        }
        
        # When: Saving and restoring state
        web_app.save_cascading_state(state)
        restored_state = web_app.load_cascading_state()
        
        # Then: State should be preserved
        assert restored_state["Manager"]["selected"] == "Review Status"
        assert restored_state["Manager"]["Review Status"]["selected"] == "Evaluate Next Actions"
    
    def test_template_builder_integration_end_to_end(self, web_app):
        """Test complete integration of cascading combo boxes in template builder."""
        # Given: A complete template builder session
        template = "As a [Role], I want to [What], so that [Why]"
        selections = {
            "Role": "Manager",
            "What": "Review Status", 
            "Why": "Evaluate Next Actions"
        }
        
        # When: Building the final prompt
        with patch.object(web_app, 'load_cascading_relationships') as mock_load:
            mock_load.return_value = {
                "Manager": {
                    "Review Status": ["Evaluate Next Actions", "Review Performance"]
                }
            }
            
            final_prompt = web_app.build_final_prompt(template, selections)
        
        # Then: Should generate the complete prompt
        expected = "As a Manager, I want to Review Status, so that Evaluate Next Actions"
        assert final_prompt == expected
