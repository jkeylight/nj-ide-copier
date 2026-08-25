"""
Helpers - Common utility functions.

Provides language extension mapping, debouncing, and timestamp formatting.
"""

import time
import functools
from typing import Callable


# Language to file extension mapping
LANGUAGE_EXTENSIONS = {
    "python": "py",
    "javascript": "js",
    "typescript": "ts",
    "java": "java",
    "cpp": "cpp",
    "c": "c",
    "csharp": "cs",
    "html": "html",
    "css": "css",
    "json": "json",
    "markdown": "md",
    "sql": "sql",
    "bash": "sh",
    "shell": "sh",
    "yaml": "yml",
    "xml": "xml",
    "rust": "rs",
    "go": "go",
    "ruby": "rb",
    "php": "php",
    "swift": "swift",
    "kotlin": "kt",
    "scala": "scala",
    "r": "r",
    "perl": "pl",
    "lua": "lua",
    "dart": "dart",
}


def get_file_extension(language: str) -> str:
    """Get file extension for a given language."""
    return LANGUAGE_EXTENSIONS.get(language.lower(), "txt")


def format_timestamp(ts: float) -> str:
    """Format a timestamp as a human-readable string."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def debounce(wait: float) -> Callable:
    """Decorator that debounces a function call."""
    def decorator(func: Callable) -> Callable:
        last_called = [0.0]

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if now - last_called[0] >= wait:
                last_called[0] = now
                return func(*args, **kwargs)
        return wrapper
    return decorator
