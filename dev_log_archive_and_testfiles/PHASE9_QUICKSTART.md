# Phase 9 Quickstart: Context Management

Quick reference for using Phase 9 context management features.

---

## Testing

Run the test suite:

```bash
venv/bin/python test_phase9.py
```

Expected: All 15 tests pass ✅

---

## Quick Overview

**What it does:** Automatically manages conversation context to enable unlimited length conversations while reducing costs.

**How it works:** When context usage reaches a threshold (default 70%), older messages are intelligently summarized while preserving recent and important messages.

**User impact:** Seamless - happens automatically in the background.

---

## Accessing Context Management

**Location:** Sidebar → "🧠 Context Management" → "Context Usage & Strategy"

### What You'll See:

```
Current Context:
Context: 45,000/200,000 tokens    22.5% 🟢
[████░░░░░░░░░░░░░░]

Breakdown:
• Messages: 42,000 tokens
• System: 2,500 tokens
• Tools: 500 tokens
• Remaining: 155,000 tokens
```

---

## Strategies

Choose your management strategy:

| Strategy | When Summarizes | Keeps | Best For |
|----------|----------------|-------|----------|
| **Aggressive** | At 50% | 5 recent | High-volume chats |
| **Balanced** ⭐ | At 70% | 10 recent | General use (default) |
| **Conservative** | At 85% | 20 recent | Technical work |
| **Manual** | Never | All | Full control |

---

## Common Actions

### View Context Usage

1. Open sidebar
2. Expand "Context Usage & Strategy"
3. See current usage with color indicator:
   - 🟢 Green: < 50% (healthy)
   - 🟡 Yellow: 50-70% (approaching)
   - 🔴 Red: > 70% (high)

### Change Strategy

1. Open "Context Usage & Strategy"
2. Select strategy from dropdown
3. Adjust "Preserve Recent Messages" slider if desired
4. Changes apply immediately

### Force Summarization

1. Open "Context Usage & Strategy"
2. Click "📝 Force Summarize Now"
3. System summarizes older messages
4. See success message with savings

### Disable Auto-Summarization

1. Open "Context Usage & Strategy"
2. Uncheck "Enable Auto-Summarization"
3. Manual control only

---

## Automatic Behavior

### What Happens Automatically:

```
1. You send a message
2. System checks context usage
3. If over threshold (e.g., 70%):
   ✓ Identifies last 10 messages (recent)
   ✓ Identifies bookmarked messages
   ✓ Identifies code blocks, errors
   ✓ Summarizes remaining older messages
   ✓ Shows notification: "ℹ️ Summarized 25 messages, saved 15,000 tokens"
4. API call proceeds with optimized context
5. You continue chatting normally
```

### What Gets Preserved:

✅ Recent N messages (default: 10)
✅ Messages with code blocks
✅ Error messages
✅ User bookmarks (future)
✅ Long user questions

### What Gets Summarized:

📝 Old simple Q&A
📝 Acknowledgments
📝 Redundant tool calls
📝 Transient messages

---

## Cost Savings Example

### Before Context Management:
```
Conversation: 100 messages
Context: 150,000 tokens
Cost per request: $0.45 (Sonnet 4.5)
```

### After Context Management:
```
Conversation: 100 messages
Context: 20,000 tokens (summary + recent + important)
Cost per request: $0.06 (Sonnet 4.5)

Savings: 86.5% 💰
```

---

## Troubleshooting

### Context Not Summarizing?

**Check:**
- Is auto-summarization enabled?
- Is context above threshold? (70% for balanced)
- Are there enough messages to summarize? (needs > preserve count)

### Too Aggressive Summarization?

**Solutions:**
- Change to "Conservative" strategy (85% threshold)
- Increase "Preserve Recent Messages" (10 → 20)
- Switch to "Manual" mode

### Lost Important Information?

**Prevention:**
- Future: Bookmark important messages (UI coming)
- Current: Use "Conservative" strategy
- Current: Increase preserve count

### Want Full Control?

**Switch to Manual Mode:**
1. Set strategy to "Manual"
2. Disable auto-summarization
3. Use "Force Summarize Now" when needed

---

## Quick Reference

### Session State Variables

```python
st.session_state.context_manager       # ContextManager instance
st.session_state.context_strategy      # "balanced", "aggressive", etc.
st.session_state.preserve_recent_count # Number of recent to keep
st.session_state.auto_summarize        # True/False
```

### Strategy Thresholds

```python
THRESHOLDS = {
    "aggressive": 0.5,    # 50% = 100,000 tokens
    "balanced": 0.7,      # 70% = 140,000 tokens
    "conservative": 0.85, # 85% = 170,000 tokens
    "manual": 1.0         # Never
}
```

### Model Context Limits

All Claude models: **200,000 tokens**

---

## Tips & Best Practices

### For General Chat:
- Use **Balanced** strategy (default)
- Preserve 10 recent messages
- Enable auto-summarization

### For Coding Sessions:
- Use **Conservative** strategy
- Preserve 20 recent messages
- Code blocks automatically preserved

### For Research/Learning:
- Use **Conservative** strategy
- Preserve 15-20 recent messages
- Manually summarize when taking breaks

### For High-Volume Q&A:
- Use **Aggressive** strategy
- Preserve 5 recent messages
- Maximizes cost savings

---

## Testing Individual Components

### Test Context Tracker

```bash
venv/bin/python -c "
from core.context_tracker import ContextTracker

tracker = ContextTracker('claude-sonnet-4-5')
messages = [{'role': 'user', 'content': 'Hello'}]

stats = tracker.calculate_total_context(messages, 'System', [])
print(f'Tokens: {stats[\"total_tokens\"]:,} / {stats[\"max_tokens\"]:,}')
print(f'Usage: {stats[\"usage_percent\"]:.1f}%')
"
```

### Test Summarizer

```bash
venv/bin/python -c "
from core.summarizer import ConversationSummarizer

summarizer = ConversationSummarizer(client=None)
messages = [
    {'role': 'user', 'content': 'What is 2+2?'},
    {'role': 'assistant', 'content': '2+2 equals 4.'}
]

summary = summarizer.summarize_messages(messages, 'balanced')
print(f'Summary: {summary}')
"
```

### Test Context Manager

```bash
venv/bin/python -c "
from core.context_manager import ContextManager

manager = ContextManager(None, 'claude-sonnet-4-5', 'balanced')
messages = [{'role': 'user', 'content': 'Hello'}]

stats = manager.get_context_stats(messages, 'System', None)
print(f'Strategy: {stats[\"strategy\"]}')
print(f'Threshold: {stats[\"threshold_percent\"]*100}%')
print(f'Usage: {stats[\"usage_percent\"]:.1f}%')
"
```

---

## Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `core/context_tracker.py` | Token tracking | 212 |
| `core/summarizer.py` | Summarization | 306 |
| `core/message_pruner.py` | Importance scoring | 265 |
| `core/context_manager.py` | Orchestration | 303 |
| `test_phase9.py` | Test suite | 370 |

---

## Advanced Configuration

### Custom Strategy

```python
# In core/context_manager.py
STRATEGY_CONFIGS["custom"] = {
    "threshold_percent": 0.6,  # Summarize at 60%
    "preserve_recent": 15,     # Keep last 15
    "summarization_style": "balanced",
    "description": "Custom 60% threshold"
}
```

### Custom Importance Scoring

```python
# In core/message_pruner.py
# Modify calculate_message_importance() method
# Adjust scores for different message types
```

---

## Monitoring Context Usage

### In Real-Time:

Watch the context indicator in sidebar:
- Changes color based on usage
- Updates after each message
- Shows remaining capacity

### After Summarization:

Look for info messages:
```
ℹ️ Summarized 25 older messages. Saved ~15,000 tokens.
```

### Statistics:

Check "Statistics" section:
```
• Messages summarized: 45
• Tokens saved: 28,000
• Bookmarked: 2
```

---

## FAQ

**Q: Will I lose important messages?**
A: No. Code blocks, errors, and recent messages are always preserved.

**Q: Can I see what was summarized?**
A: Yes. The summary message shows in the conversation.

**Q: Does this cost extra?**
A: Summarization has a tiny cost (~$0.001-0.01) but saves much more ($0.10+).

**Q: Can I disable it?**
A: Yes. Uncheck "Enable Auto-Summarization" or use "Manual" strategy.

**Q: How do I know it's working?**
A: You'll see info notifications when summarization occurs.

**Q: What if I want more control?**
A: Use "Conservative" strategy or "Manual" mode with manual summarization.

---

## What's Summarized

### High Priority (Never Summarized):
- ✅ Recent 10 messages (configurable)
- ✅ Code blocks (```...```)
- ✅ Error messages
- ✅ Long user questions (>100 chars)
- ✅ Images

### Low Priority (Often Summarized):
- 📝 Acknowledgments ("OK", "Sure", etc.)
- 📝 Simple tool calls
- 📝 Redundant messages
- 📝 Old Q&A exchanges

---

## Performance Impact

### Negligible:
- Token calculation: < 1ms per message
- Importance scoring: < 1ms per message
- Threshold checking: < 1ms

### Minimal:
- Summarization: 2-5 seconds (only when needed)
- Frequency: Once per 20-50 messages (balanced strategy)

### Overall:
- Imperceptible to user
- Happens in background
- No workflow interruption

---

## Getting Help

**Tests failing?**
```bash
venv/bin/python test_phase9.py
```

**Context not working?**
- Check auto-summarization is enabled
- Verify context usage in sidebar
- Try forcing summarization manually

**Need more control?**
- Switch to Manual strategy
- Adjust preserve count slider
- Disable auto-summarization

---

## Success Indicators

You'll know Phase 9 is working when:

✅ Conversations continue beyond 100 messages
✅ Context usage stays below 90%
✅ You see occasional summarization notifications
✅ API costs decrease over long conversations
✅ Response times remain fast

---

🎉 **Phase 9 Complete!** Enjoy unlimited conversations!

For detailed information, see `PHASE9_COMPLETE.md`
