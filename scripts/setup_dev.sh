#!/bin/bash
echo "Setting up development environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pytest
python -m pytest tests/ -v
echo "✅ Dev setup complete!"
