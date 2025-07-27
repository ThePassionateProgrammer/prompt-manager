#!/usr/bin/env python3
"""
Manual test script for the Prompt Manager API

This script tests the API endpoints by making actual HTTP requests.
"""

import requests
import json
import time


def test_api():
    """Test the API endpoints manually."""
    base_url = "http://localhost:5000/api"
    
    print("=== Testing Prompt Manager API ===\n")
    
    # Test health check
    print("1. Testing health check...")
    response = requests.get(f"{base_url}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print()
    
    # Test creating a prompt
    print("2. Testing prompt creation...")
    prompt_data = {
        "name": "Test API Prompt",
        "text": "This is a test prompt created via API",
        "category": "test"
    }
    
    response = requests.post(f"{base_url}/prompts", json=prompt_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        created_prompt = response.json()
        prompt_id = created_prompt['id']
        print(f"   Created prompt ID: {prompt_id}")
        print(f"   Prompt data: {json.dumps(created_prompt, indent=2)}")
    else:
        print(f"   Error: {response.json()}")
    print()
    
    # Test getting all prompts
    print("3. Testing get all prompts...")
    response = requests.get(f"{base_url}/prompts")
    print(f"   Status: {response.status_code}")
    prompts = response.json()
    print(f"   Found {len(prompts)} prompts")
    for prompt in prompts:
        print(f"   - {prompt['name']} (ID: {prompt['id']})")
    print()
    
    # Test getting categories
    print("4. Testing get categories...")
    response = requests.get(f"{base_url}/categories")
    print(f"   Status: {response.status_code}")
    categories = response.json()
    print(f"   Categories: {categories}")
    print()
    
    # Test search
    print("5. Testing search...")
    response = requests.get(f"{base_url}/search?q=test")
    print(f"   Status: {response.status_code}")
    search_results = response.json()
    print(f"   Search results: {len(search_results)} prompts")
    for result in search_results:
        print(f"   - {result['name']}")
    print()
    
    # Test getting suggestions
    print("6. Testing suggestions...")
    response = requests.get(f"{base_url}/suggestions?q=test")
    print(f"   Status: {response.status_code}")
    suggestions = response.json()
    print(f"   Suggestions: {suggestions}")
    print()
    
    # Test updating a prompt (if we have one)
    if 'prompt_id' in locals():
        print("7. Testing prompt update...")
        update_data = {
            "name": "Updated API Prompt",
            "text": "This prompt has been updated via API",
            "category": "updated"
        }
        
        response = requests.put(f"{base_url}/prompts/{prompt_id}", json=update_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            updated_prompt = response.json()
            print(f"   Updated prompt: {json.dumps(updated_prompt, indent=2)}")
        else:
            print(f"   Error: {response.json()}")
        print()
        
        # Test deleting the prompt
        print("8. Testing prompt deletion...")
        response = requests.delete(f"{base_url}/prompts/{prompt_id}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print(f"   Error: {response.json()}")
        print()
    
    print("=== API Test Complete ===")


if __name__ == '__main__':
    print("Starting API test...")
    print("Make sure the API server is running on http://localhost:5000")
    print("You can start it with: python -c \"from src.prompt_manager.api import PromptManagerAPI; api = PromptManagerAPI(); api.run(debug=True)\"")
    print()
    
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server.")
        print("Please make sure the server is running on http://localhost:5000")
    except Exception as e:
        print(f"Error: {e}") 