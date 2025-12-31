# Phase 7-8 Implementation Plan: Error Handling & Rate Limiting 🛡️⏱️

## Overview

**Goal**: Enhance error handling with retry logic, implement rate limiting, and provide better user feedback for API issues.

**Complexity**: Medium
**Estimated Time**: 3-4 hours
**Priority**: Medium-High

---

## Current State

### What we have:
- ✅ Basic error catching (AuthenticationError, RateLimitError, APIError)
- ✅ Logging for errors
- ✅ Simple error re-raising to UI

### What's missing:
- ❌ Automatic retry logic with exponential backoff
- ❌ Rate limit tracking and prevention
- ❌ Token usage tracking
- ❌ User-friendly error messages
- ❌ Rate limit status display in UI
- ❌ Graceful degradation strategies
- ❌ Overloaded error handling (Claude-specific)

---

## Phase 7: Enhanced Error Handling

### Problem Statement

**Current issues**:
1. Errors immediately crash the conversation
2. No retry logic for transient failures
3. Technical error messages confuse users
4. No handling for Claude-specific errors (overloaded_error)
5. No exponential backoff for rate limits

### Solution Design

**Error Categories**:

1. **Retryable Errors** (auto-retry with backoff)
   - `RateLimitError` - Too many requests
   - `OverloadedError` - Claude servers busy
   - `APIStatusError` (500-599) - Server errors
   - `APIConnectionError` - Network issues

2. **User-Fixable Errors** (show helpful message)
   - `AuthenticationError` - Invalid API key
   - `PermissionDeniedError` - Insufficient permissions
   - `InvalidRequestError` - Malformed request
   - `NotFoundError` - Invalid model/endpoint

3. **Fatal Errors** (stop immediately)
   - Unexpected exceptions
   - Timeout errors (after retries)

---

### Implementation Tasks

#### **Task 1: Enhanced Error Classes**

**Location**: `core/errors.py` (new file)

**Create custom error classes**:
```python
class ApexAurumError(Exception):
    """Base exception for Apex Aurum"""
    pass

class RetryableError(ApexAurumError):
    """Error that should be retried"""
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after

class UserFixableError(ApexAurumError):
    """Error that user can fix"""
    def __init__(self, message, help_text=None):
        super().__init__(message)
        self.help_text = help_text

class FatalError(ApexAurumError):
    """Fatal error, cannot continue"""
    pass
```

---

#### **Task 2: Retry Logic Decorator**

**Location**: `core/retry_handler.py` (new file)

**Features**:
- Exponential backoff (1s, 2s, 4s, 8s, 16s)
- Maximum retries (default: 3)
- Jitter to prevent thundering herd
- Retry-After header respect
- Logging of retry attempts

**Example**:
```python
@retry_on_error(max_retries=3, base_delay=1.0)
def call_claude_api(...):
    # API call here
    pass
```

---

#### **Task 3: Error Message Translator**

**Location**: `core/error_messages.py` (new file)

**Convert technical errors to user-friendly messages**:

```python
ERROR_MESSAGES = {
    "authentication_error": {
        "title": "🔑 Authentication Failed",
        "message": "Your API key is invalid or expired.",
        "action": "Please check your ANTHROPIC_API_KEY in .env file."
    },
    "rate_limit_error": {
        "title": "⏱️ Rate Limit Reached",
        "message": "Too many requests. Please wait a moment.",
        "action": "Retrying automatically..."
    },
    "overloaded_error": {
        "title": "🚦 Claude is Busy",
        "message": "Claude's servers are experiencing high load.",
        "action": "Retrying in a few seconds..."
    },
    # ... more messages
}
```

---

#### **Task 4: Update API Client**

**Location**: `core/api_client.py`

**Changes**:
1. Add retry decorator to `create_message()`
2. Catch and classify errors
3. Extract retry-after from headers
4. Return user-friendly errors
5. Add timeout configuration
6. Log detailed error context

**Pseudocode**:
```python
@retry_on_error(max_retries=3)
def create_message(self, ...):
    try:
        response = self.client.messages.create(...)
        return response
    except anthropic.RateLimitError as e:
        # Extract retry_after from headers
        retry_after = extract_retry_after(e)
        raise RetryableError("Rate limit hit", retry_after)
    except anthropic.OverloadedError as e:
        raise RetryableError("Claude overloaded")
    except anthropic.AuthenticationError as e:
        raise UserFixableError(
            "Invalid API key",
            "Check ANTHROPIC_API_KEY in .env"
        )
    # ... more error handling
```

---

#### **Task 5: UI Error Display**

**Location**: `main.py` - `process_message()`

**Changes**:
1. Catch custom error types
2. Display user-friendly messages
3. Show retry progress
4. Offer actions (retry manually, check settings)

**UI Mockup**:
```
┌─────────────────────────────────────┐
│ ⏱️ Rate Limit Reached              │
│                                     │
│ Too many requests. Please wait.    │
│                                     │
│ Retrying in 3 seconds...           │
│ [⚪⚪⚪⚪⚪] Attempt 2/3              │
└─────────────────────────────────────┘
```

---

## Phase 8: Rate Limiting

### Problem Statement

**Current issues**:
1. No awareness of rate limits
2. Can't prevent hitting limits
3. No token usage tracking
4. No visual feedback on usage
5. Users don't know when they're close to limits

### Solution Design

**Claude API Rate Limits** (Tier 1):
- **Requests**: 50 per minute
- **Input tokens**: 40,000 per minute
- **Output tokens**: 8,000 per minute

**Strategy**:
1. Track requests and tokens per minute
2. Implement sliding window counter
3. Add pre-emptive throttling
4. Display usage in UI
5. Queue requests when near limit

---

### Implementation Tasks

#### **Task 6: Rate Limiter Class**

**Location**: `core/rate_limiter.py` (new file)

**Features**:
- Sliding window tracking (last 60 seconds)
- Token counting (estimate before API call)
- Request queuing
- Automatic throttling
- Usage statistics

**Example**:
```python
class RateLimiter:
    def __init__(self,
                 max_requests_per_min=50,
                 max_input_tokens_per_min=40000,
                 max_output_tokens_per_min=8000):
        self.request_history = []
        self.token_history = []
        # ... initialization

    def can_make_request(self, estimated_tokens=0):
        """Check if request would exceed limits"""
        # Check request count
        # Check token count
        # Return (can_proceed, wait_time)

    def record_request(self, input_tokens, output_tokens):
        """Record a completed request"""
        # Add to history with timestamp

    def get_usage_stats(self):
        """Get current usage statistics"""
        # Return dict with current usage
```

---

#### **Task 7: Token Counting**

**Location**: `core/token_counter.py` (new file)

**Method**:
- Use `anthropic` SDK's token counting (if available)
- Fallback: Estimate (1 token ≈ 4 characters)
- Count text + images + tool schemas

**Example**:
```python
def count_tokens(messages, tools=None, model="claude-sonnet-4.5"):
    """
    Estimate token count for a request.

    Includes:
    - Message text
    - Image tokens (~170 per image)
    - Tool schemas (~50-200 per tool)
    """
    total = 0

    # Count message tokens
    for msg in messages:
        total += estimate_message_tokens(msg)

    # Count tool tokens
    if tools:
        total += len(tools) * 100  # ~100 tokens per tool

    return total
```

---

#### **Task 8: Integrate Rate Limiter**

**Location**: `core/api_client.py`

**Changes**:
1. Add rate_limiter instance
2. Check before API calls
3. Wait if needed
4. Record usage after calls
5. Return usage stats

**Pseudocode**:
```python
class ClaudeAPIClient:
    def __init__(self, ...):
        self.rate_limiter = RateLimiter()

    def create_message(self, ...):
        # Estimate tokens
        estimated = count_tokens(messages, tools)

        # Check rate limit
        can_proceed, wait_time = self.rate_limiter.can_make_request(estimated)

        if not can_proceed:
            logger.info(f"Rate limit approaching, waiting {wait_time}s")
            time.sleep(wait_time)

        # Make API call
        response = self.client.messages.create(...)

        # Record usage
        self.rate_limiter.record_request(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens
        )

        return response
```

---

#### **Task 9: UI Rate Limit Display**

**Location**: `main.py` - Sidebar

**Add usage display**:
```python
st.subheader("📊 API Usage")
with st.expander("Rate Limit Status", expanded=False):
    usage = st.session_state.rate_limiter.get_usage_stats()

    st.metric("Requests (this minute)",
              f"{usage['requests']}/50")
    st.progress(usage['requests'] / 50)

    st.metric("Input Tokens (this minute)",
              f"{usage['input_tokens']:,}/40,000")
    st.progress(usage['input_tokens'] / 40000)

    st.metric("Output Tokens (this minute)",
              f"{usage['output_tokens']:,}/8,000")
    st.progress(usage['output_tokens'] / 8000)
```

**UI Mockup**:
```
📊 API Usage
├── [Expand] Rate Limit Status
│
│   Requests (this minute): 12/50
│   [████░░░░░░] 24%
│
│   Input Tokens: 8,432/40,000
│   [██░░░░░░░░] 21%
│
│   Output Tokens: 1,234/8,000
│   [██░░░░░░░░] 15%
```

---

#### **Task 10: Cost Tracking (Bonus)**

**Location**: `core/cost_tracker.py` (new file)

**Features**:
- Track total tokens used
- Calculate costs per model
- Display session cost
- Display total cost

**Pricing** (as of Dec 2024):
- **Opus 4.5**: $15 input / $75 output per 1M tokens
- **Sonnet 4.5**: $3 input / $15 output per 1M tokens
- **Sonnet 3.7**: $3 input / $15 output per 1M tokens
- **Haiku 3.5**: $0.25 input / $1.25 output per 1M tokens

**UI Display**:
```python
st.caption(f"💰 Session cost: ${session_cost:.4f}")
st.caption(f"💰 Total cost: ${total_cost:.2f}")
```

---

## File Structure After Phase 7-8

```
claude-version/
├── core/
│   ├── api_client.py              # ← Modified: Retry logic, rate limiting
│   ├── errors.py                  # ← New: Custom error classes
│   ├── retry_handler.py           # ← New: Retry decorator
│   ├── error_messages.py          # ← New: User-friendly messages
│   ├── rate_limiter.py            # ← New: Rate limit tracking
│   ├── token_counter.py           # ← New: Token estimation
│   └── cost_tracker.py            # ← New: Cost tracking (bonus)
│
├── main.py                         # ← Modified: Error display, usage UI
└── tests/
    └── test_phase7-8.py           # ← New: Error & rate limit tests
```

---

## Implementation Sequence

### Order of Tasks
1. ✅ **Task 1**: Custom error classes (foundation)
2. ✅ **Task 2**: Retry logic decorator
3. ✅ **Task 3**: Error message translator
4. ✅ **Task 4**: Update API client with retries
5. ✅ **Task 5**: UI error display
6. ✅ **Task 6**: Rate limiter class
7. ✅ **Task 7**: Token counter
8. ✅ **Task 8**: Integrate rate limiter
9. ✅ **Task 9**: UI rate limit display
10. ✅ **Task 10**: Cost tracking (bonus)

**Dependencies**:
- Tasks 1-3 can be done in parallel
- Task 4 depends on 1-3
- Task 5 depends on 4
- Tasks 6-7 can be done in parallel
- Task 8 depends on 6-7
- Task 9 depends on 8
- Task 10 independent (bonus)

---

## Testing Strategy

### Error Handling Tests
```python
def test_retry_on_rate_limit():
    """Simulate rate limit, verify retry"""

def test_retry_on_overload():
    """Simulate overload error, verify retry"""

def test_no_retry_on_auth_error():
    """Auth error should not retry"""

def test_exponential_backoff():
    """Verify backoff timing"""

def test_user_friendly_messages():
    """Verify message translation"""
```

### Rate Limiting Tests
```python
def test_rate_limiter_tracking():
    """Verify request tracking"""

def test_rate_limiter_throttling():
    """Verify throttling when near limit"""

def test_token_counting():
    """Verify token estimation accuracy"""

def test_sliding_window():
    """Verify 60-second window"""

def test_usage_stats():
    """Verify usage statistics"""
```

---

## Error Handling Examples

### Example 1: Rate Limit with Retry
```
User: "Analyze this code"

System: ⏱️ Rate Limit Reached
        Too many requests. Retrying...
        [████░░] Attempt 2/3 (waiting 4s)

Claude: [responds after retry succeeds]
```

### Example 2: Authentication Error
```
User: "Hello"

System: 🔑 Authentication Failed
        Your API key is invalid or expired.

        Action: Please check ANTHROPIC_API_KEY
                in your .env file.

        [Retry] [Check Settings]
```

### Example 3: Overloaded Error
```
User: "What's 2+2?"

System: 🚦 Claude is Busy
        Servers are experiencing high load.

        Retrying automatically...
        [⚪⚪⚪⚪⚪] Attempt 1/3

Claude: [responds after retry]
```

---

## Rate Limiting Examples

### Example 1: Normal Usage
```
Sidebar:
📊 API Usage
├── Requests: 8/50 (16%)
├── Input Tokens: 2,341/40,000 (6%)
└── Output Tokens: 892/8,000 (11%)

Status: ✅ All systems normal
```

### Example 2: Approaching Limit
```
Sidebar:
📊 API Usage
├── Requests: 45/50 (90%) ⚠️
├── Input Tokens: 38,234/40,000 (96%) ⚠️
└── Output Tokens: 7,123/8,000 (89%) ⚠️

Status: ⚠️ Approaching limits
        Next request may be delayed
```

### Example 3: Limit Hit
```
System: ⏱️ Rate Limit Reached
        Waiting 15 seconds before next request...
        [████████░░] 80% complete
```

---

## Configuration

### Environment Variables
```bash
# .env additions
RATE_LIMIT_REQUESTS_PER_MIN=50
RATE_LIMIT_INPUT_TOKENS_PER_MIN=40000
RATE_LIMIT_OUTPUT_TOKENS_PER_MIN=8000
MAX_RETRIES=3
RETRY_BASE_DELAY=1.0
REQUEST_TIMEOUT=60.0
```

### Settings in UI
```python
st.subheader("🛡️ Error Handling")
with st.expander("Advanced", expanded=False):
    max_retries = st.slider("Max Retries", 0, 5, 3)
    timeout = st.slider("Timeout (seconds)", 10, 120, 60)
    enable_rate_limiting = st.checkbox("Enable Rate Limiting", True)
```

---

## Success Criteria

Phase 7-8 complete when:
- ✅ Errors automatically retry with backoff
- ✅ User-friendly error messages displayed
- ✅ Rate limits tracked and respected
- ✅ Token usage counted
- ✅ Usage displayed in UI
- ✅ Requests throttled near limits
- ✅ All tests pass
- ✅ No user-facing crashes from API errors

---

## Timeline

| Task | Time | Priority |
|------|------|----------|
| 1. Error classes | 20 min | High |
| 2. Retry handler | 30 min | High |
| 3. Error messages | 20 min | High |
| 4. Update API client | 40 min | High |
| 5. UI error display | 30 min | High |
| 6. Rate limiter | 40 min | High |
| 7. Token counter | 30 min | Medium |
| 8. Integrate limiter | 30 min | High |
| 9. UI usage display | 20 min | Medium |
| 10. Cost tracking | 30 min | Low |
| **Testing** | 60 min | High |
| **Total** | **~5 hours** | |

---

## Benefits

### For Users
- ✅ **Resilience**: Automatic recovery from transient errors
- ✅ **Clarity**: Understand what went wrong and why
- ✅ **Awareness**: See API usage in real-time
- ✅ **Control**: Avoid hitting rate limits
- ✅ **Transparency**: Know session costs

### For Developers
- ✅ **Reliability**: Fewer error-related bugs
- ✅ **Monitoring**: Track API usage patterns
- ✅ **Debugging**: Better error logging
- ✅ **Maintenance**: Easier to add new error handling

---

## Optional Enhancements

**Not required for Phase 7-8, but nice to have**:
- Request queuing system
- Circuit breaker pattern
- Fallback to cheaper models on rate limit
- Email alerts for repeated errors
- Webhook for error notifications
- Per-user rate limiting (multi-user)
- Historical usage charts
- Cost budget alerts

---

## Ready to Implement? 🚀

This plan provides:
- ✅ Robust error handling with retries
- ✅ Comprehensive rate limiting
- ✅ User-friendly error messages
- ✅ Real-time usage tracking
- ✅ Cost transparency
- ✅ Better UX during errors

**Next step**: Start implementing Task 1 (Error Classes)?

---

*Planning Document | December 29, 2025*
