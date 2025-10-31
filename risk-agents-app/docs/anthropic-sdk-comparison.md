# Anthropic Agent SDK vs Our RiskAgentClient Implementation

**Date**: October 23, 2025 (Updated)
**Purpose**: Compare official Anthropic Python Agent SDK with our custom RiskAgentClient implementation

---

## Executive Summary

**Official Anthropic Agent SDK**: A comprehensive, stateful agent framework designed for complex, multi-turn conversations with tool execution, MCP server integration, automatic skill discovery, and advanced agent orchestration.

**Our RiskAgentClient**: A lightweight, domain-specific wrapper around the Anthropic Messages API focused on enhanced Skills Framework integration, Knowledge Layer, progressive disclosure, and REST API compatibility.

**Key Insight**: Both the Agent SDK and our implementation support **Agent Skills** (`.claude/skills/` with `SKILL.md` files). Our implementation extends the official Skills Framework with enhanced organization, Knowledge Layer integration, and explicit API control.

**Architecture**: We're using the **Messages API** (lower-level) with an enhanced Skills Framework implementation, rather than the **Agent SDK** (higher-level framework) with automatic skill triggering.

---

## Architecture Comparison

### Official Anthropic Agent SDK

```
┌─────────────────────────────────────────┐
│     Anthropic Agent SDK                 │
│  ┌────────────────────────────────┐    │
│  │   ClaudeSDKClient              │    │
│  │   - Stateful sessions          │    │
│  │   - Tool execution             │    │
│  │   - MCP server integration     │    │
│  │   - Hooks & permissions        │    │
│  │   - Async-first                │    │
│  └────────────────────────────────┘    │
│              ↓                          │
│  ┌────────────────────────────────┐    │
│  │   Messages API                 │    │
│  │   (Anthropic SDK)              │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Our RiskAgentClient Implementation

```
┌─────────────────────────────────────────┐
│     Risk Agents Application             │
│  ┌────────────────────────────────┐    │
│  │   RiskAgentClient              │    │
│  │   - Skills Framework           │    │
│  │   - Knowledge Layer            │    │
│  │   - Context Manager            │    │
│  │   - REST API compatible        │    │
│  └────────────────────────────────┘    │
│              ↓                          │
│  ┌────────────────────────────────┐    │
│  │   Messages API                 │    │
│  │   (Anthropic SDK)              │    │
│  └────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

**Note**: We're using the `Anthropic` class directly (Messages API), not `ClaudeSDKClient` (Agent SDK).

---

## Feature-by-Feature Comparison

| Feature | Official Agent SDK | Our RiskAgentClient | Status |
|---------|-------------------|---------------------|--------|
| **Basic Messaging** | ✅ Via ClaudeSDKClient | ✅ Via Anthropic client | ✅ Equivalent |
| **Streaming** | ✅ Async streaming | ✅ Sync streaming | ✅ Implemented |
| **Stateful Sessions** | ✅ Built-in | ➖ External (ContextManager) | ✅ Different approach |
| **Tool Execution** | ✅ @tool decorator | ❌ Not implemented | ⚠️ Could add |
| **MCP Servers** | ✅ create_sdk_mcp_server() | ❌ Not used | ℹ️ Not needed for MVP |
| **Custom Prompts** | ✅ System prompts | ✅ System prompts | ✅ Equivalent |
| **Context Management** | ✅ Built-in conversation | ✅ ContextManager | ✅ Custom implementation |
| **Async/Await** | ✅ Async-first | ➖ Sync (with async option) | ℹ️ REST API friendly |
| **Hooks** | ✅ Request/response hooks | ❌ Not implemented | ℹ️ Not needed |
| **Permissions** | ✅ Granular control | ➖ API-level only | ℹ️ Simpler |
| **Skills Framework** | ✅ `.claude/skills/` + SKILL.md | ✅ Same + enhanced | ✅ Compatible + extended |
| **Skill Triggering** | ✅ Automatic (Claude decides) | ✅ Explicit (API controls) | ℹ️ Different approach |
| **Skill Organization** | ➖ Flat structure | ✅ Nested + hybrid | ✅ Scales to 100+ |
| **Knowledge Layer** | ❌ Not included | ✅ Core feature | ✅ Our addition |
| **Progressive Disclosure** | ✅ 3 levels (metadata/instructions/resources) | ✅ 4 levels + file-based | ✅ Enhanced |
| **REST API Compatible** | ➖ Async-only | ✅ Designed for REST | ✅ Our advantage |

---

## Code Comparison

### Official Agent SDK Usage

```python
from claude_sdk import ClaudeSDKClient

# Agent SDK - Stateful, async
async with ClaudeSDKClient(
    model="claude-sonnet-4-20250514",
    system_prompt="You are a helpful assistant",
    tools=[my_tool_1, my_tool_2],
    mcp_servers=["my-server"]
) as client:
    # Send query
    await client.query("Create a Python project")

    # Stream response
    async for message in client.receive_response():
        print(message)

    # Continue conversation (stateful)
    await client.query("Add error handling")
    async for message in client.receive_response():
        print(message)
```

**Key Characteristics**:
- Async/await required
- Stateful within context manager
- Tool execution built-in
- MCP server integration
- Continuous conversation without manual state management

### Our RiskAgentClient Usage

```python
from agent.agent_client import RiskAgentClient
from agent.context_manager import ContextManager

# Our Implementation - Skills-focused, REST-friendly
client = RiskAgentClient(skills_dir=Path(".claude/skills"))
context_manager = ContextManager(context_dir=Path("context"))

# Create session (external state management)
session_id = context_manager.create_session(user_id="user123")

# Query 1
response = client.query(
    user_message="Extract action items from this meeting",
    context=context_manager.consult(session_id=session_id),
    system_prompt=None  # Uses Skills-aware default
)

# Update session
context_manager.update_session(
    session_id,
    add_history={"query": "Extract action items", "response": response}
)

# Query 2 (session continues via external context)
response = client.query(
    user_message="Format them as a table",
    context=context_manager.consult(session_id=session_id)
)

# Streaming variant
for chunk in client.query_stream(
    user_message="Generate meeting minutes",
    context=context_manager.consult(session_id=session_id)
):
    print(chunk, end='', flush=True)
```

**Key Characteristics**:
- Sync by default (async-compatible via FastAPI)
- External state via ContextManager
- Skills Framework integrated
- REST API compatible
- Manual conversation history management

---

## When to Use Which?

### Use Official Agent SDK When:
1. **Building complex agents** with multi-step reasoning and tool execution
2. **Need automatic tool discovery** and execution
3. **Using MCP servers** for extended capabilities
4. **Building autonomous agents** that can execute multiple tools
5. **Need advanced hooks** for request/response modification
6. **Async-first architecture** is natural for your application
7. **Don't need REST API** exposure (or willing to wrap it)

**Example Use Cases**:
- Code generation agents that execute compilers
- Data analysis agents that query databases
- DevOps agents that interact with infrastructure
- Research agents that browse and synthesize information

### Use Our RiskAgentClient When:
1. **Building REST APIs** that serve agent functionality
2. **Need Skills Framework** organization (domain/category/skill)
3. **Want progressive disclosure** of information
4. **Need Knowledge Layer** for domain-specific reference material
5. **Prefer explicit state management** (sessions, captures, consultation)
6. **Sync execution is fine** (or handling async at API layer)
7. **Don't need tool execution** (or implementing separately)

**Example Use Cases**:
- Meeting minutes capture service (our use case)
- Project management assistants
- Document generation APIs
- Knowledge base Q&A systems
- Domain-specific AI services

---

## Technical Deep Dive

### State Management

#### Official Agent SDK: Built-in Stateful Sessions
```python
async with ClaudeSDKClient() as client:
    await client.query("First question")
    # SDK automatically maintains conversation history

    await client.query("Follow-up question")
    # Context from first query is automatically included
```

**Pros**:
- Automatic conversation continuity
- No manual state tracking
- Simpler code for conversational agents

**Cons**:
- State lives in memory (lost on restart)
- Harder to persist to database
- Less control over what's included

#### Our Implementation: External State Management
```python
# Create session (persisted to disk)
session_id = context_manager.create_session(user_id="user123")

# Query 1
response = client.query(
    user_message="First question",
    context=context_manager.consult(session_id=session_id)
)

# Manually update history
context_manager.update_session(
    session_id,
    add_history={"query": "First question", "response": response}
)

# Query 2
response = client.query(
    user_message="Follow-up question",
    context=context_manager.consult(session_id=session_id)  # Includes history
)
```

**Pros**:
- State persisted to disk (survives restarts)
- Full control over what's included in context
- Can store in database easily
- Can load context selectively (performance)

**Cons**:
- Manual history management
- More code to maintain state
- Risk of forgetting to update state

---

### Tool Execution

#### Official Agent SDK: Decorator-Based Tools
```python
from claude_sdk import tool

@tool
def get_weather(location: str) -> str:
    """Get current weather for a location."""
    # Implementation
    return f"Weather in {location}: Sunny, 72°F"

async with ClaudeSDKClient(tools=[get_weather]) as client:
    await client.query("What's the weather in London?")
    # SDK automatically detects need for tool, calls get_weather, returns result
```

**How it works**:
1. Claude decides to use tool
2. SDK intercepts tool call
3. Executes Python function
4. Injects result back into conversation
5. Claude incorporates result into response

#### Our Implementation: No Built-in Tool Execution
We don't have automatic tool execution. If we needed it, we'd implement it at the API layer:

```python
# Option 1: Manual tool execution in API endpoint
@router.post("/query")
async def query_with_tools(request: QueryRequest):
    # Check if response includes tool call
    response = client.query(request.query)

    # If tool call detected (manual parsing)
    if "get_weather" in response:
        weather = get_weather("London")
        # Second query with tool result
        response = client.query(f"The weather is: {weather}")

    return {"response": response}

# Option 2: Use Skills Framework instead
# Skills are explicit, not automatic
response = client.query(
    user_message="What's the weather?",
    skill_name="weather-checker"  # Explicit skill invocation
)
```

**Why we don't have it**:
- MVP doesn't require tool execution
- Skills Framework provides similar capability (explicit vs automatic)
- Can add later if needed

---

### Streaming

#### Official Agent SDK: Async Streaming
```python
async with ClaudeSDKClient() as client:
    await client.query("Write a long document")

    async for message in client.receive_response():
        if message.type == "content":
            print(message.text, end='', flush=True)
        elif message.type == "tool_use":
            # Handle tool execution
            pass
```

#### Our Implementation: Sync Streaming (FastAPI Compatible)
```python
# Sync streaming generator
def query_stream(user_message: str) -> Iterator[str]:
    with self.client.messages.stream(...) as stream:
        for text in stream.text_stream:
            yield text

# Used in FastAPI with Server-Sent Events
@router.post("/query/stream")
async def query_stream(request: QueryRequest):
    async def generate():
        for chunk in agent_client.query_stream(request.query):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

**Both support streaming, just different async patterns.**

---

## Skills Framework Comparison

### Official Agent SDK Skills
**Purpose**: Extend Claude with specialized capabilities stored as SKILL.md files

**Structure**:
```
.claude/skills/
└── meeting-minutes-capture/
    └── SKILL.md
```

**SKILL.md Format**:
```yaml
---
name: meeting-minutes-capture
description: Capture meeting minutes from transcripts
---
# Skill instructions...
```

**Triggering**: Automatic (Claude detects when to use skill)
**Progressive Disclosure**: 3 levels (metadata, instructions, resources)

### Our Enhanced Skills Framework
**Purpose**: Same as official + enhanced organization + Knowledge Layer integration

**Structure**:
```
.claude/skills/
└── change-agent/                    # Domain (our enhancement)
    └── meeting-minutes-capture/     # Skill (compatible)
        ├── SKILL.md                 # Same format + enhanced metadata
        ├── instructions/            # Multiple instruction files (our enhancement)
        │   ├── capture.md
        │   └── extract-actions.md
        └── resources/               # Structured resources (our enhancement)
            ├── examples.md
            └── template.md
```

**SKILL.md Format**:
```yaml
---
name: meeting-minutes-capture
description: Capture meeting minutes from transcripts
domain: change-agent               # Our addition
category: meeting-management       # Our addition
taxonomy: change-agent/meeting-management  # Our addition
parameters: [transcript, date]     # Our addition
output_format: structured_markdown # Our addition
---
# Skill instructions...
```

**Triggering**: Explicit (API caller specifies skill)
**Progressive Disclosure**: 4 levels (metadata, instructions, resources, code) + file-based organization

### Key Differences

| Aspect | Official Agent SDK Skills | Our Enhanced Skills |
|--------|--------------------------|-------------------|
| **Location** | `.claude/skills/` | `.claude/skills/` (same) |
| **File Name** | `SKILL.md` | `SKILL.md` (same) |
| **YAML Metadata** | name, description | name, description + domain, category, taxonomy, parameters |
| **Organization** | Flat (skill-name/) | Nested (domain/skill-name/) + hybrid support |
| **Instructions** | Single SKILL.md | Multiple files in instructions/ directory |
| **Resources** | Mentioned | Structured resources/ directory |
| **Triggering** | Automatic (Claude decides) | Explicit (API controls) |
| **Knowledge Integration** | None | Knowledge Layer linked |
| **Compatibility** | Standard | ✅ Backward compatible with standard |

**Result**: Our implementation extends official Skills Framework while maintaining compatibility.

---

## Knowledge Layer - Our Unique Addition

Neither the Agent SDK nor the Messages API includes a Knowledge Layer. This is our innovation inspired by your Risk Taxonomy Framework.

### What It Provides

```
knowledge/
└── change-agent/
    ├── meeting-management/
    │   ├── meeting-types.md (6 meeting types)
    │   ├── action-items-standards.md (5-element structure)
    │   └── decision-capture.md (decision documentation)
    └── meta/
        └── knowledge-evolution.md (dual context pattern)
```

**Purpose**: Domain-specific reference material that enhances skill execution

**How It Works**:
1. Skill references knowledge: "See action-items-standards.md"
2. API loads knowledge document
3. Knowledge included in system prompt
4. Claude applies standards from knowledge

**Example**:
```python
# Load knowledge
standards = skills_loader.load_knowledge(
    "change-agent",
    "meeting-management",
    "action-items-standards.md"
)

# Enhance system prompt
system_prompt = f"""
{base_prompt}

# ACTION ITEM STANDARDS
{standards}

Apply these standards when extracting action items.
"""

# Query with enhanced knowledge
response = client.query(user_message, system_prompt=system_prompt)
```

**Result**: Claude produces action items with all 5 required elements (WHAT, WHO, WHEN, WHY, Dependencies) because the standards are in the prompt.

**This is unique to our implementation** - not available in Agent SDK or Messages API.

---

## Should We Switch to Agent SDK?

### Reasons to Consider Switching

1. **Automatic Skill Discovery**: If we want Claude to choose skills automatically
2. **Need Tool Execution**: If we want automatic tool calling via @tool decorator
3. **MCP Server Integration**: If we want to use MCP servers
4. **Hooks**: If we need request/response modification
5. **Stateful Simplicity**: Prefer built-in conversation management

### Reasons to Keep Our Implementation

1. **✅ Compatible with Official Skills**: Our Skills Framework aligns with Agent SDK's approach
2. **✅ Enhanced Organization**: Nested domain/category structure scales to 100+ skills
3. **✅ Knowledge Layer**: Our unique innovation, not available in Agent SDK
4. **✅ REST API Compatible**: Easier to expose via FastAPI
5. **✅ Explicit Control**: Better for testing and API usage (specify which skill to use)
6. **✅ Enhanced Metadata**: Domain, category, parameters support API integration
7. **✅ Already Built**: Working and tested (100+ hours invested)
8. **✅ Dual Context Pattern**: Implements your Risk Taxonomy insights
9. **✅ Progressive Disclosure**: Enhanced with file-based organization

### Hybrid Approach (Recommended)

**Keep current implementation** for Skills Framework + Knowledge Layer

**Add Agent SDK features** selectively if needed:
- Add tool execution at API layer (if needed)
- Add MCP server integration (if needed)
- Keep our Skills/Knowledge architecture

**Example**:
```python
class RiskAgentClient:
    def query_with_tools(self, user_message: str, tools: List[Tool]):
        # Use Agent SDK for this query
        async with ClaudeSDKClient(tools=tools) as sdk_client:
            return await sdk_client.query(user_message)

    def query_with_skill(self, user_message: str, skill_name: str):
        # Use our Skills Framework
        skill = skills_loader.load_skill(skill_name)
        return self.query(user_message, system_prompt=skill)
```

**Best of both worlds!**

---

## Summary

### Official Anthropic Agent SDK
- **Purpose**: Full-featured agent framework with automatic skill discovery
- **Strengths**: Tool execution, MCP servers, automatic state, automatic skill triggering
- **Skills Support**: ✅ `.claude/skills/` with SKILL.md (flat structure, automatic discovery)
- **Best For**: Autonomous agents, complex workflows, tool-heavy apps

### Our RiskAgentClient
- **Purpose**: Enhanced Skills Framework + Knowledge Layer with REST API integration
- **Strengths**: Compatible with official skills + enhanced organization, Knowledge Layer, explicit control, REST-friendly
- **Skills Support**: ✅ Same `.claude/skills/` + nested organization + enhanced metadata + Knowledge integration
- **Best For**: Domain-specific AI services, REST APIs, structured guidance, explicit skill control

### Our Verdict
**Keep our implementation** because:
1. ✅ **Compatible with official Skills Framework** - can use standard Anthropic skills
2. ✅ **Enhanced organization** - nested structure scales to 100+ skills
3. ✅ **Knowledge Layer** is unique and valuable (Risk Taxonomy dual context pattern)
4. ✅ **Progressive disclosure** enhanced with file-based organization
5. ✅ **REST API compatibility** is important for our use case
6. ✅ **Explicit control** better for testing and API usage
7. ✅ Already invested and working

**Consider adding Agent SDK features** if we need:
- Automatic skill discovery (Claude chooses skill)
- Automatic tool execution
- MCP server integration
- More complex autonomous behavior

---

## Next Steps (Optional Enhancements)

If you want to add Agent SDK features while keeping our architecture:

1. **Tool Execution**:
   - Add `@tool` decorator support
   - Integrate with Skills Framework
   - Keep Skills for structured tasks, Tools for dynamic actions

2. **MCP Servers**:
   - Add MCP server integration
   - Use for data access (databases, APIs)
   - Keep Skills for task guidance

3. **Async Refactor**:
   - Make RiskAgentClient async-compatible
   - Keep sync interface for backwards compatibility
   - Better FastAPI integration

4. **Hooks**:
   - Add request/response hooks
   - Use for logging, monitoring, debugging
   - Keep simple for now

**Current implementation is production-ready as-is.** These are enhancements, not requirements.

---

**Document Version**: 1.0
**Created**: October 23, 2025
**Author**: Claude Assistant
**Status**: Comprehensive comparison complete
