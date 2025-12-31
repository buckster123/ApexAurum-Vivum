# ApexAurum Quick Commands Reference

**Quick reference sheet for common commands**

---

## Navigation

```bash
# Project root
cd /home/llm/claude/claude-version

# Important directories
cd core/              # Core systems
cd tools/             # Tool implementations
cd ui/                # UI components
cd dev_log_archive_and_testfiles/  # Documentation
```

---

## Health Checks

```bash
# Full health check
python -c "from tools import ALL_TOOLS; print(f'✓ {len(ALL_TOOLS)} tools loaded')"
test -f .env && echo "✓ Environment configured" || echo "⚠ Missing .env"
ps aux | grep streamlit | grep -v grep && echo "✓ Streamlit running" || echo "○ Not running"
wc -l main.py

# Tool count (should be 30)
python -c "from tools import ALL_TOOLS; print(len(ALL_TOOLS))"

# Environment check
cat .env | grep ANTHROPIC_API_KEY | head -c 40

# Imports check
python -c "from core import ClaudeAPIClient; from tools import ALL_TOOLS; print('✓ Imports OK')"

# Agent tools check
python -c "from tools.agents import agent_spawn; print('✓ Agent tools OK')"
```

---

## Application Control

```bash
# Start Streamlit
streamlit run main.py

# Start with specific port
streamlit run main.py --server.port 8502

# Stop Streamlit
pkill -f streamlit

# Check if running
ps aux | grep streamlit | grep -v grep

# View running processes
ps aux | grep python
```

---

## Testing

```bash
# Individual test suites
python test_basic.py
python test_streaming.py
python test_tools.py
python test_cost_tracker.py
python test_vector_db.py
python test_semantic_search.py
python test_knowledge_manager.py
python test_agents.py

# Quick import test
python -c "from tools import ALL_TOOLS; print(f'✓ {len(ALL_TOOLS)} tools')"

# Agent functionality test
python -c "from tools.agents import agent_spawn; result = agent_spawn('test', run_async=False); print(result)"
```

---

## Logging

```bash
# Live log monitoring
tail -f app.log

# Recent entries
tail -100 app.log

# Search for errors
grep ERROR app.log

# Search for warnings
grep WARN app.log

# Recent errors
grep ERROR app.log | tail -20

# Clear logs
> app.log
```

---

## Code Navigation

```bash
# Find function
grep -rn "def function_name" .

# Find class
grep -rn "class ClassName" .

# Find imports
grep -rn "import module_name" .

# Find string
grep -rn "search string" .

# Search in specific directory
grep -rn "search" core/
grep -rn "search" tools/

# Count occurrences
grep -r "search" . | wc -l
```

---

## File Operations

```bash
# Count lines in all code
wc -l core/*.py tools/*.py ui/*.py main.py

# Count Python files
find . -name "*.py" | wc -l

# List large files
find . -name "*.py" -exec wc -l {} + | sort -n | tail -10

# Find recent changes
find . -name "*.py" -mtime -1

# View specific line range (main.py is 4169 lines)
sed -n '1300,1400p' main.py
```

---

## Git Operations (if using)

```bash
# Status
git status

# Diff
git diff

# Add and commit
git add .
git commit -m "Description"

# View history
git log --oneline

# View recent commits
git log -10 --oneline
```

---

## Environment & Dependencies

```bash
# Check Python version (should be 3.9+)
python --version

# List installed packages
pip list

# Check specific packages
pip list | grep -E "anthropic|streamlit|chromadb|voyageai"

# Install/update dependencies
pip install -r requirements.txt

# Update specific package
pip install --upgrade package-name

# Check environment variables
env | grep API
```

---

## Database & Storage

```bash
# Check storage files
ls -lh sandbox/*.json

# View conversations
cat sandbox/conversations.json | python -m json.tool | head -50

# View agents
cat sandbox/agents.json | python -m json.tool

# View memory
cat sandbox/memory.json | python -m json.tool

# Backup storage
cp -r sandbox/ sandbox_backup_$(date +%Y%m%d)/
```

---

## Performance & Monitoring

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check CPU usage
top -bn1 | head -20

# Monitor Python processes
ps aux | grep python

# Check port usage
lsof -i :8501

# Network connectivity test
ping -c 3 api.anthropic.com
```

---

## Quick Fixes

```bash
# Restart Streamlit (most common fix)
pkill -f streamlit && streamlit run main.py

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Reset environment
source /path/to/venv/bin/activate  # if using venv
```

---

## Documentation

```bash
# View docs in terminal
cat PROJECT_STATUS.md
cat DEVELOPMENT_GUIDE.md
cat README.md

# Search documentation
grep -r "search term" dev_log_archive_and_testfiles/

# List all phase docs
ls -1 dev_log_archive_and_testfiles/PHASE*.md

# List all test files
ls -1 dev_log_archive_and_testfiles/test_*.py
```

---

## Development Shortcuts

```bash
# Create new branch (if using git)
git checkout -b feature/new-feature

# Quick commit (if using git)
git add . && git commit -m "Quick commit" && git push

# Run Python in project context
python -i -c "from tools import *; from core import *"

# Test specific function
python -c "from module import function; print(function(args))"

# Format Python files (if black installed)
black *.py core/*.py tools/*.py

# Count TODOs
grep -r "TODO" . --include="*.py" | wc -l
```

---

## Agent System Specific

```bash
# Check agent tools loaded
python -c "from tools.agents import agent_spawn, socratic_council; print('✓ Agent tools loaded')"

# View agent storage
cat sandbox/agents.json | python -m json.tool

# Count agents
python -c "import json; data=json.load(open('sandbox/agents.json')); print(f'{len(data)} agents')" 2>/dev/null || echo "No agents yet"

# Test agent spawn (sync)
python -c "from tools.agents import agent_spawn; print(agent_spawn('Test task', run_async=False))"
```

---

## Debugging

```bash
# Enable debug mode
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run main.py

# Python debug
python -m pdb main.py

# Check for syntax errors
python -m py_compile main.py
python -m py_compile core/*.py

# Validate JSON files
python -m json.tool < sandbox/conversations.json > /dev/null && echo "Valid" || echo "Invalid"

# Check imports without running
python -m importlib.util main.py
```

---

## Emergency Commands

```bash
# Kill all Python processes (DANGER!)
pkill -9 python

# Kill all Streamlit processes
pkill -9 streamlit

# Force stop on specific port
kill -9 $(lsof -t -i:8501)

# Clear all cache and restart
rm -rf __pycache__ */__pycache__ && pkill streamlit && streamlit run main.py

# Backup everything before major changes
tar -czf apex_backup_$(date +%Y%m%d_%H%M%S).tar.gz . --exclude=venv --exclude=__pycache__
```

---

## One-Liners

```bash
# Complete health check
cd /home/llm/claude/claude-version && python -c "from tools import ALL_TOOLS; print(f'{len(ALL_TOOLS)} tools')" && test -f .env && echo "✓ Ready" || echo "⚠ Issues"

# Quick restart
pkill streamlit; sleep 1; streamlit run main.py &

# Count all Python lines
find . -name "*.py" -not -path "./venv/*" -exec wc -l {} + | tail -1

# Check all imports
python -c "from core import *; from tools import *; from ui import *; print('✓ All imports OK')"

# Full status
echo "Tools:" && python -c "from tools import ALL_TOOLS; print(len(ALL_TOOLS))" && echo "Lines:" && wc -l main.py && echo "Env:" && test -f .env && echo "OK"
```

---

## URL Quick Access

```bash
# Open in default browser (if GUI available)
xdg-open http://localhost:8501  # Linux
open http://localhost:8501      # macOS

# Show URL
echo "App URL: http://localhost:8501"

# Check if port accessible
curl -I http://localhost:8501 2>/dev/null && echo "✓ Accessible" || echo "⚠ Not accessible"
```

---

**Tip:** Add these to bash aliases for even faster access:

```bash
# In ~/.bashrc or ~/.bash_aliases
alias apex='cd /home/llm/claude/claude-version'
alias apex-start='cd /home/llm/claude/claude-version && streamlit run main.py'
alias apex-logs='tail -f /home/llm/claude/claude-version/app.log'
alias apex-check='python -c "from tools import ALL_TOOLS; print(f\"{len(ALL_TOOLS)} tools loaded\")"'
```

---

**Last Updated:** 2025-12-31
