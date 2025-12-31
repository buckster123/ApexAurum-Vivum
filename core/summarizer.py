"""
Conversation Summarizer for Context Management

Summarizes conversation segments to compress context while preserving
key information, decisions, and technical details.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConversationSummarizer:
    """
    Summarizes conversation segments to reduce token usage.

    Uses Claude API to generate intelligent summaries that preserve
    important information while significantly reducing token count.
    """

    def __init__(self, client=None):
        """
        Initialize conversation summarizer

        Args:
            client: ClaudeAPIClient instance (optional, for actual API calls)
        """
        self.client = client

        # Summarization prompts for different strategies
        self.prompts = {
            "aggressive": (
                "Summarize this conversation segment in 1-2 sentences. "
                "Include only the most critical facts and decisions. "
                "Be extremely concise."
            ),
            "balanced": (
                "Summarize this conversation segment in 2-4 sentences. "
                "Preserve key facts, decisions, and technical details. "
                "Be concise but informative."
            ),
            "conservative": (
                "Summarize this conversation segment in a detailed paragraph. "
                "Preserve all important facts, decisions, code snippets, and technical context. "
                "Maintain enough detail for future reference."
            )
        }

        logger.info("Conversation summarizer initialized")

    def summarize_messages(
        self,
        messages: List[Dict[str, Any]],
        strategy: str = "balanced"
    ) -> str:
        """
        Summarize a list of messages into concise text

        Args:
            messages: List of message dicts to summarize
            strategy: Summarization strategy
                - "aggressive": Very brief (50-100 tokens)
                - "balanced": Moderate (100-300 tokens)
                - "conservative": Detailed (300-500 tokens)

        Returns:
            Summary text
        """
        if not messages:
            return ""

        # Build conversation text
        conversation_text = self._format_messages_for_summary(messages)

        # Get strategy prompt
        strategy_prompt = self.prompts.get(strategy, self.prompts["balanced"])

        # If client available, use API to generate summary
        if self.client:
            try:
                summary = self._generate_summary_with_api(
                    conversation_text,
                    strategy_prompt
                )
                logger.info(
                    f"Summarized {len(messages)} messages using {strategy} strategy "
                    f"(API call)"
                )
                return summary
            except Exception as e:
                logger.warning(f"API summarization failed: {e}, using fallback")
                # Fall through to fallback

        # Fallback: Simple rule-based summary
        summary = self._generate_summary_fallback(messages, strategy)
        logger.info(
            f"Summarized {len(messages)} messages using {strategy} strategy "
            f"(fallback method)"
        )
        return summary

    def _format_messages_for_summary(
        self,
        messages: List[Dict[str, Any]]
    ) -> str:
        """
        Format messages into readable text for summarization

        Args:
            messages: List of messages

        Returns:
            Formatted conversation text
        """
        lines = []

        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Handle array content (text + images)
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif isinstance(item, dict) and item.get("type") == "image":
                        text_parts.append("[Image]")
                content = " ".join(text_parts)

            # Truncate very long messages
            if len(content) > 500:
                content = content[:500] + "..."

            lines.append(f"{role.capitalize()}: {content}")

        return "\n".join(lines)

    def _generate_summary_with_api(
        self,
        conversation_text: str,
        strategy_prompt: str
    ) -> str:
        """
        Generate summary using Claude API

        Args:
            conversation_text: Formatted conversation
            strategy_prompt: Summarization instructions

        Returns:
            Generated summary
        """
        # Use Haiku model for cost-effective summarization
        response = self.client.simple_message(
            prompt=f"{strategy_prompt}\n\nConversation:\n{conversation_text}",
            model="claude-3-5-haiku-20241022",
            max_tokens=500
        )

        return response.strip()

    def _generate_summary_fallback(
        self,
        messages: List[Dict[str, Any]],
        strategy: str
    ) -> str:
        """
        Generate summary using rule-based fallback

        Args:
            messages: List of messages
            strategy: Summarization strategy

        Returns:
            Rule-based summary
        """
        # Count message types
        user_messages = sum(1 for m in messages if m.get("role") == "user")
        assistant_messages = sum(1 for m in messages if m.get("role") == "assistant")

        # Look for key indicators
        has_code = any(
            "```" in str(m.get("content", ""))
            for m in messages
        )
        has_error = any(
            "error" in str(m.get("content", "")).lower()
            for m in messages
        )

        # Build summary based on strategy
        if strategy == "aggressive":
            summary = (
                f"Discussion with {user_messages} user messages and "
                f"{assistant_messages} responses."
            )
        elif strategy == "conservative":
            summary = (
                f"Conversation segment containing {user_messages} user questions/requests "
                f"and {assistant_messages} assistant responses. "
            )
            if has_code:
                summary += "Included code examples and implementations. "
            if has_error:
                summary += "Discussed errors and troubleshooting. "
        else:  # balanced
            summary = (
                f"Exchanged {user_messages} messages discussing various topics. "
            )
            if has_code:
                summary += "Included code. "

        return summary

    def identify_important_messages(
        self,
        messages: List[Dict[str, Any]],
        bookmarked_indices: Optional[set] = None
    ) -> List[int]:
        """
        Identify message indices that should not be summarized

        Args:
            messages: List of messages
            bookmarked_indices: Set of user-bookmarked message indices

        Returns:
            List of message indices to preserve
        """
        important_indices = []

        if bookmarked_indices is None:
            bookmarked_indices = set()

        for index, message in enumerate(messages):
            # Always preserve bookmarked messages
            if index in bookmarked_indices:
                important_indices.append(index)
                continue

            content = str(message.get("content", ""))

            # Preserve messages with code blocks
            if "```" in content:
                important_indices.append(index)
                continue

            # Preserve error messages (from both user and assistant)
            if "error" in content.lower():
                important_indices.append(index)
                continue

            # Preserve user directives (often important decisions)
            if message.get("role") == "user" and len(content) > 100:
                # Longer user messages often contain important instructions
                important_indices.append(index)
                continue

        logger.debug(
            f"Identified {len(important_indices)} important messages "
            f"out of {len(messages)}"
        )

        return important_indices

    def create_summary_message(
        self,
        summary_text: str,
        original_count: int,
        token_savings: int = 0
    ) -> Dict[str, Any]:
        """
        Create a summary message block

        Args:
            summary_text: The summary content
            original_count: Number of original messages summarized
            token_savings: Estimated tokens saved (optional)

        Returns:
            Message dict in Claude format
        """
        content = f"📝 Summary of {original_count} previous messages:\n\n{summary_text}"

        if token_savings > 0:
            content += f"\n\n(Saved ~{token_savings:,} tokens)"

        return {
            "role": "assistant",
            "content": content
        }

    def should_preserve_message(
        self,
        message: Dict[str, Any],
        index: int,
        bookmarked_indices: Optional[set] = None
    ) -> bool:
        """
        Check if a single message should be preserved

        Args:
            message: Message dict
            index: Message index
            bookmarked_indices: Set of bookmarked indices

        Returns:
            True if message should not be summarized
        """
        if bookmarked_indices and index in bookmarked_indices:
            return True

        content = str(message.get("content", ""))

        # Preserve code
        if "```" in content:
            return True

        # Preserve errors
        if "error" in content.lower():
            return True

        # Preserve long user messages
        if message.get("role") == "user" and len(content) > 100:
            return True

        return False
