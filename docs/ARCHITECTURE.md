# NJ IDE Copier - Architecture

## Components
1. **Browser Extension** — Detects code on DeepSeek pages, sends to server
2. **Python Server** (port 8765) — Version tracking, error detection, IDE integration
3. **Core Services** — CodeVersionManager, ErrorTracker, IDEDetector, CodeAnalyzer
4. **IDE Plugins** — VS Code, JetBrains, Sublime Text
5. **Web Dashboard** — Management interface at /dashboard

## Data Flow
DeepSeek → Extension → HTTP POST → Server → VersionManager → File/Clipboard → IDE
