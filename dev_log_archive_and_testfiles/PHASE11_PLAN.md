# Phase 11 Implementation Plan: Streaming Improvements

## Overview

Enhance the user experience by adding real-time streaming of responses, tool execution visibility, and progress indicators. Currently, the app shows a simple "Thinking..." spinner during API calls, with no visibility into text generation or tool execution progress.

**Goal:** Provide real-time feedback during all operations - text streaming, tool execution, agent status updates - for a more responsive and transparent user experience.

---

## Current State Analysis

### What Works:
- ✅ Basic API communication with Claude
- ✅ Tool calling loop completes successfully
- ✅ Multi-agent system with async execution
- ✅ Context management for long conversations

### Current Limitations:
- ❌ No real-time text streaming (blocks until complete response)
- ❌ No visibility into tool execution (what tool is running?)
- ❌ No partial tool results (wait for all tools to complete)
- ❌ Generic "Thinking..." spinner (not informative)
- ❌ Agent status requires manual refresh
- ❌ Multi-step tool chains appear frozen during execution

### Technical Foundation:
- `ClaudeAPIClient` already supports streaming (`stream=True` parameter)
- `ToolCallLoop.run()` is synchronous and non-streaming
- Streamlit supports `st.write_stream()` for streaming content
- Main loop in `main.py:1044` uses blocking `.run()` call

---

## Goals

### Primary Goals:
1. **Real-time Text Streaming** - Display text as it's generated (word-by-word)
2. **Tool Execution Visibility** - Show which tools are running
3. **Partial Tool Results** - Display tool results as they complete
4. **Progress Indicators** - Clear feedback for all long operations
5. **Agent Status Streaming** - Real-time agent progress updates

### Secondary Goals:
6. Better error handling during streaming
7. Cancellation support (future consideration)
8. Streaming for Socratic council voting
9. Performance metrics display (tokens/sec, time elapsed)

---

## Implementation Tasks

### Task 1: Add Streaming Response Handler
**File:** `core/streaming.py` (NEW)

**Purpose:** Core streaming infrastructure for text and tool execution

**Components:**
1. `StreamingResponseHandler` class
   - Handles streaming text chunks
   - Buffers and yields text incrementally
   - Emits events for tool use detection

2. `ToolExecutionTracker` class
   - Tracks running tools
   - Provides status updates
   - Emits progress events

3. `StreamEvent` dataclass
   - Event types: text_delta, tool_start, tool_complete, thinking, error
   - Carries event-specific data
   - Timestamp for each event

**Methods:**
```python
class StreamingResponseHandler:
    def __init__(self, api_client):
        self.api_client = api_client

    def stream_message(self, messages, system, model, tools, **kwargs):
        """Stream a message and yield events"""
        # Yields StreamEvent objects

    def process_stream_chunk(self, chunk):
        """Process individual stream chunk"""

class StreamEvent:
    event_type: str  # "text_delta", "tool_start", "tool_complete", "thinking"
    data: Any
    timestamp: float
```

**Lines:** ~250 lines

---

### Task 2: Update Tool Calling Loop for Streaming
**File:** `core/tool_processor.py` (MODIFY)

**Changes:**
1. Add `run_streaming()` method to `ToolCallLoop`
   - Parallel to existing `run()` method
   - Yields events during execution
   - Handles tool calls with streaming

2. Stream-aware tool execution
   - Emit tool start event before execution
   - Execute tool
   - Emit tool complete event with result
   - Continue streaming text

**New Method:**
```python
class ToolCallLoop:
    def run_streaming(
        self,
        messages,
        system,
        model,
        tools,
        **kwargs
    ) -> Generator[StreamEvent, None, Tuple[Any, List]]:
        """
        Run tool loop with streaming support.
        Yields StreamEvent objects during execution.
        Returns final (response, messages) tuple.
        """
        iteration = 0
        current_messages = messages.copy()

        while iteration < self.max_iterations:
            # Yield thinking event
            yield StreamEvent(
                event_type="thinking",
                data=f"Processing (step {iteration + 1})...",
                timestamp=time.time()
            )

            # Stream response
            for event in self.stream_handler.stream_message(...):
                yield event

                if event.event_type == "tool_use":
                    # Execute tool and yield result
                    tool_result = self.execute_tool(event.data)
                    yield StreamEvent(
                        event_type="tool_complete",
                        data=tool_result,
                        timestamp=time.time()
                    )

            # Check if done
            if stop_reason == "end_turn":
                break

        return response, current_messages
```

**Lines:** ~150 lines added

---

### Task 3: Create Streaming UI Components
**File:** `ui/streaming_display.py` (NEW)

**Purpose:** Streamlit components for displaying streaming content

**Components:**

1. `StreamingTextDisplay`
   - Container for streaming text
   - Updates in real-time
   - Handles markdown rendering

2. `ToolExecutionDisplay`
   - Shows currently executing tools
   - Progress bars for tool execution
   - Tool results as they complete

3. `StatusIndicator`
   - Animated indicator (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏)
   - Shows current operation
   - Time elapsed

**Usage:**
```python
with StreamingTextDisplay() as display:
    for event in stream_generator:
        if event.event_type == "text_delta":
            display.append(event.data)
        elif event.event_type == "tool_start":
            display.show_tool_start(event.data)
        elif event.event_type == "tool_complete":
            display.show_tool_result(event.data)
```

**Components:**
```python
class StreamingTextDisplay:
    """Display for streaming text content"""

    def __init__(self):
        self.container = st.empty()
        self.text_buffer = ""

    def append(self, text: str):
        """Append text to display"""
        self.text_buffer += text
        self.container.markdown(self.text_buffer)

    def finalize(self):
        """Mark display as complete"""
        # Add checkmark or completion indicator

class ToolExecutionDisplay:
    """Display for tool execution progress"""

    def __init__(self):
        self.tools_container = st.empty()
        self.active_tools = {}

    def start_tool(self, tool_name: str, tool_id: str):
        """Show tool starting"""
        self.active_tools[tool_id] = {
            "name": tool_name,
            "status": "running",
            "start_time": time.time()
        }
        self._render()

    def complete_tool(self, tool_id: str, result: Any):
        """Mark tool as complete"""
        if tool_id in self.active_tools:
            self.active_tools[tool_id]["status"] = "complete"
            self.active_tools[tool_id]["result"] = result
            self.active_tools[tool_id]["end_time"] = time.time()
        self._render()

    def _render(self):
        """Render current tool states"""
        with self.tools_container:
            for tool_id, tool_data in self.active_tools.items():
                status_emoji = "🔄" if tool_data["status"] == "running" else "✅"
                st.write(f"{status_emoji} **{tool_data['name']}**")
                if tool_data["status"] == "complete":
                    with st.expander("Result", expanded=False):
                        st.json(tool_data["result"])
```

**Lines:** ~200 lines

---

### Task 4: Integrate Streaming into Main Loop
**File:** `main.py` (MODIFY)

**Changes to `process_message()` function:**

1. Replace spinner with streaming display
2. Use `run_streaming()` instead of `run()`
3. Handle stream events in real-time
4. Update UI as events arrive

**Before (current):**
```python
with st.chat_message("assistant", avatar="🤖"):
    with st.spinner("Thinking..."):
        response, updated_messages = st.session_state.loop.run(...)
        response_text = extract_text_from_response(response)
        st.markdown(response_text)
```

**After (streaming):**
```python
with st.chat_message("assistant", avatar="🤖"):
    text_display = StreamingTextDisplay()
    tool_display = ToolExecutionDisplay()

    try:
        stream_gen = st.session_state.loop.run_streaming(
            messages=messages_for_api,
            system=st.session_state.system_prompt,
            model=st.session_state.model,
            max_tokens=st.session_state.max_tokens,
            tools=tools
        )

        response_text = ""
        for event in stream_gen:
            if event.event_type == "text_delta":
                text_display.append(event.data)
                response_text += event.data

            elif event.event_type == "tool_start":
                tool_display.start_tool(
                    event.data["name"],
                    event.data["id"]
                )

            elif event.event_type == "tool_complete":
                tool_display.complete_tool(
                    event.data["tool_id"],
                    event.data["result"]
                )

            elif event.event_type == "thinking":
                text_display.show_status(event.data)

        text_display.finalize()

        # Get final response from generator return
        response, updated_messages = stream_gen.return_value

    except Exception as e:
        st.error(f"Error during streaming: {e}")
```

**Lines:** ~100 lines modified

---

### Task 5: Add Agent Status Streaming
**File:** `tools/agents.py` (MODIFY)

**Purpose:** Real-time agent status updates

**Changes:**
1. Add progress callback to `Agent.execute()`
2. Emit status updates during execution
3. Store progress events in agent storage

**New Methods:**
```python
class Agent:
    def execute(self, progress_callback=None):
        """Execute agent with optional progress callback"""
        self.status = "running"
        self.started_at = datetime.now()

        if progress_callback:
            progress_callback("Agent started", 0.0)

        try:
            # Create message
            if progress_callback:
                progress_callback("Sending request to Claude...", 0.2)

            # Process with streaming
            for chunk in self.client.create_message(..., stream=True):
                if progress_callback:
                    progress_callback("Receiving response...", 0.5)
                # Process chunk

            if progress_callback:
                progress_callback("Complete", 1.0)

            self.status = "completed"

        except Exception as e:
            if progress_callback:
                progress_callback(f"Failed: {e}", -1.0)
            self.status = "failed"
```

**Agent Status Display in Sidebar:**
```python
# In sidebar agent list
for agent in agents_data:
    if agent["status"] == "running":
        # Show progress bar
        progress = agent.get("progress", 0.0)
        st.progress(progress)
        st.caption(agent.get("progress_message", "Running..."))
```

**Lines:** ~80 lines added/modified

---

### Task 6: Add Streaming Settings UI
**File:** `main.py` (MODIFY - Sidebar)

**Add to Settings Section:**

```python
st.divider()
st.subheader("⚡ Streaming Settings")

# Enable/disable streaming
st.session_state.streaming_enabled = st.toggle(
    "Enable Streaming",
    value=st.session_state.get("streaming_enabled", True),
    help="Stream responses in real-time (faster perceived response)"
)

if st.session_state.streaming_enabled:
    # Show tool execution
    st.session_state.show_tool_execution = st.toggle(
        "Show Tool Execution",
        value=st.session_state.get("show_tool_execution", True),
        help="Display tools as they execute"
    )

    # Show partial results
    st.session_state.show_partial_results = st.toggle(
        "Show Partial Tool Results",
        value=st.session_state.get("show_partial_results", True),
        help="Show tool results immediately when available"
    )

    # Streaming speed (for demo/testing)
    st.session_state.streaming_delay = st.slider(
        "Streaming Delay (ms)",
        min_value=0,
        max_value=100,
        value=0,
        help="Add artificial delay for testing (0 = full speed)"
    )
```

**Lines:** ~30 lines

---

### Task 7: Create Streaming Test Suite
**File:** `test_phase11.py` (NEW)

**Tests:**
1. ✅ Streaming handler initializes
2. ✅ Text streaming yields chunks
3. ✅ Tool events emitted correctly
4. ✅ Tool execution tracked properly
5. ✅ Stream completes successfully
6. ✅ Error handling during streaming
7. ✅ Multiple tool calls handled
8. ✅ Agent progress updates work
9. ✅ UI components render correctly
10. ✅ Streaming settings persist
11. ✅ Fallback to non-streaming works
12. ✅ Stream cancellation (if implemented)

**Lines:** ~350 lines

---

## UI Mockups

### Before (Current):
```
👤 User: Calculate 2+2 and tell me a joke

🤖 Assistant:
   ⏳ Thinking...

   [Waits 5-10 seconds]

   2+2 equals 4. Here's a joke: Why did the chicken cross the road...
```

### After (Streaming):
```
👤 User: Calculate 2+2 and tell me a joke

🤖 Assistant:
   🔄 calculator(a=2, b=2)  [0.5s]
   ✅ calculator → 4

   Let me calculate that for you. 2+2 equals 4.

   Now for a joke: Why did the chicken cross...
   [Text streams in word-by-word]
```

---

### Tool Execution Display:

**Single Tool:**
```
🔄 **search_web**
   Query: "Python best practices"
   ⏱️ 2.3s elapsed
```

**Multiple Tools (Parallel):**
```
✅ **read_file** (0.1s)
   └─ Result: 145 lines read

🔄 **search_code** (1.2s elapsed)
   └─ Searching for "def main"...

✅ **list_files** (0.05s)
   └─ Found 23 files
```

**Tool Results Expander:**
```
✅ **search_web** (2.3s)
   ▼ Result
     {
       "results": [
         {"title": "PEP 8", "url": "..."},
         ...
       ],
       "count": 10
     }
```

---

### Agent Status Streaming:

**Sidebar Agent Card (Running):**
```
🔄 agent_123456789
   Research quantum computing...
   Type: researcher

   [████████░░░░░░░░░░] 45%
   💬 Processing response...

   ⏱️ 12s elapsed
```

**Sidebar Agent Card (Completed):**
```
✅ agent_123456788
   Write documentation...
   Type: writer

   ✓ Complete (15s)
   [View Result]
```

---

## Technical Considerations

### Streaming vs Non-Streaming

**When to Use Streaming:**
- ✅ Regular user messages (text responses)
- ✅ Tool calling with user-facing actions
- ✅ Long-form content generation
- ✅ Multi-step reasoning tasks

**When to Skip Streaming:**
- ❌ Agent execution (background threads)
- ❌ Silent tool calls (internal operations)
- ❌ User preference (disabled in settings)

### Performance Impact

**Benefits:**
- Better perceived performance (faster time-to-first-token)
- User engagement during long operations
- Ability to read while still generating
- Transparency in tool usage

**Tradeoffs:**
- Slightly more complex code
- More UI updates (could affect performance)
- Requires careful state management

### Error Handling

**Scenarios:**
1. **Stream interruption** - Show partial content + error
2. **Tool execution failure** - Mark tool as failed in display
3. **Network issues** - Retry with exponential backoff
4. **User cancellation** - Future feature (stop generation)

---

## Session State Variables

New session state variables:

```python
# Streaming settings
st.session_state.streaming_enabled = True
st.session_state.show_tool_execution = True
st.session_state.show_partial_results = True
st.session_state.streaming_delay = 0  # ms

# Streaming state
st.session_state.current_stream = None  # Active stream generator
st.session_state.stream_buffer = ""  # Text buffer
st.session_state.active_tools = {}  # Currently executing tools
```

---

## Testing Strategy

### Unit Tests:
1. Test `StreamingResponseHandler` with mock API responses
2. Test `ToolExecutionTracker` state management
3. Test event emission and consumption
4. Test error handling during streaming

### Integration Tests:
1. Test full streaming flow (text + tools)
2. Test multi-tool execution display
3. Test agent progress updates
4. Test fallback to non-streaming

### Manual Testing:
1. Verify text streams smoothly (no lag)
2. Verify tool execution is visible
3. Verify agent status updates in real-time
4. Test with different models (Haiku/Sonnet/Opus)
5. Test with complex multi-step tasks
6. Test error scenarios (API failure, tool errors)

---

## Implementation Order

### Phase 1 - Core Streaming (Tasks 1-2)
1. Create `core/streaming.py`
2. Add streaming support to `ToolCallLoop`
3. Test basic streaming without UI

### Phase 2 - UI Components (Task 3)
4. Create `ui/streaming_display.py`
5. Test components in isolation
6. Verify rendering performance

### Phase 3 - Integration (Task 4)
7. Update `main.py` to use streaming
8. Handle all stream events
9. Test end-to-end flow

### Phase 4 - Enhancements (Tasks 5-6)
10. Add agent status streaming
11. Add settings UI
12. Test all features together

### Phase 5 - Testing & Polish (Task 7)
13. Create comprehensive test suite
14. Fix bugs and edge cases
15. Performance optimization
16. Documentation

---

## Success Criteria

Phase 11 will be considered complete when:

✅ Text streams in real-time (visible word-by-word generation)
✅ Tool execution is visible during processing
✅ Tool results display as they complete
✅ Agent status updates without manual refresh
✅ All 12 tests pass
✅ No performance degradation vs current non-streaming
✅ Settings allow enabling/disabling streaming
✅ Error handling works correctly during streaming
✅ Documentation updated with streaming features

---

## File Changes Summary

### New Files:
- `core/streaming.py` (~250 lines) - Streaming infrastructure
- `ui/streaming_display.py` (~200 lines) - UI components
- `test_phase11.py` (~350 lines) - Test suite
- `PHASE11_PLAN.md` (this file)
- `PHASE11_COMPLETE.md` (after implementation)
- `PHASE11_QUICKSTART.md` (after implementation)

### Modified Files:
- `core/tool_processor.py` (+~150 lines) - Add streaming to loop
- `tools/agents.py` (+~80 lines) - Agent progress updates
- `main.py` (~130 lines modified) - Streaming integration + settings
- `core/__init__.py` (~10 lines) - Export streaming classes

**Total New Code:** ~800 lines
**Total Modified Code:** ~220 lines

---

## Future Enhancements (Post-Phase 11)

Possible future additions:

1. **Stream Cancellation** - Stop generation mid-stream
2. **Token-by-Token Display** - Even more granular than word-by-word
3. **Streaming Cost Tracking** - Real-time cost updates during streaming
4. **Streaming Export** - Save streaming logs for debugging
5. **Parallel Tool Streaming** - Multiple tools streaming results simultaneously
6. **Voice Output** - TTS for streaming text
7. **Custom Streaming Animations** - User-configurable visual effects
8. **Streaming Performance Metrics** - Tokens/sec, latency graphs

---

## Dependencies

### Required:
- `anthropic` Python SDK (already installed) - has streaming support
- `streamlit` (already installed) - has `st.empty()` for updates

### No New Dependencies Needed! ✅

All required functionality is already available in existing dependencies.

---

## Risk Assessment

### Low Risk:
- ✅ Streaming API already available
- ✅ Streamlit supports real-time updates
- ✅ Can fallback to non-streaming if issues

### Medium Risk:
- ⚠️ Complex state management during streaming
- ⚠️ UI performance with frequent updates
- ⚠️ Error handling during partial streams

### Mitigation:
- Thorough testing of state transitions
- Performance monitoring during development
- Comprehensive error handling
- Fallback to non-streaming mode

---

## Notes

### Important Considerations:

1. **Backward Compatibility:** Non-streaming mode must still work (user setting)
2. **Performance:** Streaming should not slow down overall execution
3. **Error Recovery:** Partial streams must handle errors gracefully
4. **State Management:** Careful tracking of streaming state
5. **Testing:** Both streaming and non-streaming paths must be tested

### Edge Cases to Handle:

- Empty responses (no text generated)
- Tool-only responses (no text, just tool calls)
- Streaming errors mid-response
- Very fast responses (single chunk)
- Very slow responses (timeout scenarios)
- Multiple consecutive tool calls
- Nested tool calls (tool calling another tool)

---

## Estimated Effort

- **Core Streaming Infrastructure:** 4-6 hours
- **UI Components:** 3-4 hours
- **Integration:** 2-3 hours
- **Agent Status Streaming:** 2-3 hours
- **Testing:** 3-4 hours
- **Documentation:** 1-2 hours

**Total:** 15-22 hours of focused development

---

## Ready for Implementation?

This plan provides:
- ✅ Clear task breakdown (7 tasks)
- ✅ Detailed technical specifications
- ✅ UI mockups and examples
- ✅ Comprehensive testing strategy
- ✅ Success criteria
- ✅ Risk assessment

**Next Step:** Get user approval and proceed with implementation!

---

**Plan Status:** ✅ Ready for Review
**Created:** 2025-12-29
**Phase:** 11 - Streaming Improvements
