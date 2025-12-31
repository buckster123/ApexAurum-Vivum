---
name: apex-maintainer
description: Quick status check and onboarding for ApexAurum - Claude Edition project. Use when starting a new session, checking project status, verifying setup, getting oriented, or when asked about the project structure, what's working, what's pending, or how to continue development.
allowed-tools: Bash(find:*), Bash(ls:*), Bash(grep:*), Bash(wc:*), Read, Glob
---

# ApexAurum Project Maintainer

**Project:** ApexAurum - Claude Edition
**Type:** Production-grade AI chat platform with Claude API
**Status:** V1.0 Beta - 95% Complete, Production Ready
**Location:** `/home/llm/ApexAurum`

---

## Quick Orientation (2 minutes)

When starting a new session or asked about project status, follow these steps:

### 1. Run Health Check

```bash
cd `/home/llm/ApexAurum`

# Check tool count (should be 30)
python -c "from tools import ALL_TOOLS; print(f'✓ {len(ALL_TOOLS)} tools loaded')" 2>/dev/null || echo "⚠ Tools not loading"

# Check environment
test -f .env && echo "✓ Environment configured" || echo "⚠ Missing .env"

# Check if app is running
ps aux | grep streamlit | grep -v grep && echo "✓ Streamlit running" || echo "○ Streamlit not running"

# Check main.py exists
test -f main.py && wc -l main.py || echo "⚠ main.py missing"
```

### 2. Read Essential Documentation

**ALWAYS read these first (in order):**

1. **PROJECT_STATUS.md** (5 min) - Current state, what works, what's pending
   - Located: `/home/llm/ApexAurum/PROJECT_STATUS.md`/``
   - Contains: Current metrics, completeness status, pending work

2. **DEVELOPMENT_GUIDE.md** (scan as needed) - How to work with the codebase
   - Located: `/home/llm/ApexAurum/DEVELOPMENT_GUIDE.md`
   - Contains: Common tasks, troubleshooting, code navigation

3. If working on **agents**: Read `/home/llm/ApexAurum/dev_log_archive_and_testfiles/AGENT_INTEGRATION_TODO.md`
   - Agent system code complete, needs UI testing

### 3. Provide Status Summary

After checks, summarize:
- Tools count (should be 30)
- Environment status
- What's currently pending (check PROJECT_STATUS.md)
- Streamlit status
- Quick next steps

---

## What This Project Is

**ApexAurum - Claude Edition**: Production-grade Claude API chat interface with:

- 🤖 Multi-agent orchestration (spawn independent AI agents)
- 💰 50-90% cost savings (intelligent prompt caching)
- 🔍 Semantic search (vector embeddings, ChromaDB)
- 📚 Knowledge base (persistent memory)
- 🛠️ 30 tools (filesystem, web, code exec, agents, vector search, knowledge, etc.)
- 🧠 Context management (5 strategies, auto-summarization)
- ⚡ Real-time streaming responses

**Code Stats:**
- ~15,669 lines of production code
- 4,169 lines in main.py (Streamlit UI)
- 24 core modules, 7 tool modules, 2 UI modules
- 40+ documentation files
- 8 test suites

---

## Current Status

### ✅ What's Complete (95%)

- Core chat system (100%)
- Tool system with 30 tools (100%)
- Prompt caching with 4 strategies (100%)
- Context management with 5 strategies (100%)
- Vector search & knowledge base (100%)
- Conversation management (100%)
- Cost & rate tracking (100%)
- Beautiful Streamlit UI (100%)
- Multi-agent system CODE (100%)

### ⚠️ What's Pending (5%)

- **Agent UI Integration** - Code complete, needs testing
  - 5 agent tools created (`tools/agents.py`)
  - Tools registered (30 total)
  - Needs: Streamlit restart + UI testing
  - See: `/home/llm/ApexAurum/dev_log_archive_and_testfiles/AGENT_INTEGRATION_TODO.md`

- **Optional Enhancements**
  - Agent monitoring sidebar (optional)
  - Additional polish and refinements

---

## Project Structure

```
ApexAurum/
├── main.py                      ⭐ Main app (4,169 lines)
├── PROJECT_STATUS.md            📚 Current status report
├── DEVELOPMENT_GUIDE.md         📚 Developer onboarding
├── README.md                    📚 Project README
│
├── core/                        🔥 Core systems (24 files, ~9,500 lines)
│   ├── api_client.py            - Claude API wrapper
│   ├── cache_manager.py         - Prompt caching
│   ├── cost_tracker.py          - Cost tracking
│   ├── context_manager.py       - Context optimization
│   ├── vector_db.py             - Vector search
│   └── ...                      - 19 other modules
│
├── tools/                       🛠️ Tools (7 files, ~1,800 lines)
│   ├── agents.py                ⚠️ Needs UI testing
│   ├── utilities.py             - Core tools (time, calc, web)
│   ├── filesystem.py            - File operations
│   ├── memory.py                - Key-value storage
│   ├── code_execution.py        - Python execution
│   └── vector_search.py         - Search & knowledge
│
├── ui/                          🎨 UI components (2 files)
│   └── streaming_display.py     - Streaming text
│
├── sandbox/                     💾 Runtime storage
│   ├── conversations.json       - Saved conversations
│   ├── agents.json              - Agent state
│   └── memory.json              - Memory store
│
├── .claude/skills/              🤖 This skill!
│   └── apex-maintainer/
│
└── dev_log_archive_and_testfiles/  📚 Development docs
    ├── PHASE[1-14]_*.md         - 14 phase docs
    ├── V1.0_BETA_RELEASE.md    - Feature list
    ├── PROJECT_SUMMARY.md       - Dev journey
    ├── AGENT_INTEGRATION_TODO.md - Agent status
    └── test_*.py                - 8 test suites
```

---

## Common Tasks

### Starting the Application

```bash
cd /home/llm/claude/claude-version
streamlit run main.py

# Access at: http://localhost:8501
```

### Running Tests

```bash
# Individual tests
python test_basic.py
python test_agents.py

# Verify tool imports
python -c "from tools import ALL_TOOLS; print(f'✓ {len(ALL_TOOLS)} tools')"

# Test agent functionality
python -c "from tools.agents import agent_spawn; print('✓ Agent tools load')"
```

### Checking Logs

```bash
# Live monitoring
tail -f app.log

# Recent errors
grep ERROR app.log | tail -20
```

### Verifying Environment

```bash
# Check API key configured
grep ANTHROPIC_API_KEY .env | head -c 40

# Check Python version
python --version  # Should be 3.9+

# Check dependencies
pip list | grep -E "anthropic|streamlit|chromadb"
```

---

## Immediate Next Steps

### If Agent UI Testing Needed:

1. **Restart Streamlit:**
   ```bash
   pkill -f streamlit
   streamlit run main.py
   ```

2. **Verify 30 tools in UI:**
   - Check sidebar shows "✅ 30 tools available"
   - Expand "View Available Tools"
   - Look for: agent_spawn, agent_status, agent_result, agent_list, socratic_council

3. **Test via chat:**
   - "Spawn a researcher agent to find the capital of France"
   - "Check status of agent_[ID]"
   - "Get result from agent_[ID]"
   - "Run a council to decide: Python vs JavaScript"

4. **Mark complete** if tests pass

### If Adding Features:

1. Read DEVELOPMENT_GUIDE.md section on making changes
2. Follow existing patterns in relevant modules
3. Run tests after changes
4. Update documentation

### If Troubleshooting:

1. Check `tail -f app.log` for errors
2. Verify tool count: `python -c "from tools import ALL_TOOLS; print(len(ALL_TOOLS))"`
3. Check DEVELOPMENT_GUIDE.md troubleshooting section
4. Restart Streamlit if needed

---

## Key Commands Reference

```bash
# Project location
cd /home/llm/claude/claude-version

# Start app
streamlit run main.py

# Check tools
python -c "from tools import ALL_TOOLS; print(len(ALL_TOOLS))"

# View logs
tail -f app.log

# Run tests
python test_basic.py

# Check environment
cat .env

# Kill Streamlit
pkill -f streamlit

# Count code lines
wc -l core/*.py tools/*.py ui/*.py main.py

# Find code
grep -r "function_name" .

# Check processes
ps aux | grep streamlit
```

---

## Important Files for AI Assistants

**Read these in order for quick orientation:**

1. **PROJECT_STATUS.md** - Complete current state
2. **DEVELOPMENT_GUIDE.md** - How to work with code
3. **ai-assistant-notes.md** - Internal notes (this skill directory)
4. **AGENT_INTEGRATION_TODO.md** - Agent system status

**For deep dives:**
- `dev_log_archive_and_testfiles/V1.0_BETA_RELEASE.md` - All features
- `dev_log_archive_and_testfiles/PROJECT_SUMMARY.md` - Dev journey
- `dev_log_archive_and_testfiles/PHASE14_COMPLETE.md` - Caching details
- `dev_log_archive_and_testfiles/PHASE13.X_COMPLETE.md` - Vector search

---

## When User Asks...

### "What's the status?"
1. Run health check commands
2. Read PROJECT_STATUS.md
3. Summarize: tools count, what's complete, what's pending
4. Note any issues found

### "How do I get started?"
1. Show Quick Start from README.md
2. Verify environment (API keys in .env)
3. Guide through: pip install → configure .env → streamlit run

### "What's pending?"
1. Read PROJECT_STATUS.md "What's Pending" section
2. Currently: Agent UI testing
3. Point to AGENT_INTEGRATION_TODO.md

### "How do I [add/modify/test] something?"
1. Check DEVELOPMENT_GUIDE.md relevant section
2. Show example from existing code
3. Point to test files for reference

### "Where is [file/function/feature]?"
1. Use grep: `grep -r "search_term" .`
2. Check project structure in PROJECT_STATUS.md
3. Main locations: main.py (UI), core/ (systems), tools/ (tools)

---

## Success Indicators

**Everything is healthy when:**
- ✅ Tool count = 30
- ✅ .env file exists with ANTHROPIC_API_KEY
- ✅ `python -c "from tools import ALL_TOOLS"` succeeds
- ✅ main.py exists and is 4,169 lines
- ✅ Streamlit starts without errors
- ✅ Sidebar shows "30 tools available"

**Needs attention when:**
- ⚠️ Tool count ≠ 30
- ⚠️ Import errors
- ⚠️ Missing .env
- ⚠️ Streamlit crashes
- ⚠️ "Tools not loading" message

---

## Additional Resources

See companion files in this skill directory:
- `quick-commands.md` - Command reference sheet
- `ai-assistant-notes.md` - Internal notes for AI assistants

---

**Last Updated:** 2025-12-31
**Project Version:** 1.0 Beta
**Status:** Production Ready, Agent UI Testing Pending
