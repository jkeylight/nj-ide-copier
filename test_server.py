import requests
import json

# Test the exact request the browser extension sends
payload = {
    "code": "def hello():\n    print('hi')",
    "language": "python",
    "context": {
        "platform": "DeepSeek",
        "url": "https://chat.deepseek.com",
        "timestamp": 1234567890
    }
}

print("Sending:", json.dumps(payload, indent=2))
r = requests.post('http://localhost:8765/code/update', json=payload)
print("Status:", r.status_code)
print("Response:", r.json())
