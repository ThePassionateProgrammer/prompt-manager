"""
End-to-End Tests for Prompt Manager

These tests verify the complete user workflow from start to finish,
including all major features and their interactions.
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch
from src.prompt_manager.prompt_manager import PromptManager


class TestEndToEndWorkflow:
    """Test complete user workflows from start to finish."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([], f)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        os.unlink(temp_file)
    
    @pytest.fixture
    def manager(self, temp_storage):
        """Create a PromptManager instance with temporary storage."""
        return PromptManager(temp_storage)
    
    def test_complete_prompt_lifecycle(self, manager):
        """Test complete prompt lifecycle: create → search → edit → delete."""
        # 1. Create a new prompt
        prompt_id = manager.add_prompt(
            name="Test Prompt",
            text="This is a test prompt for end-to-end testing.",
            category="testing"
        )
        assert prompt_id is not None
        
        # 2. Verify prompt was created
        prompt = manager.get_prompt(prompt_id)
        assert prompt.name == "Test Prompt"
        assert prompt.text == "This is a test prompt for end-to-end testing."
        assert prompt.category == "testing"
        
        # 3. Search for the prompt
        search_results = manager.search_prompts("test")
        assert len(search_results) == 1
        assert search_results[0].id == prompt_id
        
        # 4. Edit the prompt
        success = manager.update_prompt(
            prompt_id,
            name="Updated Test Prompt",
            text="This is an updated test prompt.",
            category="updated"
        )
        assert success is True
        
        # 5. Verify the edit
        updated_prompt = manager.get_prompt(prompt_id)
        assert updated_prompt.name == "Updated Test Prompt"
        assert updated_prompt.text == "This is an updated test prompt."
        assert updated_prompt.category == "updated"
        
        # 6. Delete the prompt
        success = manager.delete_prompt(prompt_id)
        assert success is True
        
        # 7. Verify deletion
        deleted_prompt = manager.get_prompt(prompt_id)
        assert deleted_prompt is None
        
        # 8. Verify it's not in search results
        search_results = manager.search_prompts("test")
        assert len(search_results) == 0
    
    def test_template_builder_workflow(self, manager):
        """Test complete template builder workflow."""
        # 1. Create a template prompt
        template_id = manager.add_prompt(
            name="User Story Template",
            text="As a [role], I want to [what], so that I can [why]",
            category="template"
        )
        
        # 2. Verify template was created
        template = manager.get_prompt(template_id)
        assert "[role]" in template.text
        assert "[what]" in template.text
        assert "[why]" in template.text
        
        # 3. Generate a specific prompt from template
        generated_text = template.text.replace("[role]", "Developer")
        generated_text = generated_text.replace("[what]", "Write code")
        generated_text = generated_text.replace("[why]", "Build better software")
        
        # 4. Create the generated prompt
        generated_id = manager.add_prompt(
            name="Generated User Story",
            text=generated_text,
            category="generated"
        )
        
        # 5. Verify generated prompt
        generated = manager.get_prompt(generated_id)
        assert generated.text == "As a Developer, I want to Write code, so that I can Build better software"
        assert generated.category == "generated"
        
        # 6. Search for generated prompts
        generated_results = manager.search_prompts("generated")
        assert len(generated_results) == 1
        assert generated_results[0].id == generated_id
    
    def test_import_export_workflow(self, manager, temp_storage):
        """Test import/export functionality."""
        # 1. Create some test prompts
        prompt1_id = manager.add_prompt(
            name="Export Test 1",
            text="First test prompt for export",
            category="export"
        )
        prompt2_id = manager.add_prompt(
            name="Export Test 2", 
            text="Second test prompt for export",
            category="export"
        )
        
        # 2. Export prompts (simulate export functionality)
        prompts = manager.list_prompts()
        export_data = {
            'export_date': '2024-01-01T00:00:00',
            'total_prompts': len(prompts),
            'prompts': []
        }
        
        for prompt in prompts:
            export_data['prompts'].append({
                'id': prompt.id,
                'name': prompt.name,
                'text': prompt.text,
                'category': prompt.category,
                'created_at': prompt.created_at,
                'modified_at': prompt.modified_at
            })
        
        # 3. Create a new manager for import testing
        import_manager = PromptManager(temp_storage + "_import")
        
        # 4. Import the exported data
        imported_count = 0
        for prompt_data in export_data['prompts']:
            try:
                # Check if prompt already exists
                existing = import_manager.search_prompts(prompt_data['name'])
                if not existing:
                    import_manager.add_prompt(
                        name=prompt_data['name'],
                        text=prompt_data['text'],
                        category=prompt_data['category']
                    )
                    imported_count += 1
            except Exception:
                continue
        
        # 5. Verify import
        assert imported_count == 2
        
        # 6. Verify imported prompts
        imported_prompts = import_manager.list_prompts()
        assert len(imported_prompts) == 2
        
        # 7. Verify prompt content
        names = [p.name for p in imported_prompts]
        assert "Export Test 1" in names
        assert "Export Test 2" in names
    
    def test_error_handling_workflow(self, manager):
        """Test error handling in various scenarios."""
        # 1. Try to get non-existent prompt
        non_existent_prompt = manager.get_prompt("non-existent-id")
        assert non_existent_prompt is None
        
        # 2. Try to delete non-existent prompt
        delete_success = manager.delete_prompt("non-existent-id")
        assert delete_success is False
        
        # 3. Try to update non-existent prompt
        update_success = manager.update_prompt("non-existent-id", "name", "text", "category")
        assert update_success is False
        
        # 4. Create prompt with empty name (should work without validation)
        empty_name_id = manager.add_prompt("", "Some text", "category")
        assert empty_name_id is not None
        
        # 5. Create prompt with empty text (should work without validation)
        empty_text_id = manager.add_prompt("Name", "", "category")
        assert empty_text_id is not None
    
    def test_search_functionality_workflow(self, manager):
        """Test comprehensive search functionality."""
        # 1. Create prompts with different content
        manager.add_prompt("Python Code", "Write Python code for web scraping", "coding")
        manager.add_prompt("JavaScript Code", "Write JavaScript for DOM manipulation", "coding")
        manager.add_prompt("Writing Guide", "How to write effective documentation", "writing")
        manager.add_prompt("Analysis Report", "Analyze data and create reports", "analysis")
        
        # 2. Test search by name
        results = manager.search_prompts("Python")
        assert len(results) == 1
        assert results[0].name == "Python Code"
        
        # 3. Test search by content
        results = manager.search_prompts("web scraping")
        assert len(results) == 1
        assert "web scraping" in results[0].text
        
        # 4. Test search by category (using list_prompts)
        results = manager.list_prompts("coding")
        assert len(results) == 2
        categories = [r.category for r in results]
        assert all(cat == "coding" for cat in categories)
        
        # 5. Test search with no results
        results = manager.search_prompts("nonexistent")
        assert len(results) == 0
    
    def test_category_management_workflow(self, manager):
        """Test category management functionality."""
        # 1. Create prompts in different categories
        categories = ["coding", "writing", "analysis", "creative"]
        for i, category in enumerate(categories):
            manager.add_prompt(
                f"Prompt {i+1}",
                f"Content for {category} prompt",
                category
            )
        
        # 2. Get all prompts and verify categories
        all_prompts = manager.list_prompts()
        assert len(all_prompts) == 4
        
        # 3. Test category filtering
        coding_prompts = manager.list_prompts("coding")
        assert len(coding_prompts) == 1
        
        # 4. Update category
        coding_prompt = coding_prompts[0]
        success = manager.update_prompt(
            coding_prompt.id,
            category="updated-coding"
        )
        assert success is True
        
        # 5. Verify category update
        updated_prompt = manager.get_prompt(coding_prompt.id)
        assert updated_prompt.category == "updated-coding"
    
    def test_bulk_operations_workflow(self, manager):
        """Test bulk operations functionality."""
        # 1. Create multiple prompts
        prompt_ids = []
        for i in range(5):
            prompt_id = manager.add_prompt(
                f"Bulk Prompt {i+1}",
                f"Content for bulk prompt {i+1}",
                "bulk"
            )
            prompt_ids.append(prompt_id)
        
        # 2. Verify all prompts were created
        all_prompts = manager.list_prompts()
        assert len(all_prompts) == 5
        
        # 3. Bulk update category
        for prompt_id in prompt_ids:
            prompt = manager.get_prompt(prompt_id)
            success = manager.update_prompt(
                prompt_id,
                category="updated-bulk"
            )
            assert success is True
        
        # 4. Verify bulk update
        updated_prompts = manager.list_prompts()
        categories = [p.category for p in updated_prompts]
        assert all(cat == "updated-bulk" for cat in categories)
        
        # 5. Bulk delete
        for prompt_id in prompt_ids:
            success = manager.delete_prompt(prompt_id)
            assert success is True
        
        # 6. Verify bulk delete
        remaining_prompts = manager.list_prompts()
        assert len(remaining_prompts) == 0


class TestWebInterfaceIntegration:
    """Test web interface integration with the backend."""
    
    def test_web_interface_initialization(self):
        """Test that web interface can be initialized."""
        from enhanced_simple_server import app
        assert app is not None
        assert app.name == 'enhanced_simple_server'
    
    def test_web_routes_registration(self):
        """Test that all web routes are properly registered."""
        from enhanced_simple_server import app
        
        # Check essential routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        essential_routes = ['/', '/add', '/search', '/edit', '/export', '/import', '/template-builder']
        
        for route in essential_routes:
            assert route in routes, f"Route {route} not found in registered routes"
    
    def test_template_builder_integration(self):
        """Test template builder integration with web interface."""
        from enhanced_simple_server import app
        
        # Check template builder routes
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        template_routes = [
            '/template/parse',
            '/template/generate-dropdowns', 
            '/template/update-options',
            '/template/generate-final',
            '/template/edit-mode',
            '/template/generate'
        ]
        
        for route in template_routes:
            assert route in routes, f"Template route {route} not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 