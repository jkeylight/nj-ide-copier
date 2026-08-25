"""
File Manager - Manages code files and project directories.

Provides language-to-extension mapping, temp file creation, and
project directory organization.
"""

import time
from pathlib import Path
from typing import Optional

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
    "typescriptreact": "tsx",
    "javascriptreact": "jsx",
}

# Default filenames for common languages
DEFAULT_FILENAMES = {
    "python": "main.py",
    "javascript": "index.js",
    "typescript": "index.ts",
    "html": "index.html",
    "css": "style.css",
    "json": "config.json",
    "yaml": "config.yml",
    "markdown": "readme.md",
    "java": "Main.java",
    "go": "main.go",
    "rust": "main.rs",
    "ruby": "main.rb",
    "php": "index.php",
    "swift": "main.swift",
    "kotlin": "Main.kt",
    "c": "main.c",
    "cpp": "main.cpp",
    "csharp": "Program.cs",
}


class FileManager:
    """Manages code files and project directories."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.home() / ".deepseek-copier"
        self.projects_dir = self.base_dir / "projects"
        self.temp_dir = self.base_dir / "temp"

        # Ensure directories exist
        self.projects_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def get_extension(self, language: str) -> str:
        """Get file extension for a given language."""
        return LANGUAGE_EXTENSIONS.get(language.lower(), "txt")

    def get_default_filename(self, language: str) -> str:
        """Get default filename for a given language."""
        return DEFAULT_FILENAMES.get(language.lower(), f"code.{self.get_extension(language)}")

    def create_code_file(
        self,
        code: str,
        language: str,
        block_id: Optional[str] = None,
    ) -> Path:
        """Create a file for code with smart naming."""
        if block_id:
            file_dir = self.projects_dir / block_id
        else:
            file_dir = self.projects_dir / f"snippet-{int(time.time())}"

        file_dir.mkdir(parents=True, exist_ok=True)

        filename = self.get_default_filename(language)
        file_path = file_dir / filename
        file_path.write_text(code, encoding="utf-8")

        return file_path

    def create_project_dir(self, project_name: str) -> Path:
        """Create an organized project directory."""
        project_dir = self.projects_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir

    def cleanup_temp_files(self, older_than_hours: int = 24):
        """Remove temporary files older than specified hours."""
        cutoff_time = time.time() - (older_than_hours * 3600)

        for file_path in self.temp_dir.rglob("*"):
            if file_path.is_file():
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
