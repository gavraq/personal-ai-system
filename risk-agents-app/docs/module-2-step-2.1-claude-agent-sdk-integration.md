# Module 2, Step 2.1: Claude Agent SDK Integration

**Completed**: October 22, 2025

## What We Built

In this step, we created the `RiskAgentClient` class - a wrapper around Anthropic's Claude SDK that provides Skills Framework awareness. This is the core AI engine that powers Risk Agents.

## Why This Matters

The `RiskAgentClient` is the bridge between our application and Claude AI. It:
- Manages communication with Claude API
- Injects Skills Framework context into queries
- Supports both standard and streaming responses
- Provides session context to Claude
- Makes Claude "aware" of our skills structure

## File Created

**File**: `backend/agent/agent_client.py` (250 lines)

## Key Concepts Explained

### 1. What is the Anthropic SDK?

The Anthropic SDK is the official Python library for interacting with Claude AI. It provides:
- Authentication with API keys
- Message sending/receiving
- Streaming support for real-time responses
- Error handling

**Example of basic SDK usage**:
```python
from anthropic import Anthropic

client = Anthropic(api_key="your-key")
response = client.messages.create(
    model="claude-sonnet-4-20250514",  # Sonnet 4.5 - latest model
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### 2. Why Wrap the SDK?

Instead of using the Anthropic SDK directly everywhere, we created a wrapper class because:

1. **Skills Framework Integration**: We need Claude to know about our skills
2. **Context Management**: We inject session data into queries
3. **Consistent Configuration**: Model settings in one place
4. **Reusability**: Same client used throughout the app
5. **Easier Testing**: Can mock the wrapper for tests

### 3. System Prompts

A **system prompt** tells Claude who it is and what it can do. Our system prompt:
- Explains Claude is "Risk Agents"
- Lists available skill domains and categories
- Describes how to use skills
- Sets the tone and behavior

**Example from our code**:
```python
def _build_system_prompt(self) -> str:
    return """You are Risk Agents, a specialized AI assistant for project management.

    You have access to a Skills Framework organized in a .claude/skills directory.

    Available skill domains:
    - Meeting Management
    - Project Setup
    - Requirements Gathering
    ...
    """
```

This is why Claude "knows" about our skills without us having to tell it every time!

### 4. Standard vs Streaming Queries

**Standard Query**: Get the complete response all at once
```python
response = client.query("Help me capture meeting minutes")
# response = "Here's how to capture minutes... [complete text]"
```

**Streaming Query**: Get response in chunks as it's generated
```python
for chunk in client.query_stream("Help me capture meeting minutes"):
    print(chunk, end='')  # Prints: H...e...r...e...'...s... [real-time]
```

Streaming provides better user experience - users see text appearing rather than waiting.

### 5. Context Injection

Context is additional information provided to Claude:
```python
context = {
    "project_name": "Risk Agents",
    "current_task": "Creating meeting minutes",
    "user_role": "Project Manager"
}

response = client.query("Help me", context=context)
```

Claude receives this context and can use it to give more relevant answers.

## Code Walkthrough

Let's walk through the key parts of `RiskAgentClient`:

### Class Initialization

```python
def __init__(self, skills_dir: Path):
    self.skills_dir = skills_dir
    self.api_key = os.getenv("ANTHROPIC_API_KEY")

    if not self.api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    self.client = Anthropic(api_key=self.api_key)
    self.model = "claude-sonnet-4-20250514"
    self.max_tokens = 8192
```

**What's happening**:
1. Store skills directory path (will be used later)
2. Get API key from environment variable (from .env file)
3. Validate API key exists (fail early if missing)
4. Create Anthropic client with the key
5. Set model (Claude Sonnet 4.5 - latest and best as of May 2025)
6. Set max response length (8192 tokens ≈ 6000 words - Sonnet 4.5 upgrade!)

**Why this design**:
- Environment variables keep secrets out of code
- Path injection makes testing easier
- Fail fast if API key missing (better than failing during first query)

### Standard Query Method

```python
def query(
    self,
    user_message: str,
    context: Optional[Dict[str, Any]] = None,
    system_prompt: Optional[str] = None
) -> str:
    # Build system prompt with Skills Framework awareness
    final_system_prompt = system_prompt or self._build_system_prompt()

    # Add context to system prompt if provided
    if context:
        context_text = self._format_context(context)
        final_system_prompt += f"\n\n{context_text}"

    # Call Claude API
    response = self.client.messages.create(
        model=self.model,
        max_tokens=self.max_tokens,
        system=final_system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    # Extract text from response
    return response.content[0].text
```

**What's happening**:
1. Build or use provided system prompt (tells Claude who it is)
2. If context provided, add it to system prompt (gives Claude session info)
3. Call Claude API with system prompt and user message
4. Extract just the text from response (Claude returns structured object)

**Parameters explained**:
- `user_message`: What the user asked ("Help me capture meeting minutes")
- `context`: Optional session data (project name, user info, etc.)
- `system_prompt`: Optional custom prompt (usually we use default)

**Return value**: Claude's response as plain text string

### Streaming Query Method

```python
def query_stream(
    self,
    user_message: str,
    context: Optional[Dict[str, Any]] = None,
    system_prompt: Optional[str] = None
) -> Iterator[str]:
    # Build system prompt (same as query method)
    final_system_prompt = system_prompt or self._build_system_prompt()

    if context:
        context_text = self._format_context(context)
        final_system_prompt += f"\n\n{context_text}"

    # Stream response from Claude
    with self.client.messages.stream(
        model=self.model,
        max_tokens=self.max_tokens,
        system=final_system_prompt,
        messages=[{"role": "user", "content": user_message}]
    ) as stream:
        for text in stream.text_stream:
            yield text
```

**What's happening**:
1. Same setup as `query` method (system prompt, context)
2. Use `messages.stream()` instead of `messages.create()`
3. Use `with` statement to manage stream lifecycle
4. `yield` each text chunk as it arrives (generator pattern)

**Generator Pattern**:
- `yield` makes this a generator function
- Caller can iterate: `for chunk in client.query_stream(...)`
- Memory efficient - doesn't load entire response at once
- Real-time delivery - chunks sent immediately

### System Prompt Builder

```python
def _build_system_prompt(self) -> str:
    return """You are Risk Agents, a specialized AI assistant for project management.

    You have access to a Skills Framework organized in a .claude/skills directory.
    Each skill follows progressive disclosure - you can load metadata, instructions, and resources as needed.

    ## Available Skill Domains

    ### Change Agent (Project Management)
    Skills organized by category:
    - **Meeting Management**: meeting-minutes-capture, action-item-tracking, follow-up-generator
    - **Project Setup**: project-charter-generator, stakeholder-analysis, project-plan-template
    - **Requirements Gathering**: business-requirements-capture, requirement-validation, use-case-generator
    - **Project Artifacts**: raci-matrix-generator, communication-plan, risk-register-setup
    - **Status Tracking**: status-report-generator, milestone-tracker, issue-log-manager

    ## How to Use Skills

    When a user asks for help:
    1. Identify which skill(s) are relevant to their request
    2. Load the skill metadata to understand its purpose and parameters
    3. If needed, load detailed instructions from the skill's instructions/ directory
    4. Execute the skill with the provided information
    5. Format the output according to the skill's specification

    ...
    """
```

**What's happening**:
1. Define who Claude is ("Risk Agents")
2. Explain the Skills Framework structure
3. List available skill domains and categories
4. Provide instructions on how to use skills
5. Set expectations for behavior and output

**Why this works**:
- Claude reads this EVERY time it responds
- Makes Claude "aware" of skills without loading all skill files
- Guides Claude on how to help users
- Sets professional, helpful tone

### Context Formatter

```python
def _format_context(self, context: Dict[str, Any]) -> str:
    context_lines = ["## Session Context"]

    for key, value in context.items():
        if value:
            context_lines.append(f"**{key.replace('_', ' ').title()}**: {value}")

    return "\n".join(context_lines)
```

**What's happening**:
1. Start with "Session Context" header
2. Loop through context dictionary
3. Format each key-value pair nicely (replace _ with spaces, capitalize)
4. Join all lines with newlines

**Example transformation**:
```python
# Input:
context = {
    "project_name": "Risk Agents",
    "user_role": "Project Manager"
}

# Output:
## Session Context
**Project Name**: Risk Agents
**User Role**: Project Manager
```

This formatted text is appended to the system prompt.

### Utility Methods

```python
def get_available_skills(self) -> List[str]:
    """Scan skills directory and return list of skill names"""
    skills = []

    for domain_dir in self.skills_dir.iterdir():
        if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
            for skill_dir in domain_dir.iterdir():
                if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                    skills.append(f"{domain_dir.name}/{skill_dir.name}")

    return skills
```

**What's happening**:
1. Scan the skills directory
2. Look for domain directories (change-agent, etc.)
3. Look for skill directories within domains
4. Check if SKILL.md exists (confirms it's a valid skill)
5. Add to list in format "domain/skill-name"

**Example output**:
```python
[
    "change-agent/meeting-minutes-capture",
    "change-agent/action-item-tracking",
    "change-agent/project-charter-generator",
    ...
]
```

```python
def test_connection(self) -> Dict[str, Any]:
    """Test if API connection works"""
    try:
        response = self.query("Hello! Please respond with 'Connection successful'")
        return {
            "status": "connected",
            "model": self.model,
            "response": response[:100],
            "skills_available": len(self.get_available_skills())
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

**What's happening**:
1. Try a simple query to Claude
2. If successful, return status with model info and skills count
3. If error, catch it and return error status

**Why this is useful**:
- Quick way to verify API key is valid
- Check if Claude is responding
- See how many skills are available
- Useful for debugging connection issues

## How to Use This Client

### Example 1: Simple Query

```python
from pathlib import Path
from agent import RiskAgentClient

# Create client
client = RiskAgentClient(skills_dir=Path(".claude/skills"))

# Ask a question
response = client.query("Help me capture meeting minutes from this transcript: ...")

print(response)
```

### Example 2: Query with Context

```python
# Create client
client = RiskAgentClient(skills_dir=Path(".claude/skills"))

# Prepare context
context = {
    "project_name": "Risk Agents MVP",
    "meeting_date": "2025-10-22",
    "attendees": ["John", "Sarah", "Mike"]
}

# Ask with context
response = client.query(
    "Create meeting minutes from this transcript: ...",
    context=context
)

print(response)
```

### Example 3: Streaming Response

```python
# Create client
client = RiskAgentClient(skills_dir=Path(".claude/skills"))

# Stream response
print("Claude: ", end='')
for chunk in client.query_stream("Help me create a project charter"):
    print(chunk, end='', flush=True)  # Print each chunk immediately
print()  # Newline at end
```

### Example 4: Test Connection

```python
# Create client
client = RiskAgentClient(skills_dir=Path(".claude/skills"))

# Test connection
status = client.test_connection()

if status["status"] == "connected":
    print(f"✅ Connected to Claude ({status['model']})")
    print(f"📚 {status['skills_available']} skills available")
else:
    print(f"❌ Connection failed: {status['error']}")
```

## Environment Setup

The client needs the `ANTHROPIC_API_KEY` environment variable:

**File**: `.env` (already created in Module 1)
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx  # Your actual API key
```

**How to get an API key**:
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new key
5. Copy and paste into `.env` file

**Cost**: Claude API is pay-per-use:
- ~$3 per million input tokens
- ~$15 per million output tokens
- Most queries: $0.01 - $0.05 each

## Dependencies Required

Already installed in Module 1 (`pyproject.toml`):
```toml
dependencies = [
    "anthropic>=0.34.0",  # Anthropic SDK
    ...
]
```

## Testing the Client

We'll test this in Step 2.7, but here's what we'll verify:

- [ ] Client initializes without errors
- [ ] API key is loaded from environment
- [ ] System prompt is generated correctly
- [ ] Can make a simple query to Claude
- [ ] Streaming responses work
- [ ] Context injection works
- [ ] Skills directory is scanned correctly
- [ ] Error handling works (invalid API key)

## Common Issues & Solutions

### Issue 1: "ANTHROPIC_API_KEY environment variable not set"

**Cause**: Missing API key in .env file

**Solution**:
```bash
# Add to .env file
echo "ANTHROPIC_API_KEY=sk-ant-api03-xxxxx" >> .env

# Restart Docker containers to pick up new env var
docker-compose restart backend
```

### Issue 2: API key doesn't work

**Cause**: Invalid or expired API key

**Solution**:
- Check API key is copied correctly (no extra spaces)
- Verify key is active in Anthropic console
- Check account has credits/billing set up

### Issue 3: "ImportError: No module named 'anthropic'"

**Cause**: Anthropic package not installed

**Solution**:
```bash
# The package is already in pyproject.toml, so rebuild Docker:
docker-compose build backend
docker-compose up backend
```

### Issue 4: Slow responses

**Cause**: Claude takes 5-30 seconds to respond (normal for complex queries)

**Solution**:
- Use streaming queries for better UX
- Show loading indicator to user
- Consider caching common responses
- This is why we built streaming support!

## Design Decisions Explained

### Why use environment variables for API key?
- **Security**: Never commit secrets to Git
- **Flexibility**: Different keys for dev/staging/production
- **Standard practice**: Industry best practice for secrets

### Why wrap the Anthropic SDK?
- **Abstraction**: Hide implementation details
- **Skills integration**: Need to inject system prompt
- **Testing**: Easier to mock wrapper than SDK
- **Future-proofing**: Can swap AI providers later

### Why both query() and query_stream()?
- **Different use cases**:
  - `query()`: Simple responses, batch processing
  - `query_stream()`: Interactive chat, better UX
- **Same interface**: Both take same parameters
- **Easy to switch**: Change one word in calling code

### Why store skills_dir in client?
- **Future use**: Will use to load skill details
- **Validation**: Can check skills exist
- **Dynamic prompts**: System prompt can list actual skills
- **Loose coupling**: Client doesn't need to know about SkillsLoader yet

## What's Next

In **Step 2.2**, we'll create the `SkillsLoader` class that:
- Implements progressive disclosure
- Loads skill metadata from SKILL.md files
- Loads instructions and resources on-demand
- Provides skill browsing and filtering

The `RiskAgentClient` will eventually use `SkillsLoader` to load specific skill instructions when Claude needs them!

## Key Takeaways

1. **RiskAgentClient wraps Anthropic SDK** with Skills Framework awareness
2. **System prompts make Claude aware** of skills without loading files
3. **Streaming provides better UX** for interactive responses
4. **Context injection gives Claude session information**
5. **Environment variables keep secrets safe**
6. **The client is reusable** throughout the application

---

**Files Created**: 1 (`backend/agent/agent_client.py`)
**Lines of Code**: 250
**Time to Complete**: ~45 minutes
**Dependencies**: anthropic package (already installed)

**Next Step**: [Module 2, Step 2.2: Skills Loader Implementation](module-2-step-2.2-skills-loader.md)
