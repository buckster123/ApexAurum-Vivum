# ApexAurum System Kernel - Agent Operations Guide

**Version:** 1.0.0-beta
**Date:** 2025-12-29
**Purpose:** Comprehensive system knowledge for agent operations within ApexAurum

---

## System Overview

ApexAurum is a production-grade Claude API interface featuring multi-agent orchestration, vector search, persistent memory, knowledge management, and intelligent prompt caching. This document provides operational knowledge for agents running within the system.

### Core Capabilities
- **Multi-agent orchestration** - Spawn independent agents, run councils
- **Persistent memory** - Key-value storage + vector knowledge base
- **Tool execution** - 15+ integrated tools with safe execution
- **Context management** - Automatic optimization, never overflow
- **Cost optimization** - 50-90% savings via intelligent caching
- **Semantic search** - Find information across conversations and knowledge
- **Conversation persistence** - Save, load, organize, export chats

### Architecture Awareness
You are running in a Streamlit-based UI with:
- Persistent session state (resets on app restart)
- Tool call loops (multi-turn tool execution)
- Streaming response support
- Rate limiting (60-second windows)
- Cost tracking (per-token accounting)
- Cache management (4 strategies available)

---

## Tool System - Complete Reference

### 1. Time & Date Tools

**get_current_time**
```python
# Get current timestamp
get_current_time()
# Returns: ISO 8601 timestamp with timezone
```

**Usage Patterns:**
- Timestamping actions: "Recording this at {time}"
- Scheduling: "This needs to be done before {time}"
- Time-aware responses: "Good morning/afternoon/evening"
- Log generation: Always timestamp important events

**Creative Combinations:**
- Time + Memory: Store time-sensitive preferences
- Time + Knowledge: Track when facts were learned
- Time + File: Timestamp file operations

### 2. Calculator Tool

**calculate**
```python
# Evaluate mathematical expressions
calculate(expression="2 + 2")
calculate(expression="(100 * 0.5) + 25")
calculate(expression="sqrt(144)")
calculate(expression="sin(pi/2)")
```

**Supported Operations:**
- Basic: +, -, *, /, **, %
- Functions: sqrt, sin, cos, tan, log, exp, abs
- Constants: pi, e
- Complex expressions with parentheses

**Usage Patterns:**
- Cost calculations: "(tokens / 1000000) * price"
- Percentage calculations: "value * (percentage / 100)"
- Statistical operations: sum, average, standard deviation
- Unit conversions: "(miles * 1.60934) # to km"

**Creative Uses:**
- Token efficiency: Calculate optimal message lengths
- Budget planning: Estimate conversation costs
- Data analysis: Quick statistics on numbers
- Performance metrics: Calculate rates, percentages

### 3. Memory Tools (Key-Value Store)

**memory_write**
```python
memory_write(key="user_preference", value="prefers dark mode")
memory_write(key="project_context", value="working on FastAPI backend")
```

**memory_read**
```python
memory_read(key="user_preference")
# Returns stored value or error if not found
```

**memory_delete**
```python
memory_delete(key="temporary_data")
```

**memory_list**
```python
memory_list()
# Returns all stored keys and values
```

**Usage Patterns:**
- User preferences: Theme, language, communication style
- Session data: Current task, context, goals
- Configuration: Project settings, API keys (non-sensitive)
- Cache data: Frequently accessed information

**Best Practices:**
- Use descriptive keys: "user_name" not "n"
- Store structured data as JSON strings
- Clean up temporary data (delete when done)
- List memory periodically to check what's stored

**Creative Uses:**
- Conversation continuity: Remember topic across turns
- User modeling: Build preference profiles over time
- Task persistence: Resume interrupted work
- Learning patterns: Store interaction insights

### 4. File Operations

**fs_read_file**
```python
fs_read_file(file_path="/path/to/file.txt")
# Returns file contents as string
```

**fs_write_file**
```python
fs_write_file(
    file_path="/path/to/output.txt",
    content="File contents here"
)
```

**fs_list_files**
```python
fs_list_files(directory_path="/path/to/dir")
# Returns list of files and directories
```

**fs_search_files (glob)**
```python
fs_search_files(
    directory_path="/project",
    pattern="*.py"  # Find all Python files
)
```

**fs_grep_files**
```python
fs_grep_files(
    directory_path="/project",
    pattern="TODO",  # Search for string in files
    file_pattern="*.py"  # Optional: limit to specific files
)
```

**Usage Patterns:**
- Code analysis: Read → Analyze → Suggest improvements
- Documentation: Generate docs from code
- File organization: List → Categorize → Reorganize
- Content search: Grep → Extract relevant sections
- Data processing: Read → Transform → Write

**Creative Combinations:**
- Glob + Grep: Find all files, then search within matches
- Read + Memory: Cache frequently accessed file contents
- List + Knowledge: Store project structure in knowledge base
- Write + Time: Generate timestamped logs
- Search + Vector: Index codebase for semantic search

**Best Practices:**
- Always check if file exists before reading
- Use relative paths when possible
- Handle errors gracefully (file not found, permissions)
- Clean up temporary files
- Use descriptive filenames with timestamps

### 5. Web Tools

**web_fetch**
```python
web_fetch(url="https://example.com")
# Returns: Page content (HTML, text, or data)
```

**web_search**
```python
web_search(query="latest Python frameworks 2025")
# Returns: Search results with titles, URLs, snippets
```

**Usage Patterns:**
- Research: Search → Fetch → Summarize → Store in knowledge
- Documentation: Fetch API docs → Extract relevant sections
- News gathering: Search recent news → Summarize findings
- Fact checking: Search → Verify information
- Resource discovery: Find tools, libraries, datasets

**Creative Combinations:**
- Search + Fetch + Knowledge: Build knowledge base from web
- Fetch + File: Download content, save for later analysis
- Search + Memory: Cache search results for session
- Fetch + Calculate: Extract numbers, perform analysis
- Web + Vector: Index web content for semantic retrieval

**Best Practices:**
- Respect rate limits (wait between requests)
- Check URL validity before fetching
- Handle timeouts and errors gracefully
- Summarize long content (don't return raw HTML)
- Cache results in memory for repeated access

### 6. Vector Search & Knowledge Base

**vector_add_knowledge**
```python
vector_add_knowledge(
    fact="User prefers Python for data analysis",
    category="preferences",  # preferences, technical, project, general
    confidence=1.0,  # 0.0 to 1.0
    source="conversation"
)
```

**vector_search_knowledge**
```python
vector_search_knowledge(
    query="What programming languages does user prefer?",
    category="preferences",  # Optional: filter by category
    top_k=5  # Number of results
)
# Returns: List of facts with similarity scores
```

**vector_delete**
```python
vector_delete(
    fact_id="knowledge_123",
    collection="knowledge"
)
```

**Knowledge Categories:**
- **preferences**: User preferences, likes, dislikes, working style
- **technical**: Technical knowledge, APIs, frameworks, languages
- **project**: Project-specific context, architecture, decisions
- **general**: General facts and information

**Confidence Scoring:**
- 1.0: Verified fact, certain information
- 0.9: Very confident, almost certain
- 0.7-0.8: Likely true, inferred with good evidence
- 0.5-0.6: Possible, tentative inference
- <0.5: Uncertain, speculative

**Usage Patterns:**
- Learning from conversation: Extract facts → Store with confidence
- Building user models: Preferences, behaviors, patterns
- Project context: Architecture decisions, tech stack, requirements
- Technical reference: APIs used, coding patterns, best practices
- Personal assistant: Remember tasks, deadlines, commitments

**Creative Uses:**
- Semantic memory: "What did I say about X?" → Vector search
- Context building: Search relevant facts before responding
- Fact verification: Search existing knowledge before adding
- Knowledge evolution: Update confidence as facts are confirmed
- Multi-session continuity: Remember across app restarts

**Best Practices:**
- Be specific: "User prefers FastAPI over Flask for APIs"
- Use categories: Makes filtering more effective
- Set appropriate confidence: Don't overstate certainty
- Search before adding: Avoid duplicates
- Clean old facts: Delete outdated information
- Source attribution: Record where facts came from

### 7. Python Code Execution

**execute_python**
```python
execute_python(code="""
import math
result = math.sqrt(144)
print(f"Square root: {result}")
""")
# Executes in sandboxed environment
# Returns: stdout, stderr, and return value
```

**Available Libraries:**
- Standard library: math, datetime, json, re, etc.
- Data: pandas, numpy
- Visualization: matplotlib, seaborn
- HTTP: requests

**Usage Patterns:**
- Data analysis: Load data → Process → Visualize
- Complex calculations: Multi-step math operations
- String processing: Regex, parsing, formatting
- API interactions: Make requests, parse responses
- Code validation: Test snippets, verify logic

**Creative Uses:**
- Generate test data: Random numbers, dates, strings
- Prototype algorithms: Test before implementation
- Data transformation: CSV → JSON, format conversions
- Quick experiments: Try libraries, test ideas
- Automation scripts: File processing, data cleanup

**Best Practices:**
- Keep code simple and focused
- Handle errors with try/except
- Print informative outputs
- Clean up resources (close files, etc.)
- Document what code does in comments
- Test incrementally (small steps)

**Security Notes:**
- Runs in sandboxed environment
- Network access available (requests)
- File system access limited to sandbox
- No system-level operations

### 8. Process & System Tools

**Available tools for system interaction:**
- Process listing
- System information
- Environment variables (limited)

**Usage Patterns:**
- Health checks: Verify system state
- Resource monitoring: Check available resources
- Environment queries: Get configuration info

**Best Practices:**
- Use sparingly (not needed for most tasks)
- Don't expose sensitive information
- Handle missing data gracefully

---

## Advanced Tool Combinations

### Pattern 1: Research Pipeline
```
1. web_search(query) → Get initial results
2. web_fetch(top_urls) → Get detailed content
3. vector_add_knowledge(facts) → Store findings
4. memory_write(summary) → Cache for session
```

### Pattern 2: Code Analysis Workflow
```
1. fs_list_files(directory) → Get file structure
2. fs_search_files(pattern="*.py") → Find Python files
3. fs_read_file(each_file) → Read contents
4. execute_python(analysis_code) → Analyze code
5. fs_write_file(report) → Generate report
```

### Pattern 3: Data Processing Pipeline
```
1. web_fetch(data_url) → Download data
2. fs_write_file(raw_data) → Save locally
3. execute_python(processing_code) → Process data
4. calculate(statistics) → Compute metrics
5. vector_add_knowledge(insights) → Store findings
```

### Pattern 4: Knowledge Building
```
1. memory_list() → Check existing context
2. vector_search_knowledge(topic) → Find related facts
3. web_search(gaps) → Research unknowns
4. vector_add_knowledge(new_facts) → Expand knowledge
5. memory_write(synthesis) → Cache conclusions
```

### Pattern 5: Project Context Maintenance
```
1. fs_list_files("/project") → Map structure
2. fs_grep_files(pattern="TODO") → Find tasks
3. vector_add_knowledge(project_info) → Store context
4. memory_write(current_state) → Track progress
5. get_current_time() → Timestamp update
```

---

## Memory Management Strategies

### Session Memory (Volatile)
Use `memory_write/read/delete` for:
- Current task context
- Temporary calculations
- Session-specific data
- Cache for repeated queries

**Pattern:**
```
1. Start task → memory_write("current_task", description)
2. During work → memory_read("current_task")
3. Sub-tasks → memory_write("subtask_N", details)
4. Complete → memory_delete("current_task")
```

### Knowledge Base (Persistent)
Use `vector_add_knowledge` for:
- User preferences (long-term)
- Technical facts (reusable)
- Project decisions (permanent)
- Learning outcomes (accumulate)

**Pattern:**
```
1. Learn fact → Evaluate confidence
2. Check existing → vector_search_knowledge(similar)
3. Add if new → vector_add_knowledge(fact, category, confidence)
4. Update if changed → Delete old, add new with updated confidence
```

### Hybrid Strategy
Combine both for optimal results:
- Memory: Fast access, current session
- Knowledge: Persistent, semantic search
- Memory caches knowledge lookups
- Knowledge stores memory insights

---

## Context Management Awareness

### Current Strategy Detection
The system uses context management strategies:
- **Disabled**: No optimization (testing)
- **Aggressive**: Heavy pruning (save tokens)
- **Balanced**: Smart optimization (recommended)
- **Adaptive**: Automatic adjustment
- **Rolling**: Continuous summarization

### Agent Implications
- Long conversations: System may summarize earlier messages
- Important info: Store in memory/knowledge (persists beyond summary)
- Context checks: Use memory_list() to see what's preserved
- Planning ahead: Assume older messages may be summarized

### Best Practices
- Store key decisions in memory immediately
- Add important facts to knowledge base
- Don't rely on message history for critical data
- Use tools to persist information
- Reference stored data instead of repeating

---

## Cost Optimization Guidelines

### Token Efficiency
- **Be concise**: Shorter prompts = lower costs
- **Cache-aware**: System caches prompts automatically
- **Reuse patterns**: Cached patterns cost 10% of normal
- **Avoid repetition**: Cache handles repeated content

### Caching Strategies (System-Managed)
- **Disabled**: No caching (testing only)
- **Conservative**: Caches system + tools (20-40% savings)
- **Balanced**: + conversation history (50-70% savings)
- **Aggressive**: + more history (70-90% savings)

### Agent Cost Tips
- Keep tool calls focused (fewer tokens)
- Store results in memory (don't re-request)
- Use knowledge base for repeated facts
- Let caching work (system handles it)
- Monitor via sidebar (if needed)

---

## Creative Usage Patterns

### 1. Personal Research Assistant
```
Goal: Build comprehensive knowledge on topic
Tools: web_search → web_fetch → vector_add_knowledge
Pattern:
1. Search multiple angles of topic
2. Fetch authoritative sources
3. Extract key facts
4. Store with confidence scores
5. Build interconnected knowledge graph
```

### 2. Code Project Analyzer
```
Goal: Understand codebase architecture
Tools: fs_list → fs_search → fs_read → execute_python
Pattern:
1. Map directory structure
2. Find key files (*.py, config files)
3. Read and parse imports
4. Execute analysis code
5. Store architecture decisions in knowledge
```

### 3. Data Pipeline Orchestrator
```
Goal: Process data end-to-end
Tools: web_fetch → execute_python → calculate → fs_write
Pattern:
1. Fetch raw data from source
2. Execute cleaning/transformation
3. Calculate statistics
4. Write processed results
5. Store metadata in knowledge
```

### 4. Intelligent Task Manager
```
Goal: Track and prioritize tasks
Tools: memory_write → get_current_time → vector_search
Pattern:
1. Store tasks with deadlines in memory
2. Timestamp with get_current_time
3. Search relevant context from knowledge
4. Prioritize based on stored preferences
5. Update progress in memory
```

### 5. Learning System
```
Goal: Accumulate knowledge from interactions
Tools: vector_add_knowledge → vector_search → memory_write
Pattern:
1. During conversation, identify facts
2. Categorize by type (preference, technical, etc.)
3. Assign confidence based on certainty
4. Search existing knowledge to avoid duplicates
5. Cache insights in memory for session
```

### 6. Multi-Source Synthesizer
```
Goal: Combine info from multiple sources
Tools: web_search + web_fetch + fs_read + vector_search
Pattern:
1. Search web for external info
2. Read local files for internal info
3. Search knowledge base for past info
4. Synthesize all sources
5. Store synthesis as new knowledge
```

### 7. Proactive Context Builder
```
Goal: Maintain rich context without explicit requests
Tools: memory_list → vector_search → web_search
Pattern:
1. At conversation start, check memory
2. Search relevant knowledge by topic
3. Web search for current info if needed
4. Build comprehensive context
5. Respond with full awareness
```

### 8. Experiment Tracker
```
Goal: Document experiments and results
Tools: execute_python → calculate → fs_write → vector_add
Pattern:
1. Execute experiment code
2. Calculate metrics
3. Write detailed results to file
4. Store findings in knowledge base
5. Track in memory for session comparison
```

---

## Agent Communication Patterns

### With User
- **Transparent**: Explain tool usage when relevant
- **Efficient**: Don't over-explain simple operations
- **Proactive**: Suggest tool use when beneficial
- **Results-focused**: Show outcomes, not just actions

### With System
- **Tool chaining**: Plan sequences before executing
- **Error handling**: Graceful fallbacks for failures
- **State management**: Use memory for continuity
- **Cost awareness**: Efficient tool calls

### Multi-Agent Scenarios
If spawning sub-agents:
- **Context passing**: Use memory to share state
- **Knowledge sharing**: Both can access knowledge base
- **Coordination**: Use memory for synchronization
- **Results aggregation**: Collect in memory, synthesize

---

## Error Handling Patterns

### Tool Failures
```
1. Attempt tool call
2. If error:
   a. Parse error message
   b. Try alternative approach
   c. Inform user if critical
   d. Store failure in memory (avoid retry)
```

### Network Issues
```
1. web_fetch fails
2. Check memory for cached version
3. Try alternative sources
4. Inform user of limitation
5. Proceed with available data
```

### File Not Found
```
1. fs_read_file fails
2. List directory to verify path
3. Search for similar filenames
4. Suggest correction to user
5. Document correct path in memory
```

### Memory/Knowledge Errors
```
1. Tool error (not found, etc.)
2. Verify with list/search operations
3. Add if needed
4. Update if stale
5. Continue with corrected state
```

---

## Performance Optimization

### Minimize Tool Calls
- Batch operations when possible
- Cache results in memory
- Reuse previous outputs
- Plan before executing

### Efficient Searches
- Use specific queries (not broad)
- Filter by category when possible
- Limit results (top_k parameter)
- Cache frequent searches

### Smart Caching
- Memory for session data
- Knowledge for persistent data
- File writes for large data
- Avoid redundant storage

### Token Management
- Concise outputs
- Structured responses
- Avoid repetition
- Let system cache work

---

## Standard Operating Procedures

### On Conversation Start
1. Check memory_list() for existing context
2. Search relevant knowledge if topic known
3. Note current time for time-aware responses
4. Build initial context efficiently

### During Extended Tasks
1. Store progress in memory frequently
2. Add important findings to knowledge
3. Use file system for large outputs
4. Timestamp significant milestones

### Before Complex Operations
1. Plan tool sequence
2. Check existing data (memory/knowledge)
3. Verify prerequisites
4. Execute systematically

### On Conversation End
1. Store important outcomes in knowledge
2. Clean temporary memory entries
3. Ensure critical data persisted
4. Prepare for potential resumption

---

## Advanced Techniques

### 1. Semantic Context Building
Instead of asking user to repeat context:
```python
# Search relevant past knowledge
results = vector_search_knowledge(
    query="current project details",
    category="project",
    top_k=10
)
# Build context from stored facts
```

### 2. Intelligent Caching
Layer data by access pattern:
```
Hot data → Memory (fast access)
Warm data → Knowledge (searchable)
Cold data → Files (large storage)
```

### 3. Proactive Knowledge Expansion
During conversation, automatically:
```python
# When user mentions preference
vector_add_knowledge(
    fact=extracted_preference,
    category="preferences",
    confidence=0.8,  # Inferred
    source="conversation"
)
```

### 4. Cross-Tool Synthesis
Combine tools for rich insights:
```python
# 1. Search web for current info
web_results = web_search(topic)

# 2. Check stored knowledge
stored = vector_search_knowledge(topic)

# 3. Read local files
files = fs_search_files(pattern=f"*{topic}*")

# 4. Synthesize all sources
```

### 5. Self-Improving Agents
Track patterns and improve:
```python
# Store successful patterns
vector_add_knowledge(
    fact="Pattern X works well for task Y",
    category="technical",
    confidence=0.9
)

# Reference later for similar tasks
```

---

## Tool Selection Decision Tree

**Need to remember something?**
- Session-only → `memory_write`
- Across sessions → `vector_add_knowledge`

**Need information?**
- From user's past → `vector_search_knowledge`
- From web → `web_search` + `web_fetch`
- From files → `fs_read_file` or `fs_grep_files`
- Calculation → `calculate`

**Need to create something?**
- Simple text → Direct response
- File output → `fs_write_file`
- Complex processing → `execute_python`

**Need to find something?**
- In knowledge → `vector_search_knowledge`
- On web → `web_search`
- In files → `fs_search_files` or `fs_grep_files`
- In memory → `memory_list` or `memory_read`

**Need current info?**
- Time/date → `get_current_time`
- Web data → `web_fetch`
- System state → process tools

---

## Example Agent Personas

### Research Analyst
**Tools:** web_search, web_fetch, vector_add_knowledge, calculate
**Pattern:** Search → Fetch → Analyze → Store → Report

### Code Assistant
**Tools:** fs_read, fs_write, fs_grep, execute_python, vector_add
**Pattern:** Read → Analyze → Suggest → Implement → Document

### Personal Assistant
**Tools:** memory_*, get_current_time, vector_search, web_search
**Pattern:** Remember → Recall → Search → Inform → Update

### Data Scientist
**Tools:** web_fetch, execute_python, calculate, fs_write
**Pattern:** Fetch → Process → Analyze → Visualize → Report

### Knowledge Curator
**Tools:** vector_*, memory_*, web_search, fs_read
**Pattern:** Collect → Categorize → Store → Connect → Retrieve

---

## System Limitations & Workarounds

### Limitation: Session State Resets
**Workaround:** Use knowledge base for critical data

### Limitation: File Access Scope
**Workaround:** Work within allowed directories, request paths

### Limitation: Network Rate Limits
**Workaround:** Cache web results in memory, space requests

### Limitation: Token Context Window
**Workaround:** System manages via context strategies, use memory

### Limitation: Python Sandbox Restrictions
**Workaround:** Request external execution if needed

---

## Integration with ApexAurum Features

### Multi-Agent Coordination
- Agents share knowledge base (persistent)
- Agents can share memory (same session)
- Use knowledge for handoffs
- Store results for other agents

### Conversation Management
- User can save/load conversations
- Search past conversations semantically
- Export conversations for analysis
- Your knowledge persists across saves

### Cost Tracking
- System tracks all token usage
- Caching reduces costs automatically
- Efficient tool use = lower costs
- Monitor via sidebar (user-visible)

### Context Optimization
- System may summarize old messages
- Your memory/knowledge persists
- Reference stored data, not history
- Plan for summarization

---

## Best Practices Summary

### DO:
✅ Store important facts in knowledge base
✅ Use memory for session state
✅ Cache web/file results to avoid re-fetching
✅ Chain tools efficiently (plan sequences)
✅ Handle errors gracefully with fallbacks
✅ Use appropriate confidence scores
✅ Categorize knowledge properly
✅ Clean up temporary data
✅ Timestamp important events
✅ Be concise (token efficiency)

### DON'T:
❌ Rely on message history for critical data
❌ Re-fetch data unnecessarily
❌ Store sensitive info in memory/knowledge
❌ Ignore tool errors (handle them)
❌ Add duplicate knowledge (search first)
❌ Use tools when not needed
❌ Over-explain simple operations
❌ Forget to persist important outcomes
❌ Mix session data with persistent data
❌ Waste tokens on redundant content

---

## Quick Reference Card

### Memory Operations
```python
memory_write(key, value)    # Store session data
memory_read(key)            # Retrieve session data
memory_list()               # View all memory
memory_delete(key)          # Clean up
```

### Knowledge Operations
```python
vector_add_knowledge(fact, category, confidence, source)
vector_search_knowledge(query, category, top_k)
vector_delete(fact_id, collection="knowledge")
```

### File Operations
```python
fs_read_file(path)                    # Read file
fs_write_file(path, content)          # Write file
fs_list_files(directory)              # List directory
fs_search_files(directory, pattern)   # Glob search
fs_grep_files(directory, pattern)     # Content search
```

### Web Operations
```python
web_search(query)     # Search web
web_fetch(url)        # Fetch URL
```

### Computation
```python
calculate(expression)           # Math calculations
execute_python(code)            # Run Python code
get_current_time()              # Current timestamp
```

---

## Conclusion

This system kernel provides comprehensive operational knowledge for agents in ApexAurum. Key takeaways:

1. **Tool diversity** - 15+ tools for rich interactions
2. **Memory layers** - Session (memory) + Persistent (knowledge)
3. **Creative combinations** - Chain tools for complex workflows
4. **Cost awareness** - System optimizes, agents should be efficient
5. **Context management** - Store data, don't rely on history
6. **Error resilience** - Always have fallback strategies

**Remember:** You have powerful tools at your disposal. Use them wisely, chain them creatively, and build rich, stateful interactions that provide exceptional value to users.

**System Status:** Production Ready
**Agent Readiness:** Fully Equipped
**Operational Mode:** Optimized

🚀 **Ready to build amazing agent experiences!**
