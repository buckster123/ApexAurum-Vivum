"""
Export Engine for Conversations

Handles exporting conversations to various formats:
- JSON (complete, lossless)
- Markdown (readable, shareable)
- HTML (styled, presentable)
- TXT (simple, universal)
- PDF (optional, requires reportlab)
"""

import json
import html
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ExportEngine:
    """Main export engine for conversations"""

    def __init__(self):
        """Initialize export engine"""
        self.exporters = {
            "json": JSONExporter(),
            "markdown": MarkdownExporter(),
            "html": HTMLExporter(),
            "txt": TXTExporter(),
        }

        # Try to add PDF exporter if reportlab available
        try:
            self.exporters["pdf"] = PDFExporter()
        except ImportError:
            logger.info("PDF export not available (reportlab not installed)")

    def export_conversation(
        self,
        conversation: Dict[str, Any],
        format: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Export a single conversation.

        Args:
            conversation: Conversation dict with messages
            format: Export format (json, markdown, html, txt, pdf)
            options: Format-specific options

        Returns:
            Exported content as bytes
        """
        format_lower = format.lower()

        if format_lower not in self.exporters:
            raise ValueError(f"Unsupported format: {format}. Available: {list(self.exporters.keys())}")

        exporter = self.exporters[format_lower]
        options = options or {}

        return exporter.export(conversation, options)

    def export_multiple(
        self,
        conversations: List[Dict[str, Any]],
        format: str,
        combine: bool = False,
        options: Optional[Dict[str, Any]] = None
    ) -> Union[bytes, List[bytes]]:
        """
        Export multiple conversations.

        Args:
            conversations: List of conversation dicts
            format: Export format
            combine: If True, combine into single file
            options: Format-specific options

        Returns:
            Single bytes if combined, List[bytes] otherwise
        """
        if combine:
            # For JSON, combine into array
            if format.lower() == "json":
                combined = {
                    "exported_at": datetime.now().isoformat(),
                    "count": len(conversations),
                    "conversations": conversations
                }
                return json.dumps(combined, indent=2).encode("utf-8")

            # For other formats, concatenate with separators
            exports = []
            for conv in conversations:
                exports.append(self.export_conversation(conv, format, options))

            separator = b"\n\n" + b"=" * 80 + b"\n\n"
            return separator.join(exports)
        else:
            # Return list of individual exports
            return [
                self.export_conversation(conv, format, options)
                for conv in conversations
            ]

    def get_mime_type(self, format: str) -> str:
        """Get MIME type for format"""
        mime_types = {
            "json": "application/json",
            "markdown": "text/markdown",
            "html": "text/html",
            "txt": "text/plain",
            "pdf": "application/pdf"
        }
        return mime_types.get(format.lower(), "application/octet-stream")

    def get_file_extension(self, format: str) -> str:
        """Get file extension for format"""
        return format.lower()


class BaseExporter:
    """Base class for exporters"""

    def export(self, conversation: Dict[str, Any], options: Dict[str, Any]) -> bytes:
        """Export conversation to bytes"""
        raise NotImplementedError


class JSONExporter(BaseExporter):
    """Export to JSON format"""

    def export(self, conversation: Dict[str, Any], options: Dict[str, Any]) -> bytes:
        """Export to JSON with optional metadata"""
        include_metadata = options.get("include_metadata", True)
        include_stats = options.get("include_stats", True)

        output = conversation.copy()

        # Add export metadata
        if include_metadata:
            output["exported_at"] = datetime.now().isoformat()
            output["export_format"] = "json"

        # Add statistics
        if include_stats:
            stats = self._calculate_stats(conversation)
            output["statistics"] = stats

        return json.dumps(output, indent=2, ensure_ascii=False).encode("utf-8")

    def _calculate_stats(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate conversation statistics"""
        messages = conversation.get("messages", [])

        user_msgs = [m for m in messages if m.get("role") == "user"]
        assistant_msgs = [m for m in messages if m.get("role") == "assistant"]

        # Estimate tokens (rough)
        total_chars = sum(len(str(m.get("content", ""))) for m in messages)
        estimated_tokens = total_chars // 4  # Rough estimate

        return {
            "total_messages": len(messages),
            "user_messages": len(user_msgs),
            "assistant_messages": len(assistant_msgs),
            "estimated_tokens": estimated_tokens,
            "first_message": messages[0].get("timestamp") if messages else None,
            "last_message": messages[-1].get("timestamp") if messages else None,
        }


class MarkdownExporter(BaseExporter):
    """Export to Markdown format"""

    def export(self, conversation: Dict[str, Any], options: Dict[str, Any]) -> bytes:
        """Export to Markdown"""
        lines = []

        # Title
        title = conversation.get("title", "Untitled Conversation")
        lines.append(f"# {title}\n")

        # Metadata
        created_at = conversation.get("created_at", "Unknown")
        if isinstance(created_at, str):
            created_at = created_at.split("T")[0]  # Just date

        lines.append(f"**Created:** {created_at}")

        model = conversation.get("metadata", {}).get("model_used", "Unknown")
        lines.append(f"**Model:** {model}")

        messages = conversation.get("messages", [])
        lines.append(f"**Messages:** {len(messages)}\n")

        # Tags if available
        tags = conversation.get("metadata", {}).get("tags", [])
        if tags:
            lines.append(f"**Tags:** {', '.join(tags)}\n")

        lines.append("---\n")
        lines.append("## Conversation\n")

        # Messages
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Format role header
            if role == "user":
                lines.append("**User:**")
            elif role == "assistant":
                lines.append("**Assistant:**")
            else:
                lines.append(f"**{role.title()}:**")

            # Handle array content (text blocks)
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        lines.append(item.get("text", ""))
            else:
                lines.append(str(content))

            lines.append("")  # Blank line between messages

        return "\n".join(lines).encode("utf-8")


class HTMLExporter(BaseExporter):
    """Export to HTML format"""

    def export(self, conversation: Dict[str, Any], options: Dict[str, Any]) -> bytes:
        """Export to styled HTML"""
        title = html.escape(conversation.get("title", "Untitled Conversation"))
        created_at = conversation.get("created_at", "Unknown")
        messages = conversation.get("messages", [])

        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{title}</title>",
            "<meta charset='utf-8'>",
            self._get_css(),
            "</head>",
            "<body>",
            f"<h1>{title}</h1>",
            "<div class='metadata'>",
            f"<p><strong>Created:</strong> {created_at}</p>",
            f"<p><strong>Messages:</strong> {len(messages)}</p>",
            "</div>",
            "<div class='conversation'>"
        ]

        # Add messages
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Extract text from content
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                content = "\n".join(text_parts)

            content_html = html.escape(str(content)).replace("\n", "<br>")

            html_parts.append(f"<div class='message {role}'>")
            html_parts.append(f"<div class='role'>{role.title()}</div>")
            html_parts.append(f"<div class='content'>{content_html}</div>")
            html_parts.append("</div>")

        html_parts.extend([
            "</div>",
            "</body>",
            "</html>"
        ])

        return "\n".join(html_parts).encode("utf-8")

    def _get_css(self) -> str:
        """Get CSS styling"""
        return """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        max-width: 800px;
        margin: 40px auto;
        padding: 20px;
        line-height: 1.6;
        color: #333;
    }
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }
    .metadata {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
    .conversation {
        margin-top: 30px;
    }
    .message {
        margin: 20px 0;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ddd;
    }
    .message.user {
        background: #e3f2fd;
        border-left-color: #2196f3;
    }
    .message.assistant {
        background: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .role {
        font-weight: bold;
        margin-bottom: 8px;
        color: #555;
    }
    .content {
        white-space: pre-wrap;
        word-wrap: break-word;
    }
</style>
"""


class TXTExporter(BaseExporter):
    """Export to plain text format"""

    def export(self, conversation: Dict[str, Any], options: Dict[str, Any]) -> bytes:
        """Export to plain text"""
        lines = []

        # Title and metadata
        title = conversation.get("title", "Untitled Conversation")
        lines.append(title)
        lines.append("=" * len(title))
        lines.append("")

        created_at = conversation.get("created_at", "Unknown")
        lines.append(f"Created: {created_at}")

        messages = conversation.get("messages", [])
        lines.append(f"Messages: {len(messages)}")
        lines.append("")
        lines.append("-" * 80)
        lines.append("")

        # Messages
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Extract text from content
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                content = "\n".join(text_parts)

            lines.append(f"{role.upper()}:")
            lines.append(str(content))
            lines.append("")

        return "\n".join(lines).encode("utf-8")


class PDFExporter(BaseExporter):
    """Export to PDF format (requires reportlab)"""

    def __init__(self):
        """Initialize PDF exporter"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            self.available = True
        except ImportError:
            self.available = False
            raise ImportError("reportlab required for PDF export")

    def export(self, conversation: Dict[str, Any], options: Dict[str, Any]) -> bytes:
        """Export to PDF"""
        if not self.available:
            raise RuntimeError("PDF export not available")

        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from io import BytesIO

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title = conversation.get("title", "Untitled Conversation")
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 12))

        # Metadata
        created_at = conversation.get("created_at", "Unknown")
        story.append(Paragraph(f"Created: {created_at}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Messages
        messages = conversation.get("messages", [])
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Extract text
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                content = "\n".join(text_parts)

            story.append(Paragraph(f"<b>{role.title()}:</b>", styles['Heading2']))
            story.append(Paragraph(str(content), styles['Normal']))
            story.append(Spacer(1, 12))

        doc.build(story)
        return buffer.getvalue()
