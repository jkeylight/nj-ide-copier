"""
Server Configuration - Loads and manages server settings.

Supports configuration from .env files and JSON config files
with sensible defaults.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Server configuration loaded from environment and config files."""

    def __init__(self):
        load_dotenv()

        self.storage_dir = Path(os.getenv(
            "DEEPSEEK_STORAGE_DIR",
            str(Path.home() / ".deepseek-copier"),
        ))
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Server settings
        self.server_port = int(os.getenv("DEEPSEEK_SERVER_PORT", "8765"))
        self.server_host = os.getenv("DEEPSEEK_SERVER_HOST", "localhost")

        # IDE settings
        self.default_ide = os.getenv("DEEPSEEK_DEFAULT_IDE", "auto")

        # Feature flags
        self.enable_versioning = os.getenv(
            "DEEPSEEK_ENABLE_VERSIONING", "true"
        ).lower() == "true"
        self.enable_error_tracking = os.getenv(
            "DEEPSEEK_ENABLE_ERROR_TRACKING", "true"
        ).lower() == "true"

        # Logging
        self.log_level = os.getenv("DEEPSEEK_LOG_LEVEL", "INFO")

        # Security
        self.secret_key = os.getenv("DEEPSEEK_SECRET_KEY", "default-secret-key-change-me")

        # Infrastructure
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///deepseek.db")

        # Load JSON config overrides
        self._load_json_config()

    def _load_json_config(self):
        """Load additional config from JSON file."""
        config_file = self.storage_dir / "config.json"
        if config_file.exists():
            try:
                data = json.loads(config_file.read_text())
                # Override with JSON values
                for key, value in data.items():
                    attr_key = key
                    if hasattr(self, attr_key):
                        setattr(self, attr_key, value)
            except Exception as e:
                print(f"Warning: Could not load config.json: {e}")

    def save(self):
        """Save current config to JSON file."""
        config_file = self.storage_dir / "config.json"
        data = {
            "server_port": self.server_port,
            "server_host": self.server_host,
            "default_ide": self.default_ide,
            "enable_versioning": self.enable_versioning,
            "enable_error_tracking": self.enable_error_tracking,
            "log_level": self.log_level,
        }
        config_file.write_text(json.dumps(data, indent=2))

    def get(self, key: str, default=None):
        """Get a config value."""
        return getattr(self, key, default)
