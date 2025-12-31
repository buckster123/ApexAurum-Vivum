# Phase 9 Implementation Plan: Context Management

## Overview

Phase 9 adds intelligent context window management to enable unlimited conversation length, reduce costs, and improve performance through automatic summarization and smart pruning.

---

## Goals

1. **Enable unlimited conversations** - Never hit context limits
2. **Reduce API costs** - Remove redundant tokens from context
3. **Improve performance** - Smaller contexts = faster responses
4. **Preserve important information** - Smart pruning keeps what matters
5. **User control** - Configurable strategies and manual overrides

---

## Architecture

### Core Components

```
core/
├── context_manager.py      # Main context management orchestrator
├── summarizer.py           # Conversation summarization logic
├── message_pruner.py       # Smart message pruning
└── context_tracker.py      # Enhanced token tracking

main.py                      # UI updates for context display
```

---

## Task Breakdown

### Task 1: Context Tracker (Enhanced Token Tracking)

**File:** `core/context_tracker.py`

**Purpose:** Track token usage across entire conversation context

**Features:**
- Calculate total context tokens (messages + system + tools)
- Track per-message token counts
- Identify messages approaching token limits
- Support different model context windows

**Functions:**
```python
class ContextTracker:
    def __init__(self, model: str):
        """Initialize with model-specific context limits"""
        self.model = model
        self.max_tokens = self.get_model_context_limit()

    def get_model_context_limit(self) -> int:
        """Get max context tokens for model"""
        # Opus/Sonnet: 200K, Haiku: 200K

    def calculate_total_context(
        self,
        messages: List[Dict],
        system: str,
        tools: List[Dict]
    ) -> Dict[str, int]:
        """Calculate total tokens in context"""
        # Returns: {
        #     "messages_tokens": 5000,
        #     "system_tokens": 500,
        #     "tools_tokens": 300,
        #     "total_tokens": 5800,
        #     "max_tokens": 200000,
        #     "usage_percent": 2.9,
        #     "remaining_tokens": 194200
        # }

    def get_message_token_breakdown(
        self,
        messages: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Get token count for each message"""
        # Returns: [
        #     {"index": 0, "role": "user", "tokens": 50},
        #     {"index": 1, "role": "assistant", "tokens": 200},
        #     ...
        # ]

    def should_summarize(
        self,
        total_tokens: int,
        threshold_percent: float = 0.7
    ) -> bool:
        """Check if context should be summarized"""
        # True if > 70% of context limit used
```

**Model Context Limits:**
- Claude Opus 4.5: 200,000 tokens
- Claude Sonnet 4.5: 200,000 tokens
- Claude Sonnet 3.7: 200,000 tokens
- Claude Haiku 3.5: 200,000 tokens

---

### Task 2: Conversation Summarizer

**File:** `core/summarizer.py`

**Purpose:** Summarize conversation segments to compress context

**Features:**
- Summarize ranges of messages
- Preserve key information (code, decisions, facts)
- Generate concise but informative summaries
- Support different summarization strategies

**Functions:**
```python
class ConversationSummarizer:
    def __init__(self, client: ClaudeAPIClient):
        """Initialize with API client for summarization"""
        self.client = client

    def summarize_messages(
        self,
        messages: List[Dict],
        strategy: str = "balanced"
    ) -> str:
        """
        Summarize a list of messages into concise text

        Strategy:
        - "aggressive": Very brief summary (50-100 tokens)
        - "balanced": Moderate summary (100-300 tokens)
        - "conservative": Detailed summary (300-500 tokens)
        """
        # Use Claude to generate summary
        # Prompt: "Summarize this conversation segment concisely,
        #          preserving key facts, decisions, and technical details."

    def identify_important_messages(
        self,
        messages: List[Dict]
    ) -> List[int]:
        """
        Identify message indices that should not be summarized

        Important messages:
        - Contains code blocks
        - User directives/decisions
        - Error messages
        - Bookmarked by user
        """

    def create_summary_message(
        self,
        summary_text: str,
        original_count: int,
        token_savings: int
    ) -> Dict[str, Any]:
        """
        Create a summary message block

        Format:
        {
            "role": "system",
            "content": "📝 Summary of {original_count} messages:\n{summary_text}\n\n(Saved {token_savings} tokens)"
        }
        """
```

**Summarization Strategy:**

1. **Aggressive** (50-100 tokens):
   - Single paragraph summary
   - Only critical facts
   - Use: High-volume conversations

2. **Balanced** (100-300 tokens):
   - Multi-paragraph with key points
   - Preserve technical details
   - Use: Default strategy

3. **Conservative** (300-500 tokens):
   - Detailed with context
   - Preserve most information
   - Use: Complex technical discussions

---

### Task 3: Message Pruner

**File:** `core/message_pruner.py`

**Purpose:** Intelligently remove or compress less important messages

**Features:**
- Identify redundant messages
- Remove simple acknowledgments
- Compress tool call details
- Preserve important context

**Functions:**
```python
class MessagePruner:
    def __init__(self):
        """Initialize pruner with heuristics"""

    def calculate_message_importance(
        self,
        message: Dict,
        context: Dict
    ) -> float:
        """
        Score message importance (0.0 - 1.0)

        High importance:
        - User requests/questions (0.9)
        - Code blocks (0.8)
        - Error messages (0.8)
        - Bookmarked messages (1.0)

        Low importance:
        - Simple acknowledgments (0.2)
        - Redundant tool calls (0.3)
        - "Please wait" messages (0.1)
        """

    def prune_messages(
        self,
        messages: List[Dict],
        target_token_count: int,
        preserve_recent: int = 5
    ) -> List[Dict]:
        """
        Remove low-importance messages to reach target token count

        Strategy:
        1. Score all messages by importance
        2. Keep recent N messages untouched
        3. Remove lowest-scoring messages first
        4. Stop when target token count reached
        """

    def compress_tool_calls(
        self,
        message: Dict
    ) -> Dict:
        """
        Compress verbose tool call messages

        Before: "Tool 'fs_read_file' returned 5000 characters..."
        After: "Tool 'fs_read_file' completed successfully"
        """

    def is_redundant(
        self,
        message: Dict,
        previous_messages: List[Dict]
    ) -> bool:
        """Check if message is redundant"""
        # Detect repeated information
        # E.g., "OK", "Got it", "Sure", etc.
```

**Importance Scoring:**

| Message Type | Score | Rationale |
|--------------|-------|-----------|
| User question | 0.9 | Essential context |
| Code blocks | 0.8 | Technical reference |
| Error messages | 0.8 | Debugging context |
| Tool results (important) | 0.7 | State changes |
| Assistant explanations | 0.6 | Informative |
| Simple tool calls | 0.4 | Often redundant |
| Acknowledgments | 0.2 | Low value |
| "Thinking..." messages | 0.1 | Transient |
| Bookmarked | 1.0 | User-marked important |

---

### Task 4: Context Manager (Orchestrator)

**File:** `core/context_manager.py`

**Purpose:** Orchestrate all context management operations

**Features:**
- Coordinate tracking, summarization, and pruning
- Apply user-selected strategies
- Handle message bookmarking
- Manage rolling summaries

**Functions:**
```python
class ContextManager:
    def __init__(
        self,
        client: ClaudeAPIClient,
        model: str,
        strategy: str = "balanced"
    ):
        """Initialize context manager"""
        self.tracker = ContextTracker(model)
        self.summarizer = ConversationSummarizer(client)
        self.pruner = MessagePruner()
        self.strategy = strategy
        self.bookmarked_indices = set()
        self.rolling_summary = ""

    def manage_context(
        self,
        messages: List[Dict],
        system: str,
        tools: List[Dict],
        preserve_recent: int = 10
    ) -> Tuple[List[Dict], str]:
        """
        Main context management method

        Returns:
            (managed_messages, context_summary)

        Process:
        1. Calculate current context usage
        2. Check if management needed (>70% full)
        3. Identify messages to preserve (recent + bookmarked)
        4. Summarize or prune older messages
        5. Update rolling summary
        6. Return optimized message list
        """

    def bookmark_message(self, index: int):
        """Mark message as important (never summarize)"""
        self.bookmarked_indices.add(index)

    def unbookmark_message(self, index: int):
        """Remove bookmark from message"""
        self.bookmarked_indices.discard(index)

    def get_context_stats(
        self,
        messages: List[Dict],
        system: str,
        tools: List[Dict]
    ) -> Dict[str, Any]:
        """Get detailed context statistics"""
        # Returns stats for UI display

    def force_summarize(
        self,
        messages: List[Dict],
        preserve_recent: int = 5
    ) -> List[Dict]:
        """Manually trigger summarization"""
```

**Context Management Strategies:**

1. **Aggressive:**
   - Threshold: 50% context used
   - Preserve: Last 5 messages
   - Summarization: Aggressive (50-100 tokens)
   - Best for: High-volume conversations

2. **Balanced (Default):**
   - Threshold: 70% context used
   - Preserve: Last 10 messages
   - Summarization: Balanced (100-300 tokens)
   - Best for: General use

3. **Conservative:**
   - Threshold: 85% context used
   - Preserve: Last 20 messages
   - Summarization: Conservative (300-500 tokens)
   - Best for: Technical discussions

4. **Manual:**
   - No automatic management
   - User triggers summarization
   - Full control

---

### Task 5: UI Integration

**File:** `main.py`

**Purpose:** Display context usage and controls

**UI Components:**

#### 1. Context Usage Display (Sidebar)

```
📊 Context Usage
└─ Current Context

   Context: 45K/200K  [████░░░░░░] 22.5%

   Breakdown:
   • Messages:   42,000 tokens (93%)
   • System:      2,500 tokens (6%)
   • Tools:         500 tokens (1%)

   Strategy: Balanced
   Rolling Summary: Active

   [Force Summarize Now]
```

#### 2. Context Strategy Settings

```
⚙️ Context Management

Strategy:
( ) Aggressive  - Summarize at 50% (keeps 5 recent)
(•) Balanced    - Summarize at 70% (keeps 10 recent)
( ) Conservative - Summarize at 85% (keeps 20 recent)
( ) Manual      - No auto-summarization

Preserve Recent Messages: [10] slider (1-50)

☑ Enable Rolling Summary
☑ Auto-compress Tool Calls
```

#### 3. Message Bookmarking (In Chat)

Add bookmark button to each message:
```
User: Can you implement Phase 9?
                                    [🔖 Bookmark]```

Bookmarked messages displayed with indicator:
```
🔖 User: Can you implement Phase 9?
```

#### 4. Summarization Notifications

When context is summarized, show info message:
```
ℹ️ Context Summarized
Compressed 25 older messages into summary.
Saved 15,000 tokens. View summary below.

📝 Summary of previous messages:
[Summary text here...]
```

---

### Task 6: Session State Updates

**File:** `main.py`

**Updates to session state:**

```python
# Initialize in session state
if "context_manager" not in st.session_state:
    st.session_state.context_manager = ContextManager(
        client=st.session_state.client,
        model=st.session_state.model,
        strategy="balanced"
    )

if "context_strategy" not in st.session_state:
    st.session_state.context_strategy = "balanced"

if "preserve_recent_count" not in st.session_state:
    st.session_state.preserve_recent_count = 10

if "auto_summarize" not in st.session_state:
    st.session_state.auto_summarize = True

if "rolling_summary_enabled" not in st.session_state:
    st.session_state.rolling_summary_enabled = True
```

---

### Task 7: Integration with Message Processing

**File:** `main.py` - Update `process_message()` function

```python
def process_message(user_input):
    # ... existing code ...

    # Before sending to API, manage context
    if st.session_state.auto_summarize:
        managed_messages, context_summary = st.session_state.context_manager.manage_context(
            messages=st.session_state.messages,
            system=system_prompt,
            tools=tools,
            preserve_recent=st.session_state.preserve_recent_count
        )

        # If messages were summarized, show notification
        if len(managed_messages) < len(st.session_state.messages):
            original_count = len(st.session_state.messages)
            new_count = len(managed_messages)
            st.info(f"ℹ️ Summarized {original_count - new_count} messages to optimize context")

        # Use managed messages for API call
        messages_for_api = managed_messages
    else:
        messages_for_api = st.session_state.messages

    # ... rest of API call ...
```

---

### Task 8: Testing

**File:** `test_phase9.py`

**Test Coverage:**

```python
# Test 1: Context tracker calculates correctly
def test_context_tracker():
    tracker = ContextTracker("claude-sonnet-4-5")
    assert tracker.max_tokens == 200000
    
    messages = [{"role": "user", "content": "Hello"}]
    stats = tracker.calculate_total_context(messages, "", [])
    assert stats["total_tokens"] > 0
    assert stats["usage_percent"] < 1.0

# Test 2: Summarizer creates summaries
def test_summarizer():
    messages = [
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "2+2 equals 4."}
    ]
    # Mock summarizer without API call
    summary = "User asked about math, assistant answered."
    assert len(summary) < sum(len(m["content"]) for m in messages)

# Test 3: Message pruner scores correctly
def test_message_pruner():
    pruner = MessagePruner()
    
    user_msg = {"role": "user", "content": "Can you help?"}
    score = pruner.calculate_message_importance(user_msg, {})
    assert score >= 0.8  # User questions are important
    
    ack_msg = {"role": "assistant", "content": "OK"}
    score = pruner.calculate_message_importance(ack_msg, {})
    assert score <= 0.3  # Acknowledgments are low priority

# Test 4: Context manager orchestration
def test_context_manager():
    # Mock client
    manager = ContextManager(None, "claude-sonnet-4-5", "balanced")
    
    # Test bookmarking
    manager.bookmark_message(5)
    assert 5 in manager.bookmarked_indices
    
    manager.unbookmark_message(5)
    assert 5 not in manager.bookmarked_indices

# Test 5: Strategy thresholds
def test_strategy_thresholds():
    tracker = ContextTracker("claude-sonnet-4-5")
    
    # 60% usage, aggressive threshold is 50%
    assert tracker.should_summarize(120000, threshold_percent=0.5)
    
    # 60% usage, conservative threshold is 85%
    assert not tracker.should_summarize(120000, threshold_percent=0.85)

# Test 6: Token breakdown per message
def test_message_token_breakdown():
    tracker = ContextTracker("claude-sonnet-4-5")
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    breakdown = tracker.get_message_token_breakdown(messages)
    assert len(breakdown) == 2
    assert breakdown[0]["role"] == "user"
    assert breakdown[0]["tokens"] > 0

# Test 7: Important message identification
def test_important_message_identification():
    pruner = MessagePruner()
    
    code_msg = {"role": "assistant", "content": "```python\nprint('hello')\n```"}
    error_msg = {"role": "assistant", "content": "Error: File not found"}
    ack_msg = {"role": "assistant", "content": "OK"}
    
    # Code and errors should be marked important
    assert pruner.calculate_message_importance(code_msg, {}) > 0.7
    assert pruner.calculate_message_importance(error_msg, {}) > 0.7
    assert pruner.calculate_message_importance(ack_msg, {}) < 0.3

# Test 8: Tool call compression
def test_tool_call_compression():
    pruner = MessagePruner()
    
    verbose_tool = {
        "role": "assistant",
        "content": "Tool 'fs_read_file' returned 5000 characters of data..."
    }
    
    compressed = pruner.compress_tool_calls(verbose_tool)
    assert len(compressed["content"]) < len(verbose_tool["content"])

# Test 9: Redundancy detection
def test_redundancy_detection():
    pruner = MessagePruner()
    
    previous = [
        {"role": "assistant", "content": "I'll help with that."}
    ]
    
    redundant = {"role": "assistant", "content": "OK"}
    assert pruner.is_redundant(redundant, previous)
    
    unique = {"role": "assistant", "content": "Here's the implementation:"}
    assert not pruner.is_redundant(unique, previous)

# Test 10: Context stats UI data
def test_context_stats():
    manager = ContextManager(None, "claude-sonnet-4-5", "balanced")
    
    messages = [{"role": "user", "content": "Hello"}]
    stats = manager.get_context_stats(messages, "System prompt", [])
    
    assert "total_tokens" in stats
    assert "usage_percent" in stats
    assert "remaining_tokens" in stats
    assert "messages_tokens" in stats
```

**Expected:** All 10 tests pass

---

## Implementation Order

### Phase 1: Foundation (Tasks 1-2)
1. Create `core/context_tracker.py` - Enhanced token tracking
2. Create `core/summarizer.py` - Conversation summarization

### Phase 2: Intelligence (Tasks 3-4)
3. Create `core/message_pruner.py` - Smart pruning
4. Create `core/context_manager.py` - Orchestrator

### Phase 3: Integration (Tasks 5-7)
5. Update `main.py` - UI components
6. Update `main.py` - Session state
7. Update `main.py` - Message processing integration

### Phase 4: Testing (Task 8)
8. Create `test_phase9.py` - Comprehensive tests
9. Run tests and fix issues
10. Document completion

---

## User Experience Flow

### Automatic Mode (Default)

1. User has long conversation
2. Context reaches 70% (balanced strategy)
3. System automatically summarizes older messages
4. Shows info notification: "Summarized 15 messages, saved 8K tokens"
5. User continues chatting seamlessly
6. Never hits context limit

### Manual Mode

1. User disables auto-summarization
2. Context usage shown in sidebar: 85% full
3. Warning when approaching limit: "⚠️ Context 85% full"
4. User clicks "Force Summarize Now" button
5. System summarizes with preview
6. User continues chatting

### Bookmarking Flow

1. User sees important message (e.g., code snippet)
2. Clicks bookmark icon 🔖 on message
3. Message marked with 🔖 indicator
4. That message never gets summarized
5. Always available in context

---

## Benefits Summary

✅ **Unlimited conversations** - Never worry about context limits  
✅ **Cost reduction** - Remove 30-50% of redundant tokens  
✅ **Faster responses** - Smaller contexts reduce latency  
✅ **Smart preservation** - Keeps important information  
✅ **User control** - Multiple strategies + manual override  
✅ **Transparent** - Clear visibility of context usage  
✅ **Seamless** - Automatic management, no user intervention needed

---

## Technical Considerations

### Summarization API Costs

- Summarization uses Claude API (additional cost)
- Conservative estimate: 1 API call per 20 messages summarized
- Cost: ~$0.001-0.01 per summarization
- Savings: Much more than cost (removes 10K+ tokens from future calls)

**Example:**
- Summarize 20 messages (cost: $0.01)
- Saves 10,000 tokens from context
- 10,000 tokens × $3/1M = $0.03 saved per request
- Break-even after 1 request, pure savings after that

### Performance Impact

- Token calculation: Fast (< 1ms per message)
- Importance scoring: Fast (< 1ms per message)
- Summarization: Requires API call (~2-5 seconds)
- Overall: Minimal impact, only when threshold reached

### Storage Considerations

- Summaries stored in conversation JSON
- Original messages can be archived separately
- Minimal additional storage (summaries are compressed)

---

## Configuration Options

Users can configure in sidebar:

| Setting | Options | Default | Description |
|---------|---------|---------|-------------|
| **Strategy** | Aggressive, Balanced, Conservative, Manual | Balanced | When to summarize |
| **Preserve Recent** | 1-50 messages | 10 | How many recent messages to keep |
| **Auto Summarize** | On/Off | On | Enable automatic summarization |
| **Rolling Summary** | On/Off | On | Maintain cumulative summary |
| **Compress Tools** | On/Off | On | Compress verbose tool calls |

---

## Example Scenarios

### Scenario 1: Long Coding Session

- **Messages:** 50 (code generation, debugging, iterations)
- **Context:** 95K tokens (48% usage)
- **Action:** No summarization (< 70% threshold)
- **Result:** Full context preserved

### Scenario 2: Extended Discussion

- **Messages:** 100 (mixed conversation)
- **Context:** 150K tokens (75% usage)
- **Action:** Summarize messages 1-80, keep 81-100
- **Result:** Context reduced to 90K tokens (45% usage)

### Scenario 3: High-Volume Chat

- **Messages:** 200 (lots of simple Q&A)
- **Strategy:** Aggressive (50% threshold)
- **Action:** Summarize frequently, keep last 5
- **Result:** Context stays around 50-60K tokens

---

## Success Metrics

Phase 9 is successful when:

1. ✅ Users can have conversations of any length
2. ✅ Context never exceeds 90% of limit
3. ✅ Average context size reduced by 30-50%
4. ✅ No important information lost
5. ✅ Summarization is transparent and informative
6. ✅ All tests pass (10/10)

---

## Future Enhancements (Post-Phase 9)

- **Prompt caching** - Cache summaries for better performance
- **Export summaries** - Save conversation summaries separately
- **Summary regeneration** - Re-summarize with different strategies
- **Multi-level summaries** - Hierarchical summarization
- **Semantic clustering** - Group related messages before summarizing

---

## Ready to Implement!

This plan provides:
- 8 clear tasks with specific deliverables
- Detailed technical specifications
- UI/UX mockups
- Comprehensive test plan
- Implementation order

Estimated complexity: **Medium-High**  
Estimated time: **4-6 hours** (with testing)

Let's build Phase 9! 🚀
