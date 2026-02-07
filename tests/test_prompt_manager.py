# tests/test_prompt_manager.py

import pytest
import tempfile
import os
from src.prompt_manager.prompt_manager import PromptManager
from src.prompt_manager.prompt import Prompt


class TestPromptManager:
    @pytest.fixture
    def temp_manager(self):
        """Create a PromptManager with a temporary storage file."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = tmp.name
        
        manager = PromptManager(tmp_path)
        yield manager
        
        # Cleanup
        try:
            os.unlink(tmp_path)
        except:
            pass
    
    def test_add_prompt_returns_guid(self, temp_manager):
        prompt_id = temp_manager.add_prompt("Test Prompt", "Hello world", "test")
        
        assert isinstance(prompt_id, str)
        assert len(prompt_id) > 0
        assert prompt_id in temp_manager.prompts
    
    def test_add_prompt_sets_id(self, temp_manager):
        prompt_id = temp_manager.add_prompt("Test Prompt", "Hello world", "test")
        
        prompt = temp_manager.prompts[prompt_id]
        assert prompt.id == prompt_id
        assert prompt.name == "Test Prompt"
        assert prompt.text == "Hello world"
        assert prompt.category == "test"
    
    def test_get_prompt_by_id(self, temp_manager):
        prompt_id = temp_manager.add_prompt("Test Prompt", "Hello world", "test")
        
        prompt = temp_manager.get_prompt(prompt_id)
        assert prompt is not None
        assert prompt.name == "Test Prompt"
    
    def test_get_prompt_by_id_not_found(self, temp_manager):
        prompt = temp_manager.get_prompt("non-existent-id")
        assert prompt is None
    
    def test_get_prompt_by_name(self, temp_manager):
        temp_manager.add_prompt("Test Prompt", "Hello world", "test")
        
        prompt = temp_manager.get_prompt_by_name("Test Prompt")
        assert prompt is not None
        assert prompt.name == "Test Prompt"
    
    def test_get_prompt_by_name_not_found(self, temp_manager):
        prompt = temp_manager.get_prompt_by_name("Non-existent")
        assert prompt is None
    
    def test_list_prompts_empty(self, temp_manager):
        prompts = temp_manager.list_prompts()
        assert len(prompts) == 0
    
    def test_list_prompts_all(self, temp_manager):
        temp_manager.add_prompt("Prompt 1", "Text 1", "cat1")
        temp_manager.add_prompt("Prompt 2", "Text 2", "cat2")
        
        prompts = temp_manager.list_prompts()
        assert len(prompts) == 2
        names = [p.name for p in prompts]
        assert "Prompt 1" in names
        assert "Prompt 2" in names
    
    def test_list_prompts_by_category(self, temp_manager):
        temp_manager.add_prompt("Prompt 1", "Text 1", "cat1")
        temp_manager.add_prompt("Prompt 2", "Text 2", "cat1")
        temp_manager.add_prompt("Prompt 3", "Text 3", "cat2")
        
        prompts = temp_manager.list_prompts("cat1")
        assert len(prompts) == 2
        for prompt in prompts:
            assert prompt.category == "cat1"
    
    def test_delete_prompt_success(self, temp_manager):
        prompt_id = temp_manager.add_prompt("Test Prompt", "Hello world", "test")
        
        result = temp_manager.delete_prompt(prompt_id)
        assert result is True
        assert len(temp_manager.prompts) == 0
        assert temp_manager.get_prompt(prompt_id) is None
    
    def test_delete_prompt_not_found(self, temp_manager):
        result = temp_manager.delete_prompt("non-existent-id")
        assert result is False
    
    def test_update_prompt_success(self, temp_manager):
        prompt_id = temp_manager.add_prompt("Old Name", "Old Text", "old_cat")
        
        result = temp_manager.update_prompt(prompt_id, "New Name", "New Text", "new_cat")
        assert result is True
        
        prompt = temp_manager.get_prompt(prompt_id)
        assert prompt.name == "New Name"
        assert prompt.text == "New Text"
        assert prompt.category == "new_cat"
    
    def test_update_prompt_partial(self, temp_manager):
        prompt_id = temp_manager.add_prompt("Original", "Original Text", "original")
        
        result = temp_manager.update_prompt(prompt_id, text="Updated Text")
        assert result is True
        
        prompt = temp_manager.get_prompt(prompt_id)
        assert prompt.name == "Original"  # Unchanged
        assert prompt.text == "Updated Text"  # Changed
        assert prompt.category == "original"  # Unchanged
    
    def test_update_prompt_not_found(self, temp_manager):
        result = temp_manager.update_prompt("non-existent-id", name="New Name")
        assert result is False
    
    def test_search_prompts_by_name(self, temp_manager):
        temp_manager.add_prompt("Hello World", "Some text", "test")
        temp_manager.add_prompt("Goodbye", "Other text", "test")
        
        results = temp_manager.search_prompts("hello")
        assert len(results) == 1
        assert results[0].name == "Hello World"
    
    def test_search_prompts_by_text(self, temp_manager):
        temp_manager.add_prompt("Prompt 1", "Hello world text", "test")
        temp_manager.add_prompt("Prompt 2", "Goodbye text", "test")
        
        results = temp_manager.search_prompts("world")
        assert len(results) == 1
        assert "world" in results[0].text.lower()
    
    def test_search_prompts_case_insensitive(self, temp_manager):
        temp_manager.add_prompt("HELLO WORLD", "Some text", "test")
        
        results = temp_manager.search_prompts("hello")
        assert len(results) == 1
        assert results[0].name == "HELLO WORLD"
    
    def test_search_prompts_no_results(self, temp_manager):
        temp_manager.add_prompt("Test Prompt", "Some text", "test")
        
        results = temp_manager.search_prompts("nonexistent")
        assert len(results) == 0