# Phase 10 Quickstart: Agent Tools UI & Management

Quick reference for using Phase 10 multi-agent features.

---

## Testing

Run the test suite:

```bash
venv/bin/python test_phase10.py
```

Expected: All 12 tests pass ✅

---

## Quick Overview

**What it does:** Enables spawning specialized AI agents, running them in parallel, and using Socratic council voting for consensus decisions.

**How it works:** Agents execute tasks independently in background threads, with results stored persistently. UI provides full management and result viewing.

**User impact:** Can delegate work to multiple agents simultaneously, get consensus on decisions, and manage complex workflows.

---

## Accessing Agent Management

**Location:** Sidebar → "📦 Agent Management" → "Multi-Agent System"

### What You'll See:

```
Multi-Agent System:
🔄 Refresh Status

Running: 2  Completed: 5  Failed: 0

Recent Agents:
⏳ agent_123456789
   Research quantum computing...
   Type: researcher

✅ agent_123456788
   Write documentation for Phase 10
   Type: writer
   [View Result]

➕ Spawn New Agent
🗳️ Start Socratic Council
```

---

## Agent Types

| Type | Icon | Best For |
|------|------|----------|
| **General** | 🤖 | Any task, general questions |
| **Researcher** | 🔍 | Research, information gathering |
| **Coder** | 💻 | Programming, code tasks |
| **Analyst** | 📊 | Data analysis, insights |
| **Writer** | ✍️ | Content creation, documentation |

---

## Common Actions

### Spawn a New Agent

1. Click "➕ Spawn New Agent" in sidebar
2. Fill in task description (detailed = better results)
3. Select agent type
4. Choose model:
   - **Haiku**: Fast & cheap (simple tasks)
   - **Sonnet**: Balanced (most tasks)
   - **Opus**: Best quality (complex tasks)
5. Toggle "Run in background" for async
6. Click "Spawn Agent"
7. Agent appears in list immediately

### View Agent Results

1. Wait for agent to show ✅ Completed
2. Click "View Result" button
3. See full agent details:
   - Agent ID and type
   - Original task
   - Complete result
   - Runtime
4. Click "Close" to return

### Run Socratic Council

1. Click "🗳️ Start Socratic Council"
2. Enter your question
3. Add 2-5 options (click "Add Option" for more)
4. Set number of agents (3-7 recommended)
5. Choose model
6. Click "Start Vote"
7. Wait for results (voting happens in parallel)
8. See winner with vote breakdown

### Refresh Agent List

- Click "🔄 Refresh Status" to update
- Auto-refresh every 10 seconds (configurable)
- Status updates: Pending → Running → Completed/Failed

---

## Model Selection Guide

### When to use each model:

**Haiku** (Fast & Cheap)
- Simple questions
- Quick tasks
- Large numbers of agents (council with 10+ agents)
- Repetitive operations

**Sonnet** (Balanced) ⭐ DEFAULT
- Most general tasks
- Moderate complexity
- Best value for quality
- Recommended for councils

**Opus** (Best Quality)
- Complex reasoning
- Critical decisions
- Technical analysis
- Important research

---

## Socratic Council Strategies

### Small Council (3 agents)
- Quick consensus
- Simple decisions
- Lower cost
- May lack diversity

### Medium Council (5-7 agents) ⭐ RECOMMENDED
- Balanced perspectives
- Good consensus strength
- Reasonable cost/time
- Diverse viewpoints

### Large Council (10 agents)
- High confidence decisions
- Very diverse perspectives
- Higher cost/time
- Overkill for simple choices

---

## Usage Examples

### Example 1: Parallel Research
```
Goal: Research 3 different topics simultaneously

1. Spawn Agent 1:
   Task: "Research latest ML frameworks in 2024"
   Type: Researcher, Model: Sonnet, Async: Yes

2. Spawn Agent 2:
   Task: "Research web security best practices"
   Type: Researcher, Model: Sonnet, Async: Yes

3. Spawn Agent 3:
   Task: "Research API design patterns"
   Type: Researcher, Model: Sonnet, Async: Yes

4. All run in parallel (saves time)
5. View each result when completed
```

### Example 2: Code Review Council
```
Goal: Get consensus on best implementation

1. Start Socratic Council
2. Question: "Which implementation is better?"
3. Options:
   - Implementation A (recursive)
   - Implementation B (iterative)
   - Implementation C (functional)
4. Agents: 5, Model: Sonnet
5. Results show technical consensus
```

### Example 3: Content Creation
```
Goal: Generate different content pieces

1. Spawn Writer Agent 1:
   Task: "Write README for Phase 10"
   Type: Writer, Model: Sonnet

2. Spawn Writer Agent 2:
   Task: "Write API documentation"
   Type: Writer, Model: Haiku

3. Spawn Writer Agent 3:
   Task: "Write user guide"
   Type: Writer, Model: Sonnet

4. Get all content pieces simultaneously
```

### Example 4: Decision Making
```
Goal: Choose architecture for project

1. Start Socratic Council
2. Question: "Best architecture for this project?"
3. Options:
   - Microservices
   - Monolith
   - Serverless
4. Agents: 7, Model: Sonnet
5. Get data-driven decision with reasoning
```

---

## Agent Status Indicators

| Icon | Status | Meaning |
|------|--------|---------|
| ⏳ | Pending | Waiting to start |
| 🔄 | Running | Currently executing |
| ✅ | Completed | Successfully finished |
| ❌ | Failed | Error occurred |

---

## Best Practices

### Task Descriptions

**Good:**
```
"Research the top 5 Python web frameworks in 2024,
comparing their performance, ease of use, and community
support. Include specific metrics where available."
```

**Bad:**
```
"Tell me about Python web frameworks"
```

**Key:** Be specific, include context, state desired output format

### Agent Type Selection

- Use **specialized types** when possible (better results)
- **General** type works for everything but less optimized
- **Researcher** for gathering information
- **Coder** for code tasks (even explanations)
- **Analyst** for data and metrics
- **Writer** for documentation and content

### Council Questions

**Good:**
```
"Which database provides the best performance for
read-heavy workloads with 10M+ records?"

Options:
- PostgreSQL with read replicas
- MongoDB with sharding
- Redis with persistence
- Cassandra cluster
```

**Bad:**
```
"Which database is best?"

Options:
- PostgreSQL
- MongoDB
```

**Key:** Specific context, clear evaluation criteria, relevant options

---

## Cost Management

### Agent Costs

Approximate costs per agent execution:

| Model | Simple Task | Moderate Task | Complex Task |
|-------|-------------|---------------|--------------|
| Haiku | $0.001-0.005 | $0.005-0.01 | $0.01-0.03 |
| Sonnet | $0.01-0.03 | $0.03-0.10 | $0.10-0.30 |
| Opus | $0.05-0.15 | $0.15-0.50 | $0.50-2.00 |

### Council Costs

Cost = (Number of Agents × Cost per Agent)

Examples:
- 3 agents × Haiku: ~$0.02
- 5 agents × Sonnet: ~$0.25
- 7 agents × Sonnet: ~$0.35
- 10 agents × Haiku: ~$0.10

**Tip:** Use Haiku for large councils on simple decisions

---

## Performance Tips

### Faster Results
1. Use **async mode** for background execution
2. Use **Haiku** for simple tasks
3. **Spawn multiple agents** in parallel (not sequential)
4. Keep task descriptions **concise**

### Better Quality
1. Use **specific agent types**
2. Provide **detailed context** in task
3. Use **Sonnet or Opus** for complex work
4. Use **larger councils** (5-7 agents) for decisions

### Cost Optimization
1. Start with **Haiku**, upgrade if needed
2. Use **general agents** for mixed tasks
3. **Smaller councils** (3 agents) for simple decisions
4. Reuse **completed agent results** instead of re-running

---

## Troubleshooting

### Agent Stuck in "Running"?

**Check:**
- Is the task too complex? (may take 60+ seconds)
- Is there a network issue?
- Try refreshing the agent list

**Solution:**
- Wait longer (complex tasks can take minutes)
- Check API key is set correctly
- Check console/logs for errors

### Agent Failed?

**Check:**
- Error message in agent card
- API key configured correctly
- Task description valid

**Solution:**
- Read error message
- Fix issue (usually API key or invalid input)
- Spawn new agent with corrected input

### No Results Showing?

**Check:**
- Agent status (should be ✅ Completed)
- Click "View Result" button
- Check storage file exists: `./sandbox/agents.json`

**Solution:**
- Wait for completion
- Refresh agent list
- Check file permissions

### Council Not Starting?

**Check:**
- At least 2 options provided
- All options have text
- Number of agents > 0

**Solution:**
- Fill in all required fields
- Remove empty options
- Check API key is set

---

## Storage & Persistence

### Agent Storage

**Location:** `./sandbox/agents.json`

**Format:**
```json
{
  "agents": {
    "agent_123": {
      "task": "Research quantum computing",
      "status": "completed",
      "result": "...",
      ...
    }
  }
}
```

### Persistence Features

✅ Agents survive app restarts
✅ Full execution history preserved
✅ Results available indefinitely
✅ Can be exported/shared

### Cleanup

Currently manual:
1. Open `./sandbox/agents.json`
2. Remove old agent entries
3. Save file

**Future:** Automatic cleanup of old agents

---

## Keyboard Shortcuts

Currently none - all actions via buttons.

**Future:** Planned shortcuts:
- `Ctrl+Shift+A` - Spawn agent
- `Ctrl+Shift+C` - Start council
- `Ctrl+Shift+R` - Refresh agents

---

## Testing Individual Components

### Test Agent Spawn

```bash
venv/bin/python -c "
from tools.agents import agent_spawn

result = agent_spawn(
    task='Say hello in one word',
    agent_type='general',
    model='haiku',
    run_async=False
)

print(f'Success: {result.get(\"success\")}')
print(f'Agent ID: {result.get(\"agent_id\")}')
"
```

### Test Agent List

```bash
venv/bin/python -c "
from tools.agents import agent_list

result = agent_list()
print(f'Total agents: {result[\"count\"]}')
for agent in result['agents']:
    print(f'  {agent[\"agent_id\"]}: {agent[\"status\"]}')
"
```

### Test Socratic Council

```bash
venv/bin/python -c "
from tools.agents import socratic_council

result = socratic_council(
    question='Which is simpler?',
    options=['A', 'B'],
    num_agents=3,
    model='haiku'
)

print(f'Winner: {result[\"winner\"]}')
print(f'Votes: {result[\"votes\"]}')
"
```

---

## Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `tools/agents.py` | Agent system | 657 |
| `main.py` (lines 795-872) | Sidebar UI | 78 |
| `main.py` (lines 1155-1237) | Spawn dialog | 83 |
| `main.py` (lines 1239-1300) | Result viewer | 62 |
| `main.py` (lines 1302-1413) | Council UI | 112 |
| `test_phase10.py` | Test suite | 284 |

---

## Advanced Usage

### Custom Agent Types

Currently fixed 5 types. To add custom:
1. Modify `tools/agents.py`
2. Add type to agent type list
3. Add to UI radio buttons
4. Update tests

### Custom Models

Currently supports Haiku/Sonnet/Opus. To add:
1. Update model mapping in `agent_spawn()`
2. Add to UI dropdowns
3. Test with new model

### Agent Templates

**Future Feature:** Pre-configured agents for common tasks
```python
Templates:
- "Research paper summarizer"
- "Code reviewer"
- "Documentation writer"
- "Bug analyzer"
```

---

## Monitoring Agents

### Real-Time

Watch agent list in sidebar:
- Status updates automatically
- Color-coded status indicators
- Refresh button for manual update

### After Completion

Check results:
1. Click "View Result"
2. Read full output
3. Note runtime for performance tracking

### Statistics

**Future:** Planned statistics panel:
- Total agents spawned
- Success/failure rates
- Average runtime by type
- Cost tracking

---

## FAQ

**Q: How many agents can run at once?**
A: No hard limit, but practical limit is ~10-20 (thread/API limits)

**Q: Can agents access my conversation history?**
A: No, agents are independent. Future feature planned.

**Q: Can I chain agents (output → input)?**
A: Not currently. Manual copy-paste needed. Future feature planned.

**Q: Do agents persist across restarts?**
A: Yes, all agents saved to `./sandbox/agents.json`

**Q: Can I export agent results?**
A: Manual copy-paste currently. Export feature planned.

**Q: What happens if an agent fails?**
A: Status shows ❌, error message displayed, agent saved with error

**Q: Can I cancel a running agent?**
A: Not currently. Future feature planned.

**Q: How long do agents take?**
A: Varies by task (3-60+ seconds). Complex tasks can take minutes.

**Q: Is there a limit to task length?**
A: No hard limit, but keep under 1000 words for best results

**Q: Can I use my own prompts?**
A: Yes, task description is your prompt (but system prompt is fixed)

---

## Success Indicators

You'll know Phase 10 is working when:

✅ Can spawn agents from UI
✅ Agents execute and complete
✅ Results viewable and complete
✅ Multiple agents run in parallel
✅ Socratic council produces winner
✅ Agent list updates correctly
✅ Storage file created

---

🎉 **Phase 10 Complete!** Enjoy multi-agent workflows!

For detailed information, see `PHASE10_COMPLETE.md`
