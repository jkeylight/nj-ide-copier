"""
Error Tracker - Detects, classifies, and tracks code errors.

Provides error classification for 17 error types, fix suggestions,
and error statistics over time. Improved version with better pattern matching.
"""

import time
import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ErrorType:
    """Represents an error type with patterns and fix suggestions."""
    name: str
    patterns: List[str]
    suggestion: str
    severity: str = "medium"


class ErrorTracker:
    """Tracks and analyzes code errors with classification and suggestions."""
    
    ERROR_TYPES = {
        "syntax_error": ErrorType(
            name="Syntax Error",
            patterns=[r"SyntaxError", r"syntax error", r"Syntax error", r"invalid syntax", r"Unexpected token", r"Parse error"],
            suggestion="Check for missing colons, parentheses, brackets, or quotes. Ensure proper indentation and keyword spelling.",
            severity="high"
        ),
        "type_error": ErrorType(
            name="Type Error",
            patterns=[r"TypeError", r"type error", r"cannot unpack non-iterable", r"'NoneType' object is not", r"not subscriptable"],
            suggestion="Verify variable types match expected types. Ensure proper type conversion using int(), str(), list(), etc.",
            severity="medium"
        ),
        "value_error": ErrorType(
            name="Value Error",
            patterns=[r"ValueError", r"value error", r"invalid literal", r"could not convert"],
            suggestion="Check if the value is within acceptable range and matches expected format.",
            severity="medium"
        ),
        "attribute_error": ErrorType(
            name="Attribute Error",
            patterns=[r"AttributeError", r"attribute error", r"has no attribute", r"'.*' object has no attribute"],
            suggestion="Verify that the attribute/method exists on the object. Check for typos in attribute names.",
            severity="medium"
        ),
        "name_error": ErrorType(
            name="Name Error",
            patterns=[r"NameError", r"name error", r"name '.*' is not defined", r"undefined", r"cannot access before declaration"],
            suggestion="Check if the variable/function is defined before use. Verify spelling and import statements.",
            severity="high"
        ),
        "index_error": ErrorType(
            name="Index Error",
            patterns=[r"IndexError", r"index error", r"list index out of range", r"index .* out of bounds"],
            suggestion="Ensure the index is within bounds (0 to length-1). Add bounds checking before accessing elements.",
            severity="medium"
        ),
        "key_error": ErrorType(
            name="Key Error",
            patterns=[r"KeyError", r"key error", r"Key '.*' not found", r"missing.*key"],
            suggestion="Check if the key exists in the dictionary. Use dict.get() with a default value or check with 'in' operator.",
            severity="low"
        ),
        "import_error": ErrorType(
            name="Import Error",
            patterns=[r"ImportError", r"ModuleNotFoundError", r"module not found", r"import error", r"cannot import", r"No module named"],
            suggestion="Verify the module is installed (pip install) and the path is correct. Check for circular imports.",
            severity="high"
        ),
        "runtime_error": ErrorType(
            name="Runtime Error",
            patterns=[r"RuntimeError", r"runtime error", r"maximum recursion", r"stack overflow"],
            suggestion="Check for infinite loops, recursive calls without proper base cases, or memory issues.",
            severity="high"
        ),
        "indentation_error": ErrorType(
            name="Indentation Error",
            patterns=[r"IndentationError", r"indentation error", r"unexpected indent", r"unindent does not match", r"inconsistent indentation"],
            suggestion="Use consistent indentation (either tabs OR spaces, not mixed). Recommended: 4 spaces per level.",
            severity="medium"
        ),
        "zero_division": ErrorType(
            name="Zero Division Error",
            patterns=[r"ZeroDivisionError", r"division by zero", r"division or modulo by zero", r"float division by zero"],
            suggestion="Add a check for zero before division: 'if divisor != 0' before performing division.",
            severity="medium"
        ),
        "file_not_found": ErrorType(
            name="File Not Found Error",
            patterns=[r"FileNotFoundError", r"No such file", r"file not found", r"[Errno 2]", r"ENOENT"],
            suggestion="Verify the file path is correct and the file exists. Use os.path.exists() to check before access.",
            severity="medium"
        ),
        "permission_error": ErrorType(
            name="Permission Error",
            patterns=[r"PermissionError", r"permission denied", r"access denied", r"[Errno 13]", r"EACCES"],
            suggestion="Check file permissions. Run with appropriate privileges or change file permissions with chmod.",
            severity="medium"
        ),
        "connection_error": ErrorType(
            name="Connection Error",
            patterns=[r"ConnectionError", r"connection refused", r"connection timeout", r"network error", r"ConnectionResetError", r"[Errno 111]"],
            suggestion="Check network connectivity, firewall settings, and that the target service is running.",
            severity="high"
        ),
        "timeout_error": ErrorType(
            name="Timeout Error",
            patterns=[r"TimeoutError", r"timed out", r"timeout", r"Request timeout", r"Read timeout"],
            suggestion="Increase timeout values or check if the service is responding. Verify network latency.",
            severity="medium"
        ),
        "assertion_error": ErrorType(
            name="Assertion Error",
            patterns=[r"AssertionError", r"assertion failed"],
            suggestion="Review the assertion condition. The expected condition was not met - check input validation.",
            severity="medium"
        ),
        "memory_error": ErrorType(
            name="Memory Error",
            patterns=[r"MemoryError", r"out of memory", r"memory allocation failed"],
            suggestion="Reduce memory usage by processing data in chunks, deleting unused objects, or increasing system RAM.",
            severity="critical"
        ),
    }
    
    GENERIC_ERROR_PATTERNS = [
        r"\bError:", r"\bException:", r"\bfailed", r"\bFailed", r"\bERROR", r"\bEXCEPTION",
        r"\bTraceback", r"\bfault", r"\bIssue:", r"\bBug:", r"\bProblem:", r"\bdoesn't work",
        r"\bnot working", r"\bbroken",
    ]

    def __init__(self):
        self.error_history: List[Dict] = []
        self.error_patterns: Dict[str, Dict] = {}
        self.stats = {
            "total_errors": 0, "fixed_errors": 0,
            "by_severity": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "by_type": {}
        }

    def track_error(self, code: str, error_message: str, language: str, context: Optional[Dict] = None):
        """Record an error occurrence with code snippet and classification."""
        error_entry = {
            "timestamp": time.time(), "language": language,
            "error_message": error_message, "code_snippet": code[:500] if code else "",
            "context": context or {}
        }
        self.error_history.append(error_entry)
        self.stats["total_errors"] += 1

        error_type = self.classify_error(error_message)
        error_info = self.ERROR_TYPES.get(error_type)
        
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = {
                "count": 0, "examples": [], "fixes": [],
                "severity": error_info.severity if error_info else "medium",
                "name": error_info.name if error_info else error_type.replace("_", " ").title()
            }
            if error_type not in self.stats["by_type"]:
                self.stats["by_type"][error_type] = 0

        self.error_patterns[error_type]["count"] += 1
        self.stats["by_type"][error_type] += 1
        
        if error_info:
            self.stats["by_severity"][error_info.severity] += 1
        
        if len(self.error_patterns[error_type]["examples"]) < 10:
            self.error_patterns[error_type]["examples"].append({
                "error": error_message, "code": code[:200] if code else "",
                "timestamp": time.time()
            })

    def classify_error(self, error_message: str) -> str:
        """Classify error type using comprehensive pattern matching."""
        if not error_message:
            return "unknown_error"
        
        for error_type, error_info in self.ERROR_TYPES.items():
            for pattern in error_info.patterns:
                if re.search(pattern, error_message, re.IGNORECASE):
                    return error_type
        
        for pattern in self.GENERIC_ERROR_PATTERNS:
            if re.search(pattern, error_message):
                return "generic_error"
        
        return "unknown_error"

    def suggest_fix(self, error_type: str, code: str = "", language: str = "") -> Optional[Dict]:
        """Get comprehensive fix suggestion for an error type."""
        error_info = self.ERROR_TYPES.get(error_type)
        
        if error_info:
            return {
                "type": error_info.name, "suggestion": error_info.suggestion,
                "severity": error_info.severity, "code_snippet": code, "language": language
            }
        
        return {
            "type": "Unknown Error",
            "suggestion": "Review the error message carefully. Check logs for more details. Consider searching for this specific error online.",
            "severity": "medium", "code_snippet": code, "language": language
        }

    def get_fix_for_error_message(self, error_message: str, code: str = "") -> Optional[Dict]:
        """Get fix suggestion directly from an error message."""
        error_type = self.classify_error(error_message)
        return self.suggest_fix(error_type, code)

    def mark_error_fixed(self, error_message: str) -> bool:
        """Mark an error as fixed."""
        self.stats["fixed_errors"] += 1
        return True

    def get_error_statistics(self) -> Dict:
        """Generate comprehensive error statistics report."""
        error_rate = (
            (self.stats["fixed_errors"] / self.stats["total_errors"] * 100)
            if self.stats["total_errors"] > 0 else 0
        )
        
        sorted_errors = sorted(self.error_patterns.items(), key=lambda x: x[1]["count"], reverse=True)
        
        return {
            "status": "success",
            "total_errors": self.stats["total_errors"],
            "fixed_errors": self.stats["fixed_errors"],
            "unfixed_errors": self.stats["total_errors"] - self.stats["fixed_errors"],
            "fix_rate": round(error_rate, 2),
            "by_severity": self.stats["by_severity"],
            "by_type": {
                name: {"count": info["count"], "severity": info["severity"], "name": info["name"]}
                for name, info in sorted_errors
            },
            "most_common_error": sorted_errors[0][0] if sorted_errors else None,
            "recent_errors": self.error_history[-10:],
            "top_errors": [
                {"type": name, "count": info["count"], "severity": info["severity"]}
                for name, info in sorted_errors[:5]
            ]
        }

    def export_errors(self, format: str = "json") -> Dict:
        """Export error data in specified format."""
        if format == "json":
            return {
                "error_history": self.error_history,
                "error_patterns": self.error_patterns,
                "statistics": self.get_error_statistics()
            }
        elif format == "markdown":
            md = "# Error Report\n\n"
            md += f"**Total Errors:** {self.stats['total_errors']}\n"
            md += f"**Fixed:** {self.stats['fixed_errors']}\n"
            md += f"**Fix Rate:** {self.stats.get('fix_rate', 0)}%\n\n"
            md += "## Errors by Type\n\n"
            md += "| Type | Count | Severity |\n|------|-------|----------|\n"
            for error_type, info in self.error_patterns.items():
                md += f"| {error_type} | {info['count']} | {info['severity']} |\n"
            return {"markdown": md}
        
        return self.error_history

    def clear_history(self):
        """Clear error history."""
        self.error_history = []
        self.error_patterns = {}
        self.stats = {
            "total_errors": 0, "fixed_errors": 0,
            "by_severity": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "by_type": {}
        }
