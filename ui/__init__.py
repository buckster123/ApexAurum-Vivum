"""
UI Components Module

Provides Streamlit UI components for the application.
"""

from .streaming_display import (
    StreamingTextDisplay,
    ToolExecutionDisplay,
    StatusIndicator,
    StreamingProgressBar,
    format_tool_for_display,
    create_streaming_container,
    estimate_completion_time,
)

from .keyboard_shortcuts import (
    QUICK_REFERENCE,
    render_cheat_sheet,
)

__all__ = [
    # Streaming display
    "StreamingTextDisplay",
    "ToolExecutionDisplay",
    "StatusIndicator",
    "StreamingProgressBar",
    "format_tool_for_display",
    "create_streaming_container",
    "estimate_completion_time",
    # Quick reference
    "QUICK_REFERENCE",
    "render_cheat_sheet",
]
