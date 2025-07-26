from typing import List, Dict, Any
from ..prompt import Prompt


class SearchService:
    """Business rules for prompt search functionality."""
    
    def __init__(self):
        self.default_search_fields = ['name', 'text']
        self.max_search_results = 100
    
    def search_prompts(self, prompts: List[Prompt], query: str, 
                      fields: List[str] = None, 
                      max_results: int = None) -> List[Prompt]:
        """Search prompts by query across specified fields."""
        if not query.strip():
            return []
        
        if fields is None:
            fields = self.default_search_fields
        
        if max_results is None:
            max_results = self.max_search_results
        
        query_lower = query.lower().strip()
        results = []
        
        for prompt in prompts:
            if self._prompt_matches_query(prompt, query_lower, fields):
                results.append(prompt)
                
                if len(results) >= max_results:
                    break
        
        return results
    
    def search_prompts_by_category(self, prompts: List[Prompt], category: str) -> List[Prompt]:
        """Search prompts by exact category match."""
        if not category.strip():
            return []
        
        category_lower = category.lower().strip()
        return [prompt for prompt in prompts if prompt.category.lower() == category_lower]
    
    def get_categories(self, prompts: List[Prompt]) -> List[str]:
        """Get unique categories from prompts."""
        categories = set()
        for prompt in prompts:
            if prompt.category:
                categories.add(prompt.category)
        
        return sorted(list(categories))
    
    def get_prompts_by_category(self, prompts: List[Prompt], category: str) -> List[Prompt]:
        """Get all prompts in a specific category."""
        if not category.strip():
            return []
        
        category_lower = category.lower().strip()
        return [prompt for prompt in prompts if prompt.category.lower() == category_lower]
    
    def _prompt_matches_query(self, prompt: Prompt, query: str, fields: List[str]) -> bool:
        """Check if a prompt matches the search query."""
        for field in fields:
            if field == 'name' and query in prompt.name.lower():
                return True
            elif field == 'text' and query in prompt.text.lower():
                return True
            elif field == 'category' and query in prompt.category.lower():
                return True
            elif field == 'id' and query in prompt.id.lower():
                return True
        
        return False
    
    def search_with_filters(self, prompts: List[Prompt], 
                          query: str = None,
                          category: str = None,
                          max_results: int = None) -> List[Prompt]:
        """Search prompts with multiple filters."""
        filtered_prompts = prompts
        
        # Filter by category first
        if category:
            filtered_prompts = self.get_prompts_by_category(filtered_prompts, category)
        
        # Then search by query
        if query:
            filtered_prompts = self.search_prompts(filtered_prompts, query, max_results=max_results)
        
        return filtered_prompts
    
    def get_search_suggestions(self, prompts: List[Prompt], partial_query: str) -> List[str]:
        """Get search suggestions based on partial query."""
        if not partial_query.strip():
            return []
        
        partial_lower = partial_query.lower().strip()
        suggestions = set()
        
        for prompt in prompts:
            # Check name
            if partial_lower in prompt.name.lower():
                suggestions.add(prompt.name)
            
            # Check category
            if partial_lower in prompt.category.lower():
                suggestions.add(prompt.category)
        
        return sorted(list(suggestions))[:10]  # Limit to 10 suggestions 