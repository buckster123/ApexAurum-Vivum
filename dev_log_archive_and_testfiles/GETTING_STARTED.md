# Getting Started with Apex Aurum Claude Edition

Welcome! This guide will help you get started with adapting the Moonshot-based Apex Aurum to use Claude's API.

## 📋 Project Status

**Current Phase:** Planning & Documentation Complete ✅

The project structure is set up, and comprehensive documentation has been created. You're ready to start implementation!

## 📁 What's Been Set Up

```
claude-version/
├── 📄 README.md                    # Main project overview
├── 📄 .env.example                 # Environment template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 requirements.txt             # Python dependencies
├── 📄 GETTING_STARTED.md          # This file!
│
├── 📂 prompts/                     # System prompts (to be created)
├── 📂 sandbox/                     # Sandboxed execution environment
│   ├── 📂 db/                     # SQLite + ChromaDB storage
│   ├── 📂 config/                 # YAML configurations
│   └── 📂 agents/                 # Agent workspaces
│
└── 📂 docs/                        # Comprehensive documentation
    ├── MIGRATION_GUIDE.md         # Detailed API differences
    ├── IMPLEMENTATION_PLAN.md     # 12-phase implementation plan
    └── QUICK_REFERENCE.md         # Code snippets & quick tips
```

## 🎯 What You Need to Do Next

### Option 1: Read & Plan (Recommended First Step)
Start by understanding the architecture and plan:

1. **Read the Migration Guide** (15 min)
   ```bash
   cat docs/MIGRATION_GUIDE.md
   ```
   Understand the key API differences between Moonshot and Claude.

2. **Review the Implementation Plan** (30 min)
   ```bash
   cat docs/IMPLEMENTATION_PLAN.md
   ```
   See the 12-phase plan with time estimates and priorities.

3. **Quick Reference** (5 min)
   ```bash
   cat docs/QUICK_REFERENCE.md
   ```
   Keep this open while coding for quick code snippets.

### Option 2: Jump Right In
If you want to start coding immediately:

1. **Set up environment:**
   ```bash
   cd claude-version
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure API key:**
   ```bash
   cp .env.example .env
   # Edit .env and add: ANTHROPIC_API_KEY=sk-ant-...
   ```

3. **Start with Phase 1** (Core API Client)
   Create `core/api_client.py` and implement basic Claude integration.
   See `docs/IMPLEMENTATION_PLAN.md` → Phase 1 for details.

## 📚 Documentation Guide

### Quick Lookup Table

| When you need... | Read this... |
|------------------|--------------|
| API syntax differences | `docs/QUICK_REFERENCE.md` |
| Understanding why things changed | `docs/MIGRATION_GUIDE.md` |
| Implementation step-by-step | `docs/IMPLEMENTATION_PLAN.md` |
| Project overview & features | `README.md` |
| Getting started | This file! |

### Documentation Breakdown

#### 1. MIGRATION_GUIDE.md (~2,500 words)
**What it covers:**
- Side-by-side comparison of Moonshot vs Claude APIs
- 11 critical differences explained in detail
- Common pitfalls and solutions
- Migration checklist
- Testing strategy

**When to read it:**
- Before starting any code changes
- When you encounter API differences
- When debugging format issues

#### 2. IMPLEMENTATION_PLAN.md (~4,000 words)
**What it covers:**
- 12 implementation phases with priorities
- Detailed file structure
- Estimated time per phase (38-54 hours total)
- Risk assessment
- Code reuse strategy (80% unchanged!)
- Success criteria

**When to read it:**
- Planning your work schedule
- Understanding the project scope
- Deciding what to implement first
- Tracking progress

#### 3. QUICK_REFERENCE.md (~1,500 words)
**What it covers:**
- Code snippets for common conversions
- Quick comparison tables
- Essential imports
- Tool schema converter functions
- Common pitfalls with examples

**When to read it:**
- While actively coding
- When you need a quick syntax reminder
- When converting specific components

#### 4. README.md (~3,000 words)
**What it covers:**
- Project overview and features
- Installation instructions
- Full tool list (30+ tools)
- Usage examples
- Configuration guide
- Troubleshooting

**When to read it:**
- Understanding what the app does
- Setting up for the first time
- Sharing with others

## 🚀 Recommended Implementation Order

### Week 1: Core Functionality (Critical)
**Goal:** Get basic chat working with Claude

- [ ] **Day 1-2: Phase 1** - Core API Client
  - Create `core/api_client.py`
  - Implement basic Claude API calls
  - Test with simple prompts (no tools)
  - *Estimated: 4-6 hours*

- [ ] **Day 3-4: Phase 2** - Tool System
  - Create `core/tool_adapter.py`
  - Convert tool schemas to Claude format
  - Test schema generation
  - *Estimated: 6-8 hours*

- [ ] **Day 5-7: Phase 3** - Streaming & Tools
  - Implement streaming handler
  - Tool execution loop
  - Test multi-turn conversations
  - *Estimated: 4-6 hours*

### Week 2: Integration & Essential Features
**Goal:** Full app running with essential tools

- [ ] **Day 8-9: Phase 4 & 5** - State & UI
  - Integrate AppState class
  - Update Streamlit UI
  - Test full app flow
  - *Estimated: 4-6 hours*

- [ ] **Day 10: Phase 6 & 7** - Images & Errors
  - Implement image handling
  - Error handling for Claude
  - *Estimated: 3-5 hours*

- [ ] **Day 11-12: Phase 8** - Rate Limiting
  - Implement rate limiter
  - Token counting
  - Test under load
  - *Estimated: 3-4 hours*

- [ ] **Day 13-14: Phase 12** - Testing
  - Write tests
  - Fix bugs
  - Document issues
  - *Estimated: 6-8 hours*

### Week 3: Advanced Features (Optional)
**Goal:** Feature parity with original

- [ ] **Phase 9:** Memory system
- [ ] **Phase 10:** Multi-agent system
- [ ] **Phase 11:** Native tools replacement

## 🧪 Testing Checkpoints

After each phase, test these scenarios:

### ✅ Phase 1 Complete
```python
# Can make basic API call?
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    system="You are helpful",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.content[0].text)
```

### ✅ Phase 2 Complete
```python
# Can convert tool schema?
openai_tool = {...}
claude_tool = convert_tool_schema(openai_tool)
assert "input_schema" in claude_tool
assert "function" not in claude_tool
```

### ✅ Phase 3 Complete
```python
# Can call tool and continue?
# Test: Ask Claude to read a file → execute tool → Claude responds
```

### ✅ Phase 5 Complete
```bash
# Can run full Streamlit app?
streamlit run main.py
# Navigate to localhost:8501
# Send a message
# Should see response
```

## 💡 Pro Tips for Implementation

### 1. Start Small, Test Often
Don't try to implement everything at once. Get one piece working, test it thoroughly, then move on.

```python
# Good: Test each component
def test_api_client():
    response = call_claude_simple()
    assert response is not None

def test_tool_conversion():
    converted = convert_tool_schema(sample_tool)
    assert validate_claude_format(converted)

# Bad: Test everything together
def test_everything():
    # 500 lines of untested code...
```

### 2. Keep Original as Reference
The original `main.py` is your source of truth. When in doubt, check how it was done there.

```bash
# Compare implementations
diff original/main.py claude-version/main.py
```

### 3. Use Type Hints
Makes debugging much easier:

```python
from anthropic.types import Message, TextBlock, ToolUseBlock

def process_message(msg: Message) -> str:
    """Clear input/output types"""
    ...
```

### 4. Log Everything (At First)
```python
import logging
logger.info(f"Sending to Claude: {messages}")
logger.info(f"Tool schema: {tool}")
logger.info(f"Response: {response}")
```

### 5. Test with Cheap Model First
Use `claude-3-5-haiku` for testing to save money:

```python
TEST_MODEL = "claude-3-5-haiku-20241022"  # Cheapest
PROD_MODEL = "claude-sonnet-4-5-20250929"  # Production
```

## 🐛 Common Issues & Solutions

### "System message in messages array"
```python
# WRONG
messages = [{"role": "system", "content": "..."}]

# RIGHT
system = "..."
messages = []  # No system here
response = client.messages.create(system=system, messages=messages, ...)
```

### "Tool results not working"
```python
# WRONG
messages.append({"role": "tool", "content": result})

# RIGHT
messages.append({
    "role": "user",
    "content": [{"type": "tool_result", "tool_use_id": id, "content": result}]
})
```

### "Response not streaming"
```python
# Make sure to iterate over events
for event in response:
    if event.type == "content_block_delta":
        print(event.delta.text)
```

## 📞 Getting Help

### Before Asking for Help:
1. ✅ Check `app.log` for error messages
2. ✅ Read the error message carefully (Claude's are usually clear)
3. ✅ Search in `docs/QUICK_REFERENCE.md`
4. ✅ Compare with `original/main.py`
5. ✅ Check [Anthropic Docs](https://docs.anthropic.com/)

### Where to Get Help:
- 📖 Anthropic's official documentation
- 💬 Anthropic Discord/Community
- 📧 Anthropic support (for API issues)
- 🐛 GitHub Issues (for this project)

## 🎓 Learning Resources

### Essential Reading
1. [Anthropic API Docs](https://docs.anthropic.com/)
2. [Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
3. [Streaming Guide](https://docs.anthropic.com/en/api/streaming)

### Example Projects
1. [Anthropic Quickstarts](https://github.com/anthropics/anthropic-quickstarts)
2. [Tool Use Examples](https://github.com/anthropics/anthropic-cookbook)

## 🏁 Success Milestones

Track your progress:

- [ ] **Milestone 1:** Hello World - Basic API call works
- [ ] **Milestone 2:** First Tool - One tool call works end-to-end
- [ ] **Milestone 3:** Tool Loop - Multiple tool calls in sequence work
- [ ] **Milestone 4:** UI Live - Streamlit app running
- [ ] **Milestone 5:** Full Chat - Complete conversation with tools
- [ ] **Milestone 6:** Memory Works - Can store and retrieve memories
- [ ] **Milestone 7:** Images Work - Can analyze uploaded images
- [ ] **Milestone 8:** All Tools Work - All 30+ tools functional
- [ ] **Milestone 9:** Production Ready - Error handling, rate limiting, tests
- [ ] **Milestone 10:** Feature Parity - Matches all original functionality

## 🎯 Quick Start Commands

```bash
# 1. Setup
cd claude-version
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your API key

# 3. Create first file
mkdir -p core
touch core/__init__.py
touch core/api_client.py

# 4. Start coding!
# Follow Phase 1 in docs/IMPLEMENTATION_PLAN.md
```

## 📝 Your First Task

**Right now, do this:**

1. Read `docs/QUICK_REFERENCE.md` (10 minutes)
2. Set up your virtual environment
3. Install dependencies
4. Create `core/api_client.py`
5. Write a simple function to call Claude API
6. Test it!

**Example first function:**
```python
# core/api_client.py
from anthropic import Anthropic
import os

def test_claude_connection():
    """Test basic Claude API connection"""
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        system="You are a helpful assistant.",
        messages=[{"role": "user", "content": "Say hello in one sentence."}]
    )

    return response.content[0].text

if __name__ == "__main__":
    result = test_claude_connection()
    print(f"Claude says: {result}")
```

Run it:
```bash
python core/api_client.py
```

If you see a response from Claude, congratulations! You're ready to continue with Phase 1.

---

## 🙌 You Got This!

Remember:
- **80% of the code** doesn't need to change
- **Documentation** is your friend
- **Test often** to catch issues early
- **Start simple** and build up
- **Ask questions** when stuck

The hard part (planning and documentation) is done. Now it's just execution!

Good luck! 🚀
