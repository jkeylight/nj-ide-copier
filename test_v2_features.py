#!/usr/bin/env python3
"""
Test script for NJ IDE Copier v2.0 new features.
"""

import requests
import json

print('=' * 70)
print('TESTING NJ IDE COPIER v2.0 - NEW FEATURES')
print('=' * 70)

# Test 1: Error Detection Improvement
print('\n📊 TEST 1: Improved Error Detection')
print('-' * 50)
payload = {
    'code': 'def buggy():\n    raise Exception("something went wrong")',
    'language': 'python',
    'context': {'test': 'error_detection'},
    'error_info': {'message': 'Error: something went wrong'}
}
r = requests.post('http://localhost:8765/code/update', json=payload)
result = r.json()
print(f'Status: {r.status_code}')
print(f'Error detected: {result.get("error_detected")}')
print(f'Suggestions: {result.get("suggestions", [])}')

# Test 2: Chat Export
print('\n📄 TEST 2: Chat Export to Markdown')
print('-' * 50)
chat_data = {
    'title': 'Test Chat Export',
    'platform': 'DeepSeek',
    'messages': [
        {
            'id': 'msg1',
            'role': 'user',
            'content': 'How do I fix this error?',
            'codeBlocks': []
        },
        {
            'id': 'msg2',
            'role': 'assistant',
            'content': 'Here is a solution:\n\n```python\ndef hello():\n    print("Hello, World!")\n```',
            'codeBlocks': [
                {'code': 'def hello():\n    print("Hello, World!")', 'language': 'python'}
            ]
        },
        {
            'id': 'msg3',
            'role': 'user',
            'content': 'I have an error: Error: file not found at /path/to/file',
            'codeBlocks': []
        }
    ]
}
r = requests.post('http://localhost:8765/chat/full', json=chat_data)
result = r.json()
print(f'Status: {r.status_code}')
print(f'Export file: {result.get("export_filename")}')
print(f'Blocks processed: {result.get("blocks_processed")}')
print(f'Export summary: {json.dumps(result.get("export_summary", {}), indent=2)}')

# Test 3: Get Error Statistics
print('\n📈 TEST 3: Error Statistics')
print('-' * 50)
r = requests.get('http://localhost:8765/errors/stats')
result = r.json()
print(f'Status: {r.status_code}')
print(f'Total errors: {result.get("total_errors")}')
print(f'By type: {json.dumps(result.get("by_type", {}), indent=2)}')

# Test 4: List Exports
print('\n📁 TEST 4: List Export Files')
print('-' * 50)
r = requests.get('http://localhost:8765/exports')
result = r.json()
print(f'Status: {r.status_code}')
print(f'Export count: {result.get("count")}')
for exp in result.get('exports', [])[:3]:
    print(f'  - {exp["filename"]} ({exp["size"]} bytes)')

# Test 5: Different Error Types
print('\n🐛 TEST 5: Different Error Types')
print('-' * 50)
errors = [
    ('SyntaxError in code', 'SyntaxError: invalid syntax'),
    ('Import error', 'ModuleNotFoundError: No module named'),
    ('Value error', 'ValueError: could not convert'),
]

for name, error_msg in errors:
    payload = {
        'code': 'x = 1',
        'language': 'python',
        'error_info': {'message': error_msg}
    }
    r = requests.post('http://localhost:8765/code/update', json=payload)
    result = r.json()
    suggestions = result.get('suggestions', [])
    print(f'{name}:')
    if suggestions:
        print(f'  Suggestion: {suggestions[0].get("suggestion", "N/A")[:60]}...')

print('\n' + '=' * 70)
print('✅ ALL TESTS COMPLETED')
print('=' * 70)
