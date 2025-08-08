import pytest
from approvaltests import verify
from prompt_manager.business.template_parser import TemplateParser
from prompt_manager.business.component_manager import ComponentManager
from prompt_manager.business.template_storage import TemplateStorage


class TestTemplateApprovals:
    """Use Approvals for dynamic output validation."""
    
    def test_template_parsing_outputs(self):
        """Verify template parsing generates expected combo box structures."""
        parser = TemplateParser()
        
        test_cases = [
            "As a [Role], I want to [What], so that I can [Why]",
            "Given [Context], when [Action], then [Result]",
            "Review this code as a [Role] with focus on [Aspect]",
            "Create a [Type] that [Function] for [Purpose]"
        ]
        
        results = []
        for template in test_cases:
            combo_boxes = parser.generate_combo_boxes(template)
            results.append({
                "template": template,
                "combo_boxes": combo_boxes
            })
        
        verify(results)
    
    def test_component_hierarchy_validation(self):
        """Verify component hierarchy structure and relationships."""
        manager = ComponentManager()
        components = manager.get_all_components()
        
        # Extract hierarchy information
        hierarchy_info = {}
        for tag, components_list in components.items():
            hierarchy_info[tag] = {
                "root_components": len([c for c in components_list if not c.get("parent")]),
                "child_components": len([c for c in components_list if c.get("parent")]),
                "total_components": len(components_list),
                "parent_relationships": {}
            }
            
            # Group by parent
            for comp in components_list:
                parent = comp.get("parent", "root")
                if parent not in hierarchy_info[tag]["parent_relationships"]:
                    hierarchy_info[tag]["parent_relationships"][parent] = []
                hierarchy_info[tag]["parent_relationships"][parent].append(comp["label"])
        
        verify(hierarchy_info)
    
    def test_final_prompt_generation(self):
        """Verify final prompt generation from various selections."""
        parser = TemplateParser()
        
        test_scenarios = [
            {
                "template": "As a [Role], I want to [What], so that I can [Why]",
                "selections": [
                    {"tag": "Role", "value": "Programmer", "enabled": True},
                    {"tag": "What", "value": "Writing Code", "enabled": True},
                    {"tag": "Why", "value": "Implement a Feature", "enabled": True}
                ]
            },
            {
                "template": "Given [Context], when [Action], then [Result]",
                "selections": [
                    {"tag": "Context", "value": "User is logged in", "enabled": True},
                    {"tag": "Action", "value": "User clicks submit", "enabled": True},
                    {"tag": "Result", "value": "Form is processed", "enabled": True}
                ]
            }
        ]
        
        results = []
        for scenario in test_scenarios:
            final_prompt = parser.generate_prompt_from_selections(
                scenario["template"], 
                scenario["selections"]
            )
            results.append({
                "template": scenario["template"],
                "selections": scenario["selections"],
                "final_prompt": final_prompt
            })
        
        verify(results)
    
    def test_template_storage_round_trip(self):
        """Verify template storage and loading preserves all data."""
        storage = TemplateStorage()
        
        test_templates = [
            {
                "name": "User Story Template",
                "description": "Standard user story format",
                "template": "As a [Role], I want to [What], so that I can [Why]",
                "combo_boxes": [
                    {"tag": "Role", "value": "Programmer", "enabled": True},
                    {"tag": "What", "value": "Writing Code", "enabled": True},
                    {"tag": "Why", "value": "Implement a Feature", "enabled": True}
                ]
            },
            {
                "name": "Code Review Template",
                "description": "Code review format",
                "template": "Review this code as a [Role] with focus on [Aspect]",
                "combo_boxes": [
                    {"tag": "Role", "value": "Senior Developer", "enabled": True},
                    {"tag": "Aspect", "value": "Security", "enabled": True}
                ]
            }
        ]
        
        results = []
        for template_data in test_templates:
            # Save template
            template_id = storage.save_template(template_data)
            
            # Load template
            loaded_template = storage.load_template(template_id)
            
            # Normalize dynamic data for consistent testing
            normalized_original = self._normalize_template_data(template_data)
            normalized_loaded = self._normalize_template_data(loaded_template)
            
            # Compare normalized data
            comparison = {
                "original": normalized_original,
                "loaded": normalized_loaded,
                "matches": normalized_original == normalized_loaded
            }
            results.append(comparison)
            
            # Clean up
            storage.delete_template(template_id)
        
        verify(results)
    
    def _normalize_template_data(self, template_data):
        """Normalize template data by removing dynamic fields for consistent testing."""
        normalized = template_data.copy()
        
        # Remove dynamic fields
        normalized.pop('id', None)
        normalized.pop('created_date', None)
        normalized.pop('updated_date', None)
        
        return normalized
