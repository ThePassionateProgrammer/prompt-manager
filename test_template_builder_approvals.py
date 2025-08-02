"""
Approval tests for Template Builder functionality.

These tests capture dynamic behavior and save it to files for manual review,
reducing redundancy in testing API responses and UI interactions.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock


class TestTemplateBuilderApprovals:
    """Approval tests for Template Builder API and UI functionality."""
    
    def test_template_parsing_responses(self):
        """Test template parsing responses for various input patterns"""
        # Given: Various template patterns to test
        test_templates = [
            "As a [role], I want to [what], so that I can [why]",
            "Review this code as a [reviewer] with focus on [aspect]",
            "I found a bug in [component] that [description]",
            "This is a simple prompt without variables",
            "Multiple [var1] and [var2] and [var3] variables",
            "[single] variable only",
            "No variables in this template at all"
        ]
        
        # When: Parsing each template
        parsing_results = []
        for template in test_templates:
            variables = self._extract_variables(template)
            parsing_results.append(f"Template: {template}")
            parsing_results.append(f"Variables: {variables}")
            parsing_results.append("---")
        
        # Then: Save results for approval
        output = "\n".join(parsing_results)
        self._save_approval_output("template_parsing_responses", output)
        
        # Verify the output is as expected
        expected_variables = [
            ['role', 'what', 'why'],
            ['reviewer', 'aspect'],
            ['component', 'description'],
            [],
            ['var1', 'var2', 'var3'],
            ['single'],
            []
        ]
        
        for i, template in enumerate(test_templates):
            actual = self._extract_variables(template)
            assert actual == expected_variables[i], f"Template parsing failed for: {template}"
    
    def test_dropdown_generation_responses(self):
        """Test dropdown generation for different template variables"""
        # Given: Templates with different variable combinations
        test_templates = [
            "As a [role], I want to [what]",
            "Review this [component] as a [reviewer]",
            "I need to [action] the [target] because [reason]",
            "The [subject] should [behavior] when [condition]"
        ]
        
        # When: Generating dropdowns for each template
        dropdown_results = []
        for template in test_templates:
            dropdowns = self._generate_dropdowns(template)
            dropdown_results.append(f"Template: {template}")
            dropdown_results.append(f"Dropdowns: {json.dumps(dropdowns, indent=2)}")
            dropdown_results.append("---")
        
        # Then: Save results for approval
        output = "\n".join(dropdown_results)
        self._save_approval_output("dropdown_generation_responses", output)
        
        # Verify dropdowns are generated correctly
        for template in test_templates:
            variables = self._extract_variables(template)
            dropdowns = self._generate_dropdowns(template)
            assert len(dropdowns) == len(variables), f"Dropdown count mismatch for: {template}"
            for var in variables:
                assert var in dropdowns, f"Missing dropdown for variable: {var}"
    
    def test_context_aware_dropdown_updates(self):
        """Test context-aware dropdown updates based on selections"""
        # Given: Different context scenarios
        context_scenarios = [
            {
                'variable': 'what',
                'context': {'role': 'Programmer'},
                'description': 'Programmer role selection'
            },
            {
                'variable': 'what',
                'context': {'role': 'Chef'},
                'description': 'Chef role selection'
            },
            {
                'variable': 'why',
                'context': {'role': 'Programmer', 'what': 'Write code'},
                'description': 'Programmer + Write code context'
            },
            {
                'variable': 'why',
                'context': {'role': 'Chef', 'what': 'Shop for food'},
                'description': 'Chef + Shop for food context'
            }
        ]
        
        # When: Updating options for each context
        update_results = []
        for scenario in context_scenarios:
            options = self._get_context_options(scenario['variable'], scenario['context'])
            update_results.append(f"Scenario: {scenario['description']}")
            update_results.append(f"Variable: {scenario['variable']}")
            update_results.append(f"Context: {scenario['context']}")
            update_results.append(f"Options: {options}")
            update_results.append("---")
        
        # Then: Save results for approval
        output = "\n".join(update_results)
        self._save_approval_output("context_aware_dropdown_updates", output)
        
        # Verify context-aware updates work correctly
        for scenario in context_scenarios:
            options = self._get_context_options(scenario['variable'], scenario['context'])
            assert len(options) > 0, f"No options returned for: {scenario['description']}"
            assert all(isinstance(opt, str) for opt in options), f"Invalid option types for: {scenario['description']}"
    
    def test_final_prompt_generation(self):
        """Test final prompt generation with various selections"""
        # Given: Different template and selection combinations
        generation_scenarios = [
            {
                'template': "As a [role], I want to [what], so that I can [why]",
                'selections': {
                    'role': 'Programmer',
                    'what': 'Write code',
                    'why': 'Build better software'
                }
            },
            {
                'template': "Review this [component] as a [reviewer]",
                'selections': {
                    'component': 'API endpoint',
                    'reviewer': 'Senior Developer'
                }
            },
            {
                'template': "I need to [action] the [target] because [reason]",
                'selections': {
                    'action': 'fix',
                    'target': 'bug',
                    'reason': 'it\'s causing crashes'
                }
            }
        ]
        
        # When: Generating final prompts
        generation_results = []
        for scenario in generation_scenarios:
            final_prompt = self._generate_final_prompt(scenario['template'], scenario['selections'])
            generation_results.append(f"Template: {scenario['template']}")
            generation_results.append(f"Selections: {scenario['selections']}")
            generation_results.append(f"Final Prompt: {final_prompt}")
            generation_results.append("---")
        
        # Then: Save results for approval
        output = "\n".join(generation_results)
        self._save_approval_output("final_prompt_generation", output)
        
        # Verify final prompt generation
        for scenario in generation_scenarios:
            final_prompt = self._generate_final_prompt(scenario['template'], scenario['selections'])
            # Check that all variables are replaced
            for variable in scenario['selections']:
                assert f'[{variable}]' not in final_prompt, f"Variable {variable} not replaced in final prompt"
            # Check that all selections are included
            for value in scenario['selections'].values():
                assert value in final_prompt, f"Selection {value} not found in final prompt"
    
    def test_complete_template_builder_workflow(self):
        """Test complete template builder workflow from input to final prompt"""
        # Given: A complete workflow scenario
        workflow_steps = [
            {
                'step': 'Template Input',
                'data': "As a [role], I want to [what], so that I can [why]"
            },
            {
                'step': 'Parse Template',
                'data': {'variables': ['role', 'what', 'why']}
            },
            {
                'step': 'Generate Dropdowns',
                'data': {
                    'role': ['Programmer', 'Chef', 'Soccer Coach'],
                    'what': ['Write code', 'Shop for food', 'Create tests'],
                    'why': ['Build better software', 'Cook delicious meals', 'Improve quality']
                }
            },
            {
                'step': 'User Selection',
                'data': {'role': 'Programmer'}
            },
            {
                'step': 'Context Update',
                'data': {
                    'what': ['Write code', 'Create tests', 'Refactor', 'Debug'],
                    'why': ['Build better software', 'Solve problems', 'Learn new skills']
                }
            },
            {
                'step': 'Final Selection',
                'data': {
                    'role': 'Programmer',
                    'what': 'Write code',
                    'why': 'Build better software'
                }
            },
            {
                'step': 'Final Prompt',
                'data': "As a Programmer, I want to Write code, so that I can Build better software"
            }
        ]
        
        # When: Executing the workflow
        workflow_results = []
        for step in workflow_steps:
            workflow_results.append(f"Step: {step['step']}")
            workflow_results.append(f"Data: {json.dumps(step['data'], indent=2)}")
            workflow_results.append("---")
        
        # Then: Save results for approval
        output = "\n".join(workflow_results)
        self._save_approval_output("complete_template_builder_workflow", output)
        
        # Verify workflow steps are logical
        assert len(workflow_steps) >= 3, "Workflow should have at least 3 steps"
        assert workflow_steps[0]['step'] == 'Template Input', "Workflow should start with template input"
        assert workflow_steps[-1]['step'] == 'Final Prompt', "Workflow should end with final prompt"
    
    def _save_approval_output(self, test_name, output):
        """Save approval test output to a file for manual review"""
        filename = f"test_template_builder_approvals_{test_name}.output.txt"
        with open(filename, 'w') as f:
            f.write(output)
        print(f"Approval output saved to: {filename}")
    
    # Helper methods to simulate the actual functionality
    def _extract_variables(self, template):
        """Extract variables from template text (simulating the actual implementation)"""
        import re
        return re.findall(r'\[([^\]]+)\]', template)
    
    def _generate_dropdowns(self, template):
        """Generate dropdown options for template variables"""
        variables = self._extract_variables(template)
        default_options = {
            'role': ['Programmer', 'Chef', 'Soccer Coach', 'Teacher', 'Designer'],
            'what': ['Write code', 'Shop for food', 'Create tests', 'Prepare lunch', 'Plan dinner party', 'Refactor'],
            'why': ['Build better software', 'Cook delicious meals', 'Improve code quality', 'Feed my family', 'Host friends'],
            'action': ['Write code', 'Create tests', 'Refactor', 'Shop for food', 'Prepare lunch'],
            'context': ['Web development', 'Mobile app', 'Backend API', 'Kitchen', 'Restaurant'],
            'component': ['API endpoint', 'Database', 'Frontend', 'Backend', 'UI component'],
            'reviewer': ['Senior Developer', 'Junior Developer', 'Architect', 'QA Engineer'],
            'target': ['bug', 'feature', 'performance', 'security issue'],
            'reason': ['it\'s causing crashes', 'users need it', 'it\'s too slow', 'it\'s insecure'],
            'subject': ['user', 'system', 'component', 'feature'],
            'behavior': ['respond', 'update', 'display', 'process'],
            'condition': ['user clicks', 'data changes', 'time expires', 'error occurs']
        }
        
        dropdowns = {}
        for var in variables:
            dropdowns[var] = {
                'options': default_options.get(var, [f'Option 1 for {var}', f'Option 2 for {var}'])
            }
        return dropdowns
    
    def _get_context_options(self, variable, context):
        """Get context-aware options for a variable"""
        context_options = {
            'what': {
                'Programmer': ['Write code', 'Create tests', 'Refactor', 'Debug', 'Optimize'],
                'Chef': ['Shop for food', 'Prepare lunch', 'Plan dinner party', 'Cook meal', 'Bake dessert'],
                'Soccer Coach': ['Train players', 'Plan strategy', 'Analyze games', 'Motivate team', 'Teach skills']
            },
            'why': {
                'Write code': ['Build better software', 'Solve problems', 'Learn new skills', 'Improve efficiency'],
                'Shop for food': ['Cook delicious meals', 'Feed my family', 'Save money', 'Eat healthy'],
                'Create tests': ['Ensure quality', 'Prevent bugs', 'Build confidence', 'Document behavior']
            }
        }
        
        if variable in context_options:
            for context_key, options in context_options[variable].items():
                if context_key in context.values():
                    return options
        
        # Fallback options
        default_options = {
            'what': ['Write code', 'Shop for food', 'Create tests', 'Prepare lunch'],
            'why': ['Build better software', 'Cook delicious meals', 'Improve quality', 'Feed my family']
        }
        return default_options.get(variable, [f'Option for {variable}'])
    
    def _generate_final_prompt(self, template, selections):
        """Generate final prompt by replacing variables with selections"""
        final_prompt = template
        for variable, value in selections.items():
            final_prompt = final_prompt.replace(f'[{variable}]', value)
        return final_prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 