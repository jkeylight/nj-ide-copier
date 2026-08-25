# NJ IDE Copier v2.0.0

An intelligent bridge between DeepSeek AI chat and development environments. It automatically captures, versions, and transfers code from DeepSeek conversations directly into your IDE with smart error tracking and version management.

## Quick Start

```bash
# 1. Install
pip install -e .

# 2. Start the server
nj-ide-copier

# 3. Load browser extension (Chrome → chrome://extensions/ → Load unpacked → browser_extension/)
```

## Features

- **Code Block Detection** — Auto-detect code in DeepSeek responses
- **Full Chat Export (Markdown)** — Export entire conversations as Markdown
- **Arena.ai Support** — Compatible with Arena.ai chat interface
- **Browser Extension UI Overhaul (2026 look)** — Modernized extension interface
- **Version Tracking** — Track every code change with diff history
- **Error Detection** — Detect and classify errors, suggest fixes
- **IDE Auto-Detection** — Finds VS Code, JetBrains, Sublime, and more
- **Multi-IDE Support** — Works with 10+ IDEs across platforms
- **Clipboard Integration** — Automatic clipboard copy
- **Smart Update Handling** — Distinguishes original/error/fixed/optimized code

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         DeepSeek Chat (Browser)                     │
│  ┌───────────────────────────────────────────────┐  │
│  │  Browser Extension (content.js)               │  │
│  │  • Code Block Detection    • Full Chat Export  │  │
│  │  • Error Detection         • Version Tracking  │  │
│  └───────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP/WebSocket (port 8765)
                       ▼
┌─────────────────────────────────────────────────────┐
│         Local Python Server                         │
│  ┌───────────────────────────────────────────────┐  │
│  │  Core Services                                │  │
│  │  • Version Manager    • Error Tracker         │  │
│  │  • IDE Detector       • Code Analyzer         │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Storage: JSON + File System                  │  │
│  └───────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │ Native APIs
                       ▼
┌─────────────────────────────────────────────────────┐
│         IDE Integration                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐     │
│  │ VS Code  │  │ JetBrains│  │ Sublime/Other│     │
│  └──────────┘  └──────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────┘
```

## Supported IDEs

| IDE | Platform | Detection Method |
|-----|----------|-----------------|
| Visual Studio Code | macOS, Windows, Linux | PATH + App bundle |
| PyCharm | macOS, Windows | Application path |
| IntelliJ IDEA | macOS, Windows | Application path |
| WebStorm | macOS, Windows | Application path |
| PhpStorm | macOS, Windows | Application path |
| GoLand | macOS, Windows | Application path |
| CLion | macOS, Windows | Application path |
| Sublime Text | macOS, Windows, Linux | PATH + App bundle |
| Atom | macOS, Windows, Linux | PATH |
| Notepad++ | Windows | Program Files |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/code/update` | Update/create code version |
| POST | `/chat/full` | Export full chat |
| POST | `/version/revert` | Revert to previous version |
| GET | `/versions` | Get version history |
| GET | `/errors/stats` | Get error statistics |
| GET | `/status` | Server status + detected IDEs |
| GET | `/config` | Get configuration |

## Configuration

Create `~/.deepseek-copier/config.json`:

```json
{
  "server_port": 8765,
  "default_ide": "auto",
  "enable_versioning": true,
  "enable_error_tracking": true,
  "log_level": "INFO"
}
```

Or use environment variables (see `.env.example`).

## Development

```bash
# Setup dev environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start dev server
python -m src.server.main
```

## License

MIT License - See [LICENSE](LICENSE) for details.
