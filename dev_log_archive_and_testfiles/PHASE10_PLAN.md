# Phase 10 Implementation Plan: Agent Tools UI & Management

## Overview

The agent tools are **already fully implemented** in `tools/agents.py`:
- ✅ `agent_spawn` - Spawn sub-agents
- ✅ `agent_status` - Check agent status
- ✅ `agent_result` - Get agent results
- ✅ `agent_list` - List all agents
- ✅ `socratic_council` - Multi-agent voting

**What Phase 10 Adds:** UI and management interface for users to:
- View active agents in real-time
- Spawn agents manually (without asking Claude)
- Monitor agent progress
- View agent results
- Manage agent history
- Run Socratic councils from UI

---

## Current State Verification

### Tools Implementation ✅

**File:** `tools/agents.py` (657 lines)

**Features:**
- `AgentManager` class with persistence
- Thread-based async execution
- 5 agent types (general, researcher, coder, analyst, writer)
- Tool calling support for agents
- Socratic council voting system
- JSON storage in `./sandbox/agents.json`

**Registration:** ✅ Registered in `tools/__init__.py`

### What's Missing

**UI Components:**
- ❌ Agent management panel
- ❌ Active agents viewer
- ❌ Manual spawn interface
- ❌ Status monitoring
- ❌ Results display
- ❌ Socratic council UI

---

## Implementation Tasks

### Task 1: Agent Management UI (Sidebar Panel)

**File:** `main.py` (sidebar section)

**Purpose:** Central panel for viewing and managing agents

**UI Layout:**
```
📦 Agent Management
└─ Active Agents (X running)

   [Refresh Status]

   Agent #agent_123
   Type: researcher
   Status: 🔄 Running
   Task: "Research Python history..."
   Started: 2m ago
   [View Result] [Cancel]

   Agent #agent_456
   Type: coder
   Status: ✅ Completed
   Task: "Write a sorting algorithm..."
   Completed: 5m ago
   [View Result] [Delete]

   ───────────────────────────

   [➕ Spawn New Agent]
   [🗳️ Run Socratic Council]

   Statistics:
   • Total Agents: 12
   • Running: 2
   • Completed: 9
   • Failed: 1
```

**Implementation:**
```python
st.divider()
st.subheader("📦 Agent Management")
with st.expander("Multi-Agent System", expanded=False):
    # Import agent manager
    from tools.agents import _agent_manager

    # Refresh button
    if st.button("🔄 Refresh Status", key="refresh_agents"):
        st.rerun()

    # Get all agents
    agents_data = _agent_manager.list_agents()

    if agents_data:
        # Count by status
        running = sum(1 for a in agents_data if a["status"] == "running")
        completed = sum(1 for a in agents_data if a["status"] == "completed")
        failed = sum(1 for a in agents_data if a["status"] == "failed")

        st.caption(f"**Active Agents ({running} running)**")

        # Display each agent
        for agent in agents_data:
            with st.container():
                # Status emoji
                status_emoji = {
                    "pending": "⏳",
                    "running": "🔄",
                    "completed": "✅",
                    "failed": "❌"
                }

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"{status_emoji.get(agent['status'], '❔')} **Agent #{agent['agent_id'][-6:]}**")
                    st.caption(f"Type: {agent['agent_type']} | Status: {agent['status']}")

                    # Truncate task
                    task = agent['task'][:50] + "..." if len(agent['task']) > 50 else agent['task']
                    st.caption(f"Task: *{task}*")

                with col2:
                    if agent['status'] == 'completed':
                        if st.button("📄 Result", key=f"result_{agent['agent_id']}"):
                            # Store agent ID for result display
                            st.session_state.view_agent_result = agent['agent_id']
                            st.rerun()
                    elif agent['status'] == 'running':
                        st.caption("In progress...")

                st.divider()

        # Statistics
        st.caption("**Statistics:**")
        st.caption(f"• Total: {len(agents_data)} | Running: {running} | Completed: {completed} | Failed: {failed}")

    else:
        st.info("No agents spawned yet")

    # Action buttons
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Spawn Agent", key="spawn_agent_btn", use_container_width=True):
            st.session_state.show_spawn_agent = True
            st.rerun()
    with col2:
        if st.button("🗳️ Council", key="council_btn", use_container_width=True):
            st.session_state.show_council = True
            st.rerun()
```

---

### Task 2: Spawn Agent Dialog

**File:** `main.py` (after sidebar or in main area)

**Purpose:** Manual agent spawning interface

**UI Layout:**
```
Spawn New Agent

Task Description:
[Text area - "Describe the task for the agent..."]

Agent Type:
( ) General - Any task
(•) Researcher - Research and gather information
( ) Coder - Write and explain code
( ) Analyst - Analyze data and provide insights
( ) Writer - Create content

Model:
[Dropdown: Haiku (fast/cheap) / Sonnet (balanced) / Opus (best)]

Run Mode:
☑ Run in background (async)

[Cancel]  [Spawn Agent]
```

**Implementation:**
```python
# In main chat area or modal
if st.session_state.get("show_spawn_agent", False):
    st.markdown("### ➕ Spawn New Agent")

    with st.form("spawn_agent_form"):
        task = st.text_area(
            "Task Description",
            placeholder="Describe the task for the agent...",
            height=100,
            help="Be specific about what you want the agent to do"
        )

        agent_type = st.radio(
            "Agent Type",
            options=[
                "general - Any task",
                "researcher - Research and gather information",
                "coder - Write and explain code",
                "analyst - Analyze data and provide insights",
                "writer - Create content"
            ],
            help="Choose the type of agent based on the task"
        )

        model = st.selectbox(
            "Model",
            options=[
                "Haiku (fast & cheap)",
                "Sonnet (balanced)",
                "Opus (best quality)"
            ],
            index=0,
            help="Haiku recommended for most tasks"
        )

        run_async = st.checkbox(
            "Run in background",
            value=True,
            help="Run asynchronously (recommended)"
        )

        col1, col2 = st.columns(2)
        with col1:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        with col2:
            spawn = st.form_submit_button("Spawn Agent", type="primary", use_container_width=True)

        if cancel:
            st.session_state.show_spawn_agent = False
            st.rerun()

        if spawn and task:
            # Parse agent type
            agent_type_key = agent_type.split(" -")[0].strip()

            # Parse model
            model_map = {
                "Haiku (fast & cheap)": "claude-3-5-haiku-20241022",
                "Sonnet (balanced)": "claude-3-7-sonnet-20250219",
                "Opus (best quality)": "claude-opus-4-20250514"
            }
            model_id = model_map[model]

            # Spawn agent
            from tools.agents import agent_spawn

            result = agent_spawn(
                task=task,
                agent_type=agent_type_key,
                model=model_id,
                run_async=run_async
            )

            if result.get("success"):
                st.success(f"✅ Agent spawned: {result.get('agent_id')}")
                st.session_state.show_spawn_agent = False
                st.rerun()
            else:
                st.error(f"❌ Error: {result.get('error')}")
```

---

### Task 3: Agent Result Viewer

**File:** `main.py` (main area)

**Purpose:** Display agent results in detail

**UI Layout:**
```
📄 Agent Result

Agent: #agent_123
Type: researcher
Status: ✅ Completed

Task:
"Research the history of Python programming language"

Result:
[Full result text displayed here, with markdown rendering]

Runtime: 45 seconds
Completed: 2024-12-29 14:30:15

[Copy Result]  [Close]
```

**Implementation:**
```python
# In main area
if st.session_state.get("view_agent_result"):
    agent_id = st.session_state.view_agent_result

    from tools.agents import agent_result, _agent_manager

    st.markdown("### 📄 Agent Result")

    result_data = agent_result(agent_id)

    if result_data.get("found"):
        agent = _agent_manager.get_agent(agent_id)

        # Agent info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Agent ID", f"#{agent_id[-6:]}")
        with col2:
            st.metric("Type", agent.agent_type)
        with col3:
            st.metric("Status", result_data.get("status"))

        # Task
        st.markdown("**Task:**")
        st.info(result_data.get("task"))

        # Result
        if result_data.get("status") == "completed":
            st.markdown("**Result:**")
            st.markdown(result_data.get("result"))

            # Runtime
            if agent.started_at and agent.completed_at:
                runtime = (agent.completed_at - agent.started_at).total_seconds()
                st.caption(f"Runtime: {runtime:.1f} seconds")

        elif result_data.get("status") == "failed":
            st.error(f"**Error:** {result_data.get('error')}")

        # Actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 Copy Result", use_container_width=True):
                # Copy to clipboard (requires streamlit >= 1.30)
                pass
        with col2:
            if st.button("❌ Close", use_container_width=True):
                del st.session_state.view_agent_result
                st.rerun()
    else:
        st.error("Agent not found")
        if st.button("Close"):
            del st.session_state.view_agent_result
            st.rerun()
```

---

### Task 4: Socratic Council UI

**File:** `main.py` (main area)

**Purpose:** Run multi-agent voting from UI

**UI Layout:**
```
🗳️ Socratic Council - Multi-Agent Voting

Question:
[Text input: "What question should the agents vote on?"]

Options: (2-5 options)
Option 1: [Text input]
Option 2: [Text input]
[+ Add Option]

Number of Agents: [Slider: 3-9, step 2]
Model: [Dropdown: Sonnet / Opus]

[Cancel]  [Run Council]

───────────────────────────

Results:
Winner: FastAPI (5/7 votes) ✅

Votes:
• FastAPI: █████ 5
• Flask: ██ 2
• Django: 0

Agent Reasoning:
Agent 1 → FastAPI: "Modern async support..."
Agent 2 → FastAPI: "Great documentation..."
Agent 3 → Flask: "Simpler for small projects..."
[Show all reasoning]
```

**Implementation:**
```python
if st.session_state.get("show_council", False):
    st.markdown("### 🗳️ Socratic Council - Multi-Agent Voting")

    with st.form("socratic_council_form"):
        question = st.text_input(
            "Question",
            placeholder="What question should the agents vote on?",
            help="Be clear and specific"
        )

        st.write("**Options** (2-5 options):")

        # Dynamic options
        if "council_options" not in st.session_state:
            st.session_state.council_options = ["", ""]

        options = []
        for i in range(len(st.session_state.council_options)):
            opt = st.text_input(
                f"Option {i+1}",
                value=st.session_state.council_options[i],
                key=f"opt_{i}"
            )
            if opt:
                options.append(opt)

        if len(st.session_state.council_options) < 5:
            if st.form_submit_button("➕ Add Option"):
                st.session_state.council_options.append("")
                st.rerun()

        num_agents = st.slider(
            "Number of Agents",
            min_value=3,
            max_value=9,
            value=3,
            step=2,
            help="Use odd numbers to avoid ties"
        )

        model = st.selectbox(
            "Model",
            options=["Sonnet (recommended)", "Opus (best reasoning)"],
            help="Sonnet provides good balance of quality and cost"
        )

        col1, col2 = st.columns(2)
        with col1:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        with col2:
            run = st.form_submit_button("Run Council", type="primary", use_container_width=True)

        if cancel:
            st.session_state.show_council = False
            st.session_state.council_options = ["", ""]
            st.rerun()

        if run and question and len(options) >= 2:
            # Run council
            from tools.agents import socratic_council

            model_id = "claude-3-7-sonnet-20250219" if "Sonnet" in model else "claude-opus-4-20250514"

            with st.spinner(f"Running council with {num_agents} agents..."):
                result = socratic_council(
                    question=question,
                    options=options,
                    num_agents=num_agents,
                    model=model_id
                )

            if result.get("success"):
                st.success("✅ Council completed!")

                # Display results
                st.markdown("### Results")

                winner = result.get("winner")
                votes = result.get("votes")
                winner_votes = result.get("winner_votes")

                st.metric("Winner", f"{winner} ({winner_votes}/{num_agents} votes)")

                # Vote chart
                st.write("**Votes:**")
                for opt, count in votes.items():
                    bar = "█" * count
                    st.write(f"• {opt}: {bar} {count}")

                # Reasoning
                st.write("**Agent Reasoning:**")
                for item in result.get("reasoning", []):
                    with st.expander(f"Agent {item['agent']} → {item['vote']}"):
                        st.write(item['reasoning'])

            else:
                st.error(f"❌ Error: {result.get('error')}")
```

---

### Task 5: Session State Initialization

**File:** `main.py` (init_session_state function)

**Purpose:** Initialize agent-related session state

**Implementation:**
```python
def init_session_state():
    # ... existing initialization ...

    # Agent UI state (Phase 10)
    if "show_spawn_agent" not in st.session_state:
        st.session_state.show_spawn_agent = False

    if "show_council" not in st.session_state:
        st.session_state.show_council = False

    if "council_options" not in st.session_state:
        st.session_state.council_options = ["", ""]

    if "view_agent_result" not in st.session_state:
        st.session_state.view_agent_result = None

    if "agent_refresh_interval" not in st.session_state:
        st.session_state.agent_refresh_interval = 10  # seconds
```

---

### Task 6: Real-Time Agent Monitoring (Optional Enhancement)

**File:** `main.py`

**Purpose:** Auto-refresh agent status

**Implementation:**
```python
import time

# In sidebar agent section
if agents_data and any(a["status"] == "running" for a in agents_data):
    # Auto-refresh for running agents
    st.caption("🔄 Auto-refresh enabled (every 10s)")

    # Use st.empty() for dynamic updates
    if "last_agent_refresh" not in st.session_state:
        st.session_state.last_agent_refresh = time.time()

    # Check if it's time to refresh
    if time.time() - st.session_state.last_agent_refresh > st.session_state.agent_refresh_interval:
        st.session_state.last_agent_refresh = time.time()
        st.rerun()
```

---

### Task 7: Testing

**File:** `test_phase10.py`

**Purpose:** Test agent UI integration

**Test Coverage:**
```python
# Test 1: Agent tools are registered
def test_agent_tools_registered():
    from tools import ALL_TOOL_SCHEMAS
    assert "agent_spawn" in ALL_TOOL_SCHEMAS
    assert "agent_status" in ALL_TOOL_SCHEMAS
    assert "agent_result" in ALL_TOOL_SCHEMAS
    assert "agent_list" in ALL_TOOL_SCHEMAS
    assert "socratic_council" in ALL_TOOL_SCHEMAS

# Test 2: Agent manager initializes
def test_agent_manager():
    from tools.agents import _agent_manager
    assert _agent_manager is not None
    agents = _agent_manager.list_agents()
    assert isinstance(agents, list)

# Test 3: Agent spawn works
def test_agent_spawn():
    from tools.agents import agent_spawn
    result = agent_spawn(
        task="Test task",
        agent_type="general",
        run_async=False
    )
    assert result.get("success") == True
    assert "agent_id" in result

# Test 4: Agent status works
def test_agent_status():
    from tools.agents import agent_spawn, agent_status
    result = agent_spawn("Test", run_async=False)
    agent_id = result["agent_id"]

    status = agent_status(agent_id)
    assert status.get("found") == True
    assert status.get("status") in ["completed", "failed"]

# Test 5: Agent result retrieval
def test_agent_result():
    from tools.agents import agent_spawn, agent_result
    result = agent_spawn("Say hello", run_async=False)
    agent_id = result["agent_id"]

    result_data = agent_result(agent_id)
    assert result_data.get("found") == True

# Test 6: Socratic council
def test_socratic_council():
    from tools.agents import socratic_council
    result = socratic_council(
        question="Which is best?",
        options=["A", "B"],
        num_agents=3
    )
    assert result.get("success") == True
    assert "winner" in result

# Test 7: UI imports
def test_ui_imports():
    with open('main.py', 'r') as f:
        content = f.read()
    assert 'Agent Management' in content
    assert 'agent_spawn' in content

# Test 8: Session state
def test_session_state():
    with open('main.py', 'r') as f:
        content = f.read()
    assert 'show_spawn_agent' in content
    assert 'show_council' in content
```

---

## Implementation Order

### Phase 1: Core UI (Tasks 1-2)
1. Add agent management panel to sidebar
2. Implement spawn agent dialog

### Phase 2: Viewing & Results (Task 3)
3. Add agent result viewer

### Phase 3: Socratic Council (Task 4)
4. Implement council UI

### Phase 4: Polish (Tasks 5-6)
5. Session state initialization
6. Optional: Real-time monitoring

### Phase 5: Testing (Task 7)
7. Create and run test suite

---

## Benefits Summary

### For Users:
✅ **Visual agent management** - See all agents at a glance
✅ **Manual spawning** - Don't need to ask Claude
✅ **Real-time monitoring** - Watch agents work
✅ **Easy results** - View results with one click
✅ **Socratic voting** - Run multi-agent decisions from UI

### For System:
✅ **No code changes to agent tools** - Tools already work
✅ **Clean separation** - UI separate from logic
✅ **Progressive enhancement** - Can use via Claude OR UI
✅ **Full transparency** - Users see agent activity

---

## UI Mockup Summary

**Sidebar Panel:**
```
📦 Agent Management
├── Active Agents (2 running)
├── Agent list with status
├── Action buttons (Spawn, Council)
└── Statistics
```

**Main Area Dialogs:**
```
➕ Spawn Agent
├── Task description
├── Agent type selector
├── Model selector
└── Run mode toggle

📄 Agent Result
├── Agent info
├── Task display
├── Result content
└── Actions (Copy, Close)

🗳️ Socratic Council
├── Question input
├── Options (2-5)
├── Agent count
├── Results display
└── Reasoning breakdown
```

---

## Success Metrics

Phase 10 is successful when:

1. ✅ Agent management panel displays in sidebar
2. ✅ Users can spawn agents manually
3. ✅ Agent status updates in real-time
4. ✅ Results display correctly
5. ✅ Socratic council runs from UI
6. ✅ All tests pass (8/8)
7. ✅ Agent tools still work via Claude

---

## Notes

### Existing Code is Solid:

The agent implementation in `tools/agents.py` is:
- ✅ Well-structured (Agent class, AgentManager)
- ✅ Properly registered
- ✅ Thread-safe (async execution)
- ✅ Persistent (JSON storage)
- ✅ Feature-complete (5 agent types, 5 tools)

**No changes needed to agent tools!**

### UI Focus:

Phase 10 is **purely additive** - adding UI on top of working tools:
- No breaking changes
- Tools continue to work via Claude
- UI provides alternative access method
- Progressive enhancement

---

## Ready to Implement! 🚀

This plan provides:
- 7 clear tasks with specific deliverables
- Detailed UI mockups and code examples
- Complete test plan
- Implementation order

Estimated complexity: **Medium**
Estimated time: **3-4 hours** (mostly UI work)

Let's build Phase 10!
