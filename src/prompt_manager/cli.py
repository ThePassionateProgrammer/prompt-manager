import sys
import json
import argparse
from typing import Optional
from .prompt_manager import PromptManager


class PromptManagerCLI:
    def __init__(self, storage_file: str = "prompts.json"):
        self.manager = PromptManager(storage_file)
    
    def add_prompt(self, name: str, text: Optional[str] = None, category: str = "general") -> bool:
        """Add a new prompt."""
        if text is None:
            # Read from stdin
            print("Enter prompt text (Ctrl+D to finish):")
            lines = []
            try:
                while True:
                    line = input()
                    lines.append(line)
            except EOFError:
                pass
            text = '\n'.join(lines)
        
        if not text.strip():
            print("Error: Prompt text cannot be empty")
            return False
        
        prompt_id = self.manager.add_prompt(name, text, category)
        print(f"Added prompt '{name}' with ID: {prompt_id}")
        return True
    
    def list_prompts(self, category: Optional[str] = None) -> bool:
        """List all prompts."""
        prompts = self.manager.list_prompts(category)
        
        if not prompts:
            if category:
                print(f"No prompts found in category '{category}'")
            else:
                print("No prompts found")
            return True
        
        # Output as JSON
        output = []
        for prompt in prompts:
            output.append(prompt.to_dict())
        
        print(json.dumps(output, indent=2))
        return True
    
    def get_prompt(self, identifier: str) -> bool:
        """Get a specific prompt by ID or name."""
        # Try by ID first
        prompt = self.manager.get_prompt(identifier)
        if prompt is None:
            # Try by name
            prompt = self.manager.get_prompt_by_name(identifier)
        
        if prompt is None:
            print(f"Error: Prompt '{identifier}' not found")
            return False
        
        # Output as JSON
        print(json.dumps(prompt.to_dict(), indent=2))
        return True
    
    def delete_prompt(self, identifier: str) -> bool:
        """Delete a prompt by ID or name."""
        # Try by ID first
        prompt = self.manager.get_prompt(identifier)
        if prompt is None:
            # Try by name
            prompt = self.manager.get_prompt_by_name(identifier)
            if prompt:
                identifier = prompt.id
        
        if not prompt:
            print(f"Error: Prompt '{identifier}' not found")
            return False
        
        result = self.manager.delete_prompt(identifier)
        if result:
            print(f"Deleted prompt '{prompt.name}'")
        else:
            print(f"Error: Failed to delete prompt '{identifier}'")
        return result
    
    def search_prompts(self, query: str) -> bool:
        """Search prompts by name or text content."""
        results = self.manager.search_prompts(query)
        
        if not results:
            print(f"No prompts found matching '{query}'")
            return True
        
        # Output as JSON
        output = []
        for prompt in results:
            output.append(prompt.to_dict())
        
        print(json.dumps(output, indent=2))
        return True


def main():
    parser = argparse.ArgumentParser(description="Prompt Manager CLI")
    parser.add_argument('--storage', default='prompts.json', help='Storage file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new prompt')
    add_parser.add_argument('name', help='Prompt name')
    add_parser.add_argument('--text', help='Prompt text (reads from stdin if not provided)')
    add_parser.add_argument('--category', default='general', help='Prompt category')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all prompts')
    list_parser.add_argument('--category', help='Filter by category')
    
    # Get command
    get_parser = subparsers.add_parser('get', help='Get a specific prompt')
    get_parser.add_argument('identifier', help='Prompt ID or name')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a prompt')
    delete_parser.add_argument('identifier', help='Prompt ID or name')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search prompts')
    search_parser.add_argument('query', help='Search query')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    cli = PromptManagerCLI(args.storage)
    
    try:
        if args.command == 'add':
            success = cli.add_prompt(args.name, args.text, args.category)
        elif args.command == 'list':
            success = cli.list_prompts(args.category)
        elif args.command == 'get':
            success = cli.get_prompt(args.identifier)
        elif args.command == 'delete':
            success = cli.delete_prompt(args.identifier)
        elif args.command == 'search':
            success = cli.search_prompts(args.query)
        else:
            print(f"Unknown command: {args.command}")
            return 1
        
        return 0 if success else 1
    
    except KeyboardInterrupt:
        print("\nOperation cancelled")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 