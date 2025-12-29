"""
Cost Tracker for Claude API

Tracks token usage and calculates costs based on Claude's pricing.

Pricing (as of December 2024):
- Claude Opus 4.5: $15/$75 per 1M input/output tokens
- Claude Sonnet 4.5: $3/$15 per 1M input/output tokens
- Claude Sonnet 3.7: $3/$15 per 1M input/output tokens
- Claude Haiku 3.5: $0.25/$1.25 per 1M input/output tokens
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


# Pricing per 1M tokens (input, output)
MODEL_PRICING = {
    "claude-opus-4-5": (15.00, 75.00),
    "claude-sonnet-4-5": (3.00, 15.00),
    "claude-sonnet-3-7": (3.00, 15.00),
    "claude-haiku-3-5": (0.25, 1.25),
}

# Cache pricing multipliers (Phase 14)
# Format: (cache_write_multiplier, cache_read_multiplier)
# Cache write = base_price * 1.25 (+25%)
# Cache read = base_price * 0.10 (-90%)
CACHE_PRICING = {
    "claude-opus-4-5": (1.25, 0.10),
    "claude-sonnet-4-5": (1.25, 0.10),
    "claude-sonnet-3-7": (1.25, 0.10),
    "claude-haiku-3-5": (1.25, 0.10),
}

# Fallback pricing if model not found
DEFAULT_PRICING = (3.00, 15.00)  # Sonnet pricing
DEFAULT_CACHE_PRICING = (1.25, 0.10)  # Standard cache multipliers


@dataclass
class UsageRecord:
    """Record of token usage for a single request"""
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    # Phase 14: Cache tokens
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_cost: float = 0.0
    cache_read_cost: float = 0.0


class CostTracker:
    """
    Tracks token usage and calculates costs.

    Maintains session and total statistics.
    """

    def __init__(self):
        """Initialize cost tracker"""
        # Session stats (reset when app restarts)
        self.session_input_tokens = 0
        self.session_output_tokens = 0
        self.session_cost = 0.0

        # Phase 14: Cache stats
        self.session_cache_creation_tokens = 0
        self.session_cache_read_tokens = 0
        self.session_cache_write_cost = 0.0
        self.session_cache_read_cost = 0.0

        # Total stats (cumulative, can be persisted)
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

        # Phase 14: Total cache stats
        self.total_cache_creation_tokens = 0
        self.total_cache_read_tokens = 0
        self.total_cache_write_cost = 0.0
        self.total_cache_read_cost = 0.0

        # Request history
        self.history: list[UsageRecord] = []

        logger.info("Cost tracker initialized")

    def get_model_pricing(self, model: str) -> tuple[float, float]:
        """
        Get pricing for a model.

        Args:
            model: Model ID (e.g., 'claude-sonnet-4-5')

        Returns:
            Tuple of (input_price_per_1m, output_price_per_1m)
        """
        # Normalize model name
        model_key = model.lower()

        # Try exact match
        if model_key in MODEL_PRICING:
            return MODEL_PRICING[model_key]

        # Try partial match
        for key in MODEL_PRICING:
            if key in model_key:
                return MODEL_PRICING[key]

        # Fallback to default
        logger.warning(f"Unknown model '{model}', using default pricing")
        return DEFAULT_PRICING

    def get_cache_pricing(self, model: str) -> tuple[float, float]:
        """
        Get cache pricing multipliers for a model (Phase 14).

        Args:
            model: Model ID (e.g., 'claude-sonnet-4-5')

        Returns:
            Tuple of (write_multiplier, read_multiplier)
        """
        # Normalize model name
        model_key = model.lower()

        # Try exact match
        if model_key in CACHE_PRICING:
            return CACHE_PRICING[model_key]

        # Try partial match
        for key in CACHE_PRICING:
            if key in model_key:
                return CACHE_PRICING[key]

        # Fallback to default
        return DEFAULT_CACHE_PRICING

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> Dict[str, float]:
        """
        Calculate cost for a request.

        Args:
            model: Model ID
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Dictionary with cost breakdown
        """
        input_price, output_price = self.get_model_pricing(model)

        # Calculate costs (price is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * input_price
        output_cost = (output_tokens / 1_000_000) * output_price
        total_cost = input_cost + output_cost

        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost
        }

    def calculate_cache_cost(
        self,
        model: str,
        cache_creation_tokens: int,
        cache_read_tokens: int
    ) -> Dict[str, float]:
        """
        Calculate cache-specific costs (Phase 14).

        Args:
            model: Model ID
            cache_creation_tokens: Tokens written to cache
            cache_read_tokens: Tokens read from cache

        Returns:
            Dictionary with cache cost breakdown
        """
        if cache_creation_tokens == 0 and cache_read_tokens == 0:
            return {
                "cache_write_cost": 0.0,
                "cache_read_cost": 0.0,
                "total_cache_cost": 0.0
            }

        # Get base input price and cache multipliers
        base_input_price, _ = self.get_model_pricing(model)
        write_mult, read_mult = self.get_cache_pricing(model)

        # Calculate cache costs
        # Cache write: base_price * 1.25 (+25%)
        cache_write_cost = (cache_creation_tokens / 1_000_000) * (base_input_price * write_mult)

        # Cache read: base_price * 0.10 (-90%)
        cache_read_cost = (cache_read_tokens / 1_000_000) * (base_input_price * read_mult)

        return {
            "cache_write_cost": cache_write_cost,
            "cache_read_cost": cache_read_cost,
            "total_cache_cost": cache_write_cost + cache_read_cost
        }

    def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cache_creation_tokens: int = 0,
        cache_read_tokens: int = 0
    ):
        """
        Record token usage and calculate cost (Phase 14: includes cache tokens).

        Args:
            model: Model ID
            input_tokens: Number of input tokens used (includes cache tokens)
            output_tokens: Number of output tokens generated
            cache_creation_tokens: Tokens written to cache (Phase 14)
            cache_read_tokens: Tokens read from cache (Phase 14)
        """
        # Calculate base costs (excluding cache tokens from input)
        regular_input_tokens = input_tokens - cache_creation_tokens - cache_read_tokens
        costs = self.calculate_cost(model, regular_input_tokens, output_tokens)

        # Calculate cache costs (Phase 14)
        cache_costs = self.calculate_cache_cost(model, cache_creation_tokens, cache_read_tokens)

        # Total cost includes both regular and cache costs
        total_cost = costs["total_cost"] + cache_costs["total_cache_cost"]

        # Update session stats
        self.session_input_tokens += input_tokens
        self.session_output_tokens += output_tokens
        self.session_cost += total_cost

        # Phase 14: Update cache stats
        self.session_cache_creation_tokens += cache_creation_tokens
        self.session_cache_read_tokens += cache_read_tokens
        self.session_cache_write_cost += cache_costs["cache_write_cost"]
        self.session_cache_read_cost += cache_costs["cache_read_cost"]

        # Update total stats
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += total_cost

        # Phase 14: Update total cache stats
        self.total_cache_creation_tokens += cache_creation_tokens
        self.total_cache_read_tokens += cache_read_tokens
        self.total_cache_write_cost += cache_costs["cache_write_cost"]
        self.total_cache_read_cost += cache_costs["cache_read_cost"]

        # Create record
        record = UsageRecord(
            timestamp=datetime.now(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=costs["input_cost"],
            output_cost=costs["output_cost"],
            total_cost=total_cost,
            cache_creation_tokens=cache_creation_tokens,
            cache_read_tokens=cache_read_tokens,
            cache_write_cost=cache_costs["cache_write_cost"],
            cache_read_cost=cache_costs["cache_read_cost"]
        )
        self.history.append(record)

        # Enhanced logging with cache info
        if cache_creation_tokens > 0 or cache_read_tokens > 0:
            logger.debug(
                f"Recorded usage: {regular_input_tokens} regular + "
                f"{cache_creation_tokens} cache_write + {cache_read_tokens} cache_read + "
                f"{output_tokens} out = ${total_cost:.6f} "
                f"(cache savings: ${cache_costs['cache_write_cost'] + cache_costs['cache_read_cost']:.6f})"
            )
        else:
            logger.debug(
                f"Recorded usage: {input_tokens} in + {output_tokens} out "
                f"= ${total_cost:.6f}"
            )

    def get_session_stats(self) -> Dict[str, any]:
        """
        Get statistics for the current session.

        Returns:
            Dictionary with session stats
        """
        return {
            "input_tokens": self.session_input_tokens,
            "output_tokens": self.session_output_tokens,
            "total_tokens": self.session_input_tokens + self.session_output_tokens,
            "cost": self.session_cost,
            "request_count": len(self.history)
        }

    def get_total_stats(self) -> Dict[str, any]:
        """
        Get cumulative statistics.

        Returns:
            Dictionary with total stats
        """
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "cost": self.total_cost,
            "request_count": len(self.history)
        }

    def get_cost_breakdown_by_model(self) -> Dict[str, Dict[str, any]]:
        """
        Get cost breakdown by model.

        Returns:
            Dictionary mapping model to usage stats
        """
        breakdown = {}

        for record in self.history:
            model = record.model
            if model not in breakdown:
                breakdown[model] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost": 0.0,
                    "request_count": 0
                }

            breakdown[model]["input_tokens"] += record.input_tokens
            breakdown[model]["output_tokens"] += record.output_tokens
            breakdown[model]["cost"] += record.total_cost
            breakdown[model]["request_count"] += 1

        return breakdown

    def reset_session(self):
        """Reset session statistics (keeps total)"""
        self.session_input_tokens = 0
        self.session_output_tokens = 0
        self.session_cost = 0.0

        # Phase 14: Reset cache stats
        self.session_cache_creation_tokens = 0
        self.session_cache_read_tokens = 0
        self.session_cache_write_cost = 0.0
        self.session_cache_read_cost = 0.0

        self.history = []
        logger.info("Session stats reset")

    def reset_all(self):
        """Reset all statistics"""
        self.reset_session()
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

        # Phase 14: Reset total cache stats
        self.total_cache_creation_tokens = 0
        self.total_cache_read_tokens = 0
        self.total_cache_write_cost = 0.0
        self.total_cache_read_cost = 0.0

        logger.info("All stats reset")
