#!/usr/bin/env python3
"""Fix remaining assertions that check messages array."""

import re

with open('tests/test_chat_context_management.py', 'r') as f:
    content = f.read()

# Pattern 1: Check system prompt assertions
# OLD: assert call_kwargs['messages'][0]['role'] == 'system'
# NEW: assert 'system_prompt' in call_kwargs
content = re.sub(
    r"assert call_kwargs\['messages'\]\[0\]\['role'\] == 'system'",
    r"assert 'system_prompt' in call_kwargs",
    content
)

# Pattern 2: Check system prompt content
# OLD: assert 'coding assistant' in call_kwargs['messages'][0]['content']
# NEW: assert 'coding assistant' in call_kwargs['system_prompt']
content = re.sub(
    r"assert '([^']+)' in call_kwargs\['messages'\]\[0\]\['content'\]",
    r"assert '\1' in call_kwargs['system_prompt']",
    content
)

# Pattern 3: Check system prompt length
# OLD: assert len(call_kwargs['messages'][0]['content']) > 0
# NEW: assert call_kwargs['system_prompt'] is not None
content = re.sub(
    r"assert len\(call_kwargs\['messages'\]\[0\]\['content'\]\) > 0",
    r"assert call_kwargs['system_prompt'] is not None",
    content
)

# Pattern 4: Remove messages array access in system prompt tests
# OLD: messages = call_kwargs['messages']
# Just remove these lines as they're no longer relevant
content = re.sub(
    r"\s+messages = call_kwargs\['messages'\]\n",
    "",
    content
)

with open('tests/test_chat_context_management.py', 'w') as f:
    f.write(content)

print("✅ Fixed remaining message array assertions")
