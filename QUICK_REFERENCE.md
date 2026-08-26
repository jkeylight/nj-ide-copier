# NJ IDE Copier v2.0 - Quick Reference

## 🚀 Quick Start

```bash
# Start server
cd /home/user/nj-ide-copier
python -c "from src.server.main import main; main()"

# Server runs on: http://localhost:8765
```

---

## 📋 API Endpoints

### Export Chat
```bash
curl -X POST http://localhost:8765/chat/full \
  -H "Content-Type: application/json" \
  -d '{"messages": [...]}'
```

### Get Error Stats
```bash
curl http://localhost:8765/errors/stats
```

### List Exports
```bash
curl http://localhost:8765/exports
```

### Update Code
```bash
curl -X POST http://localhost:8765/code/update \
  -H "Content-Type: application/json" \
  -d '{"code": "print(1)", "language": "python"}'
```

### Get Versions
```bash
curl http://localhost:8765/versions
```

### Revert Version
```bash
curl -X POST http://localhost:8765/version/revert \
  -H "Content-Type: application/json" \
  -d '{"block_id": "abc123", "version_id": "v1"}'
```

---

## 📁 Important Paths

- **Exports:** `~/.deepseek-copier/exports/`
- **Projects:** `~/.deepseek-copier/projects/`
- **Versions:** `~/.deepseek-copier/versions/`
- **Config:** `~/.deepseek-copier/config.json`

---

## ✅ What's New in v2.0

1. **Better Error Detection** - 17 error types with fix suggestions
2. **Chat Export** - Professional Markdown with TOC
3. **Export Tracking** - List all previous exports
4. **Robust API** - Better validation and error messages
5. **Statistics** - Track errors and fix rates

---

## 🐛 Common Issues

**Port already in use:**
```bash
# Stop existing server or use different port
# Edit .env: DEEPSEEK_SERVER_PORT=8766
```

**Extension not connecting:**
```bash
# Ensure server is running
curl http://localhost:8765/
# Should return server info
```

**Export not found:**
```bash
# Check exports directory
ls -la ~/.deepseek-copier/exports/
```

---

## 📊 Check Server Status

```bash
curl http://localhost:8765/status
```

---

**Server is running! Test the new features above! 🎉**
