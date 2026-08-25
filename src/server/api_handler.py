"""
API Handler - REST API endpoints for the NJ IDE Copier server.

Routes HTTP requests to the appropriate server methods and returns
JSON responses with CORS support. Improved version with robust error handling.
"""

import json
import traceback
import logging
from http.server import BaseHTTPRequestHandler
from typing import Dict, Optional

logger = logging.getLogger("nj_ide_copier")


class SmartAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the API endpoints with robust error handling."""
    
    server_instance = None
    
    ENDPOINTS = {
        "GET /": "Server info and endpoint list",
        "POST /code/update": "Update code with version tracking",
        "POST /chat/full": "Export full chat conversation",
        "POST /version/revert": "Revert to a previous version",
        "GET /status": "Server status and IDE info",
        "GET /config": "Server configuration",
        "GET /versions": "Version history (optional ?block_id=)",
        "GET /errors/stats": "Error tracking statistics",
        "GET /exports": "List recent chat exports",
    }

    def _send_json(self, data: Dict, status: int = 200):
        """Send a JSON response with CORS headers."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _send_error(self, message: str, status: int = 400, details: Optional[Dict] = None):
        """Send a structured error response."""
        response = {"status": "error", "message": message}
        if details:
            response["details"] = details
        self._send_json(response, status)

    def _read_body(self) -> Dict:
        """Read and parse JSON request body with error handling."""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                return {}
            if content_length > 10 * 1024 * 1024:
                raise ValueError("Request body too large (max 10MB)")
            post_data = self.rfile.read(content_length)
            return json.loads(post_data.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")

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

    def _validate_payload(self, data: Dict, required_fields: list) -> Optional[str]:
        """Validate that required fields are present in payload."""
        missing = [f for f in required_fields if f not in data]
        if missing:
            return f"Missing required fields: {', '.join(missing)}"
        return None

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        """Handle POST requests with robust error handling."""
        try:
            data = self._read_body()
            
            if self.path == "/code/update":
                self._handle_code_update(data)
            elif self.path == "/chat/full":
                self._handle_full_chat(data)
            elif self.path == "/version/revert":
                self._handle_version_revert(data)
            elif self.path == "/exports/delete":
                self._handle_delete_export(data)
            elif self.path in ["/", ""]:
                self._send_json({
                    "status": "running",
                    "message": "NJ IDE Copier Server",
                    "endpoints": self.ENDPOINTS,
                })
            else:
                self._send_error(f"Unknown endpoint: {self.path}", 404)
                
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            self._send_error(str(e), 400)
        except Exception as e:
            logger.error(f"POST error: {e}\n{traceback.format_exc()}")
            self._send_error(f"Internal server error: {str(e)}", 500)

    def _handle_code_update(self, data: Dict):
        """Handle code update endpoint."""
        error = self._validate_payload(data, ["code", "language"])
        if error:
            self._send_error(error, 400)
            return
        
        result = self.server_instance.handle_code_update(
            code=data.get("code", ""),
            language=data.get("language", "text"),
            context=data.get("context"),
            error_info=data.get("error_info"),
        )
        
        self._send_json(result)

    def _handle_full_chat(self, data: Dict):
        """Handle full chat export endpoint."""
        if "messages" not in data:
            self._send_error("Missing 'messages' field", 400)
            return
        
        messages = data.get("messages", [])
        if not messages:
            self._send_error("No messages to export", 400)
            return
        
        if not isinstance(messages, list):
            self._send_error("'messages' must be an array", 400)
            return
        
        from src.core.chat_exporter import ChatExporter
        
        exporter = ChatExporter()
        
        try:
            file_path = exporter.export_chat(data)
            result = self.server_instance.handle_full_chat(data)
            
            result["export_file"] = str(file_path)
            result["export_filename"] = file_path.name
            result["export_summary"] = exporter.export_summary(data)
            
            self._send_json(result)
            
        except Exception as e:
            logger.error(f"Export error: {e}\n{traceback.format_exc()}")
            self._send_error(f"Export failed: {str(e)}", 500)

    def _handle_version_revert(self, data: Dict):
        """Handle version revert endpoint."""
        error = self._validate_payload(data, ["block_id", "version_id"])
        if error:
            self._send_error(error, 400)
            return
        
        result = self.server_instance.revert_version(
            block_id=data.get("block_id"),
            version_id=data.get("version_id"),
        )
        
        self._send_json(result)

    def _handle_delete_export(self, data: Dict):
        """Handle delete export endpoint."""
        if "filename" not in data:
            self._send_error("Missing 'filename' field", 400)
            return
        
        from src.core.chat_exporter import ChatExporter
        exporter = ChatExporter()
        
        success = exporter.delete_export(data.get("filename"))
        
        if success:
            self._send_json({"status": "success", "message": "Export deleted"})
        else:
            self._send_error("Export file not found", 404)

    def do_GET(self):
        """Handle GET requests with robust error handling."""
        try:
            if self.path.startswith("/versions"):
                params = self._parse_query()
                block_id = params.get("block_id")
                result = self.server_instance.get_version_history(block_id)
                self._send_json(result)
                
            elif self.path == "/errors/stats":
                result = self.server_instance.get_error_statistics()
                self._send_json(result)
                
            elif self.path == "/status":
                result = {
                    "status": "running",
                    "ides": self.server_instance.ide_detector.list_available_ides(),
                    "active_ide": self.server_instance.ide_detector.detect_active_ide(),
                    "history_count": len(self.server_instance.history),
                    "version": "2.0.0",
                }
                self._send_json(result)
                
            elif self.path == "/config":
                result = {
                    "server_port": self.server_instance.config.server_port,
                    "server_host": self.server_instance.config.server_host,
                    "default_ide": self.server_instance.config.default_ide,
                    "enable_versioning": self.server_instance.config.enable_versioning,
                    "enable_error_tracking": self.server_instance.config.enable_error_tracking,
                    "storage_dir": str(self.server_instance.config.storage_dir),
                }
                self._send_json(result)
                
            elif self.path == "/exports":
                from src.core.chat_exporter import ChatExporter
                exporter = ChatExporter()
                exports = exporter.get_recent_exports()
                self._send_json({
                    "status": "success",
                    "exports": exports,
                    "count": len(exports)
                })
                
            elif self.path in ["/", ""]:
                result = {
                    "status": "running",
                    "message": "NJ IDE Copier Server v2.0.0",
                    "endpoints": self.ENDPOINTS,
                    "documentation": {
                        "code_update": "POST code and language to create/update version",
                        "full_chat": "POST messages array to export entire conversation",
                        "revert": "POST block_id and version_id to revert",
                    }
                }
                self._send_json(result)
                
            else:
                self._send_error(f"Unknown endpoint: {self.path}", 404)
                
        except Exception as e:
            logger.error(f"GET error: {e}\n{traceback.format_exc()}")
            self._send_error(f"Internal server error: {str(e)}", 500)

    def log_message(self, format, *args):
        """Override to provide custom logging."""
        logger.debug(f"{self.address_string()} - {format % args}")
