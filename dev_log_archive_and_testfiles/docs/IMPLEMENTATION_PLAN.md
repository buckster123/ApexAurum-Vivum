# Implementation Plan: Apex Aurum Claude Edition

## Project Overview
Adapting the Moonshot-based Apex Aurum chatbot to use Claude/Anthropic API while maintaining all local tools and functionality.

## Architecture Analysis

### Core Components (from original/main.py)
1. **State Management** (~400 lines)
   - AppState class: DB, ChromaDB, embeddings
   - Session state helpers
   - Memory cache system

2. **Tool System** (~1500 lines)
   - 30+ local tools (filesystem, code exec, memory, git, etc.)
   - Tool schema generation
   - Tool dispatcher with type coercion
   - Container/DI system

3. **Memory System** (~500 lines)
   - SQLite persistence
   - ChromaDB vector storage
   - LRU cache with salience scoring
   - Memory pruning and consolidation

4. **API Client** (~400 lines)
   - Main API calling function
   - Streaming response handler
   - Tool call processing
   - Retry logic and error handling

5. **UI/Streamlit** (~600 lines)
   - Sidebar with settings
   - Chat interface
   - File browser
   - Agent management UI

6. **Advanced Features** (~800 lines)
   - Multi-agent system
   - Socratic council (multi-LLM voting)
   - Graph-of-Thought visualization
   - YAML configuration retrieval
   - Chat log analysis

## Implementation Strategy

### Phase 1: Core API Adapter (Priority: CRITICAL)
**Goal:** Get basic Claude API calls working

**Files to Create:**
- `claude-version/core/api_client.py` - Claude API wrapper
- `claude-version/core/message_converter.py` - Format converters
- `claude-version/core/models.py` - Model configuration

**Key Changes:**
1. Replace `OpenAI` with `Anthropic` client
2. Extract system prompts from messages array
3. Convert message format (no system messages in array)
4. Implement new streaming handler for Claude events
5. Update model names enum

**Estimated Complexity:** Medium
**Lines of Code:** ~300 lines

---

### Phase 2: Tool System Adapter (Priority: CRITICAL)
**Goal:** Make all local tools work with Claude's tool format

**Files to Create:**
- `claude-version/core/tool_adapter.py` - Tool schema converter
- `claude-version/core/tool_processor.py` - Tool execution handler

**Key Changes:**
1. Convert tool schemas: `function.parameters` → `input_schema`
2. Remove `type: "function"` wrapper
3. Adapt tool result format (tool message → user message with tool_result)
4. Handle Claude's tool_use blocks
5. Update tool_use_id tracking

**Estimated Complexity:** High
**Lines of Code:** ~400 lines

---

### Phase 3: Streaming & Tool Execution (Priority: CRITICAL)
**Goal:** Handle streaming responses and tool calling in loops

**Files to Modify:**
- `claude-version/core/api_client.py`
- `claude-version/core/tool_processor.py`

**Key Changes:**
1. Rewrite streaming parser for Claude events:
   - `content_block_start`
   - `content_block_delta`
   - `content_block_stop`
   - `message_stop`
2. Extract tool_use blocks from response
3. Execute tools and format results
4. Append tool results as user messages
5. Continue conversation loop

**Estimated Complexity:** High
**Lines of Code:** ~500 lines

---

### Phase 4: State Management Integration (Priority: HIGH)
**Goal:** Integrate with existing AppState, DB, ChromaDB

**Files to Create:**
- `claude-version/main.py` (adapted from original)

**Key Changes:**
1. Copy AppState class (minimal changes needed)
2. Keep SQLite schema unchanged
3. Keep ChromaDB setup unchanged
4. Update API call counters
5. Adapt rate limiter for Claude's limits

**Estimated Complexity:** Low
**Lines of Code:** ~200 lines (mostly copy)

---

### Phase 5: UI & Streamlit Integration (Priority: HIGH)
**Goal:** Get the Streamlit UI working with new backend

**Files to Modify:**
- `claude-version/main.py`

**Key Changes:**
1. Update sidebar model selector (Claude models)
2. Update model display names
3. Remove "thinking" visualization (Moonshot-specific)
4. Keep rest of UI unchanged
5. Update error messages for Claude errors

**Estimated Complexity:** Low
**Lines of Code:** ~100 lines changes

---

### Phase 6: Image Handling (Priority: MEDIUM)
**Goal:** Support vision capabilities with Claude's format

**Files to Modify:**
- `claude-version/core/message_converter.py`

**Key Changes:**
1. Convert `image_url` format to `image` type
2. Change base64 encoding format:
   - `image_url.url` → `source.data`
   - Add `media_type` field
3. Test with uploaded images

**Estimated Complexity:** Low
**Lines of Code:** ~50 lines

---

### Phase 7: Error Handling & Retry Logic (Priority: MEDIUM)
**Goal:** Handle Anthropic-specific errors gracefully

**Files to Modify:**
- `claude-version/core/api_client.py`

**Key Changes:**
1. Replace OpenAI exceptions with Anthropic ones
2. Update retry logic for Claude's error codes
3. Handle `overloaded_error` (Claude-specific)
4. Update rate limit backoff strategy
5. Better error messages for users

**Estimated Complexity:** Low
**Lines of Code:** ~100 lines

---

### Phase 8: Rate Limiting (Priority: MEDIUM)
**Goal:** Respect Claude's rate limits

**Files to Create:**
- `claude-version/core/rate_limiter.py`

**Key Changes:**
1. Update rate limits:
   - 50 requests/min (vs 100 for Moonshot)
   - 40k input tokens/min
   - 8k output tokens/min
2. Implement token counting with tiktoken
3. Add backoff when approaching limits
4. Display rate limit status in UI

**Estimated Complexity:** Medium
**Lines of Code:** ~150 lines

---

### Phase 9: Advanced Memory Features (Priority: LOW)
**Goal:** Ensure memory consolidation works with Claude

**Files to Modify:**
- Keep existing memory functions, update API calls

**Key Changes:**
1. Update `advanced_memory_consolidate` to use Claude
2. Update summarization calls to use Claude
3. Update chat log analysis to use Claude
4. Test memory retrieval and pruning

**Estimated Complexity:** Low
**Lines of Code:** ~50 lines

---

### Phase 10: Multi-Agent System (Priority: LOW)
**Goal:** Adapt agent spawning to Claude

**Files to Modify:**
- Agent spawn functions

**Key Changes:**
1. Update `agent_spawn` to use Claude client
2. Update Socratic council to use Claude
3. Update reflect_optimize to use Claude
4. Consider: Should sub-agents use cheaper models?

**Estimated Complexity:** Medium
**Lines of Code:** ~100 lines

---

### Phase 11: Native Tools Replacement (Priority: MEDIUM)
**Goal:** Replace Moonshot's native tools with local implementations

**Files to Create:**
- `claude-version/tools/web_search.py`
- `claude-version/tools/calculator.py`

**Key Changes:**
1. Implement web search using:
   - DuckDuckGo API (free)
   - Or Brave Search API
   - Or SerpAPI (paid)
2. Implement calculator using sympy (already in codebase)
3. Register as local tools
4. Remove Formula API calls

**Estimated Complexity:** Medium
**Lines of Code:** ~200 lines

---

### Phase 12: Testing & Validation (Priority: HIGH)
**Goal:** Comprehensive testing of all features

**Test Cases:**
1. Basic chat (no tools)
2. Single tool call
3. Multiple tool calls
4. Tool chains (tool → response → tool)
5. Memory insert/retrieve
6. File operations
7. Code execution
8. Image upload
9. Long conversations
10. Agent spawning
11. Error handling
12. Rate limiting

**Files to Create:**
- `claude-version/tests/test_api_client.py`
- `claude-version/tests/test_tools.py`
- `claude-version/tests/test_memory.py`

**Estimated Complexity:** Medium
**Lines of Code:** ~500 lines

---

## File Structure

```
claude-version/
├── main.py                      # Main Streamlit app (adapted)
├── .env.example                 # Environment template
├── requirements.txt             # Dependencies
├── README.md                    # Setup instructions
│
├── core/                        # Core API & message handling
│   ├── __init__.py
│   ├── api_client.py           # Anthropic client wrapper
│   ├── message_converter.py    # OpenAI ↔ Claude format
│   ├── tool_adapter.py         # Tool schema converter
│   ├── tool_processor.py       # Tool execution handler
│   ├── models.py               # Model configuration
│   └── rate_limiter.py         # Claude rate limiting
│
├── tools/                       # Local tool implementations
│   ├── __init__.py
│   ├── filesystem.py           # File operations
│   ├── code_execution.py       # Code runner
│   ├── memory.py               # Memory tools
│   ├── web_search.py           # Web search (replacing Moonshot native)
│   ├── calculator.py           # Calculator (replacing Moonshot native)
│   ├── git_ops.py              # Git operations
│   └── ...                     # Other tools
│
├── prompts/                     # System prompts
│   ├── default.txt
│   ├── coder.txt
│   └── tools-enabled.txt
│
├── sandbox/                     # Sandboxed execution environment
│   ├── db/
│   │   ├── chatapp.db          # SQLite database
│   │   └── chroma_db/          # ChromaDB vectors
│   ├── config/                 # YAML configs
│   └── agents/                 # Agent workspaces
│
├── docs/                        # Documentation
│   ├── MIGRATION_GUIDE.md      # API differences
│   ├── IMPLEMENTATION_PLAN.md  # This file
│   └── API_REFERENCE.md        # Code documentation
│
└── tests/                       # Test suite
    ├── __init__.py
    ├── test_api_client.py
    ├── test_tools.py
    ├── test_memory.py
    └── test_streaming.py
```

## Code Reuse Strategy

### Components to Keep Unchanged (~80% of code)
- ✅ All tool implementations (fs_*, memory_*, code_execution, etc.)
- ✅ AppState class (DB, ChromaDB setup)
- ✅ Memory system (insert, query, consolidate, prune)
- ✅ Streamlit UI structure
- ✅ Session state management
- ✅ Tool dispatcher core logic
- ✅ Sandbox filesystem operations
- ✅ Git operations
- ✅ Code linting
- ✅ Visualization functions
- ✅ YAML retrieval system

### Components to Adapt (~15% of code)
- 🔄 API client initialization
- 🔄 Message format converters
- 🔄 Tool schema generation
- 🔄 Streaming response handler
- 🔄 Tool result formatting
- 🔄 Error handling
- 🔄 Rate limiting
- 🔄 Model configuration

### Components to Replace (~5% of code)
- ❌ OpenAI SDK imports → Anthropic SDK
- ❌ Moonshot native tool calls → Local implementations
- ❌ Reasoning content handling (Kimi-specific)

## Risk Assessment

### High Risk Areas
1. **Tool Calling Loop** - Claude's format is very different. Must test extensively.
2. **Token Limits** - Claude's 8k output limit vs Moonshot's 256k. May break long responses.
3. **Streaming** - Event-based streaming is different. Need careful handling.

### Medium Risk Areas
1. **Rate Limits** - More restrictive than Moonshot. May need queuing.
2. **Image Format** - Different encoding. Need thorough testing.
3. **Memory Consolidation** - Uses LLM for summarization. Token limits may cause issues.

### Low Risk Areas
1. **Database/ChromaDB** - No changes needed
2. **UI** - Minimal changes
3. **Tool Implementations** - No changes needed

## Performance Considerations

### Claude Advantages
- Better instruction following → More reliable tool use
- Stronger reasoning → Better multi-step tasks
- Better code generation
- Vision in all models

### Claude Disadvantages
- Lower token limits (8k vs 256k output)
- Slower streaming startup
- More strict rate limits
- No native web search/calc

### Optimization Strategies
1. **Prompt Caching** - Use for system prompts and tool schemas
2. **Model Selection** - Use Haiku for simple tasks, Sonnet for complex ones
3. **Token Budgeting** - Implement aggressive context pruning
4. **Batching** - Queue requests when approaching rate limits

## Timeline Estimate

| Phase | Estimated Time | Priority |
|-------|---------------|----------|
| Phase 1: Core API | 4-6 hours | CRITICAL |
| Phase 2: Tool System | 6-8 hours | CRITICAL |
| Phase 3: Streaming | 4-6 hours | CRITICAL |
| Phase 4: State Mgmt | 2-3 hours | HIGH |
| Phase 5: UI | 2-3 hours | HIGH |
| Phase 6: Images | 1-2 hours | MEDIUM |
| Phase 7: Errors | 2-3 hours | MEDIUM |
| Phase 8: Rate Limiting | 3-4 hours | MEDIUM |
| Phase 9: Memory | 2-3 hours | LOW |
| Phase 10: Agents | 3-4 hours | LOW |
| Phase 11: Native Tools | 3-4 hours | MEDIUM |
| Phase 12: Testing | 6-8 hours | HIGH |
| **TOTAL** | **38-54 hours** | |

## Success Criteria

### Minimum Viable Product (MVP)
- ✅ Basic chat works
- ✅ System prompts work
- ✅ At least 5 tools work (filesystem, time, memory)
- ✅ Streaming responses work
- ✅ Tool calling loop works
- ✅ Conversations persist to DB
- ✅ Basic error handling

### Full Feature Parity
- ✅ All 30+ tools work
- ✅ Memory system fully functional
- ✅ Multi-agent spawning works
- ✅ Image upload works
- ✅ Web search replacement works
- ✅ Rate limiting implemented
- ✅ All error cases handled
- ✅ Comprehensive test coverage

## Next Steps

1. **Start with Phase 1** - Create `core/api_client.py` with basic Claude integration
2. **Create adapter utilities** - Message and tool format converters
3. **Test incrementally** - Don't move to next phase until current one works
4. **Keep original as reference** - Don't delete original/main.py
5. **Document as you go** - Update this plan with learnings

## Questions to Resolve

1. **Web Search:** Which API to use? DuckDuckGo (free) vs Brave (paid) vs SerpAPI (paid)?
2. **Model Strategy:** Always use Sonnet, or dynamically choose based on task?
3. **Token Management:** How to handle hitting 8k output limit mid-response?
4. **Prompt Caching:** Worth the complexity for cost savings?
5. **Dual-Provider Future:** How to structure for eventual dual-provider support?

## Resources

- [Anthropic API Docs](https://docs.anthropic.com/)
- [Claude Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [OpenAI to Claude Migration](https://docs.anthropic.com/en/api/migrating-from-openai)
- [Streaming Messages](https://docs.anthropic.com/en/api/streaming)
