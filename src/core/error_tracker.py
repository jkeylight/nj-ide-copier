"""
Error Tracker - Detects, classifies, and tracks code errors.

Provides error classification for 13 error types, fix suggestions,
and error statistics over time.
"""

import time
import re
from typing import Dict, List, Optional


class ErrorTracker:
    """Tracks and analyzes code errors with classification and suggestions."""

    def __init__(self):
        self.error_history: List[Dict] = []
        self.error_patterns: Dict[str, Dict] = {}

    def track_error(self, code: str, error_message: str, language: str):
        """Record an error occurrence with code snippet and classification."""
        error_entry = {
            "timestamp": time.time(),
            "language": language,
            "error_message": error_message,
            "code_snippet": code[:500],
        }
        self.error_history.append(error_entry)

        # Track error patterns
        error_type = self.classify_error(error_message)
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = {
                "count": 0,
                "examples": [],
                "fixes": [],
            }

        self.error_patterns[error_type]["count"] += 1
        if len(self.error_patterns[error_type]["examples"]) < 5:
            self.error_patterns[error_type]["examples"].append({
                "error": error_message,
                "code": code[:200],
            })

    def classify_error(self, error_message: str) -> str:
        """Classify error type using regex pattern matching."""
        error_types = {
            "syntax_error": r"SyntaxError|syntax error",
            "type_error": r"TypeError|type error",
            "value_error": r"ValueError|value error",
            "attribute_error": r"AttributeError|attribute error",
            "name_error": r"NameError|name error|undefined",
            "index_error": r"IndexError|index error",
            "key_error": r"KeyError|key error",
            "import_error": r"ImportError|module not found|import error",
            "runtime_error": r"RuntimeError|runtime error",
            "indentation_error": r"IndentationError|indentation error",
            "zero_division": r"ZeroDivisionError|division by zero",
            "file_not_found": r"FileNotFoundError|no such file",
            "permission_error": r"PermissionError|permission denied",
        }

        for error_type, pattern in error_types.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                return error_type

        return "unknown_error"

    def suggest_fix(self, error_type: str, code: str = "", language: str = "") -> Optional[str]:
        """Suggest a fix for a common error type."""
        suggestions = {
            "syntax_error": "Check for missing colons, parentheses, or brackets",
            "type_error": "Verify variable types and ensure proper type conversion",
            "value_error": "Check if the value is within acceptable range",
            "attribute_error": "Verify that the attribute exists on the object",
            "name_error": "Check if the variable is defined before use",
            "index_error": "Ensure the index is within bounds of the list/array",
            "key_error": "Check if the key exists in the dictionary",
            "import_error": "Verify the module is installed and path is correct",
            "indentation_error": "Check for consistent indentation (tabs vs spaces)",
            "zero_division": "Add a check for zero before division",
            "file_not_found": "Verify the file path and that the file exists",
            "permission_error": "Check file permissions or run with appropriate privileges",
        }
        return suggestions.get(error_type)

    def get_error_statistics(self) -> Dict:
        """Generate error statistics report."""
        return {
            "total_errors": len(self.error_history),
            "error_types": self.error_patterns,
            "recent_errors": self.error_history[-10:],
        }
