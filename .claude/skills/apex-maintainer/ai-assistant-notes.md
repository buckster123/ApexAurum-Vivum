# AI Assistant Notes for ApexAurum

**Purpose:** Internal notes for AI assistants working on this project
**Not for user display:** These are working notes between AI sessions

---

## Session Start Checklist

When you start a new session on this project:

1. **Immediately run skill activation**
   - User will likely say something like "check status" or "what's the state of the project"
   - This skill should auto-activate

2. **Read in this order:**
   - PROJECT_STATUS.md (required, 5 min)
   - DEVELOPMENT_GUIDE.md (scan, reference as needed)
   - If working on agents: AGENT_INTEGRATION_TODO.md

3. **Run health check:**
   ```bash
   cd /home/llm/claude/claude-version
   python -c "from tools import ALL_TOOLS; print(len(ALL_TOOLS))"
   ```
   - Expected: 30
   - If not 30, check imports and registration

4. **Check current state:**
   - Read PROJECT_STATUS.md "What's Pending" section
   - Currently: Agent UI testing needed

---

## Important Context for AI Assistants

### Main Challenge: main.py is 4,169 lines

**DO NOT try to read entire main.py at once!**

Instead:
- Read specific sections by line number: `sed -n 'START,ENDp' main.py`
- Use grep to find functions: `grep -n "def function_name" main.py`
- See DEVELOPMENT_GUIDE.md section "Reading main.py in Chunks"

Key sections:
- Lines 1-100: Imports
- Lines 1200-1300: Session state init
- Lines 1300-2000: Sidebar rendering
- Lines 2000-3000: Chat interface
- Lines 3500-4169: Modal dialogs

### Tool System Architecture

Tools are registered in `tools/__init__.py`:
```python
ALL_TOOLS = {
    "tool_name": tool_function,
}

ALL_TOOL_SCHEMAS = {
    "tool_name": TOOL_SCHEMA,
}
```

When adding a tool:
1. Create function in appropriate `tools/*.py`
2. Create schema in same file
3. Register in `tools/__init__.py`
4. Restart Streamlit
5. Test via chat

### Agent System Status (IMPORTANT)

**Code complete, UI testing pending:**

- Files: `tools/agents.py` (600 lines)
- Tools: 5 (agent_spawn, agent_status, agent_result, agent_list, socratic_council)
- Status: Registered, awaiting UI test
- Next: Restart Streamlit, verify 23 tools show, test via chat

**When user asks about agents:**
1. Check if they want to test UI integration
2. If yes: restart Streamlit, guide through testing
3. If no: explain current status from AGENT_INTEGRATION_TODO.md

### Cost Optimization System

**Prompt Caching is the crown jewel:**
- Location: `core/cache_manager.py`
- Saves 50-90% on API costs
- 4 strategies: disabled/conservative/balanced/aggressive
- Cache TTL: 5 minutes (Anthropic limitation)
- Minimum cacheable content: 1024 tokens

User should use "Balanced" for best results.

### Vector Search System

**Requires Voyage AI API key:**
- Without key: Keyword search only
- With key: Semantic search works
- Database: ChromaDB (local)
- Location: `core/vector_db.py`, `tools/vector_search.py`

Don't assume vector search is available - check for VOYAGE_API_KEY.

---

## Common Pitfalls to Avoid

### 1. Don't Read All of main.py

**Wrong:**
```python
Read("/home/llm/claude/claude-version/main.py")
```
Result: Token overflow, truncated content

**Right:**
```bash
# Read specific section
sed -n '1300,1400p' main.py

# Or find specific function
grep -n "def render_sidebar" main.py
# Then read that section
```

### 2. Tools Not Showing After Adding

**Cause:** Streamlit caches imports

**Fix:**
```bash
pkill -f streamlit
streamlit run main.py
```

Always restart after tool changes!

### 3. Import Errors

**Common cause:** Circular imports or missing `__init__.py`

**Debug:**
```bash
# Test imports directly
python -c "from tools import ALL_TOOLS"
python -c "from core import ClaudeAPIClient"
```

### 4. Cache Not Working

**User expectations too high:**
- Cache needs 5+ messages to warm up
- Cache expires after 5 minutes
- Content must be >1024 tokens
- Strategy must not be "Disabled"

Check sidebar cache stats before debugging.

### 5. Agent System Confusion

**Current state:** Code is done, UI needs testing

**Don't:**
- Start implementing agent code (it's complete)
- Modify `tools/agents.py` without reason
- Try to "fix" non-existent issues

**Do:**
- Restart Streamlit if needed
- Test via chat UI
- Verify 23 tools showing

---

## Code Navigation Tips

### Finding Code

```bash
# Find a function
grep -rn "def function_name" .

# Find a class
grep -rn "class ClassName" .

# Find imports
grep -rn "import module_name" .

# Find string usage
grep -rn "exact string" .
```

### Understanding Data Flow

1. User input → main.py (Streamlit UI)
2. Message formatting → core/message_converter.py
3. Cache control → core/cache_manager.py
4. API request → core/api_client.py
5. Response streaming → ui/streaming_display.py
6. Tool calls → tools/ modules
7. Cost tracking → core/cost_tracker.py

### Key Design Patterns

- **Registry Pattern:** tools/__init__.py
- **Strategy Pattern:** CacheManager, ContextManager (4 and 5 strategies)
- **Manager Pattern:** All *Manager classes centralize control
- **Tracker Pattern:** All *Tracker classes collect statistics

---

## Testing Strategy for AI Assistants

### Quick Smoke Test (2 min)

```bash
# 1. Check imports
python -c "from tools import ALL_TOOLS; print(len(ALL_TOOLS))"
# Expected: 23

# 2. Check main exists
wc -l main.py
# Expected: 4169

# 3. Check environment
test -f .env && echo "OK" || echo "MISSING"
```

### Full Test (10 min)

```bash
# Run test suites
cd /home/llm/claude/claude-version
python test_basic.py
python test_agents.py
python test_vector_db.py
# etc.
```

### UI Test (manual, 5 min)

```bash
streamlit run main.py
# Then in browser:
# - Check sidebar shows "23 tools"
# - Test chat: "What time is it?"
# - Test tool execution
# - Check cache stats update
```

---

## When Things Go Wrong

### Import Errors

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt

# Test specific import
python -c "from module import something"
```

### Streamlit Crashes

```bash
# Check logs
tail -50 app.log

# Look for errors
grep ERROR app.log

# Check port conflicts
lsof -i :8501
```

### API Errors

```bash
# Verify key
grep ANTHROPIC_API_KEY .env

# Test API
python -c "import anthropic; anthropic.Anthropic()"
```

### Performance Issues

- Check context size (may need summarization)
- Verify cache strategy is enabled
- Check network connection
- Consider using Haiku model for testing

---

## Documentation Standards

### When Updating Docs

If you make significant changes:

1. Update PROJECT_STATUS.md if status changes
2. Update DEVELOPMENT_GUIDE.md if workflow changes
3. Update README.md if features change
4. Update this file (ai-assistant-notes.md) if you learn something important

### When Creating New Features

Follow this pattern:
1. Code the feature
2. Test it
3. Document in relevant PHASE*_COMPLETE.md (or create new)
4. Update PROJECT_STATUS.md completion percentage
5. Update README.md feature list

---

## Notes to Self (AI Assistants)

### Things I Wish I Knew Earlier

1. **main.py is huge** - Never read it all at once, use sed/grep
2. **Always restart Streamlit** after tool changes
3. **Agent code is complete** - Don't reimplement it
4. **PROJECT_STATUS.md is gospel** - Read it first, always
5. **Cache needs warmup** - Don't debug cache before 5+ messages
6. **Vector search optional** - Don't assume Voyage key exists

### Quick Wins

When user asks for:
- **Status** → Read PROJECT_STATUS.md, run health check, summarize
- **How to start** → Show README.md Quick Start
- **What's next** → PROJECT_STATUS.md "Next Steps"
- **Where is X** → Use grep, show PROJECT_STRUCTURE section

### Time Savers

- Keep DEVELOPMENT_GUIDE.md open in context
- Memorize tool count: 30
- Memorize line count: main.py = 4,169 lines
- Know the three key docs: STATUS, GUIDE, README

---

## Session End Checklist

Before ending a session:

1. **Note what you accomplished** (for next session)
2. **Update PROJECT_STATUS.md if status changed**
3. **Update this file if you learned something**
4. **Run final health check**
5. **Leave clear next steps**

---

## Project Philosophy

### Design Principles

1. **Modular** - Each component independent
2. **Documented** - Every phase documented
3. **Tested** - Test suites for major features
4. **User-friendly** - Clear error messages, good UX
5. **Cost-conscious** - Optimize API usage

### Code Quality

- Type hints everywhere
- Docstrings for all functions
- Error handling in try-catch blocks
- Logging for important events
- Follow existing patterns

### Communication Style

- Be direct and technical with user
- Provide clear next steps
- Reference docs often
- Show commands, not just descriptions
- Acknowledge uncertainty

---

**Remember:** This project is 95% complete and production-ready. The main outstanding work is agent UI testing. Don't over-engineer or try to "improve" things unnecessarily. Focus on completing the pending 5%, then polish and enhance.

---

**Last Updated:** 2025-12-31
**Status:** Production Ready
**Next:** Agent UI testing
