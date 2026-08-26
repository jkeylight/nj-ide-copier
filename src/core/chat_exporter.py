"""
Chat Exporter - Export DeepSeek conversations as well-formatted Markdown.

Creates properly structured markdown files with:
- Title and metadata
- Table of contents
- Numbered code blocks
- Error indicators
- File paths to extracted code
"""

import time
import re
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ChatExporter:
    """Export chat conversations as well-formatted Markdown."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.home() / ".deepseek-copier" / "exports"
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_filename(self, chat_data: Dict = None) -> str:
        """Generate a descriptive filename for the export."""
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        
        if chat_data:
            # Try to get a meaningful name from the chat
            messages = chat_data.get("messages", [])
            if messages:
                first_msg = messages[0].get("content", "")[:50]
                # Clean the name
                safe_name = re.sub(r'[^a-zA-Z0-9]', '-', first_msg)
                safe_name = re.sub(r'-+', '-', safe_name).strip('-')
                if len(safe_name) > 20:
                    safe_name = safe_name[:20]
                if safe_name:
                    return f"chat-export-{safe_name}-{timestamp}.md"
        
        return f"chat-export-{timestamp}.md"
    
    def extract_code_blocks_from_message(self, message: Dict) -> List[Dict]:
        """Extract code blocks from a message."""
        code_blocks = message.get("codeBlocks", [])
        
        # Also try to extract from content
        content = message.get("content", "")
        if not code_blocks and content:
            # Look for markdown code blocks
            pattern = r'```(\w+)?\n(.*?)```'
            matches = re.findall(pattern, content, re.DOTALL)
            for lang, code in matches:
                code_blocks.append({
                    "code": code.strip(),
                    "language": lang or "text"
                })
        
        return code_blocks
    
    def detect_errors_in_message(self, message: Dict) -> List[Dict]:
        """Detect error indicators in a message."""
        content = message.get("content", "")
        errors = []
        
        error_patterns = [
            r"Error[:\s]+(.+?)(?:\n|$)",
            r"Exception[:\s]+(.+?)(?:\n|$)",
            r"Traceback \(most recent call last\):",
            r"(?:Error|Exception|failed|Failed).*?(?:\n(?:\s+.*?\n){0,3})",
            r"```\n(Traceback.*?)```",
        ]
        
        for pattern in error_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                error_text = match.group(0)[:200]  # Limit length
                errors.append({
                    "type": "error",
                    "text": error_text,
                    "match": match.group(1) if match.groups() else None
                })
        
        return errors
    
    def format_code_block(self, code: str, language: str, block_num: int) -> str:
        """Format a code block with language and numbering."""
        return f"```{language}\n{code}\n```"
    
    def create_table_of_contents(self, messages: List[Dict]) -> str:
        """Create a table of contents for the chat."""
        toc = ["## Table of Contents\n"]
        
        for i, message in enumerate(messages, 1):
            role = message.get("role", "unknown")
            content_preview = message.get("content", "")[:60]
            
            # Clean preview
            content_preview = re.sub(r'```.*?```', '[code]', content_preview, flags=re.DOTALL)
            content_preview = re.sub(r'\s+', ' ', content_preview).strip()
            
            if len(message.get("content", "")) > 60:
                content_preview += "..."
            
            toc.append(f"{i}. **[{role.upper()}]** {content_preview}")
            
            # Add sub-items for code blocks
            code_blocks = self.extract_code_blocks_from_message(message)
            for j, block in enumerate(code_blocks, 1):
                lang = block.get("language", "text")
                toc.append(f"   - Code Block {j} ({lang})")
        
        toc.append("")  # Empty line at end
        return "\n".join(toc)
    
    def create_metadata_section(self, chat_data: Dict) -> str:
        """Create metadata section for the export."""
        metadata = {
            "exported_at": datetime.now().isoformat(),
            "total_messages": len(chat_data.get("messages", [])),
            "platform": chat_data.get("platform", "DeepSeek"),
            "url": chat_data.get("url", "Unknown"),
        }
        
        # Count code blocks
        total_code_blocks = 0
        languages = set()
        for message in chat_data.get("messages", []):
            for block in self.extract_code_blocks_from_message(message):
                total_code_blocks += 1
                if block.get("language"):
                    languages.add(block.get("language"))
        
        metadata["total_code_blocks"] = total_code_blocks
        metadata["languages"] = sorted(list(languages))
        
        # Format metadata
        meta_lines = ["## Export Metadata\n"]
        for key, value in metadata.items():
            key_formatted = key.replace("_", " ").title()
            if isinstance(value, list):
                meta_lines.append(f"- **{key_formatted}:** {', '.join(value)}")
            else:
                meta_lines.append(f"- **{key_formatted}:** {value}")
        
        meta_lines.append("")  # Empty line
        return "\n".join(meta_lines)
    
    def export_message(
        self, 
        message: Dict, 
        message_num: int,
        include_metadata: bool = True
    ) -> str:
        """Export a single message as markdown."""
        lines = []
        
        role = message.get("role", "unknown").upper()
        content = message.get("content", "")
        timestamp = message.get("timestamp")
        
        # Message header
        header = f"### Message {message_num}"
        if role:
            header += f" [{role}]"
        lines.append(header)
        
        # Timestamp if available
        if timestamp:
            try:
                ts = datetime.fromtimestamp(timestamp)
                lines.append(f"*Timestamp: {ts.strftime('%Y-%m-%d %H:%M:%S')}*")
            except:
                pass
        
        lines.append("")  # Empty line
        
        # Detect and mark errors
        errors = self.detect_errors_in_message(message)
        if errors:
            lines.append("> ⚠️ **Error Detected**\n")
            for error in errors[:2]:  # Limit to 2 error indicators
                lines.append(f"> ```\n> {error['text'][:100]}\n> ```")
            lines.append("")
        
        # Process content
        processed_content = self._process_content(content)
        lines.append(processed_content)
        
        # Code blocks section
        code_blocks = self.extract_code_blocks_from_message(message)
        if code_blocks:
            lines.append("")  # Empty line
            lines.append("**Code Blocks:**")
            lines.append("")
            
            for i, block in enumerate(code_blocks, 1):
                lang = block.get("language", "text")
                code = block.get("code", "")
                
                lines.append(f"```{lang}")
                lines.append(code)
                lines.append("```")
                lines.append("")  # Empty line after each block
        
        return "\n".join(lines)
    
    def _process_content(self, content: str) -> str:
        """Process message content for better formatting."""
        if not content:
            return ""
        
        # Preserve code blocks but clean up formatting
        lines = content.split("\n")
        processed = []
        
        in_code_block = False
        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                processed.append(line)
            elif not in_code_block:
                # Outside code blocks, clean up whitespace
                line = line.strip()
                if line:
                    processed.append(line)
            else:
                processed.append(line)
        
        return "\n".join(processed)
    
    def export_chat(
        self, 
        chat_data: Dict,
        filename: Optional[str] = None,
        include_toc: bool = True,
        include_metadata: bool = True
    ) -> Path:
        """
        Export chat data as a well-formatted Markdown file.
        
        Args:
            chat_data: Dictionary containing chat messages and metadata
            filename: Optional custom filename (auto-generated if not provided)
            include_toc: Include table of contents
            include_metadata: Include export metadata section
            
        Returns:
            Path to the exported file
        """
        messages = chat_data.get("messages", [])
        
        if not messages:
            raise ValueError("No messages to export")
        
        # Generate filename
        if not filename:
            filename = self.generate_filename(chat_data)
        
        file_path = self.base_dir / filename
        
        # Build markdown content
        lines = []
        
        # Title
        title = chat_data.get("title", "DeepSeek Chat Export")
        lines.append(f"# {title}\n")
        
        # Metadata section
        if include_metadata:
            lines.append(self.create_metadata_section(chat_data))
        
        # Table of contents
        if include_toc:
            lines.append(self.create_table_of_contents(messages))
        
        # Separator
        lines.append("---\n")
        
        # Messages
        lines.append("## Conversation\n")
        
        for i, message in enumerate(messages, 1):
            lines.append(self.export_message(message, i, include_metadata))
            lines.append("---")
            lines.append("")
        
        # Write to file
        content = "\n".join(lines)
        file_path.write_text(content, encoding="utf-8")
        
        return file_path
    
    def export_summary(self, chat_data: Dict) -> Dict:
        """Generate export summary statistics."""
        messages = chat_data.get("messages", [])
        
        stats = {
            "total_messages": len(messages),
            "by_role": {},
            "total_code_blocks": 0,
            "languages": set(),
            "errors_detected": 0,
            "error_types": {}
        }
        
        for message in messages:
            role = message.get("role", "unknown")
            stats["by_role"][role] = stats["by_role"].get(role, 0) + 1
            
            # Count code blocks
            code_blocks = self.extract_code_blocks_from_message(message)
            stats["total_code_blocks"] += len(code_blocks)
            
            for block in code_blocks:
                if block.get("language"):
                    stats["languages"].add(block.get("language"))
            
            # Count errors
            errors = self.detect_errors_in_message(message)
            stats["errors_detected"] += len(errors)
            
            for error in errors:
                error_type = error.get("type", "unknown")
                stats["error_types"][error_type] = stats["error_types"].get(error_type, 0) + 1
        
        stats["languages"] = sorted(list(stats["languages"]))
        
        return stats
    
    def get_recent_exports(self, limit: int = 10) -> List[Dict]:
        """Get list of recent export files."""
        exports = []
        
        for file_path in sorted(self.base_dir.glob("chat-export-*.md"), reverse=True)[:limit]:
            stat = file_path.stat()
            exports.append({
                "filename": file_path.name,
                "path": str(file_path),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "modified_date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return exports
    
    def delete_export(self, filename: str) -> bool:
        """Delete an export file."""
        file_path = self.base_dir / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False


def export_chat_to_markdown(
    chat_data: Dict,
    output_dir: Optional[Path] = None,
    filename: Optional[str] = None
) -> Dict:
    """
    Convenience function to export chat data to markdown.
    
    Args:
        chat_data: Dictionary with 'messages' key containing chat messages
        output_dir: Directory to save the export (default: ~/.deepseek-copier/exports)
        filename: Custom filename (auto-generated if not provided)
        
    Returns:
        Dictionary with export status and file path
    """
    exporter = ChatExporter(output_dir)
    
    try:
        file_path = exporter.export_chat(chat_data, filename)
        stats = exporter.export_summary(chat_data)
        
        return {
            "status": "success",
            "file_path": str(file_path),
            "filename": file_path.name,
            "summary": stats
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
