# NJ IDE Copier - API Reference

## Base URL: `http://localhost:8765`

## POST /code/update
Create or update a code version.

**Request:** `{ "code": "print('hello')", "language": "python", "context": {}, "error_info": {} }`
**Response:** `{ "status": "success", "action": "created|updated|error_fixed", "block_id": "...", "version": "v1" }`

## POST /chat/full
Export full chat with code blocks.

## POST /version/revert
Revert to a previous version: `{ "block_id": "...", "version_id": "v1" }`

## GET /versions
Get all version history. Optional: `?block_id=X`

## GET /errors/stats
Get error statistics.

## GET /status
Server status and detected IDEs.

## GET /config
Current configuration.
