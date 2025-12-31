"""
Context Tracker for Claude API

Tracks token usage across conversation context to enable intelligent
context management and prevent hitting token limits.

Model Context Limits:
- Claude Opus 4.5: 200,000 tokens
- Claude Sonnet 4.5: 200,000 tokens
- Claude Sonnet 3.7: 200,000 tokens
- Claude Haiku 3.5: 200,000 tokens
"""

import logging
from typing import List, Dict, Any, Optional
from .token_counter import count_tokens, estimate_message_tokens

logger = logging.getLogger(__name__)


# Model context limits (in tokens)
MODEL_CONTEXT_LIMITS = {
    "claude-opus-4-5": 200000,
    "claude-sonnet-4-5": 200000,
    "claude-sonnet-3-7": 200000,
    "claude-3-7-sonnet": 200000,
    "claude-haiku-3-5": 200000,
    "claude-3-5-haiku": 200000,
}

DEFAULT_CONTEXT_LIMIT = 200000  # Default for unknown models


class ContextTracker:
    """
    Tracks token usage in conversation context.

    Monitors total tokens across messages, system prompt, and tools
    to enable intelligent context management.
    """

    def __init__(self, model: str):
        """
        Initialize context tracker

        Args:
            model: Model ID (e.g., 'claude-sonnet-4-5')
        """
        self.model = model
        self.max_tokens = self.get_model_context_limit()

        logger.info(f"Context tracker initialized for {model} (limit: {self.max_tokens:,} tokens)")

    def get_model_context_limit(self) -> int:
        """
        Get maximum context tokens for model

        Returns:
            Maximum context window size in tokens
        """
        # Normalize model name
        model_key = self.model.lower()

        # Try exact match
        if model_key in MODEL_CONTEXT_LIMITS:
            return MODEL_CONTEXT_LIMITS[model_key]

        # Try partial match
        for key in MODEL_CONTEXT_LIMITS:
            if key in model_key:
                return MODEL_CONTEXT_LIMITS[key]

        # Fallback to default
        logger.warning(f"Unknown model '{self.model}', using default context limit")
        return DEFAULT_CONTEXT_LIMIT

    def calculate_total_context(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculate total tokens in context

        Args:
            messages: Conversation messages
            system: System prompt (optional)
            tools: Tool schemas (optional)

        Returns:
            Dictionary with token statistics:
            - messages_tokens: Tokens in messages
            - system_tokens: Tokens in system prompt
            - tools_tokens: Tokens in tool schemas
            - total_tokens: Total tokens
            - max_tokens: Maximum allowed tokens
            - usage_percent: Percentage of context used
            - remaining_tokens: Tokens remaining
        """
        # Count tokens
        token_count = count_tokens(messages, system, tools, self.model)

        # Calculate messages tokens (input_tokens includes everything)
        messages_tokens = token_count["input_tokens"]

        # Estimate system and tools separately for breakdown
        system_tokens = 0
        if system:
            from .token_counter import estimate_text_tokens
            system_tokens = estimate_text_tokens(system)

        tools_tokens = 0
        if tools:
            from .token_counter import estimate_tool_tokens
            tools_tokens = estimate_tool_tokens(tools)

        # Adjust messages tokens (remove system and tools)
        messages_only_tokens = messages_tokens - system_tokens - tools_tokens

        total_tokens = messages_tokens
        usage_percent = (total_tokens / self.max_tokens) * 100
        remaining_tokens = self.max_tokens - total_tokens

        return {
            "messages_tokens": messages_only_tokens,
            "system_tokens": system_tokens,
            "tools_tokens": tools_tokens,
            "total_tokens": total_tokens,
            "max_tokens": self.max_tokens,
            "usage_percent": usage_percent,
            "remaining_tokens": remaining_tokens
        }

    def get_message_token_breakdown(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get token count for each message

        Args:
            messages: List of conversation messages

        Returns:
            List of dicts with per-message token counts:
            [
                {"index": 0, "role": "user", "tokens": 50},
                {"index": 1, "role": "assistant", "tokens": 200},
                ...
            ]
        """
        breakdown = []

        for index, message in enumerate(messages):
            tokens = estimate_message_tokens(message)

            breakdown.append({
                "index": index,
                "role": message.get("role", "unknown"),
                "tokens": tokens
            })

        return breakdown

    def should_summarize(
        self,
        total_tokens: int,
        threshold_percent: float = 0.7
    ) -> bool:
        """
        Check if context should be summarized

        Args:
            total_tokens: Current total token count
            threshold_percent: Threshold percentage (0.0-1.0)
                0.5 = 50%, 0.7 = 70%, 0.85 = 85%

        Returns:
            True if total_tokens exceeds threshold
        """
        threshold_tokens = self.max_tokens * threshold_percent
        should_summarize = total_tokens >= threshold_tokens

        if should_summarize:
            logger.info(
                f"Context threshold reached: {total_tokens:,} >= "
                f"{threshold_tokens:,.0f} ({threshold_percent*100}%)"
            )

        return should_summarize

    def get_context_summary(
        self,
        messages: List[Dict[str, Any]],
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        Get human-readable context summary

        Args:
            messages: Conversation messages
            system: System prompt (optional)
            tools: Tool schemas (optional)

        Returns:
            Formatted string with context statistics
        """
        stats = self.calculate_total_context(messages, system, tools)

        summary = (
            f"Context: {stats['total_tokens']:,}/{stats['max_tokens']:,} tokens "
            f"({stats['usage_percent']:.1f}%)\n"
            f"  Messages: {stats['messages_tokens']:,} tokens\n"
            f"  System: {stats['system_tokens']:,} tokens\n"
            f"  Tools: {stats['tools_tokens']:,} tokens\n"
            f"  Remaining: {stats['remaining_tokens']:,} tokens"
        )

        return summary
