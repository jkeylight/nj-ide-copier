#!/bin/bash
echo "Installing NJ IDE Copier..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
mkdir -p ~/.deepseek-copier
echo "✅ Installation complete!"
echo "Run: source venv/bin/activate && python -m src.server.main"
