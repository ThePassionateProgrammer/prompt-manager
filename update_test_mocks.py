#!/usr/bin/env python3
"""
Script to automatically update test mocks from old provider_manager pattern to new chat_service pattern.

OLD PATTERN:
    mock_provider = Mock()
    mock_provider.generate.return_value = "Response"
    mock_manager.get_provider.return_value = mock_provider

NEW PATTERN:
    mock_service.send_message.return_value = {
        'response': 'Response',
        'provider': 'openai',
        'model': 'gpt-3.5-turbo',
        ...
    }
"""

import re
import sys


def update_test_file(filepath):
    """Update test file with new mock pattern."""

    with open(filepath, 'r') as f:
        content = f.read()

    # Track changes
    changes = []

    # Pattern 1: Update parameter name from mock_manager to mock_service
    old_params = re.findall(r'def (test_\w+)\(self, mock_manager, client', content)
    if old_params:
        content = re.sub(
            r'def (test_\w+)\(self, mock_manager, client',
            r'def \1(self, mock_service, client',
            content
        )
        changes.append(f"Updated {len(old_params)} test method signatures")

    # Pattern 2: Add mock_chat_service_response fixture where needed
    # For tests that need token_usage or metadata
    token_tests = re.findall(
        r'def (test_\w+)\(self, mock_service, client\):',
        content
    )
    for test_name in token_tests:
        if 'token' in test_name.lower() or 'metadata' in test_name.lower():
            content = re.sub(
                rf'def ({test_name})\(self, mock_service, client\):',
                rf'def \1(self, mock_service, client, mock_chat_service_response):',
                content
            )
            changes.append(f"Added fixture to {test_name}")

    # Pattern 3: Replace provider mock setup with service mock
    old_pattern = r'''        mock_provider = Mock\(\)
        mock_provider\.generate\.return_value = ["'](.+?)["']
        mock_manager\.get_provider\.return_value = mock_provider'''

    def replacement(match):
        response_text = match.group(1)
        return f'''        mock_service.send_message.return_value = {{
            'response': '{response_text}',
            'provider': 'openai',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 2048,
            'token_usage': {{}},
            'metadata': {{}}
        }}'''

    new_content = re.sub(old_pattern, replacement, content, flags=re.MULTILINE)
    if new_content != content:
        changes.append("Replaced provider mock setups with service mocks")
        content = new_content

    # Pattern 4: Update assertions that check provider.generate calls
    # OLD: call_kwargs = mock_provider.generate.call_args[1]
    # NEW: call_kwargs = mock_service.send_message.call_args[1]
    content = re.sub(
        r'call_kwargs = mock_provider\.generate\.call_args\[1\]',
        r'call_kwargs = mock_service.send_message.call_args[1]',
        content
    )

    # Pattern 5: Update assertions that check 'messages' parameter
    # Service gets 'message' and 'history', not 'messages' array
    # This one is trickier - we'll leave some manual cleanup

    # Write back
    with open(filepath, 'w') as f:
        f.write(content)

    return changes


def main():
    filepath = 'tests/test_chat_context_management.py'

    print("🤖 Automated Test Mock Updater")
    print("=" * 50)
    print(f"Processing: {filepath}\n")

    try:
        changes = update_test_file(filepath)

        if changes:
            print("✅ Changes made:")
            for change in changes:
                print(f"  • {change}")
        else:
            print("ℹ️  No automatic changes needed")

        print("\n⚠️  Manual review recommended:")
        print("  • Check assertions that verify call arguments")
        print("  • Update assertions from checking 'messages' array to 'message' + 'history'")
        print("  • Verify token_usage assertions use response data structure")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
