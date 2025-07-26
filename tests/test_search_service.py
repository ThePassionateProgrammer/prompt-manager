# tests/test_search_service.py

import pytest
from src.prompt_manager.business.search_service import SearchService
from src.prompt_manager.prompt import Prompt


class TestSearchService:
    def setup_method(self):
        self.search_service = SearchService()
        
        # Create test prompts
        self.prompt1 = Prompt("Hello World", "This is a greeting prompt", "greeting")
        self.prompt1.id = "id1"
        
        self.prompt2 = Prompt("Goodbye", "This is a farewell prompt", "farewell")
        self.prompt2.id = "id2"
        
        self.prompt3 = Prompt("Python Tutorial", "Learn Python programming", "tutorial")
        self.prompt3.id = "id3"
        
        self.prompt4 = Prompt("JavaScript Guide", "Learn JavaScript basics", "tutorial")
        self.prompt4.id = "id4"
        
        self.prompts = [self.prompt1, self.prompt2, self.prompt3, self.prompt4]
    
    def test_search_prompts_by_name(self):
        """Test searching prompts by name."""
        results = self.search_service.search_prompts(self.prompts, "hello")
        
        assert len(results) == 1
        assert results[0].name == "Hello World"
    
    def test_search_prompts_by_text(self):
        """Test searching prompts by text content."""
        results = self.search_service.search_prompts(self.prompts, "greeting")
        
        assert len(results) == 1
        assert results[0].name == "Hello World"
    
    def test_search_prompts_by_category(self):
        """Test searching prompts by category."""
        results = self.search_service.search_prompts(self.prompts, "tutorial")
        
        assert len(results) == 1  # Only "Python Tutorial" contains "tutorial" in name
        assert results[0].name == "Python Tutorial"
    
    def test_search_prompts_case_insensitive(self):
        """Test that search is case insensitive."""
        results = self.search_service.search_prompts(self.prompts, "HELLO")
        
        assert len(results) == 1
        assert results[0].name == "Hello World"
    
    def test_search_prompts_empty_query(self):
        """Test search with empty query returns no results."""
        results = self.search_service.search_prompts(self.prompts, "")
        
        assert len(results) == 0
    
    def test_search_prompts_whitespace_query(self):
        """Test search with whitespace-only query returns no results."""
        results = self.search_service.search_prompts(self.prompts, "   ")
        
        assert len(results) == 0
    
    def test_search_prompts_specific_fields(self):
        """Test searching with specific fields."""
        # Search only in name field
        results = self.search_service.search_prompts(self.prompts, "learn", fields=['name'])
        
        assert len(results) == 0  # "learn" is in text, not name
        
        # Search only in text field
        results = self.search_service.search_prompts(self.prompts, "learn", fields=['text'])
        
        assert len(results) == 2  # "learn" is in both tutorial prompts
    
    def test_search_prompts_max_results(self):
        """Test that search respects max_results limit."""
        # Add more prompts to test limit
        for i in range(5, 15):
            prompt = Prompt(f"Prompt {i}", f"Text {i}", "test")
            prompt.id = f"id{i}"
            self.prompts.append(prompt)
        
        results = self.search_service.search_prompts(self.prompts, "prompt", max_results=5)
        
        assert len(results) == 5
    
    def test_search_prompts_by_category_method(self):
        """Test the search_prompts_by_category method."""
        results = self.search_service.search_prompts_by_category(self.prompts, "tutorial")
        
        assert len(results) == 2
        for prompt in results:
            assert prompt.category == "tutorial"
    
    def test_search_prompts_by_category_empty_category(self):
        """Test search by category with empty category."""
        results = self.search_service.search_prompts_by_category(self.prompts, "")
        
        assert len(results) == 0
    
    def test_get_categories(self):
        """Test getting unique categories."""
        categories = self.search_service.get_categories(self.prompts)
        
        expected_categories = ["farewell", "greeting", "tutorial"]
        assert categories == expected_categories
    
    def test_get_categories_empty_list(self):
        """Test getting categories from empty prompt list."""
        categories = self.search_service.get_categories([])
        
        assert categories == []
    
    def test_get_prompts_by_category(self):
        """Test getting prompts by category."""
        results = self.search_service.get_prompts_by_category(self.prompts, "tutorial")
        
        assert len(results) == 2
        for prompt in results:
            assert prompt.category == "tutorial"
    
    def test_get_prompts_by_category_case_insensitive(self):
        """Test getting prompts by category is case insensitive."""
        results = self.search_service.get_prompts_by_category(self.prompts, "TUTORIAL")
        
        assert len(results) == 2
        for prompt in results:
            assert prompt.category == "tutorial"
    
    def test_get_prompts_by_category_empty_category(self):
        """Test getting prompts by empty category."""
        results = self.search_service.get_prompts_by_category(self.prompts, "")
        
        assert len(results) == 0
    
    def test_search_with_filters_query_only(self):
        """Test search with filters using only query."""
        results = self.search_service.search_with_filters(self.prompts, query="hello")
        
        assert len(results) == 1
        assert results[0].name == "Hello World"
    
    def test_search_with_filters_category_only(self):
        """Test search with filters using only category."""
        results = self.search_service.search_with_filters(self.prompts, category="tutorial")
        
        assert len(results) == 2
        for prompt in results:
            assert prompt.category == "tutorial"
    
    def test_search_with_filters_both_query_and_category(self):
        """Test search with filters using both query and category."""
        results = self.search_service.search_with_filters(self.prompts, query="python", category="tutorial")
        
        assert len(results) == 1
        assert results[0].name == "Python Tutorial"
    
    def test_search_with_filters_no_filters(self):
        """Test search with filters using no filters."""
        results = self.search_service.search_with_filters(self.prompts)
        
        assert len(results) == 4  # All prompts
    
    def test_get_search_suggestions(self):
        """Test getting search suggestions."""
        suggestions = self.search_service.get_search_suggestions(self.prompts, "py")
        
        assert "Python Tutorial" in suggestions
    
    def test_get_search_suggestions_empty_query(self):
        """Test getting search suggestions with empty query."""
        suggestions = self.search_service.get_search_suggestions(self.prompts, "")
        
        assert suggestions == []
    
    def test_get_search_suggestions_whitespace_query(self):
        """Test getting search suggestions with whitespace-only query."""
        suggestions = self.search_service.get_search_suggestions(self.prompts, "   ")
        
        assert suggestions == []
    
    def test_get_search_suggestions_case_insensitive(self):
        """Test that search suggestions are case insensitive."""
        suggestions = self.search_service.get_search_suggestions(self.prompts, "PY")
        
        assert "Python Tutorial" in suggestions
    
    def test_get_search_suggestions_limit(self):
        """Test that search suggestions are limited."""
        # Add many prompts with similar names
        for i in range(20):
            prompt = Prompt(f"Python Tutorial {i}", f"Text {i}", "tutorial")
            prompt.id = f"id{i+10}"
            self.prompts.append(prompt)
        
        suggestions = self.search_service.get_search_suggestions(self.prompts, "python")
        
        assert len(suggestions) <= 10  # Limited to 10 suggestions 