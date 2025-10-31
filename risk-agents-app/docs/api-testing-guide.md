# Risk Agents API - Testing Guide

**API Version**: 0.1.0
**Base URL**: `http://localhost:8050`
**Documentation**: http://localhost:8050/docs
**Created**: October 23, 2025

## Overview

The Risk Agents API provides three main endpoint groups:
1. **Query** (`/api/query`) - Claude AI queries with Skills Framework integration
2. **Skills** (`/api/skills`) - Skills Framework browsing and management
3. **Context** (`/api/context`) - Session and context management (3 C's pattern)

All endpoints return JSON responses and follow REST conventions.

## Quick Start

### 1. Check API Health

```bash
curl http://localhost:8050/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "risk-agents-backend",
  "timestamp": "2025-10-23T08:44:54.961609Z",
  "environment": "development",
  "version": "0.1.0"
}
```

### 2. Check Component Health

```bash
# Query service health
curl http://localhost:8050/api/query/health

# Skills service health
curl http://localhost:8050/api/skills/domains  # Indirect health check

# Context service health
curl http://localhost:8050/api/context/sessions  # Indirect health check
```

## Skills Endpoints

### List All Skills

```bash
curl http://localhost:8050/api/skills/
```

**Response**:
```json
[
  {
    "name": "meeting-minutes-capture",
    "description": "Capture meeting minutes from transcripts or notes...",
    "domain": "change-agent",
    "category": "meeting-management",
    "taxonomy": "change-agent/meeting-management",
    "parameters": ["meeting_transcript", "meeting_date", "attendees"],
    "output_format": "structured_markdown",
    "estimated_duration": "2-3 minutes",
    "is_flat_structure": false
  }
]
```

### Filter Skills by Domain

```bash
curl "http://localhost:8050/api/skills/?domain=change-agent"
```

### Filter Skills by Category

```bash
curl "http://localhost:8050/api/skills/?category=meeting-management"
```

### List All Domains

```bash
curl http://localhost:8050/api/skills/domains
```

**Response**:
```json
["change-agent"]
```

### List All Categories

```bash
curl http://localhost:8050/api/skills/categories
```

**Response**:
```json
["meeting-management"]
```

### List Categories for Specific Domain

```bash
curl "http://localhost:8050/api/skills/categories?domain=change-agent"
```

### Get Complete Skill Details

```bash
curl http://localhost:8050/api/skills/change-agent/meeting-minutes-capture
```

**Response**:
```json
{
  "metadata": {
    "name": "meeting-minutes-capture",
    "description": "...",
    "domain": "change-agent",
    "category": "meeting-management",
    "taxonomy": "change-agent/meeting-management",
    "parameters": ["meeting_transcript", "meeting_date", "attendees"],
    "output_format": "structured_markdown",
    "estimated_duration": "2-3 minutes",
    "is_flat_structure": false
  },
  "content": "# Meeting Minutes Capture Skill\n\n## Purpose\n...",
  "instructions": ["capture.md", "extract-actions.md"],
  "resources": ["meeting-template.md", "examples.md"]
}
```

### Get Specific Instruction File

```bash
curl http://localhost:8050/api/skills/change-agent/meeting-minutes-capture/instructions/capture.md
```

**Response**:
```json
{
  "skill_path": "change-agent/meeting-minutes-capture",
  "instruction_file": "capture.md",
  "content": "# Capturing Meeting Minutes\n\n..."
}
```

### Get Specific Resource File

```bash
curl http://localhost:8050/api/skills/change-agent/meeting-minutes-capture/resources/meeting-template.md
```

**Response**:
```json
{
  "skill_path": "change-agent/meeting-minutes-capture",
  "resource_file": "meeting-template.md",
  "content": "# Meeting Minutes: [Title]\n\n..."
}
```

## Context Endpoints

### Create a Session

```bash
curl -X POST http://localhost:8050/api/context/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "john@example.com"
  }'
```

**Response**:
```json
{
  "session_id": "3d6c2c07-0d55-4011-97a9-659f8cc720b3",
  "user_id": "john@example.com",
  "created_at": "2025-10-23T08:44:54.961609Z",
  "updated_at": "2025-10-23T08:44:54.961624Z",
  "context": {},
  "history_count": 0
}
```

**Save the session_id for use in subsequent requests!**

### Get Session Details

```bash
SESSION_ID="3d6c2c07-0d55-4011-97a9-659f8cc720b3"
curl http://localhost:8050/api/context/sessions/$SESSION_ID
```

### Update Session Context

```bash
SESSION_ID="3d6c2c07-0d55-4011-97a9-659f8cc720b3"
curl -X PUT http://localhost:8050/api/context/sessions/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{
    "context": {
      "project": "Q4 Planning",
      "budget": 100000,
      "status": "active"
    },
    "add_history": {
      "action": "meeting_started",
      "timestamp": "2025-10-23T10:30:00Z"
    }
  }'
```

**Response**:
```json
{
  "message": "Session updated successfully"
}
```

### List All Sessions

```bash
curl http://localhost:8050/api/context/sessions
```

**Response**:
```json
[
  {
    "session_id": "3d6c2c07-0d55-4011-97a9-659f8cc720b3",
    "user_id": "john@example.com",
    "created_at": "2025-10-23T08:44:54.961609Z",
    "updated_at": "2025-10-23T08:45:23.123456Z",
    "history_count": 1
  }
]
```

### List Recent Sessions

```bash
curl "http://localhost:8050/api/context/sessions?limit=5"
```

### Delete a Session

```bash
SESSION_ID="3d6c2c07-0d55-4011-97a9-659f8cc720b3"
curl -X DELETE http://localhost:8050/api/context/sessions/$SESSION_ID
```

### Capture Information

```bash
curl -X POST http://localhost:8050/api/context/captures \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "title": "Q4 Planning Meeting",
      "date": "2025-10-23",
      "attendees": ["Alice", "Bob", "Charlie"],
      "decisions": [
        "Approved budget increase to $100k",
        "Hired 2 additional team members"
      ],
      "action_items": [
        {
          "task": "Prepare project charter",
          "owner": "Alice",
          "due_date": "2025-10-30"
        }
      ]
    },
    "capture_type": "meeting",
    "metadata": {
      "duration": "45 minutes",
      "location": "Conference Room A"
    }
  }'
```

**Response**:
```json
{
  "capture_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "capture_type": "meeting",
  "captured_at": "2025-10-23T08:46:12.345678Z"
}
```

### Get Capture Details

```bash
CAPTURE_ID="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
curl http://localhost:8050/api/context/captures/$CAPTURE_ID
```

### List All Captures

```bash
curl http://localhost:8050/api/context/captures
```

### Filter Captures by Type

```bash
curl "http://localhost:8050/api/context/captures?capture_type=meeting"
```

### Limit Capture Results

```bash
curl "http://localhost:8050/api/context/captures?limit=10"
```

### Delete a Capture

```bash
CAPTURE_ID="a1b2c3d4-e5f6-7890-abcd-ef1234567890"
curl -X DELETE http://localhost:8050/api/context/captures/$CAPTURE_ID
```

### Consult Context

```bash
SESSION_ID="3d6c2c07-0d55-4011-97a9-659f8cc720b3"
curl -X POST "http://localhost:8050/api/context/consult?query=What%20did%20we%20decide%20about%20budget&session_id=$SESSION_ID"
```

**Response**:
```json
{
  "session_context": {
    "project": "Q4 Planning",
    "budget": 100000,
    "status": "active"
  },
  "recent_captures": [
    {
      "capture_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "capture_type": "meeting",
      "captured_at": "2025-10-23T08:46:12.345678Z",
      "metadata": {
        "duration": "45 minutes",
        "location": "Conference Room A"
      }
    }
  ]
}
```

## Query Endpoints

**Note**: Query endpoints require `ANTHROPIC_API_KEY` to be set in the backend environment.

### Standard Query (Complete Response)

```bash
SESSION_ID="3d6c2c07-0d55-4011-97a9-659f8cc720b3"
curl -X POST http://localhost:8050/api/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Help me capture meeting minutes from this transcript: Meeting on Oct 23 with Alice and Bob about Q4 planning. We decided to increase budget to $100k. Alice will prepare the project charter by Oct 30.",
    "session_id": "'$SESSION_ID'",
    "include_context": true
  }'
```

**Response**:
```json
{
  "response": "I'll help you capture meeting minutes. Based on the transcript...\n\n# Meeting Minutes: Q4 Planning\n\n**Date**: October 23, 2025\n...",
  "session_id": "3d6c2c07-0d55-4011-97a9-659f8cc720b3",
  "tokens_used": 1500
}
```

### Streaming Query (Progressive Response)

```bash
SESSION_ID="3d6c2c07-0d55-4011-97a9-659f8cc720b3"
curl -X POST http://localhost:8050/api/query/stream \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze the risks in our Q4 planning approach",
    "session_id": "'$SESSION_ID'",
    "include_context": true
  }'
```

**Response** (Server-Sent Events stream):
```
data: I'll
data:  analyze
data:  the
data:  risks
data:  in
data:  your
data:  Q4
data:  planning
data: ...
data: [DONE]
```

### Query Without Session Context

```bash
curl -X POST http://localhost:8050/api/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key elements of a project charter?",
    "include_context": false
  }'
```

### Query with Custom System Prompt

```bash
curl -X POST http://localhost:8050/api/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Review this meeting transcript",
    "system_prompt": "You are a professional meeting minutes expert. Focus on extracting clear action items with owners and due dates."
  }'
```

### Check Query Service Health

```bash
curl http://localhost:8050/api/query/health
```

**Response**:
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "agent_client_initialized": true,
  "context_manager_initialized": true,
  "ready": true
}
```

## Complete Workflow Example

Here's a complete workflow combining all endpoints:

```bash
#!/bin/bash

# 1. Create a session
echo "Creating session..."
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8050/api/context/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "john@example.com"}')

SESSION_ID=$(echo $SESSION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")
echo "Session ID: $SESSION_ID"

# 2. Update session with context
echo "Updating session context..."
curl -s -X PUT http://localhost:8050/api/context/sessions/$SESSION_ID \
  -H "Content-Type: application/json" \
  -d '{
    "context": {"project": "Q4 Planning", "budget": 100000}
  }' | python3 -m json.tool

# 3. Capture meeting minutes
echo "Capturing meeting information..."
CAPTURE_RESPONSE=$(curl -s -X POST http://localhost:8050/api/context/captures \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "title": "Q4 Planning Meeting",
      "decisions": ["Approved budget increase"]
    },
    "capture_type": "meeting"
  }')

echo $CAPTURE_RESPONSE | python3 -m json.tool

# 4. Query Claude with context
echo "Querying Claude with session context..."
curl -s -X POST http://localhost:8050/api/query/ \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"What did we decide about the budget?\",
    \"session_id\": \"$SESSION_ID\",
    \"include_context\": true
  }" | python3 -m json.tool

# 5. List all sessions
echo "Listing all sessions..."
curl -s http://localhost:8050/api/context/sessions | python3 -m json.tool
```

## Interactive API Documentation

The API includes interactive Swagger UI documentation:

**Swagger UI**: http://localhost:8050/docs
- Try out endpoints directly from the browser
- See request/response schemas
- View all available parameters

**ReDoc**: http://localhost:8050/redoc
- Alternative documentation interface
- Better for reading and understanding the API

## Error Handling

### Common Error Responses

**404 Not Found**:
```json
{
  "detail": "Session not found: invalid-session-id"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Failed to create session: <error message>"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "query"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Testing Tips

### 1. Use jq for Better JSON Formatting

```bash
curl http://localhost:8050/api/skills/ | jq
```

### 2. Save Session IDs for Reuse

```bash
# Create session and save ID
SESSION_ID=$(curl -s -X POST http://localhost:8050/api/context/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test@example.com"}' | jq -r '.session_id')

echo "Session ID: $SESSION_ID"

# Reuse in subsequent requests
curl http://localhost:8050/api/context/sessions/$SESSION_ID
```

### 3. Test Error Cases

```bash
# Test with invalid session ID
curl http://localhost:8050/api/context/sessions/invalid-id

# Test with missing required fields
curl -X POST http://localhost:8050/api/query/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 4. Monitor Backend Logs

```bash
docker logs -f risk-agents-backend
```

## Rate Limiting and Performance

**Current Configuration**:
- No rate limiting (development mode)
- No request size limits
- Streaming responses for long Claude queries

**Future Enhancements**:
- Rate limiting per user/session
- Request size validation
- Response caching for repeated queries

## Next Steps

1. **Try the Swagger UI**: http://localhost:8050/docs
2. **Create a test session** and experiment with context management
3. **Capture sample meeting data** and consult it
4. **Query Claude** (requires ANTHROPIC_API_KEY) with skills integration
5. **Explore skill details** and progressive disclosure

---

**API Status**: ✅ All endpoints operational
**Documentation**: Complete
**Last Updated**: October 23, 2025
