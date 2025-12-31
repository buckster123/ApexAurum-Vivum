# Migration Guide: Moonshot API → Claude/Anthropic API

## Overview
This document outlines the key differences between the Moonshot API (OpenAI SDK) and the Anthropic Claude API, and how the Apex Aurum application has been adapted.

## Critical API Differences

### 1. **SDK & Client Initialization**

**Moonshot (OpenAI SDK):**
```python
from openai import OpenAI, AsyncOpenAI

client = OpenAI(
    api_key=MOONSHOT_API_KEY,
    base_url="https://api.moonshot.ai/v1"
)
```

**Claude (Anthropic SDK):**
```python
from anthropic import Anthropic, AsyncAnthropic

client = Anthropic(
    api_key=ANTHROPIC_API_KEY
)
# No base_url needed - it's built into the SDK
```

### 2. **Message Format**

**Moonshot:**
- System prompt is a message with role="system"
- Messages array includes system message
- Tool calls embedded in assistant messages

**Claude:**
- System prompt is a separate parameter
- Messages array ONLY contains user/assistant messages
- System prompt cannot be in messages array
- Tool use blocks are separate content blocks

**Moonshot Example:**
```python
messages = [
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
]
```

**Claude Example:**
```python
system = "You are helpful"
messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
]
```

### 3. **Model Names**

**Moonshot Models:**
- kimi-k2-thinking
- kimi-k2
- kimi-latest
- moonshot-v1-8k
- moonshot-v1-32k
- moonshot-v1-128k

**Claude Models:**
- claude-opus-4-5-20251101 (Most capable)
- claude-sonnet-4-5-20250929 (Balanced)
- claude-3-7-sonnet-20250219 (Fast)
- claude-3-5-haiku-20241022 (Fastest, cheapest)

### 4. **API Call Structure**

**Moonshot:**
```python
response = client.chat.completions.create(
    model="kimi-k2",
    messages=messages,
    tools=tools,
    tool_choice="auto",
    stream=True,
    max_tokens=256000
)
```

**Claude:**
```python
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    system=system_prompt,
    messages=messages,
    tools=tools,
    max_tokens=8192,
    stream=True
)
# Note: Claude has lower max_tokens (8192 vs 256000)
```

### 5. **Tool/Function Calling Format**

**Moonshot (OpenAI format):**
```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }
}]
```

**Claude format:**
```python
tools = [{
    "name": "get_weather",
    "description": "Get weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name"}
        },
        "required": ["location"]
    }
}]
# Note: No "function" wrapper, "input_schema" instead of "parameters"
```

### 6. **Streaming Response Handling**

**Moonshot:**
```python
for chunk in response:
    delta = chunk.choices[0].delta
    if delta.content:
        yield delta.content
    if delta.tool_calls:
        # Handle tool call deltas
        pass
```

**Claude:**
```python
for event in response:
    if event.type == "content_block_start":
        # New content block started
        pass
    elif event.type == "content_block_delta":
        if hasattr(event.delta, 'text'):
            yield event.delta.text
    elif event.type == "message_stop":
        # Message complete
        break
```

### 7. **Tool Call Response Format**

**Moonshot:**
```python
# Tool results added as separate messages
current_messages.append({
    "tool_call_id": tool_call.id,
    "role": "tool",
    "name": func_name,
    "content": result
})
```

**Claude:**
```python
# Tool results in user message with content array
messages.append({
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": tool_use.id,
        "content": result
    }]
})
```

### 8. **Image Handling**

**Moonshot:**
```python
content_parts = [
    {"type": "text", "text": message},
    {
        "type": "image_url",
        "image_url": {"url": f"data:{mime_type};base64,{img_data}"}
    }
]
```

**Claude:**
```python
content_parts = [
    {"type": "text", "text": message},
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": img_data
        }
    }
]
```

### 9. **Rate Limits**

**Moonshot Limits (estimated):**
- 100 requests/minute
- 1,000,000 tokens/minute
- 5 concurrent requests

**Claude Limits (Tier 1):**
- 50 requests/minute
- 40,000 tokens/minute (input)
- 8,000 tokens/minute (output)
- 5 concurrent requests

### 10. **Error Handling**

**Moonshot (OpenAI SDK errors):**
```python
from openai import AuthenticationError, RateLimitError, APIError

try:
    response = client.chat.completions.create(...)
except AuthenticationError:
    # Handle auth error
except RateLimitError:
    # Handle rate limit
except APIError:
    # Handle API error
```

**Claude (Anthropic SDK errors):**
```python
from anthropic import (
    APIError,
    AuthenticationError,
    RateLimitError,
    APIStatusError
)

try:
    response = client.messages.create(...)
except AuthenticationError:
    # Handle auth error
except RateLimitError:
    # Handle rate limit
except APIStatusError as e:
    # Handle HTTP status errors (e.status_code)
except APIError:
    # Handle general API error
```

### 11. **Special Features**

**Moonshot Specific:**
- Kimi thinking models with `reasoning_content` field
- Native web search and calculation tools
- Very high token limits (256k output)

**Claude Specific:**
- Extended thinking mode (opus models)
- Vision capabilities across all models
- Computer use (experimental)
- Prompt caching for efficiency
- Lower token limits (8k output max)

## Key Migration Challenges

### Challenge 1: Thinking/Reasoning Content
**Issue:** Moonshot's Kimi models have a special `reasoning_content` field for chain-of-thought reasoning.
**Solution:** Claude's extended thinking is handled automatically with opus models. No special handling needed in code.

### Challenge 2: Token Limits
**Issue:** Moonshot supports up to 256k tokens output, Claude only 8k.
**Solution:** Implement chunking/streaming strategies for long outputs. Use summarization tools.

### Challenge 3: Tool Response Format
**Issue:** Tool results go back differently (tool message vs user message with tool_result).
**Solution:** Implement converter function to transform tool results into Claude's format.

### Challenge 4: Native Tools
**Issue:** Moonshot has native web search/calc tools. Claude doesn't.
**Solution:** Implement these as local tools using Python libraries (requests, sympy, etc.).

## Migration Checklist

- [ ] Replace OpenAI SDK with Anthropic SDK
- [ ] Update all API client initializations
- [ ] Extract system prompts from messages array
- [ ] Convert tool schemas (function → input_schema)
- [ ] Rewrite streaming response handler
- [ ] Update model enums and names
- [ ] Adapt rate limiting for Claude's limits
- [ ] Convert tool result format
- [ ] Remove reasoning_content handling
- [ ] Update image encoding format
- [ ] Rewrite error handling for Anthropic exceptions
- [ ] Implement web search as local tool
- [ ] Implement calculation as local tool
- [ ] Add prompt caching (optional optimization)
- [ ] Test all tools with Claude API

## Testing Strategy

1. **Basic Message Flow:** Test simple user/assistant exchanges
2. **System Prompts:** Verify system prompt extraction works
3. **Single Tool Call:** Test one tool at a time
4. **Multi-Tool Calls:** Test multiple tools in one turn
5. **Tool Chains:** Test tool → response → tool flows
6. **Streaming:** Verify streaming text and tool calls
7. **Images:** Test vision capabilities
8. **Error Handling:** Test rate limits, auth errors, etc.
9. **Long Conversations:** Test context window management
10. **Memory System:** Verify ChromaDB integration still works

## Performance Considerations

**Moonshot Advantages:**
- Higher token limits
- Native tools (faster)
- Thinking models for complex reasoning

**Claude Advantages:**
- Better instruction following
- Stronger vision capabilities
- More reliable tool use
- Prompt caching (cost savings)
- Better code generation

## Recommended Migration Order

1. Core API client (client initialization, basic messages)
2. System prompt handling
3. Model configuration
4. Basic streaming (no tools)
5. Tool schema conversion
6. Tool execution and results
7. Streaming with tools
8. Image handling
9. Error handling
10. Rate limiting
11. Advanced features (memory, agents, etc.)
