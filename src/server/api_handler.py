"""
API Handler - REST API endpoints for the NJ IDE Copier server.

Routes HTTP requests to the appropriate server methods and returns
JSON responses with CORS support.
"""

import json
from http.server import BaseHTTPRequestHandler
from typing import Dict, Optional


class SmartAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the API endpoints."""

    server_instance = None

    def _send_json(self, data: Dict, status: int = 200):
        """Send a JSON response with CORS headers."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _read_body(self) -> Dict:
        """Read and parse JSON request body."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        post_data = self.rfile.read(content_length)
        return json.loads(post_data.decode("utf-8"))

    def _parse_query(self) -> Dict:
        """Parse URL query parameters."""
        query = self.path.split("?", 1)
        params = {}
        if len(query) > 1:
            for param in query[1].split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key] = value
        return params

    def do_POST(self):
        """Handle POST requests."""
        import traceback
        try:
            data = self._read_body()

            if self.path == "/code/update":
                result = self.server_instance.handle_code_update(
                    data.get("code", ""),
                    data.get("language", "text"),
                    data.get("context"),
                    data.get("error_info"),
                )
            elif self.path == "/chat/full":
                result = self.server_instance.handle_full_chat(data)
            elif self.path == "/version/revert":
                result = self.server_instance.revert_version(
                    data.get("block_id"),
                    data.get("version_id"),
                )
            elif self.path == "/" or self.path == "":
                result = {
                    "status": "running",
                    "message": "NJ IDE Copier Server",
                    "endpoints": {
                        "POST /code/update": "Update code version",
                        "POST /chat/full": "Export full chat",
                        "POST /version/revert": "Revert version",
                        "GET /status": "Server status",
                        "GET /config": "Server config",
                        "GET /versions": "Version history",
                        "GET /errors/stats": "Error statistics",
                    },
                }
            else:
                result = {"status": "error", "message": "Unknown endpoint"}

            self._send_json(result)

        except Exception as e:
            traceback.print_exc()
            self._send_json(
                {"status": "error", "message": str(e)},
                status=500,
            )

    def do_GET(self):
        """Handle GET requests."""
        try:
            if self.path.startswith("/versions"):
                params = self._parse_query()
                block_id = params.get("block_id")
                result = self.server_instance.get_version_history(block_id)
            elif self.path == "/errors/stats":
                result = self.server_instance.get_error_statistics()
            elif self.path == "/status":
                result = {
                    "status": "running",
                    "ides": self.server_instance.ide_detector.list_available_ides(),
                    "active_ide": self.server_instance.ide_detector.detect_active_ide(),
                    "history_count": len(self.server_instance.history),
                }
            elif self.path == "/config":
                result = {
                    "server_port": self.server_instance.config.server_port,
                    "default_ide": self.server_instance.config.default_ide,
                    "enable_versioning": self.server_instance.config.enable_versioning,
                    "enable_error_tracking": self.server_instance.config.enable_error_tracking,
                }
            elif self.path == "/" or self.path == "":
                result = {
                    "status": "running",
                    "message": "NJ IDE Copier Server",
                    "endpoints": {
                        "GET /status": "Server status",
                        "GET /config": "Server config",
                        "GET /versions": "Version history",
                        "GET /errors/stats": "Error statistics",
                        "POST /code/update": "Update code version",
                        "POST /chat/full": "Export full chat",
                        "POST /version/revert": "Revert version",
                    },
                }
            else:
                result = {"status": "error", "message": "Unknown endpoint"}

            self._send_json(result)

        except Exception as e:
            self._send_json(
                {"status": "error", "message": str(e)},
                status=500,
            )

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """Override to suppress default logging."""
        pass
