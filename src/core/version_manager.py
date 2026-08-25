"""
Version Manager - Tracks code versions, detects changes, and manages rollback.

This module provides intelligent version control for code blocks captured from
DeepSeek conversations, with automatic change detection and error fix tracking.
"""

import json
import hashlib
import difflib
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class CodeStatus(Enum):
    """Status of a code version."""
    ORIGINAL = "original"
    MODIFIED = "modified"
    ERROR = "error"
    FIXED = "fixed"
    OPTIMIZED = "optimized"
    REFACTORED = "refactored"
    DEPRECATED = "deprecated"


@dataclass
class CodeVersion:
    """Represents a single version of a code block."""
    version_id: str
    code: str
    language: str
    timestamp: float
    status: CodeStatus
    parent_version: Optional[str] = None
    error_info: Optional[Dict] = None
    change_summary: Optional[str] = None
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = hashlib.md5(self.code.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "version_id": self.version_id,
            "code": self.code,
            "language": self.language,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "parent_version": self.parent_version,
            "error_info": self.error_info,
            "change_summary": self.change_summary,
            "hash": self.hash,
        }


@dataclass
class CodeBlock:
    """Represents a code block with its full version history."""
    block_id: str
    language: str
    versions: List[CodeVersion]
    current_version: str
    file_path: Optional[Path] = None
    context: Optional[Dict] = None
    created_at: float = 0.0
    updated_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        if not self.updated_at:
            self.updated_at = time.time()

    def get_current_code(self) -> str:
        """Get the code from the current version."""
        for version in self.versions:
            if version.version_id == self.current_version:
                return version.code
        return self.versions[-1].code if self.versions else ""

    def add_version(self, version: "CodeVersion"):
        """Add a new version to this block."""
        self.versions.append(version)
        self.current_version = version.version_id
        self.updated_at = time.time()

    def get_version(self, version_id: str) -> Optional[CodeVersion]:
        """Get a specific version by ID."""
        for version in self.versions:
            if version.version_id == version_id:
                return version
        return None

    def get_history(self) -> List[Dict]:
        """Get the full version history as dictionaries."""
        return [v.to_dict() for v in self.versions]

    def to_dict(self) -> Dict:
        return {
            "block_id": self.block_id,
            "language": self.language,
            "versions": [v.to_dict() for v in self.versions],
            "current_version": self.current_version,
            "file_path": str(self.file_path) if self.file_path else None,
            "context": self.context,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class CodeVersionManager:
    """Manages code versions, detects changes, and handles rollback."""

    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.blocks: Dict[str, CodeBlock] = {}
        self.load_state()

    def load_state(self):
        """Load saved state from disk."""
        state_file = self.storage_dir / "state.json"
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                for block_data in data.get("blocks", []):
                    block = self._block_from_dict(block_data)
                    self.blocks[block.block_id] = block
            except Exception as e:
                print(f"Error loading state: {e}")

    def save_state(self):
        """Save current state to disk."""
        state_file = self.storage_dir / "state.json"
        state = {
            "blocks": [block.to_dict() for block in self.blocks.values()]
        }
        state_file.write_text(json.dumps(state, indent=2))

    def _block_from_dict(self, data: Dict) -> CodeBlock:
        """Create a CodeBlock from a dictionary."""
        versions = []
        for v_data in data.get("versions", []):
            version = CodeVersion(
                version_id=v_data["version_id"],
                code=v_data["code"],
                language=v_data["language"],
                timestamp=v_data["timestamp"],
                status=CodeStatus(v_data["status"]),
                parent_version=v_data.get("parent_version"),
                error_info=v_data.get("error_info"),
                change_summary=v_data.get("change_summary"),
                hash=v_data.get("hash", ""),
            )
            versions.append(version)

        return CodeBlock(
            block_id=data["block_id"],
            language=data["language"],
            versions=versions,
            current_version=data["current_version"],
            file_path=Path(data["file_path"]) if data.get("file_path") else None,
            context=data.get("context"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )

    def identify_block(self, code: str, language: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        Identify if code matches an existing block.
        Uses MD5 hash for exact match, then difflib similarity (>70%) for fuzzy match.
        """
        code_hash = hashlib.md5(code.encode()).hexdigest()

        # Check for exact hash match
        for block_id, block in self.blocks.items():
            for version in block.versions:
                if version.hash == code_hash:
                    return block_id

        # Check for similarity (for slightly modified code)
        for block_id, block in self.blocks.items():
            if block.language != language:
                continue

            current_code = block.get_current_code()
            similarity = self.calculate_similarity(code, current_code)

            if similarity > 0.4:  # 70% similar threshold
                return block_id

        return None

    def calculate_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity between two code strings using difflib."""
        if not code1 or not code2:
            return 0.0

        sequence_matcher = difflib.SequenceMatcher(None, code1, code2)
        return sequence_matcher.ratio()

    def detect_changes(self, old_code: str, new_code: str) -> Dict:
        """Detect and describe changes between two code versions."""
        diff = list(difflib.unified_diff(
            old_code.splitlines(keepends=True),
            new_code.splitlines(keepends=True),
            fromfile="previous",
            tofile="current",
            n=3,
        ))

        changes = {
            "diff": "".join(diff),
            "added_lines": 0,
            "removed_lines": 0,
            "modified_lines": 0,
            "summary": [],
        }

        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                changes["added_lines"] += 1
            elif line.startswith("-") and not line.startswith("---"):
                changes["removed_lines"] += 1

        # Generate summary
        if changes["added_lines"] > 0 and changes["removed_lines"] > 0:
            total = changes["added_lines"] + changes["removed_lines"]
            changes["summary"].append(f"Modified {total} lines")
        elif changes["added_lines"] > 0:
            changes["summary"].append(f"Added {changes['added_lines']} lines")
        elif changes["removed_lines"] > 0:
            changes["summary"].append(f"Removed {changes['removed_lines']} lines")

        return changes

    def detect_error_fix(self, old_code: str, new_code: str) -> bool:
        """Detect if new code is fixing errors in old code."""
        error_patterns = [
            r"Error:", r"Exception:", r"Traceback",
            r"TypeError", r"ValueError", r"AttributeError",
            r"SyntaxError", r"NameError", r"IndexError",
            r"KeyError", r"RuntimeError", r"ImportError",
        ]

        old_has_errors = any(re.search(pattern, old_code) for pattern in error_patterns)
        new_has_errors = any(re.search(pattern, new_code) for pattern in error_patterns)

        if old_has_errors and not new_has_errors:
            return True

        fix_patterns = [
            (r"except:", r"except Exception as e:"),
            (r"== None", r"is None"),
            (r"!= None", r"is not None"),
        ]

        for old_pattern, new_pattern in fix_patterns:
            if re.search(old_pattern, old_code) and re.search(new_pattern, new_code):
                return True

        return False

    def add_or_update_block(
        self,
        code: str,
        language: str,
        context: Optional[Dict] = None,
        error_info: Optional[Dict] = None,
    ) -> CodeBlock:
        """Add new block or update existing one with intelligent status detection."""
        block_id = self.identify_block(code, language, context)

        if block_id:
            block = self.blocks[block_id]
            current_code = block.get_current_code()
            changes = self.detect_changes(current_code, code)

            if error_info:
                status = CodeStatus.ERROR
            elif self.detect_error_fix(current_code, code):
                status = CodeStatus.FIXED
                old_version = block.get_version(block.current_version)
                if old_version:
                    old_version.status = CodeStatus.ERROR
                    old_version.error_info = {
                        "message": "Had errors, fixed in newer version",
                        "timestamp": time.time(),
                    }
            elif changes["added_lines"] > 0 and changes["removed_lines"] == 0:
                status = CodeStatus.OPTIMIZED
            elif len(code) < len(current_code) * 0.7:
                status = CodeStatus.REFACTORED
            else:
                status = CodeStatus.MODIFIED

            version = CodeVersion(
                version_id=f"v{len(block.versions) + 1}",
                code=code,
                language=language,
                timestamp=time.time(),
                status=status,
                parent_version=block.current_version,
                error_info=error_info,
                change_summary=", ".join(changes["summary"]) if changes["summary"] else None,
            )

            block.add_version(version)

            if block.file_path and block.file_path.exists():
                block.file_path.write_text(code, encoding="utf-8")

            self.save_state()
            return block
        else:
            block_id = hashlib.md5(f"{language}-{time.time()}".encode()).hexdigest()[:12]

            version = CodeVersion(
                version_id="v1",
                code=code,
                language=language,
                timestamp=time.time(),
                status=CodeStatus.ORIGINAL if not error_info else CodeStatus.ERROR,
                error_info=error_info,
            )

            block = CodeBlock(
                block_id=block_id,
                language=language,
                versions=[version],
                current_version="v1",
                context=context,
            )

            self.blocks[block_id] = block
            self.save_state()
            return block

    def get_block(self, block_id: str) -> Optional[CodeBlock]:
        return self.blocks.get(block_id)

    def get_all_blocks(self) -> List[CodeBlock]:
        return list(self.blocks.values())

    def get_blocks_by_language(self, language: str) -> List[CodeBlock]:
        return [b for b in self.blocks.values() if b.language == language]

    def get_recent_blocks(self, limit: int = 10) -> List[CodeBlock]:
        return sorted(self.blocks.values(), key=lambda b: b.updated_at, reverse=True)[:limit]

    def revert_to_version(self, block_id: str, version_id: str) -> bool:
        block = self.get_block(block_id)
        if not block:
            return False
        version = block.get_version(version_id)
        if not version:
            return False

        new_version = CodeVersion(
            version_id=f"v{len(block.versions) + 1}",
            code=version.code,
            language=block.language,
            timestamp=time.time(),
            status=CodeStatus.REFACTORED,
            parent_version=block.current_version,
            change_summary=f"Reverted to {version_id}",
        )

        block.add_version(new_version)

        if block.file_path and block.file_path.exists():
            block.file_path.write_text(version.code, encoding="utf-8")

        self.save_state()
        return True

    def cleanup_old_versions(self, max_versions_per_block: int = 10):
        for block in self.blocks.values():
            if len(block.versions) > max_versions_per_block:
                block.versions = block.versions[-max_versions_per_block:]
                block.current_version = block.versions[-1].version_id
        self.save_state()

    def export_history(self, fmt: str = "json") -> Path:
        export_file = self.storage_dir / f"history_{int(time.time())}.{fmt}"

        if fmt == "json":
            data = {"blocks": [b.to_dict() for b in self.blocks.values()]}
            export_file.write_text(json.dumps(data, indent=2))
        elif fmt == "markdown":
            nl = chr(10)
            md = "# Code Version History" + nl + nl
            for block in self.blocks.values():
                md += f"## Block {block.block_id} ({block.language})" + nl + nl
                for v in block.versions:
                    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(v.timestamp))
                    md += f"### {v.version_id} - {v.status.value}" + nl
                    md += f"**Time:** {ts}" + nl
                    if v.change_summary:
                        md += f"**Changes:** {v.change_summary}" + nl
                    md += nl + chr(96)*3 + block.language + nl + v.code + nl + chr(96)*3 + nl + nl
            export_file.write_text(md)

        return export_file
