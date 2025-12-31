# Phase 7-8 Quickstart: Error Handling & Rate Limiting

Quick reference for using the Phase 7-8 error handling and rate limiting features.

---

## Testing

Run the comprehensive test suite:

```bash
venv/bin/python test_phase7-8.py
```

Expected: All 15 tests pass ✅

---

## Features at a Glance

### 1. Automatic Error Recovery

Errors are automatically classified and handled:

| Error Type | Behavior | Examples |
|------------|----------|----------|
| **Retryable** | Auto-retry with backoff | Rate limits, 5xx errors, network issues |
| **User-Fixable** | Show guidance | Invalid API key, bad request |
| **Fatal** | Stop and report | Code bugs, critical issues |

### 2. Rate Limiting

Stays within API limits automatically:
- 50 requests/minute
- 40,000 input tokens/minute
- 8,000 output tokens/minute

### 3. Cost Tracking

Real-time cost calculation:
- Session costs
- Per-model breakdown
- Token usage statistics

---

## Quick Examples

### Check Usage Statistics

```python
# In the sidebar, expand "Rate Limits & Costs"
# View:
# - Request count vs limit
# - Token usage vs limits
# - Session cost
# - Progress bars for all metrics
```

### Error Handling (Automatic)

Just use the app normally. Errors are handled automatically:
- **Transient errors** → Auto-retry with exponential backoff
- **User errors** → Clear message with guidance
- **Fatal errors** → Stop with detailed error info

### View Error Messages

When an error occurs, you'll see:
```
❌ [Error Title]

[User-friendly explanation]

What to do: [Actionable guidance]
```

---

## Configuration

### Adjust Rate Limits

Edit `core/rate_limiter.py`:

```python
class RateLimiter:
    def __init__(
        self,
        max_requests_per_min=50,        # ← Adjust this
        max_input_tokens_per_min=40000, # ← Adjust this
        max_output_tokens_per_min=8000, # ← Adjust this
        safety_margin=0.9               # ← Use 90% of limits
    ):
```

### Adjust Retry Behavior

Edit `core/api_client.py`:

```python
@retry_on_error(
    max_retries=3,      # ← Number of attempts
    base_delay=1.0,     # ← Initial backoff (seconds)
    max_delay=32.0      # ← Max backoff (seconds)
)
```

---

## UI Location

### Error Display
- **Location:** Main chat area
- **When:** Error occurs during message processing
- **Shows:** Title, explanation, actionable guidance

### Usage Display
- **Location:** Sidebar → "📊 API Usage" → "Rate Limits & Costs"
- **Shows:**
  - Request count with progress bar
  - Input token usage with progress bar
  - Output token usage with progress bar
  - Session cost (dollars)
  - Total token breakdown

---

## Troubleshooting

### Rate Limit Warnings

If you see "Rate limit approaching, waiting Xs":
- **Normal behavior** - Automatic throttling to prevent hitting limits
- **Action:** Wait briefly, then continue
- **Tip:** Reduce request frequency or use Haiku model (cheaper/faster)

### Authentication Errors

If you see "Invalid API Key":
1. Check `.env` file has correct `ANTHROPIC_API_KEY`
2. Verify key is active at console.anthropic.com
3. Restart the app after fixing

### High Costs

If session costs are higher than expected:
1. Check which model you're using (Opus > Sonnet > Haiku)
2. View breakdown in "Rate Limits & Costs" expander
3. Consider switching to Haiku for simple queries
4. Clear conversation history to reduce context size

---

## Model Pricing Reference

| Model | Input (per 1M) | Output (per 1M) | Best For |
|-------|----------------|-----------------|----------|
| **Opus 4.5** | $15.00 | $75.00 | Complex reasoning |
| **Sonnet 4.5** | $3.00 | $15.00 | Balanced (default) |
| **Sonnet 3.7** | $3.00 | $15.00 | Balanced |
| **Haiku 3.5** | $0.25 | $1.25 | Simple queries |

---

## Testing Individual Components

### Test Error Classes

```bash
venv/bin/python -c "
from core.errors import RetryableError, UserFixableError, FatalError

# Create errors
retryable = RetryableError('Test', retry_after=5.0)
fixable = UserFixableError('Test', help_text='Fix this')
fatal = FatalError('Test')

print('✅ Error classes work')
"
```

### Test Rate Limiter

```bash
venv/bin/python -c "
from core.rate_limiter import RateLimiter

limiter = RateLimiter()
can_proceed, wait_time = limiter.can_make_request()
print(f'Can proceed: {can_proceed}, Wait: {wait_time}s')

limiter.record_request(100, 50)
stats = limiter.get_usage_stats()
print(f'Requests: {stats[\"requests\"]}, Tokens: {stats[\"input_tokens\"]}')
print('✅ Rate limiter works')
"
```

### Test Cost Tracker

```bash
venv/bin/python -c "
from core.cost_tracker import CostTracker

tracker = CostTracker()
tracker.record_usage('claude-sonnet-4-5', 1000, 500)

stats = tracker.get_session_stats()
print(f'Cost: \${stats[\"cost\"]:.6f}')
print(f'Tokens: {stats[\"total_tokens\"]}')
print('✅ Cost tracker works')
"
```

### Test Token Counter

```bash
venv/bin/python -c "
from core.token_counter import count_tokens

messages = [
    {'role': 'user', 'content': 'Hello, world!'}
]

result = count_tokens(messages)
print(f'Estimated tokens: {result[\"total_tokens\"]}')
print('✅ Token counter works')
"
```

---

## Key Files

| File | Purpose |
|------|---------|
| `core/errors.py` | Custom error classes |
| `core/retry_handler.py` | Retry logic with backoff |
| `core/error_messages.py` | User-friendly error messages |
| `core/rate_limiter.py` | Rate limiting with sliding window |
| `core/token_counter.py` | Token usage estimation |
| `core/cost_tracker.py` | Cost calculation and tracking |
| `core/api_client.py` | Integrated API client |
| `test_phase7-8.py` | Test suite |

---

## Advanced Usage

### Custom Error Messages

Add custom messages in `core/error_messages.py`:

```python
ERROR_MESSAGES["custom_error"] = {
    "title": "Custom Error",
    "message": "Description",
    "action": "What to do",
    "severity": "error"  # error, warning, info
}
```

### Custom Retry Callback

```python
def my_callback(attempt, max_retries, error, delay):
    print(f"Retry {attempt}/{max_retries} after {delay}s")

@retry_on_error(retry_callback=my_callback)
def my_function():
    # ...
```

### Reset Statistics

```python
# Reset session stats (keeps total)
client.rate_limiter.reset_window()
client.cost_tracker.reset_session()

# Reset everything
client.cost_tracker.reset_all()
```

---

## What's Next?

Phase 7-8 is complete! Consider:

- **Phase 9:** Context Management
- **Phase 10:** Agent Tools UI
- **Phase 11:** Streaming Improvements
- **Phase 12:** Export/Import

---

## Support

- **Tests failing?** Check that `venv` has all dependencies installed
- **API errors?** Verify API key in `.env`
- **High costs?** Switch to Haiku model for testing
- **Rate limits?** Wait briefly or increase `safety_margin` in config

---

🎉 **Phase 7-8 Complete!** Production-ready error handling and rate limiting.
