# NJ IDE Copier - VS Code Extension

Intelligent code copier that seamlessly transfers code from DeepSeek AI to VS Code.

## Features

- Automatic Code Insertion: Insert code at cursor position
- Version Tracking: Track all code versions
- Error Detection: Detect and track errors
- Code Formatting: Auto-format code on insertion
- Dashboard: View code blocks and history
- Version Rollback: Revert to previous versions
- Clipboard Integration: Copy code to clipboard

## Installation

Install from VS Code Marketplace or run:

```bash
code --install-extension nj-ide-copier-2.0.0.vsix
```

## Commands

| Command | Description |
|---------|-------------|
| NJ Copier: Start Server | Start the local server |
| NJ Copier: Insert Last Code | Insert last code at cursor |
| NJ Copier: Show Version History | View version history |
| NJ Copier: Revert to Previous Version | Rollback code |
| NJ Copier: Copy Last Code to Clipboard | Copy code |
| NJ Copier: Open Dashboard | Open dashboard |
| NJ Copier: Show Error Tracker | View errors |
| NJ Copier: Configure Settings | Open settings |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Shift+D | Insert code |
| Ctrl+Shift+H | Show history |
| Ctrl+Shift+C | Copy to clipboard |

## Requirements

- VS Code 1.75.0 or higher
- Python 3.9+ installed
- NJ IDE Copier server running
