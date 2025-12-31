# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ApexAurum - Claude Edition is a production-grade AI chat interface built on Anthropic's Claude API. It features multi-agent orchestration, vector search, intelligent prompt caching (50-90% cost savings), 30+ integrated tools, and context management with auto-summarization.

**Status:** V1.0 Beta - Production Ready (~15,000 lines of code)

## Essential Reading Before Starting

1. **PROJECT_STATUS.md** - Current implementation status and what's pending
2. **DEVELOPMENT_GUIDE.md** - Detailed developer onboarding guide

## Quick Start Commands

### Running the Application

```bash
# Start the Streamlit application
streamlit run main.py

# Start on specific port
streamlit run main.py --server.port 8502

# Kill running instances
pkill -f streamlit
```

Access at: http://localhost:8501

### Testing

```bash
# Verify tool count (should be 30)
python -c "from tools import ALL_TOOLS; print(f'{len(ALL_TOOLS)} tools loaded')"

# Test agent functionality
python -c "from tools.agents import agent_spawn; print('Agent tools OK')"

# Run test suites (in dev_log_archive_and_testfiles/tests/)
python dev_log_archive_and_testfiles/tests/test_basic.py
python dev_log_archive_and_testfiles/tests/test_agents.py
python dev_log_archive_and_testfiles/tests/test_vector_db.py
```

### Logs and Debugging

```bash
# Live log monitoring
tail -f app.log

# Search for errors
grep ERROR app.log | tail -20

# Check environment
cat .env
```

## High-Level Architecture

### System Layers

```
┌─────────────────────────────────────────┐
│     Streamlit UI (main.py)              │
│     4,169 lines - Chat, sidebar,        │
│     12+ modal dialogs                   │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     Tools Layer (tools/)                │
│     30 tools: files, agents, code,      │
│     memory, vector search, web          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     Core Systems (core/)                │
│     API client, caching, cost tracking, │
│     context management, vector DB       │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│     External Services                   │
│     Anthropic Claude, ChromaDB,         │
│     Voyage AI (optional)                │
└─────────────────────────────────────────┘
```

### Key Components

**main.py (4,169 lines)** - Monolithic Streamlit application
- Lines 1-500: Imports, configuration, state management
- Lines 500-1200: AppState class (conversation management)
- Lines 1200-2000: Sidebar rendering (controls, stats, tools)
- Lines 2000-3000: Chat interface (messages, streaming)
- Lines 3000-3500: Message and tool processing
- Lines 3500-4169: 12+ modal dialogs (search, export, knowledge, etc.)

**core/ (24 modules)** - Core infrastructure
- `api_client.py` - Claude API wrapper with streaming and retry logic
- `cache_manager.py` - Prompt caching (4 strategies: disabled/conservative/balanced/aggressive)
- `cost_tracker.py` - Token counting and cost calculation
- `context_manager.py` - Context optimization (5 strategies to prevent overflow)
- `vector_db.py` - ChromaDB integration for semantic search
- `conversation_indexer.py` - Conversation search indexing
- `tool_processor.py` - Tool registry and execution engine

**tools/ (7 modules)** - 30 tool implementations
- `utilities.py` - Time, calculator, web fetch/search, string ops
- `filesystem.py` - Sandboxed file operations (read/write/list/delete)
- `memory.py` - Key-value memory storage across conversations
- `agents.py` - Multi-agent spawning, status tracking, Socratic council
- `code_execution.py` - Safe Python code execution in sandbox
- `vector_search.py` - Vector operations and knowledge base (4 categories)

**sandbox/** - Runtime storage
- `conversations.json` - Saved conversation history
- `agents.json` - Agent state (created on first agent spawn)
- `memory.json` - Persistent key-value memory
- `*.py` - Executed code files

## Critical Architecture Patterns

### Tool Registration Pattern

All tools must be registered in `tools/__init__.py`:

```python
# 1. Import tool function and schema
from .utilities import my_tool, MY_TOOL_SCHEMA

# 2. Add to ALL_TOOLS dict
ALL_TOOLS = {
    "my_tool": my_tool,
    # ... other tools
}

# 3. Add to ALL_TOOL_SCHEMAS dict
ALL_TOOL_SCHEMAS = {
    "my_tool": MY_TOOL_SCHEMA,
    # ... other schemas
}
```

**IMPORTANT:** Streamlit caches module imports. After modifying tools, you MUST restart Streamlit or changes won't appear.

### Prompt Caching Strategy

Implemented in `core/cache_manager.py` with 4 strategies:

1. **Disabled** - No caching
2. **Conservative** - Cache system prompt + tool definitions only
3. **Balanced** - Cache system + tools + history (5+ turns back) - **Recommended**
4. **Aggressive** - Cache system + tools + history (3+ turns back)

Cache TTL is 5 minutes (Anthropic API limitation). Content must be >1024 tokens to cache. Cache hits save 90% of token costs.

### Context Management Strategies

Implemented in `core/context_manager.py` to prevent context overflow:

1. **Disabled** - No optimization
2. **Aggressive** - Summarize early (at 60% capacity)
3. **Balanced** - Summarize when needed (at 75% capacity)
4. **Adaptive** - Smart decision-making based on conversation patterns
5. **Rolling** - Keep only recent N messages

Context is tracked per-conversation and optimization is applied automatically when approaching token limits.

### Multi-Agent System

Located in `tools/agents.py`. Agents are independent Claude instances running in background threads:

- `agent_spawn(task, agent_type)` - Create agent with specific task
- `agent_status(agent_id)` - Check if agent is running/complete
- `agent_result(agent_id)` - Retrieve completed results
- `agent_list()` - List all agents
- `socratic_council(question, num_agents)` - Multi-agent voting system

Agent state persists in `sandbox/agents.json`. Each agent has: id, type, task, status, result, created_at, updated_at.

**Agent Types:** general, researcher, coder, analyst, writer

### Vector Search & Knowledge Base

Implemented in `core/vector_db.py` and `tools/vector_search.py`:

**Vector Operations:**
- `vector_add(collection, text, metadata)` - Add document
- `vector_search(collection, query, limit)` - Semantic search
- `vector_delete(collection, ids)` - Delete documents
- `vector_list_collections()` - List all collections
- `vector_get_stats(collection)` - Collection statistics

**Knowledge Base:**
- `vector_add_knowledge(content, category, tags)` - Store fact
- `vector_search_knowledge(query, category, limit)` - Retrieve facts

Knowledge categories: preferences, technical, project, general

Requires ChromaDB (included) + optional Voyage AI API key for better embeddings.

## Message Flow and Tool Execution

1. **User Input** → Streamlit text input (main.py)
2. **Message Formatting** → `core/message_converter.py` converts to Claude format
3. **Cache Control** → `core/cache_manager.py` adds cache_control blocks
4. **API Request** → `core/api_client.py` sends to Claude API with streaming
5. **Response Streaming** → `ui/streaming_display.py` renders in real-time
6. **Tool Calls Detection** → Extract tool_use blocks from response
7. **Tool Execution** → `core/tool_processor.py` executes tools safely
8. **Result Formatting** → `core/tool_adapter.py` converts results to Claude format
9. **Continue Loop** → Process continues until no more tool calls (max 5 iterations)
10. **State Persistence** → Save to session state and optionally to `sandbox/conversations.json`

## Important Implementation Details

### Streamlit Session State

Main application uses Streamlit session state (`st.session_state`) extensively:
- `messages` - Current conversation messages
- `api_client` - Initialized Claude API client
- `cost_tracker` - Token and cost statistics
- `cache_manager` - Caching strategy instance
- `context_manager` - Context optimization instance
- `current_conversation_id` - Active conversation UUID

**Session state persists during a Streamlit session but is lost on app restart.**

### Conversation Storage

Conversations saved to `sandbox/conversations.json`:

```python
{
    "id": "uuid",
    "title": "First user message or auto-generated",
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp",
    "messages": [...],  # Full message history
    "tags": [],  # User-defined tags
    "favorite": false,
    "archived": false
}
```

Use `AppState` class methods to load/save conversations. Supports batch operations.

### File Reading Strategy for main.py

main.py is 4,169 lines. When working with it:

```bash
# View specific section by line range
sed -n '1300,1500p' main.py  # View lines 1300-1500

# Find function definitions
grep -n "def function_name" main.py

# Find all dialogs
grep -n "def.*dialog" main.py

# Search for specific code
grep -n "search_term" main.py
```

### Safe Code Execution

Python code execution (`tools/code_execution.py`) uses sandboxing:
- Executes in `sandbox/` directory
- Limited execution time (30 seconds default)
- Captures stdout/stderr
- Cleans up temporary files
- Returns `{"success": bool, "output": str, "error": str}`

### Error Handling Hierarchy

Defined in `core/errors.py`:

1. **RetryableError** - Transient failures (rate limits, network issues)
2. **UserFixableError** - User can fix (invalid API key, missing file)
3. **FatalError** - Unrecoverable errors (system failures)

Error messages are user-friendly via `core/error_messages.py`.

## Configuration

### Environment Variables (.env)

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional
VOYAGE_API_KEY=pa-...  # For vector embeddings
DEFAULT_MODEL=claude-sonnet-4-5-20251022
MAX_TOKENS=64000
```

### Model Selection

Available models (defined in `core/models.py`):
- **Opus 4.5** - Most capable, slowest, most expensive
- **Sonnet 4.5** - Balanced (recommended for production)
- **Sonnet 3.7** - Faster, cheaper, good for most tasks
- **Haiku 3.5** - Fastest, cheapest (recommended for development/testing)

Model can be changed in sidebar during runtime.

## Known Issues & Limitations

### Current Issues

1. **Agent Tools UI Integration** - Agent tools are registered (30 total tools detected) but need end-to-end testing in the Streamlit UI. Code is complete and tested in isolation.

2. **Cache TTL** - Anthropic API caches expire after 5 minutes of inactivity. This is an API limitation, not a code issue.

3. **Vector Search Without Voyage AI** - Without `VOYAGE_API_KEY`, vector search falls back to basic ChromaDB embeddings. Keyword search always works.

### Design Constraints

- **Single User** - Not designed for multi-user/multi-tenant scenarios
- **Local Storage** - Uses JSON files, not database (adequate for single-user use)
- **No Authentication** - Assumes localhost-only access
- **Synchronous Tools** - Tool execution is blocking (agents use threading as workaround)
- **Session State Volatile** - Lost on app restart (conversations are saved to disk)

## Development Best Practices

### When Modifying This Codebase

1. **Always restart Streamlit after code changes** - It caches module imports
2. **Check PROJECT_STATUS.md first** - Know what's complete and what's pending
3. **Use grep to find code** - Don't guess file locations in large codebase
4. **Test tool registration** - After adding tools, verify count is correct
5. **Check logs before debugging** - Many issues are logged with context
6. **Follow existing patterns** - Tool schemas, error handling, return formats
7. **Update relevant docs** - Keep phase docs and status files current

### Adding New Tools

1. Create tool function in appropriate `tools/*.py` file
2. Define schema following existing patterns
3. Register in `tools/__init__.py` (both ALL_TOOLS and ALL_TOOL_SCHEMAS)
4. Restart Streamlit
5. Verify tool count increased: `python -c "from tools import ALL_TOOLS; print(len(ALL_TOOLS))"`

### Modifying Core Systems

Core systems (cache, cost tracking, context management) are tightly integrated. When modifying:

1. Check if change affects `main.py` integration points
2. Test with different strategies/configurations
3. Verify statistics still display correctly in sidebar
4. Check that JSON serialization still works (for conversation save/load)

## Testing Strategy

### Quick Smoke Test

```bash
# 1. Verify imports
python -c "from core import ClaudeAPIClient; from tools import ALL_TOOLS; print(f'{len(ALL_TOOLS)} tools OK')"

# 2. Start app
streamlit run main.py

# 3. In UI: Send "What time is it?" - should call time tool and respond

# 4. Check sidebar shows "30 tools available"
```

### Comprehensive Testing

Test suites are in `dev_log_archive_and_testfiles/tests/`:

- `test_basic.py` - Core API functionality
- `test_streaming.py` - Streaming responses
- `test_tools.py` - Tool execution
- `test_cost_tracker.py` - Cost calculations
- `test_vector_db.py` - Vector operations
- `test_semantic_search.py` - Search functionality
- `test_knowledge_manager.py` - Knowledge CRUD
- `test_agents.py` - Agent system

Run individual tests from project root.

## Performance Characteristics

### Response Times

- Cold start: 500-1000ms
- With cache hits: 200-500ms (40-60% faster)
- Streaming starts: <100ms to first token
- Tool execution: 50-5000ms (varies by tool)

### Cost Savings

- No optimization: ~$0.90 per 20-turn conversation
- Balanced caching: ~$0.40 per 20-turn conversation (56% savings)
- Cache hit rate: 60-80% (Balanced), 70-90% (Aggressive) after warmup

### Recommended Settings

**For production:**
- Model: Sonnet 4.5
- Cache: Balanced
- Context: Adaptive

**For development:**
- Model: Haiku 3.5
- Cache: Conservative
- Context: Balanced

## Troubleshooting

### Tools Not Showing in UI

```bash
pkill -f streamlit
python -c "from tools import ALL_TOOLS; print(len(ALL_TOOLS))"
streamlit run main.py
```

### Import Errors

```bash
pip install -r requirements.txt
python -c "from core import ClaudeAPIClient; from tools import ALL_TOOLS; print('OK')"
```

### API Errors (401 Unauthorized)

```bash
grep ANTHROPIC_API_KEY .env
# Verify key is valid at console.anthropic.com
```

### Cache Not Working

1. Check cache strategy is not "Disabled" in sidebar
2. Ensure content >1024 tokens (Anthropic requirement)
3. Wait 5+ messages for cache warmup period
4. Check logs: `grep cache app.log`

## Documentation Reference

**Quick Reference:**
- `PROJECT_STATUS.md` - Current status, pending work
- `DEVELOPMENT_GUIDE.md` - Detailed developer guide
- `README.md` - User-facing documentation

**Implementation Details:**
- `dev_log_archive_and_testfiles/PHASE14_COMPLETE.md` - Prompt caching
- `dev_log_archive_and_testfiles/PHASE13.X_COMPLETE.md` - Vector search
- `dev_log_archive_and_testfiles/PHASE10_COMPLETE.md` - Multi-agent system
- `dev_log_archive_and_testfiles/PHASE9_COMPLETE.md` - Context management
- `dev_log_archive_and_testfiles/V1.0_BETA_RELEASE.md` - Complete feature list
- `dev_log_archive_and_testfiles/PROJECT_SUMMARY.md` - Development journey

**Integration Status:**
- `dev_log_archive_and_testfiles/AGENT_INTEGRATION_TODO.md` - Agent UI testing status
- `dev_log_archive_and_testfiles/AGENT_SYSTEM.md` - Agent system documentation

---

**Last Updated:** 2025-12-31
**Version:** 1.0 Beta
**Total Code:** ~15,000 lines across 40+ Python files
