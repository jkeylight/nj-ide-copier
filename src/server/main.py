"""
Main Server - SmartDeepSeekServer orchestrator.

This is the main entry point that coordinates version management,
error tracking, IDE detection, and file management.
"""

import json
import re
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional
from http.server import HTTPServer

from src.core.version_manager import CodeVersionManager, CodeStatus
from src.core.error_tracker import ErrorTracker
from src.core.ide_detector import IDEDetector
from src.core.file_manager import FileManager
from src.server.config import Config
from src.server.api_handler import SmartAPIHandler

try:
    import pyperclip
    HAS_CLIPBOARD = True
except Exception:
    HAS_CLIPBOARD = False


class SmartDeepSeekServer:
    """Main server that orchestrates all NJ IDE Copier services."""

    def __init__(self):
        self.config = Config()
        self.version_manager = CodeVersionManager(
            self.config.storage_dir / "versions"
        )
        self.error_tracker = ErrorTracker()
        self.ide_detector = IDEDetector()
        self.file_manager = FileManager(self.config.storage_dir)
        self.history: List[Dict] = []

    def handle_code_update(
        self,
        code: str,
        language: str,
        context: Optional[Dict] = None,
        error_info: Optional[Dict] = None,
    ) -> Dict:
        """Handle code update with version tracking."""
        result = {
            "status": "success",
            "action": "created",
            "block_id": None,
            "version": None,
            "changes": None,
            "error_detected": False,
            "suggestions": [],
        }

        # Track errors if present
        if error_info and self.config.enable_error_tracking:
            self.error_tracker.track_error(
                code, error_info.get("message", ""), language
            )
            result["error_detected"] = True

            # Get fix suggestions
            error_type = self.error_tracker.classify_error(
                error_info.get("message", "")
            )
            suggestion = self.error_tracker.suggest_fix(error_type, code, language)
            if suggestion:
                result["suggestions"].append(suggestion)

        # Update version manager
        if self.config.enable_versioning:
            block = self.version_manager.add_or_update_block(
                code, language, context, error_info
            )
            result["block_id"] = block.block_id
            result["version"] = block.current_version

            # Check if this is an update
            if len(block.versions) > 1:
                result["action"] = "updated"

                # Get changes
                old_version = block.get_version(block.versions[-2].version_id)
                if old_version:
                    changes = self.version_manager.detect_changes(
                        old_version.code, code
                    )
                    result["changes"] = changes

                # Check if error fix
                if block.versions[-1].status == CodeStatus.FIXED:
                    result["action"] = "error_fixed"

        # Create file if needed
        if not error_info:
            file_path = self.file_manager.create_code_file(
                code, language, result.get("block_id")
            )
            result["file_path"] = str(file_path)

            # Update block with file path
            if result.get("block_id"):
                block = self.version_manager.get_block(result["block_id"])
                if block:
                    block.file_path = file_path
                    self.version_manager.save_state()

        # Copy to clipboard
        if HAS_CLIPBOARD:
            try:
                pyperclip.copy(code)
            except Exception:
                pass

        return result

    def handle_full_chat(self, chat_data: Dict) -> Dict:
        """Handle full chat export with all code blocks."""
        result = {
            "status": "success",
            "blocks_processed": 0,
            "blocks_updated": 0,
            "blocks_created": 0,
            "error_fixes": 0,
            "project_files": [],
        }

        messages = chat_data.get("messages", [])

        for message in messages:
            code_blocks = message.get("codeBlocks", [])

            for block in code_blocks:
                context = {
                    "message_id": message.get("id"),
                    "role": message.get("role"),
                    "content": message.get("content", "")[:500],
                }

                # Check for error indicators
                error_info = None
                if self._contains_error_indicators(message.get("content", "")):
                    error_info = {
                        "message": self._extract_error_message(
                            message.get("content", "")
                        ),
                        "context": message.get("content", "")[:500],
                    }

                update_result = self.handle_code_update(
                    block.get("code", ""),
                    block.get("language", "text"),
                    context,
                    error_info,
                )

                result["blocks_processed"] += 1

                if update_result["action"] == "updated":
                    result["blocks_updated"] += 1
                elif update_result["action"] == "error_fixed":
                    result["error_fixes"] += 1
                elif update_result["action"] == "created":
                    result["blocks_created"] += 1

                if "file_path" in update_result:
                    result["project_files"].append(update_result["file_path"])

        return result

    def _contains_error_indicators(self, text: str) -> bool:
        """Check if text contains error indicators."""
        error_patterns = [
            r"error", r"Error", r"exception", r"Exception",
            r"traceback", r"Traceback", r"failed", r"Failed",
            r"bug", r"Bug", r"issue", r"Issue",
            r"problem", r"Problem", r"not working",
            r"doesn't work", r"fix", r"Fix",
        ]
        return any(re.search(p, text) for p in error_patterns)

    def _extract_error_message(self, text: str) -> str:
        """Extract error message from text."""
        patterns = [
            r"(?:Error|Exception|Traceback)[:\s]+(.+?)(?:\n|$)",
            r"(?:error|exception)[:\s]+(.+?)(?:\n|$)",
            r"Failed[:\s]+(.+?)(?:\n|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "Unknown error"

    def get_version_history(self, block_id: Optional[str] = None) -> Dict:
        """Get version history."""
        if block_id:
            block = self.version_manager.get_block(block_id)
            if block:
                return {"status": "success", "block": block.to_dict()}
            return {"status": "error", "message": "Block not found"}

        return {
            "status": "success",
            "blocks": [b.to_dict() for b in self.version_manager.get_all_blocks()],
        }

    def revert_version(self, block_id: str, version_id: str) -> Dict:
        """Revert to a previous version."""
        success = self.version_manager.revert_to_version(block_id, version_id)

        if success:
            block = self.version_manager.get_block(block_id)
            if block and HAS_CLIPBOARD:
                try:
                    pyperclip.copy(block.get_current_code())
                except Exception:
                    pass

            return {
                "status": "success",
                "message": f"Reverted to version {version_id}",
                "current_version": block.current_version if block else version_id,
            }

        return {"status": "error", "message": "Failed to revert"}

    def get_error_statistics(self) -> Dict:
        """Get error statistics."""
        stats = self.error_tracker.get_error_statistics()
        stats["status"] = "success"
        return stats


def main():
    """Start the NJ IDE Copier server."""
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logger = logging.getLogger("nj_ide_copier")

    server = SmartDeepSeekServer()
    SmartAPIHandler.server_instance = server

    host = server.config.server_host
    port = server.config.server_port

    httpd = HTTPServer((host, port), SmartAPIHandler)
    logger.info(f"NJ IDE Copier server running on http://{host}:{port}")
    logger.info("Press Ctrl+C to stop.")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped.")
        httpd.server_close()


if __name__ == "__main__":
    main()
