# Module 2, Step 2.3: Context Manager Implementation

**Completed**: October 23, 2025

## What We Built

In this step, we created the `ContextManager` class - a session and context management system that implements the **3 C's pattern**: Capture, Curate, and Consult. This allows the Risk Agents application to maintain conversation context, store captured information, and retrieve relevant data for queries.

## Why This Matters

The `ContextManager` is essential for:
- **Session continuity**: Maintaining context across multiple interactions
- **Information capture**: Storing meeting minutes, documents, decisions
- **Context retrieval**: Providing relevant background for Claude queries
- **Conversation history**: Tracking what has been discussed
- **User-specific data**: Managing per-user sessions and captures

## File Created

**File**: `backend/agent/context_manager.py` (343 lines)

## Key Concepts Explained

### 1. What is the 3 C's Pattern?

The **3 C's** is a context management pattern:

**1. Capture** 📥
- Store information from conversations
- Save meeting minutes, documents, notes
- Record decisions and action items

**2. Curate** 🗂️
- Organize captured information
- Structure data for easy retrieval
- Add metadata and tags

**3. Consult** 🔍
- Retrieve relevant context for queries
- Provide background information to Claude
- Surface related captures and history

**Example Flow**:
```
User: "Let's discuss the Q4 project"
↓ Capture
Store: Meeting started on Q4 project
↓ Curate
Organize: Type=meeting, Topic=Q4, Date=2025-10-23
↓ Consult
Retrieve: Previous Q4 discussions, related decisions
→ Claude uses this context to respond intelligently
```

### 2. What are Sessions?

A **session** represents a conversation or workflow instance.

**Session Data Structure**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "john@example.com",
  "created_at": "2025-10-23T10:30:00Z",
  "updated_at": "2025-10-23T10:45:00Z",
  "context": {
    "project": "Q4 Planning",
    "stakeholders": ["Alice", "Bob", "Charlie"],
    "budget": 100000
  },
  "history": [
    {
      "action": "meeting_started",
      "timestamp": "2025-10-23T10:30:00Z"
    },
    {
      "action": "decision_made",
      "decision": "Approved budget increase",
      "timestamp": "2025-10-23T10:35:00Z"
    }
  ]
}
```

**Why Sessions?**
- Maintain context across multiple queries
- Track conversation flow
- Associate captures with workflows
- Enable resuming conversations

### 3. What are Captures?

A **capture** is stored information from any source.

**Capture Data Structure**:
```json
{
  "capture_id": "123e4567-e89b-12d3-a456-426614174000",
  "capture_type": "meeting",
  "captured_at": "2025-10-23T10:30:00Z",
  "data": {
    "title": "Q4 Planning Meeting",
    "attendees": ["Alice", "Bob", "Charlie"],
    "decisions": ["Approved budget increase to $100k"],
    "action_items": [
      {
        "task": "Prepare project charter",
        "owner": "Alice",
        "due_date": "2025-10-30"
      }
    ]
  },
  "metadata": {
    "duration": "45 minutes",
    "location": "Conference Room A"
  }
}
```

**Types of Captures**:
- **meeting**: Meeting minutes and outcomes
- **document**: Uploaded documents or reports
- **note**: Quick notes or reminders
- **decision**: Important decisions made
- **action_item**: Tasks and action items

### 4. File-Based Storage vs Database

**Our MVP Approach** (file-based):
```
context/
├── sessions/
│   ├── 550e8400-e29b-41d4-a716-446655440000.json
│   └── 7c9e6679-7425-40de-944b-e07fc1f90ae7.json
└── captured/
    ├── 123e4567-e89b-12d3-a456-426614174000.json
    └── 456e7890-e12b-34d5-b678-901234567890.json
```

**Pros of File-Based**:
- ✅ Simple to implement
- ✅ No database setup required
- ✅ Easy to debug (just open JSON files)
- ✅ Version control friendly (can commit to git if needed)
- ✅ Perfect for MVP and development

**Future Database Approach**:
- Better performance at scale (1000+ sessions)
- Complex queries (search, filter, aggregate)
- Concurrent access handling
- Transactional guarantees

**For now**: Files are perfect! We can upgrade later without changing the API.

### 5. UUIDs for Identifiers

**UUID** (Universally Unique Identifier) is a 128-bit identifier:

```python
import uuid

session_id = str(uuid.uuid4())
# Result: "550e8400-e29b-41d4-a716-446655440000"
```

**Why UUIDs?**
- **Globally unique**: No collisions across systems
- **No coordination needed**: Generate anywhere without checking
- **Hard to guess**: Security through obscurity (not primary security)
- **Standard format**: Recognized everywhere

**Alternative approaches** (not used):
- Auto-incrementing IDs: Require coordination, reveal count
- Random strings: Not standardized, potential collisions

### 6. ISO 8601 Timestamps

**ISO 8601** is the international timestamp standard:

```python
from datetime import datetime

timestamp = datetime.utcnow().isoformat()
# Result: "2025-10-23T10:30:45.123456"
```

**Format**: `YYYY-MM-DDTHH:MM:SS.microseconds`

**Why ISO 8601?**
- **Universal standard**: Recognized globally
- **Sortable as strings**: "2025-10-23" < "2025-10-24"
- **Timezone aware**: Can add Z (UTC) or offset
- **Human readable**: Easy to parse visually
- **JSON compatible**: Works perfectly in JSON

### 7. JSON for Data Storage

**JSON** (JavaScript Object Notation) for persistent storage:

```python
import json

data = {"name": "John", "age": 30}
with open("data.json", 'w') as f:
    json.dump(data, f, indent=2)
```

**Why JSON?**
- Human-readable text format
- Native Python support (dict ↔ JSON)
- Universal language support
- Easy to version control
- Simple to debug and inspect

## Code Walkthrough

### Initialization

```python
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import uuid


class ContextManager:
    """
    Manage session context and captured information

    This implements a simplified version of the "3 C's" (Capture, Curate, Consult):
    - Capture: Store information from conversations
    - Curate: Organize and structure captured data
    - Consult: Retrieve relevant context for queries

    For MVP, we use file-based storage. Future versions could use a database.
    """

    def __init__(self, context_dir: Path):
        """
        Initialize the Context Manager

        Args:
            context_dir: Path to context storage directory
        """
        self.context_dir = context_dir
        self.captured_dir = context_dir / "captured"
        self.sessions_dir = context_dir / "sessions"

        # Ensure directories exist
        self.captured_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
```

**What's happening**:
1. Accept `context_dir` as parameter (dependency injection for testing)
2. Create subdirectories: `captured/` and `sessions/`
3. Use `mkdir(parents=True, exist_ok=True)` to safely create directories
   - `parents=True`: Create parent directories if needed
   - `exist_ok=True`: Don't error if directory already exists

**Directory structure created**:
```
context/
├── captured/     # Captured information (meetings, docs, etc.)
└── sessions/     # Session data (conversations, workflows)
```

### Session Management

#### Creating a Session

```python
def create_session(self, user_id: Optional[str] = None) -> str:
    """
    Create a new session

    Args:
        user_id: Optional user identifier

    Returns:
        Session ID (UUID)
    """
    session_id = str(uuid.uuid4())
    session_data = {
        "session_id": session_id,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "context": {},
        "history": []
    }

    session_path = self.sessions_dir / f"{session_id}.json"
    with open(session_path, 'w') as f:
        json.dump(session_data, f, indent=2)

    return session_id
```

**What's happening**:
1. **Generate UUID**: Create unique session ID
2. **Build session data**: Initialize with empty context and history
3. **Add timestamps**: Record creation time (UTC for consistency)
4. **Save to file**: Write JSON file named `{session_id}.json`
5. **Return ID**: Give caller the session ID for future reference

**Usage example**:
```python
manager = ContextManager(Path("context"))

# Create anonymous session
session_id = manager.create_session()
# Returns: "550e8400-e29b-41d4-a716-446655440000"

# Create user-specific session
session_id = manager.create_session(user_id="john@example.com")
# Returns: "7c9e6679-7425-40de-944b-e07fc1f90ae7"
```

#### Retrieving a Session

```python
def get_session(self, session_id: str) -> Dict[str, Any]:
    """
    Retrieve session data

    Args:
        session_id: Session identifier

    Returns:
        Session data dictionary

    Raises:
        FileNotFoundError: If session doesn't exist
    """
    session_path = self.sessions_dir / f"{session_id}.json"

    if not session_path.exists():
        raise FileNotFoundError(f"Session not found: {session_id}")

    with open(session_path, 'r') as f:
        return json.load(f)
```

**What's happening**:
1. Build path to session file
2. Check if file exists (explicit error handling)
3. Read and parse JSON
4. Return complete session data

**Error handling**: Raises `FileNotFoundError` with clear message if session doesn't exist.

#### Updating a Session

```python
def update_session(
    self,
    session_id: str,
    context: Optional[Dict[str, Any]] = None,
    add_history: Optional[Dict[str, Any]] = None
) -> None:
    """
    Update session with new context or history

    Args:
        session_id: Session identifier
        context: New context data to merge
        add_history: History item to append
    """
    session = self.get_session(session_id)

    # Update context
    if context:
        session["context"].update(context)

    # Add to history
    if add_history:
        session["history"].append({
            **add_history,
            "timestamp": datetime.utcnow().isoformat()
        })

    # Update timestamp
    session["updated_at"] = datetime.utcnow().isoformat()

    # Save
    session_path = self.sessions_dir / f"{session_id}.json"
    with open(session_path, 'w') as f:
        json.dump(session, f, indent=2)
```

**What's happening**:
1. **Load session**: Get current data
2. **Merge context**: Use `.update()` to merge new context (preserves existing)
3. **Append history**: Add new history item with auto-timestamp
4. **Update timestamp**: Record when session was last modified
5. **Save**: Write updated session back to file

**The `**add_history` syntax**: Spreads dictionary contents:
```python
add_history = {"action": "decision_made", "decision": "Approved"}
{**add_history, "timestamp": "2025-10-23T10:30:00Z"}
# Result: {"action": "decision_made", "decision": "Approved", "timestamp": "2025-10-23T10:30:00Z"}
```

**Usage example**:
```python
# Add context
manager.update_session(
    session_id,
    context={"project": "Q4 Planning", "budget": 100000}
)

# Add history
manager.update_session(
    session_id,
    add_history={"action": "decision_made", "decision": "Approved budget"}
)

# Do both at once
manager.update_session(
    session_id,
    context={"status": "active"},
    add_history={"action": "meeting_started"}
)
```

#### Getting Session Context

```python
def get_session_context(self, session_id: str) -> Dict[str, Any]:
    """
    Get just the context portion of a session

    Args:
        session_id: Session identifier

    Returns:
        Context dictionary
    """
    session = self.get_session(session_id)
    return session.get("context", {})
```

**What's happening**:
1. Load full session
2. Extract just the `context` field
3. Return empty dict if no context (safe default)

**Why separate method?**
- Often you only need context, not history
- Clearer intent in code
- Simpler API for common use case

#### Getting Session History

```python
def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get session history

    Args:
        session_id: Session identifier
        limit: Optional limit on number of history items

    Returns:
        List of history items (most recent first)
    """
    session = self.get_session(session_id)
    history = session.get("history", [])

    # Reverse to get most recent first
    history = list(reversed(history))

    if limit:
        history = history[:limit]

    return history
```

**What's happening**:
1. Load session
2. Extract history (default to empty list)
3. **Reverse**: Most recent items first (more intuitive)
4. **Limit**: Optional truncation to N most recent items
5. Return filtered list

**Why reverse?**
```python
# Without reverse (chronological)
history = [
    {"action": "session_created", "timestamp": "10:30"},
    {"action": "query1", "timestamp": "10:32"},
    {"action": "query2", "timestamp": "10:35"}  # Most recent LAST
]

# With reverse (most recent first)
history = [
    {"action": "query2", "timestamp": "10:35"},  # Most recent FIRST
    {"action": "query1", "timestamp": "10:32"},
    {"action": "session_created", "timestamp": "10:30"}
]
```

Most recent first is more useful for showing "latest activity"!

### Information Capture (The First "C")

#### Capturing Information

```python
def capture(
    self,
    data: Dict[str, Any],
    capture_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Capture information (from meetings, documents, etc.)

    This is the "Capture" part of the 3 C's.

    Args:
        data: The captured data
        capture_type: Type of capture (meeting, document, note, etc.)
        metadata: Optional metadata about the capture

    Returns:
        Capture ID
    """
    capture_id = str(uuid.uuid4())
    capture_data = {
        "capture_id": capture_id,
        "capture_type": capture_type,
        "captured_at": datetime.utcnow().isoformat(),
        "data": data,
        "metadata": metadata or {}
    }

    capture_path = self.captured_dir / f"{capture_id}.json"
    with open(capture_path, 'w') as f:
        json.dump(capture_data, f, indent=2)

    return capture_id
```

**What's happening**:
1. Generate unique capture ID
2. Wrap data with metadata (type, timestamp, ID)
3. Save to `captured/` directory
4. Return capture ID for future reference

**Usage examples**:
```python
# Capture meeting minutes
capture_id = manager.capture(
    data={
        "title": "Q4 Planning Meeting",
        "attendees": ["Alice", "Bob"],
        "decisions": ["Approved budget increase"],
        "action_items": [
            {"task": "Create charter", "owner": "Alice", "due": "2025-10-30"}
        ]
    },
    capture_type="meeting",
    metadata={"duration": "45 min", "location": "Conf Room A"}
)

# Capture a document
capture_id = manager.capture(
    data={
        "filename": "requirements.pdf",
        "summary": "Project requirements document",
        "key_points": ["Budget: $100k", "Timeline: Q4", "Team: 5 people"]
    },
    capture_type="document",
    metadata={"file_size": "2.5MB", "uploaded_by": "john@example.com"}
)

# Capture a quick note
capture_id = manager.capture(
    data={"note": "Remember to follow up with stakeholders"},
    capture_type="note"
)
```

#### Retrieving a Capture

```python
def get_capture(self, capture_id: str) -> Dict[str, Any]:
    """
    Retrieve captured information

    Args:
        capture_id: Capture identifier

    Returns:
        Captured data dictionary
    """
    capture_path = self.captured_dir / f"{capture_id}.json"

    if not capture_path.exists():
        raise FileNotFoundError(f"Capture not found: {capture_id}")

    with open(capture_path, 'r') as f:
        return json.load(f)
```

**What's happening**: Same pattern as `get_session` - load and parse JSON.

#### Listing Captures

```python
def list_captures(
    self,
    capture_type: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    List all captures, optionally filtered by type

    Args:
        capture_type: Optional filter by capture type
        limit: Optional limit on number of results

    Returns:
        List of capture summaries
    """
    captures = []

    for capture_file in self.captured_dir.glob("*.json"):
        with open(capture_file, 'r') as f:
            capture = json.load(f)

            # Filter by type if specified
            if capture_type and capture.get("capture_type") != capture_type:
                continue

            # Add summary info
            captures.append({
                "capture_id": capture["capture_id"],
                "capture_type": capture["capture_type"],
                "captured_at": capture["captured_at"],
                "metadata": capture.get("metadata", {})
            })

    # Sort by date (most recent first)
    captures.sort(key=lambda x: x["captured_at"], reverse=True)

    if limit:
        captures = captures[:limit]

    return captures
```

**What's happening**:
1. **Glob files**: `glob("*.json")` finds all JSON files
2. **Load each**: Read and parse each capture
3. **Filter**: Skip captures that don't match type filter
4. **Summarize**: Return metadata only (not full data - performance!)
5. **Sort**: Most recent first
6. **Limit**: Optional truncation

**The `.glob()` method**:
```python
# Find all JSON files
files = captured_dir.glob("*.json")
# Returns iterator of Path objects

# Find all markdown files recursively
files = captured_dir.glob("**/*.md")
```

**The `lambda` function**:
```python
# Sort by captured_at field
captures.sort(key=lambda x: x["captured_at"], reverse=True)

# Equivalent to:
def get_timestamp(capture):
    return capture["captured_at"]

captures.sort(key=get_timestamp, reverse=True)
```

Lambda is just an anonymous function!

### Context Consultation (The Third "C")

```python
def consult(
    self,
    query: str,
    session_id: Optional[str] = None,
    capture_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Consult captured information and session context

    This is the "Consult" part of the 3 C's - retrieving relevant context.

    Args:
        query: The user's query
        session_id: Optional session to include context from
        capture_types: Optional list of capture types to include

    Returns:
        Dictionary with relevant context
    """
    context = {}

    # Add session context if provided
    if session_id:
        try:
            session_context = self.get_session_context(session_id)
            if session_context:
                context["session"] = session_context
        except FileNotFoundError:
            pass

    # Add recent captures
    captures = self.list_captures(limit=5)
    if captures:
        context["recent_captures"] = captures

    # TODO: Future enhancement - semantic search over captured data
    # For now, we just return recent items

    return context
```

**What's happening**:
1. **Build context dict**: Start empty
2. **Add session context**: If session provided, include its context
3. **Add recent captures**: Last 5 captures (regardless of query - MVP approach)
4. **Return combined context**: Dictionary with all relevant info

**Future enhancement** (noted in TODO):
- Semantic search: Find captures relevant to query
- Keyword matching: Search capture content
- Vector embeddings: Find similar content
- Relevance ranking: Score captures by relevance

**For MVP**: Just return recent items. Simple but effective!

**Usage example**:
```python
# Get context for a query
context = manager.consult(
    query="What decisions did we make about Q4 budget?",
    session_id=session_id
)

# Result:
{
    "session": {
        "project": "Q4 Planning",
        "budget": 100000,
        "status": "active"
    },
    "recent_captures": [
        {
            "capture_id": "123...",
            "capture_type": "meeting",
            "captured_at": "2025-10-23T10:30:00Z",
            "metadata": {"duration": "45 min"}
        },
        # ... 4 more recent captures
    ]
}

# This context is then passed to Claude for informed responses!
```

### Listing and Cleanup

#### List All Sessions

```python
def list_sessions(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    List all sessions

    Args:
        limit: Optional limit on number of results

    Returns:
        List of session summaries
    """
    sessions = []

    for session_file in self.sessions_dir.glob("*.json"):
        with open(session_file, 'r') as f:
            session = json.load(f)

            sessions.append({
                "session_id": session["session_id"],
                "user_id": session.get("user_id"),
                "created_at": session["created_at"],
                "updated_at": session["updated_at"],
                "history_count": len(session.get("history", []))
            })

    # Sort by update date (most recent first)
    sessions.sort(key=lambda x: x["updated_at"], reverse=True)

    if limit:
        sessions = sessions[:limit]

    return sessions
```

**What's happening**: Same pattern as `list_captures` - glob, load, summarize, sort, limit.

#### Delete Operations

```python
def delete_session(self, session_id: str) -> None:
    """
    Delete a session

    Args:
        session_id: Session identifier
    """
    session_path = self.sessions_dir / f"{session_id}.json"
    if session_path.exists():
        session_path.unlink()

def delete_capture(self, capture_id: str) -> None:
    """
    Delete a capture

    Args:
        capture_id: Capture identifier
    """
    capture_path = self.captured_dir / f"{capture_id}.json"
    if capture_path.exists():
        capture_path.unlink()
```

**What's happening**:
1. Build path to file
2. Check if exists (silent if not - idempotent)
3. Delete file with `.unlink()` (standard Path method)

**Why `.unlink()`?** Historical Unix terminology for deleting files.

## How to Use the ContextManager

### Example 1: Complete Session Flow

```python
from pathlib import Path
from agent import ContextManager

# Initialize
manager = ContextManager(context_dir=Path("context"))

# 1. Create session
session_id = manager.create_session(user_id="john@example.com")
print(f"Session created: {session_id}")

# 2. Add context as conversation progresses
manager.update_session(
    session_id,
    context={"project": "Q4 Planning", "budget": 100000}
)

# 3. Record history
manager.update_session(
    session_id,
    add_history={"action": "query", "query": "What's the budget?"}
)

# 4. Get context for next query
context = manager.get_session_context(session_id)
print(f"Current context: {context}")
# Output: {'project': 'Q4 Planning', 'budget': 100000}

# 5. Get recent history
history = manager.get_session_history(session_id, limit=3)
print(f"Recent history: {history}")
```

### Example 2: Capture Meeting Minutes

```python
# User completes a meeting
meeting_data = {
    "title": "Q4 Planning Meeting",
    "date": "2025-10-23",
    "attendees": ["Alice", "Bob", "Charlie"],
    "agenda": [
        "Review Q3 results",
        "Plan Q4 objectives",
        "Discuss budget"
    ],
    "decisions": [
        "Approved budget increase to $100k",
        "Hired 2 additional team members"
    ],
    "action_items": [
        {
            "task": "Prepare project charter",
            "owner": "Alice",
            "due_date": "2025-10-30"
        },
        {
            "task": "Setup project tracking",
            "owner": "Bob",
            "due_date": "2025-10-27"
        }
    ]
}

# Capture it
capture_id = manager.capture(
    data=meeting_data,
    capture_type="meeting",
    metadata={
        "duration": "45 minutes",
        "location": "Conference Room A"
    }
)

print(f"Meeting captured: {capture_id}")

# Later, retrieve it
captured_meeting = manager.get_capture(capture_id)
print(f"Retrieved: {captured_meeting['data']['title']}")
```

### Example 3: Context-Aware Query

```python
from agent import RiskAgentClient, ContextManager

# Initialize components
manager = ContextManager(context_dir=Path("context"))
client = RiskAgentClient(skills_dir=Path(".claude/skills"))

# Create session
session_id = manager.create_session(user_id="john@example.com")

# Capture meeting minutes (using meeting-minutes-capture skill)
meeting_transcript = """
Meeting on Oct 23, 2025 with Alice, Bob, and Charlie.
We discussed Q4 planning and decided to increase budget to $100k.
Alice will prepare the project charter by Oct 30.
"""

# Use Claude to capture structured minutes
structured_minutes = client.query(
    f"Capture meeting minutes from this transcript:\n{meeting_transcript}",
    context={}  # Could include session context here
)

# Save captured minutes
capture_id = manager.capture(
    data={"structured_minutes": structured_minutes},
    capture_type="meeting"
)

# Update session with meeting info
manager.update_session(
    session_id,
    context={"last_meeting": capture_id, "project": "Q4 Planning"}
)

# Later query with context
context = manager.consult(
    query="What did we decide about the Q4 budget?",
    session_id=session_id
)

# Query Claude with full context
response = client.query(
    "What did we decide about the Q4 budget?",
    context=context
)

print(response)
# Claude can reference the captured meeting and session context!
```

### Example 4: List Recent Activity

```python
# Get last 10 sessions
recent_sessions = manager.list_sessions(limit=10)

for session in recent_sessions:
    print(f"Session: {session['session_id']}")
    print(f"  User: {session['user_id']}")
    print(f"  Last updated: {session['updated_at']}")
    print(f"  History items: {session['history_count']}")
    print()

# Get last 5 meeting captures
recent_meetings = manager.list_captures(capture_type="meeting", limit=5)

for meeting in recent_meetings:
    print(f"Meeting: {meeting['capture_id']}")
    print(f"  Captured at: {meeting['captured_at']}")
    print(f"  Metadata: {meeting['metadata']}")
    print()
```

### Example 5: Cleanup Old Sessions

```python
import json
from datetime import datetime, timedelta

# Delete sessions older than 30 days
cutoff_date = (datetime.utcnow() - timedelta(days=30)).isoformat()

all_sessions = manager.list_sessions()
for session in all_sessions:
    if session['updated_at'] < cutoff_date:
        print(f"Deleting old session: {session['session_id']}")
        manager.delete_session(session['session_id'])
```

## Design Decisions Explained

### Why File-Based Storage for MVP?

**Decision**: Use JSON files instead of database

**Reasoning**:
1. **Simplicity**: No database setup, configuration, or management
2. **Development speed**: Faster to implement and test
3. **Debugging**: Just open the JSON file to see data
4. **Version control**: Can commit context to git if needed (for testing)
5. **Portability**: Works anywhere Python runs
6. **MVP-appropriate**: Perfect for initial development

**When to migrate to database**:
- 1000+ sessions or captures
- Need complex queries (search, filter, join)
- Concurrent access from multiple processes
- Performance becomes an issue

**Migration path**: The API stays the same! Just swap implementation.

### Why Separate Sessions and Captures?

**Decision**: Two separate directories and concepts

**Reasoning**:
1. **Different lifecycles**: Sessions are temporary, captures are permanent
2. **Different access patterns**: Sessions accessed frequently, captures occasionally
3. **Clear semantics**: Session = conversation, Capture = stored information
4. **Easier to manage**: Can clean up sessions without affecting captures

**Example**:
- Session lives for a few hours (user conversation)
- Capture lives forever (meeting minutes stored permanently)

### Why Include Timestamps on Everything?

**Decision**: Add `created_at`, `updated_at`, `captured_at`, `timestamp` everywhere

**Reasoning**:
1. **Audit trail**: Know when things happened
2. **Sorting**: Order by recency
3. **Filtering**: Find recent items
4. **Debugging**: Track sequence of events
5. **Compliance**: May be required for certain use cases

**Best practice**: Always timestamp data creation and modification!

### Why Use UTC?

**Decision**: `datetime.utcnow()` instead of local time

**Reasoning**:
1. **No timezone ambiguity**: Everyone uses same reference
2. **Daylight saving**: No issues with DST transitions
3. **International**: Users in different timezones
4. **Standard practice**: Industry best practice

**To display**: Convert UTC to user's local timezone in UI.

### Why Reverse History?

**Decision**: Return history items most-recent-first

**Reasoning**:
1. **User expectation**: Latest activity shown first
2. **Relevance**: Recent items usually more important
3. **UI pattern**: Feeds, notifications, etc. show newest first
4. **Limiting**: `limit=5` gets 5 most recent (not 5 oldest)

### Why Return Summaries in list_* Methods?

**Decision**: Don't include full `data` in list results

**Reasoning**:
1. **Performance**: Loading 100 captures with full data is slow
2. **Memory**: Keep response size small
3. **Use case**: Listings are for browsing, not full data access
4. **Pattern**: "List summaries, get details" is standard REST pattern

**Example**:
```python
# List: Fast, returns summaries
captures = manager.list_captures(limit=10)  # Quick!

# Get: Slower, returns full data
for capture_summary in captures:
    full_data = manager.get_capture(capture_summary['capture_id'])  # Detail when needed
```

## Key Takeaways

1. **3 C's Pattern**: Capture → Curate → Consult for context management
2. **Sessions**: Represent conversations with context and history
3. **Captures**: Store permanent information (meetings, docs, notes)
4. **File-based storage**: Perfect for MVP, easy to upgrade later
5. **UUIDs**: Globally unique identifiers for sessions and captures
6. **ISO 8601 timestamps**: Standard, sortable, timezone-aware
7. **JSON**: Human-readable, universal, version-control friendly
8. **Separation of concerns**: Sessions vs captures, context vs history

---

**Files Created**: 1 (`backend/agent/context_manager.py`)
**Lines of Code**: 343
**Time to Complete**: ~60 minutes
**Dependencies**: Standard library only (uuid, json, datetime, pathlib)

**Next Step**: [Module 2, Step 2.4: API Endpoints](module-2-step-2.4-api-endpoints.md)
