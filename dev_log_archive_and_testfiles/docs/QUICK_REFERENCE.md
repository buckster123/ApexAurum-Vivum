# Quick Reference: Moonshot → Claude Adaptation

## 🎯 TL;DR: What Changed?

**Before (Moonshot):**
```python
from openai import OpenAI
client = OpenAI(api_key=API_KEY, base_url="https://api.moonshot.ai/v1")
response = client.chat.completions.create(
    model="kimi-k2",
    messages=[
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "Hello"}
    ],
    tools=moonshot_tools,
    stream=True
)
```

**After (Claude):**
```python
from anthropic import Anthropic
client = Anthropic(api_key=API_KEY)
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    system="You are helpful",  # Separate parameter!
    messages=[
        {"role": "user", "content": "Hello"}  # No system in messages!
    ],
    tools=claude_tools,
    stream=True
)
```

## 📊 Quick Comparison Table

| Aspect | Moonshot | Claude |
|--------|----------|--------|
| **SDK** | `openai` | `anthropic` |
| **Client** | `OpenAI(base_url=...)` | `Anthropic()` |
| **Endpoint** | `chat.completions.create` | `messages.create` |
| **System** | In messages array | Separate parameter |
| **Max output** | 256k tokens | 8k tokens |
| **Rate limit** | 100 req/min | 50 req/min |
| **Tool wrapper** | `type: "function"` | None (flat structure) |
| **Tool params** | `parameters` | `input_schema` |
| **Tool result** | `role: "tool"` message | `role: "user"` with `tool_result` |
| **Streaming** | `delta.content` | Event-based |

## 🔑 Key Code Changes

### 1. Import Changes
```python
# OLD
from openai import OpenAI, AsyncOpenAI
import openai

# NEW
from anthropic import Anthropic, AsyncAnthropic
import anthropic
```

### 2. Client Initialization
```python
# OLD
client = OpenAI(
    api_key=os.getenv("MOONSHOT_API_KEY"),
    base_url="https://api.moonshot.ai/v1"
)

# NEW
client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

### 3. System Prompt Handling
```python
# OLD - System in messages array
messages = [
    {"role": "system", "content": sys_prompt},
    {"role": "user", "content": user_input}
]
response = client.chat.completions.create(
    model=model,
    messages=messages
)

# NEW - System as separate parameter
messages = [
    {"role": "user", "content": user_input}
]
response = client.messages.create(
    model=model,
    system=sys_prompt,  # Separate!
    messages=messages
)
```

### 4. Tool Schema Format
```python
# OLD - OpenAI format
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}

# NEW - Claude format
{
    "name": "get_weather",
    "description": "Get weather",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string"}
        },
        "required": ["location"]
    }
}
```

### 5. Tool Result Format
```python
# OLD - Separate tool message
messages.append({
    "role": "tool",
    "tool_call_id": tool_call.id,
    "name": "get_weather",
    "content": "Sunny, 72°F"
})

# NEW - User message with tool_result
messages.append({
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": tool_use.id,
        "content": "Sunny, 72°F"
    }]
})
```

### 6. Streaming Response
```python
# OLD - Delta-based
for chunk in response:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="")

# NEW - Event-based
for event in response:
    if event.type == "content_block_delta":
        if hasattr(event.delta, 'text'):
            print(event.delta.text, end="")
```

### 7. Error Handling
```python
# OLD
try:
    response = client.chat.completions.create(...)
except openai.RateLimitError:
    # Handle rate limit
except openai.APIError:
    # Handle API error

# NEW
try:
    response = client.messages.create(...)
except anthropic.RateLimitError:
    # Handle rate limit
except anthropic.APIError:
    # Handle API error
```

### 8. Model Names
```python
# OLD
MODELS = {
    "thinking": "kimi-k2-thinking",
    "standard": "kimi-k2",
    "fast": "moonshot-v1-8k"
}

# NEW
MODELS = {
    "best": "claude-opus-4-5-20251101",
    "balanced": "claude-sonnet-4-5-20250929",
    "fast": "claude-3-5-haiku-20241022"
}
```

## 🛠️ Tool Schema Converter

Quick function to convert OpenAI tool schemas to Claude format:

```python
def convert_tool_schema(openai_tool: dict) -> dict:
    """Convert OpenAI tool schema to Claude format"""
    if openai_tool.get("type") == "function":
        func = openai_tool["function"]
        return {
            "name": func["name"],
            "description": func.get("description", ""),
            "input_schema": func.get("parameters", {})
        }
    return openai_tool
```

## 📝 Message Converter

Convert message format:

```python
def extract_system_prompt(messages: list) -> tuple[str, list]:
    """Extract system prompt from messages array"""
    system = ""
    user_messages = []

    for msg in messages:
        if msg["role"] == "system":
            system = msg["content"]
        else:
            user_messages.append(msg)

    return system, user_messages
```

## 🔄 Streaming Event Handler

Handle Claude's event-based streaming:

```python
def handle_streaming_response(response):
    """Handle Claude streaming events"""
    current_text = ""
    tool_uses = []

    for event in response:
        if event.type == "content_block_start":
            if event.content_block.type == "tool_use":
                tool_uses.append({
                    "id": event.content_block.id,
                    "name": event.content_block.name,
                    "input": {}
                })

        elif event.type == "content_block_delta":
            delta = event.delta

            if delta.type == "text_delta":
                current_text += delta.text
                yield delta.text

            elif delta.type == "input_json_delta":
                # Accumulate tool input JSON
                tool_uses[-1]["input_json"] = tool_uses[-1].get("input_json", "") + delta.partial_json

        elif event.type == "message_stop":
            break

    return current_text, tool_uses
```

## ⚡ Rate Limiting

Claude's rate limits (Tier 1):

```python
class ClaudeRateLimiter:
    def __init__(self):
        self.rpm = 50  # requests per minute
        self.input_tpm = 40_000  # input tokens per minute
        self.output_tpm = 8_000  # output tokens per minute
        self.concurrent = 5  # concurrent requests

    def can_make_request(self, estimated_input_tokens: int) -> bool:
        # Check if request can be made
        return (
            self.requests_this_minute < self.rpm and
            self.input_tokens_this_minute + estimated_input_tokens < self.input_tpm
        )
```

## 🖼️ Image Format

```python
# OLD - Moonshot/OpenAI
{
    "type": "image_url",
    "image_url": {
        "url": f"data:image/jpeg;base64,{base64_data}"
    }
}

# NEW - Claude
{
    "type": "image",
    "source": {
        "type": "base64",
        "media_type": "image/jpeg",
        "data": base64_data  # No data: prefix!
    }
}
```

## 📦 Essential Imports

Your new imports section:

```python
import anthropic
from anthropic import Anthropic, AsyncAnthropic
from anthropic.types import Message, TextBlock, ToolUseBlock

# Remove these:
# from openai import OpenAI, AsyncOpenAI
# import openai
```

## 🎨 Model Selection Guide

```python
def select_model(task_complexity: str) -> str:
    """Select appropriate Claude model based on task"""
    models = {
        "simple": "claude-3-5-haiku-20241022",      # Fastest, cheapest
        "standard": "claude-sonnet-4-5-20250929",   # Balanced (default)
        "complex": "claude-opus-4-5-20251101",      # Best reasoning
        "coding": "claude-sonnet-4-5-20250929",     # Good at code
        "vision": "claude-sonnet-4-5-20250929",     # All models support vision
    }
    return models.get(task_complexity, models["standard"])
```

## ⚠️ Common Pitfalls

### ❌ DON'T: System in messages
```python
messages = [
    {"role": "system", "content": "You are helpful"},  # WRONG!
    {"role": "user", "content": "Hello"}
]
```

### ✅ DO: System as parameter
```python
system = "You are helpful"
messages = [{"role": "user", "content": "Hello"}]
response = client.messages.create(system=system, messages=messages, ...)
```

### ❌ DON'T: Tool role messages
```python
messages.append({
    "role": "tool",  # Claude doesn't have this!
    "content": result
})
```

### ✅ DO: User message with tool_result
```python
messages.append({
    "role": "user",
    "content": [{"type": "tool_result", "tool_use_id": id, "content": result}]
})
```

### ❌ DON'T: High max_tokens
```python
response = client.messages.create(
    max_tokens=256000,  # Claude max is 8192!
    ...
)
```

### ✅ DO: Respect Claude's limits
```python
response = client.messages.create(
    max_tokens=8192,  # or 4096 for safety
    ...
)
```

## 🧪 Quick Test

Test your setup:

```python
from anthropic import Anthropic

client = Anthropic(api_key="your-key")

# Simple test
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Say hello!"}]
)

print(response.content[0].text)
# Should print a greeting
```

## 📚 Essential Documentation Links

- [Anthropic API Reference](https://docs.anthropic.com/en/api/messages)
- [Tool Use Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [Streaming Guide](https://docs.anthropic.com/en/api/streaming)
- [Vision Guide](https://docs.anthropic.com/en/docs/build-with-claude/vision)
- [Rate Limits](https://docs.anthropic.com/en/api/rate-limits)

## 💡 Pro Tips

1. **Start with Sonnet** - Good balance of speed/quality/cost
2. **Cache system prompts** - Use prompt caching for repeated prompts (future)
3. **Batch tool calls** - Process multiple tools when possible
4. **Use appropriate models** - Don't use Opus for simple tasks
5. **Monitor rate limits** - Track requests/tokens to avoid hitting limits
6. **Handle overload errors** - Claude returns 529 when overloaded, retry with backoff
7. **Keep context tight** - 8k output limit means you need to manage context carefully
8. **Test tools incrementally** - Don't migrate all 30+ tools at once
9. **Read error messages** - Claude's errors are usually informative
10. **Use type hints** - Makes tool schemas more reliable

## 🚀 Next Steps

1. Read [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for detailed API differences
2. Read [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for the full adaptation plan
3. Start with Phase 1: Core API client
4. Test each component before moving to the next
5. Keep the original as reference

## 📞 Need Help?

- Check `app.log` for detailed error messages
- Anthropic's error messages are usually clear
- Test with simple examples before complex ones
- Use `claude-3-5-haiku` for testing (cheaper)

---

**Remember:** The core logic and tools don't change - only the API wrapper! Most of your code (~80%) will work as-is.
