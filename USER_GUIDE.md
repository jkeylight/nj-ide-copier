# NJ IDE Copier - User Guide

## Quick Start
1. Install: `pip install -e .`
2. Start server: `nj-ide-copier`
3. Load browser extension in Chrome
4. Visit DeepSeek chat and use the floating buttons

## Installation

### Python Server
```bash
pip install -e .
# or from source:
git clone <repo> && cd nj-ide-copier && pip install -r requirements.txt
```

### Browser Extension
1. Open `chrome://extensions/`
2. Enable Developer Mode
3. Click "Load unpacked" → select `browser_extension/`

### VS Code Extension
Copy `src/integrations/vscode/` to `~/.vscode/extensions/`

## Usage

### Copy Code Blocks
- Individual blocks get "📋 Copy" buttons automatically
- Use floating buttons for bulk operations

### Exporting Full Chat
1. Navigate to a DeepSeek or Arena.ai conversation
2. Click the **"📄 Copy Full Chat"** button in the floating toolbar
3. The entire conversation is exported as Markdown to your clipboard
4. Paste directly into your IDE or save as a `.md` file

**Export Options:**
- **Clipboard** — Copies formatted Markdown to clipboard (default)
- **File** — Saves to `~/.deepseek-copier/exports/` with timestamp
- **Both** — Copies to clipboard and saves to file

### Version History
Open `web_dashboard/index.html` in your browser to view version history

### Error Tracking
Errors are automatically detected and classified with fix suggestions

## Configuration
Edit `~/.deepseek-copier/config.json`:
```json
{
  "server_port": 8765,
  "default_ide": "auto",
  "enable_versioning": true,
  "enable_error_tracking": true
}
```

## Troubleshooting
- **Server won't start:** Check port 8765 isn't in use
- **Extension not connecting:** Ensure server is running
- **IDE not detected:** Add manually in config or check PATH
