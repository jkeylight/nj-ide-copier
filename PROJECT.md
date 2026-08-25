# NJ IDE Copier v2.0.0 - Project Documentation

## Overview
NJ IDE Copier is an intelligent bridge between DeepSeek AI chat and development environments. It automatically captures, versions, and transfers code with smart error tracking.

## Architecture
```
DeepSeek Chat → Browser Extension → Local Server (Python) → IDE
                                    ├── Version Manager
                                    ├── Error Tracker
                                    ├── IDE Detector
                                    └── Code Analyzer
```

## Tech Stack
- **Backend:** Python 3.9+ (HTTP server, WebSocket support)
- **Frontend:** Chrome Extension (Manifest V3), Web Dashboard
- **Integrations:** VS Code Extension, JetBrains Plugin, Sublime Plugin
- **Storage:** JSON file system + optional Redis/SQLite

## Features
| Feature | Status |
|---------|--------|
| Code Block Detection | ✅ |
| Full Chat Export | ✅ |
| Version Tracking | ✅ |
| Error Detection | ✅ |
| IDE Auto-Detection | ✅ |
| Markdown Export | ✅ |
| Web Dashboard | ✅ |

## Database Schema
```sql
-- Version state stored in state.json
-- Code files stored in ~/.deepseek-copier/projects/
-- Logs stored in ~/.deepseek-copier/deepseek.log
```

## Security
- All code stored locally
- Optional Fernet encryption
- JWT authentication available
- No cloud transmission by default

## Roadmap
- [ ] ML-based error prediction
- [ ] Team collaboration features
- [ ] Cloud sync
- [ ] Git integration
