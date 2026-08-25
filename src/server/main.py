"""
Main Server - SmartDeepSeekServer orchestrator.

This is the main entry point that coordinates version management,
error tracking, IDE detection, file management, and chat export.
Version 2.0 - Improved with robust error handling.
"""

import json
import re
import time
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional
from http.server import HTTPServer

from src.core.version_manager import CodeVersionManager, CodeStatus
from src.core.error_tracker import ErrorTracker
from src.core.ide_detector import IDEDetector
from src.core.file_manager import FileManager
from src.core.chat_exporter import ChatExporter
from src.server.config import Config
from src.server.api_handler import SmartAPIHandler

logger = logging.getLogger("nj_ide_copier")


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
        self.chat_exporter = ChatExporter(self.config.storage_dir / "exports")
        self.history: List[Dict] = []
        
        logger.info("NJ IDE Copier Server v2.0 initialized")
        logger.info(f"Storage directory: {self.config.storage_dir}")

    def handle_code_update(
        self,
        code: str,
        language: str,
        context: Optional[Dict] = None,
        error_info: Optional[Dict] = None,
    ) -> Dict:
        """Handle code update with version tracking and error detection."""
        result = {
            "status": "success",
            "action": "created",
            "block_id": None,
            "version": None,
            "changes": None,
            "error_detected": False,
            "suggestions": [],
            "file_path": None,
        }

        if not code:
            result["status"] = "error"
            result["message"] = "Code cannot be empty"
            return result

        if not language:
            language = "text"

        if error_info and self.config.enable_error_tracking:
            self.error_tracker.track_error(
                code, error_info.get("message", ""), language, context
            )
            result["error_detected"] = True

            error_type = self.error_tracker.classify_error(
                error_info.get("message", "")
            )
            suggestion = self.error_tracker.suggest_fix(error_type, code, language)
            if suggestion:
                result["suggestions"].append(suggestion)

        if self.config.enable_versioning:
            try:
                block = self.version_manager.add_or_update_block(
                    code, language, context, error_info
                )
                result["block_id"] = block.block_id
                result["version"] = block.current_version

                if len(block.versions) > 1:
                    result["action"] = "updated"

                    old_version = block.get_version(block.versions[-2].version_id)
                    if old_version:
                        changes = self.version_manager.detect_changes(
                            old_version.code, code
                        )
                        result["changes"] = changes

                    if block.versions[-1].status == CodeStatus.FIXED:
                        result["action"] = "error_fixed"
                        self.error_tracker.mark_error_fixed(
                            error_info.get("message", "") if error_info else ""
                        )

                if not error_info:
                    file_path = self.file_manager.create_code_file(
                        code, language, block.block_id
                    )
                    result["file_path"] = str(file_path)

                    block.file_path = file_path
                    self.version_manager.save_state()
                    
            except Exception as e:
                logger.error(f"Version management error: {e}")
                result["status"] = "warning"
                result["message"] = f"Version tracking error: {str(e)}"

        self._copy_to_clipboard(code)

        self.history.append({
            "timestamp": time.time(),
            "action": result["action"],
            "language": language,
            "block_id": result.get("block_id"),
        })

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
            "export_file": None,
        }

        messages = chat_data.get("messages", [])
        
        if not messages:
            result["status"] = "error"
            result["message"] = "No messages to process"
            return result

        for message in messages:
            code_blocks = message.get("codeBlocks", [])
            
            if not code_blocks:
                code_blocks = self.chat_exporter.extract_code_blocks_from_message(message)

            for block in code_blocks:
                if not block.get("code"):
                    continue
                    
                context = {
                    "message_id": message.get("id"),
                    "role": message.get("role"),
                    "content": message.get("content", "")[:500],
                }

                error_info = None
                if self._contains_error_indicators(message.get("content", "")):
                    error_message = self._extract_error_message(
                        message.get("content", "")
                    )
                    if error_message:
                        error_info = {
                            "message": error_message,
                            "context": message.get("content", "")[:500],
                        }

                try:
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

                    if update_result.get("file_path"):
                        result["project_files"].append(update_result["file_path"])
                        
                except Exception as e:
                    logger.error(f"Error processing code block: {e}")
                    result["blocks_processed"] += 1

        return result

    def export_chat(self, chat_data: Dict, filename: Optional[str] = None) -> Dict:
        """Export chat to markdown file."""
        try:
            file_path = self.chat_exporter.export_chat(chat_data, filename)
            summary = self.chat_exporter.export_summary(chat_data)
            
            return {
                "status": "success",
                "file_path": str(file_path),
                "filename": file_path.name,
                "summary": summary,
            }
        except Exception as e:
            logger.error(f"Chat export error: {e}")
            return {"status": "error", "message": str(e)}

    def _contains_error_indicators(self, text: str) -> bool:
        """Check if text contains error indicators."""
        if not text:
            return False
            
        error_patterns = [
            r"\berror\b", r"\bError\b", r"\bERROR\b",
            r"\bexception\b", r"\bException\b",
            r"\btraceback\b", r"\bTraceback\b",
            r"\bfailed\b", r"\bFailed\b",
            r"\bbug\b", r"\bBug\b",
            r"\bissue\b", r"\bIssue\b",
            r"\bproblem\b", r"\bProblem\b",
            r"\bnot working\b", r"\bdoesn't work\b",
            r"\bfix\b", r"\bFix\b",
            r"\[Errno", r"\berrno\b",
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in error_patterns)

    def _extract_error_message(self, text: str) -> Optional[str]:
        """Extract error message from text."""
        if not text:
            return None
            
        patterns = [
            r"(?:Error|Exception|Traceback)[:\s]+(.+?)(?:\n|$)",
            r"(?:error|exception)[:\s]+(.+?)(?:\n|$)",
            r"Failed[:\s]+(.+?)(?:\n|$)",
            r"\[Errno \d+\] (.+?)(?:\n|$)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                error_text = match.group(1).strip()
                if error_text and len(error_text) > 3:
                    return error_text[:200]
        
        return None

    def _copy_to_clipboard(self, code: str):
        """Copy code to clipboard if available."""
        try:
            import pyperclip
            pyperclip.copy(code)
        except ImportError:
            pass
        except Exception as e:
            logger.warning(f"Clipboard copy failed: {e}")

    def get_version_history(self, block_id: Optional[str] = None) -> Dict:
        """Get version history."""
        try:
            if block_id:
                block = self.version_manager.get_block(block_id)
                if block:
                    return {"status": "success", "block": block.to_dict()}
                return {"status": "error", "message": "Block not found"}
            
            blocks = self.version_manager.get_all_blocks()
            return {
                "status": "success",
                "blocks": [b.to_dict() for b in blocks],
                "total": len(blocks),
            }
        except Exception as e:
            logger.error(f"Version history error: {e}")
            return {"status": "error", "message": str(e)}

    def revert_version(self, block_id: str, version_id: str) -> Dict:
        """Revert to a previous version."""
        try:
            success = self.version_manager.revert_to_version(block_id, version_id)

            if success:
                block = self.version_manager.get_block(block_id)
                code = block.get_current_code() if block else ""
                
                self._copy_to_clipboard(code)

                return {
                    "status": "success",
                    "message": f"Reverted to version {version_id}",
                    "current_version": block.current_version if block else version_id,
                    "code": code,
                }

            return {"status": "error", "message": "Failed to revert"}
        except Exception as e:
            logger.error(f"Revert error: {e}")
            return {"status": "error", "message": str(e)}

    def get_error_statistics(self) -> Dict:
        """Get error statistics."""
        try:
            return self.error_tracker.get_error_statistics()
        except Exception as e:
            logger.error(f"Error statistics error: {e}")
            return {"status": "error", "message": str(e)}

    def get_exports(self) -> List[Dict]:
        """Get list of export files."""
        return self.chat_exporter.get_recent_exports()


def setup_logging(level: str = "INFO"):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    """Start the NJ IDE Copier server."""
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("NJ IDE Copier Server v2.0")
    logger.info("=" * 60)

    server = SmartDeepSeekServer()
    SmartAPIHandler.server_instance = server

    host = server.config.server_host
    port = server.config.server_port

    try:
        httpd = HTTPServer((host, port), SmartAPIHandler)
        logger.info(f"Server running on http://{host}:{port}")
        logger.info("Press Ctrl+C to stop.")
        logger.info("-" * 60)
        
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except OSError as e:
        if e.errno == 98:
            logger.error(f"Port {port} is already in use")
            logger.error("Stop the existing server or use a different port")
        else:
            logger.error(f"Server error: {e}")
            raise
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
