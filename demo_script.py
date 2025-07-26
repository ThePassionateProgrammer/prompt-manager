#!/usr/bin/env python3
"""
Demo script for the Prompt Manager

This script demonstrates basic functionality by:
1. Adding two prompts
2. Retrieving and displaying the first prompt
"""

import json
import sys
from src.prompt_manager.prompt_manager import PromptManager


def main():
    print("=== Prompt Manager Demo ===\n")
    
    # Initialize the prompt manager
    manager = PromptManager("demo_prompts.json")
    
    # Add two prompts
    print("1. Adding prompts...")
    
    prompt1_id = manager.add_prompt(
        "Greeting Prompt", 
        "Hello! How can I assist you today?", 
        "greeting"
    )
    print(f"   Added prompt 1 with ID: {prompt1_id}")
    
    prompt2_id = manager.add_prompt(
        "Farewell Prompt", 
        "Thank you for using our service. Have a great day!", 
        "farewell"
    )
    print(f"   Added prompt 2 with ID: {prompt2_id}")
    
    # List all prompts
    print("\n2. All prompts in storage:")
    prompts = manager.list_prompts()
    for prompt in prompts:
        print(f"   - {prompt.name} (ID: {prompt.id}, Category: {prompt.category})")
    
    # Get and display the first prompt
    print(f"\n3. Retrieving first prompt (ID: {prompt1_id}):")
    prompt = manager.get_prompt(prompt1_id)
    
    if prompt:
        print("   Prompt details:")
        print(f"   - Name: {prompt.name}")
        print(f"   - Category: {prompt.category}")
        print(f"   - Created: {prompt.created_at}")
        print(f"   - Modified: {prompt.modified_at}")
        print(f"   - Text: {prompt.text}")
        
        # Also display as JSON
        print("\n   JSON format:")
        print(json.dumps(prompt.to_dict(), indent=2))
    else:
        print("   Error: Prompt not found!")
        return 1
    
    print("\n=== Demo completed successfully! ===")
    print("Storage file: demo_prompts.json")
    return 0


if __name__ == '__main__':
    sys.exit(main()) 