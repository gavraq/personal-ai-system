# Module 2, Step 2.7: End-to-End Testing

**What You'll Learn**: How to test the complete integration of Claude Agent SDK, Skills Framework, Knowledge Layer, Context Manager, and API endpoints.

**Prerequisites**:
- Module 2 Steps 2.1-2.6 completed
- Docker containers running
- ANTHROPIC_API_KEY (optional, for Claude testing)

**Estimated Time**: 30-45 minutes

---

## Overview

This final step validates that all Module 2 components work together correctly. We'll test each layer individually, then test the complete integration from API request to Claude response.

### Testing Layers

```
┌─────────────────────────────────────┐
│  Layer 5: API Endpoints             │  ← Test REST API
├─────────────────────────────────────┤
│  Layer 4: Claude Agent Client       │  ← Test Claude integration
├─────────────────────────────────────┤
│  Layer 3: Knowledge Layer           │  ← Test knowledge loading
├─────────────────────────────────────┤
│  Layer 2: Skills Framework          │  ← Test skill loading
├─────────────────────────────────────┤
│  Layer 1: Context Manager           │  ← Test session management
└─────────────────────────────────────┘
```

We'll test bottom-up: Context → Skills → Knowledge → Claude → API.

---

## Test 1: Context Manager (Layer 1)

### Test Session Creation and Management

```bash
# Test creating a session
curl -X POST http://localhost:8050/api/context/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "metadata": {"test_run": "end-to-end"}
  }'
```

**Expected Response**:
```json
{
  "session_id": "uuid-here",
  "user_id": "test-user",
  "created_at": "2025-10-23T...",
  "last_updated": "2025-10-23T...",
  "context": {},
  "history": [],
  "metadata": {"test_run": "end-to-end"}
}
```

**Validation**:
- ✅ Session ID is a valid UUID
- ✅ Timestamps are ISO 8601 format
- ✅ Metadata is preserved
- ✅ Context and history are empty objects/arrays

### Test Context Capture

```bash
# Save the session_id from above, then capture some data
curl -X POST http://localhost:8050/api/context/captures \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "meeting_topic": "Product Approval Committee",
      "attendees": ["Alice", "Bob", "Charlie"],
      "decision": "Approved FX Options product"
    },
    "capture_type": "meeting",
    "metadata": {
      "meeting_date": "2025-10-23",
      "meeting_type": "decision-making"
    }
  }'
```

**Expected Response**:
```json
{
  "capture_id": "uuid-here",
  "capture_type": "meeting",
  "captured_at": "2025-10-23T...",
  "data": { ... },
  "metadata": { ... }
}
```

**Validation**:
- ✅ Capture ID is generated
- ✅ Data is preserved exactly
- ✅ Timestamp is recorded
- ✅ Capture type is correct

### Test Context Consultation

```bash
# List all captures to see our meeting
curl http://localhost:8050/api/context/captures
```

**Expected Response**:
```json
[
  {
    "capture_id": "uuid",
    "capture_type": "meeting",
    "captured_at": "2025-10-23T...",
    "data": { ... }
  }
]
```

**Validation**:
- ✅ Our captured meeting appears in the list
- ✅ All fields are present

**✅ Layer 1 Complete**: Context Manager works!

---

## Test 2: Skills Framework (Layer 2)

### Test List All Skills

```bash
# Get all available skills
curl http://localhost:8050/api/skills/
```

**Expected Response**:
```json
[
  {
    "name": "meeting-minutes-capture",
    "description": "Capture meeting minutes from transcripts...",
    "domain": "change-agent",
    "category": "meeting-management",
    "taxonomy": "change-agent/meeting-management",
    "parameters": ["meeting_transcript", "meeting_date", "attendees"],
    "output_format": "structured_markdown",
    "estimated_duration": "2-3 minutes",
    "is_flat_structure": true
  }
]
```

**Validation**:
- ✅ meeting-minutes-capture skill is listed
- ✅ All metadata fields are present
- ✅ is_flat_structure is true (we're using flat structure)

### Test Get Skill Details

```bash
# Get full skill details including instructions and resources
curl http://localhost:8050/api/skills/change-agent/meeting-minutes-capture
```

**Expected Response**:
```json
{
  "metadata": {
    "name": "meeting-minutes-capture",
    "description": "...",
    ...
  },
  "instructions": [
    "capture.md",
    "extract-actions.md"
  ],
  "resources": [
    "meeting-template.md",
    "examples.md"
  ],
  "content": "# Meeting Minutes Capture Skill\n\n..."
}
```

**Validation**:
- ✅ Metadata matches what we saw in list
- ✅ Instructions list shows 2 instruction files
- ✅ Resources list shows 2 resource files
- ✅ Content includes the full SKILL.md

### Test Load Skill Instructions

```bash
# Load a specific instruction file
curl http://localhost:8050/api/skills/change-agent/meeting-minutes-capture/instructions/capture.md
```

**Expected Response**:
```json
{
  "skill_path": "change-agent/meeting-minutes-capture",
  "instruction_file": "capture.md",
  "content": "# Capturing Meeting Minutes\n\n..."
}
```

**Validation**:
- ✅ Content loads successfully
- ✅ File name is correct
- ✅ Content is readable markdown

### Test Load Skill Resources

```bash
# Load a resource file
curl http://localhost:8050/api/skills/change-agent/meeting-minutes-capture/resources/examples.md
```

**Expected Response**:
```json
{
  "skill_path": "change-agent/meeting-minutes-capture",
  "resource_file": "examples.md",
  "content": "# Meeting Minutes Examples\n\n..."
}
```

**Validation**:
- ✅ Examples load successfully
- ✅ Content is the examples markdown

**✅ Layer 2 Complete**: Skills Framework works!

---

## Test 3: Knowledge Layer (Layer 3)

### Test Knowledge Directory Structure

First, let's verify the knowledge files exist inside the Docker container:

```bash
# Check knowledge directory in Docker container
docker exec risk-agents-backend ls -la knowledge/change-agent/meeting-management/
docker exec risk-agents-backend ls -la knowledge/change-agent/meta/
```

**Expected Output**:
```
knowledge/change-agent/meeting-management/:
-rw-r--r-- action-items-standards.md
-rw-r--r-- decision-capture.md
-rw-r--r-- meeting-types.md

knowledge/change-agent/meta/:
-rw-r--r-- knowledge-evolution.md
```

**Validation**:
- ✅ All 3 meeting-management knowledge files exist
- ✅ knowledge-evolution.md exists in meta/

### Test Knowledge Loading (Python Test)

Let's test the knowledge loading inside the container:

```bash
# Test knowledge loading via Python in Docker
docker exec risk-agents-backend python3 -c "
from pathlib import Path
from agent.skills_loader import SkillsLoader

loader = SkillsLoader(Path('.claude/skills'))

# Test 1: Get knowledge files
files = loader.get_knowledge_files('change-agent', 'meeting-management')
print(f'Knowledge files found: {len(files)}')
print(f'Files: {files}')

# Test 2: Load knowledge document
content = loader.load_knowledge('change-agent', 'meeting-management', 'action-items-standards.md')
print(f'\\nAction items standards loaded: {len(content)} characters')
print(f'First 100 chars: {content[:100]}...')

# Test 3: Load all knowledge
for file in files:
    doc = loader.load_knowledge('change-agent', 'meeting-management', file)
    print(f'\\n✓ {file}: {len(doc)} characters')

print('\\n✅ Knowledge Layer tests passed!')
"
```

**Expected Output**:
```
Knowledge files found: 3
Files: ['action-items-standards.md', 'decision-capture.md', 'meeting-types.md']

Action items standards loaded: 10000+ characters
First 100 chars: # Action Items Standards

## Purpose
Defines the standard structure and quality...

✓ action-items-standards.md: 10000+ characters
✓ decision-capture.md: 11000+ characters
✓ meeting-types.md: 9600+ characters

✅ Knowledge Layer tests passed!
```

**Validation**:
- ✅ All 3 knowledge files are found
- ✅ Each file loads successfully
- ✅ Content sizes match expectations (~10KB each)

**✅ Layer 3 Complete**: Knowledge Layer works!

---

## Test 4: Claude Agent Client (Layer 4)

**⚠️ Note**: This test requires `ANTHROPIC_API_KEY` environment variable. If you don't have it set, these tests will be skipped.

### Check if API Key is Set

```bash
# Check if ANTHROPIC_API_KEY is available in container
docker exec risk-agents-backend python3 -c "
import os
key = os.getenv('ANTHROPIC_API_KEY')
if key:
    print(f'✓ API key is set (starts with: {key[:7]}...)')
else:
    print('✗ API key not set - Claude tests will be skipped')
"
```

### Test 4a: Connection Test (Without API Key)

Even without an API key, we can test the client initialization:

```bash
# Test agent client initialization
docker exec risk-agents-backend python3 -c "
from pathlib import Path
from agent.agent_client import RiskAgentClient

try:
    client = RiskAgentClient(skills_dir=Path('.claude/skills'))
    print('✓ RiskAgentClient initialized successfully')
    print(f'✓ Model: {client.model}')
    print(f'✓ Max tokens: {client.max_tokens}')
    print(f'✓ Skills directory: {client.skills_dir}')
except Exception as e:
    print(f'✗ Error: {e}')
"
```

**Expected Output**:
```
✓ RiskAgentClient initialized successfully
✓ Model: claude-sonnet-4-20250514
✓ Max tokens: 8192
✓ Skills directory: .claude/skills
```

**Validation**:
- ✅ Client initializes without errors
- ✅ Model is Sonnet 4.5
- ✅ Max tokens is 8192
- ✅ Skills directory is configured

### Test 4b: Claude Query (With API Key Only)

**Skip this if ANTHROPIC_API_KEY is not set.**

```bash
# Test actual Claude query
docker exec risk-agents-backend python3 -c "
import os
from pathlib import Path
from agent.agent_client import RiskAgentClient

if not os.getenv('ANTHROPIC_API_KEY'):
    print('⏭️  Skipping: ANTHROPIC_API_KEY not set')
    exit(0)

try:
    client = RiskAgentClient(skills_dir=Path('.claude/skills'))

    response = client.query(
        user_message='What is 2+2? Please respond with just the number.',
        context=None,
        system_prompt='You are a helpful assistant. Respond concisely.'
    )

    print(f'✓ Claude response received: {response}')

except Exception as e:
    print(f'✗ Error querying Claude: {e}')
"
```

**Expected Output** (if API key is set):
```
✓ Claude response received: 4
```

**Validation** (if API key is set):
- ✅ Claude responds correctly
- ✅ Response is concise as requested
- ✅ No errors

### Test 4c: Claude Query with Knowledge (With API Key Only)

**Skip this if ANTHROPIC_API_KEY is not set.**

```bash
# Test Claude query with knowledge enhancement
docker exec risk-agents-backend python3 -c "
import os
from pathlib import Path
from agent.agent_client import RiskAgentClient
from agent.skills_loader import SkillsLoader

if not os.getenv('ANTHROPIC_API_KEY'):
    print('⏭️  Skipping: ANTHROPIC_API_KEY not set')
    exit(0)

try:
    # Load client and skills
    client = RiskAgentClient(skills_dir=Path('.claude/skills'))
    loader = SkillsLoader(Path('.claude/skills'))

    # Load knowledge
    action_standards = loader.load_knowledge('change-agent', 'meeting-management', 'action-items-standards.md')

    # Create system prompt with knowledge
    system_prompt = f'''You are a meeting minutes assistant.

# ACTION ITEM STANDARDS
{action_standards[:1000]}

Based on these standards, what are the 5 required elements of a complete action item? List them briefly.
'''

    response = client.query(
        user_message='List the 5 required elements.',
        system_prompt=system_prompt
    )

    print('✓ Claude response with knowledge:')
    print(response[:500])

except Exception as e:
    print(f'✗ Error: {e}')
"
```

**Expected Output** (if API key is set):
```
✓ Claude response with knowledge:
The 5 required elements of a complete action item are:

1. Task Description (WHAT) - Clear, specific, verb-led description
2. Owner (WHO) - Named individual responsible
3. Due Date (WHEN) - Specific date or deadline
4. Context (WHY) - Brief explanation of why needed
5. Dependencies (OPTIONAL) - Prerequisites or blocking factors
```

**Validation** (if API key is set):
- ✅ Claude understood the knowledge document
- ✅ Response aligns with action-items-standards.md
- ✅ Shows knowledge enhancement works

**✅ Layer 4 Complete** (if API key available): Claude integration works!
**⏭️ Layer 4 Skipped** (if no API key): Will test in production with real key

---

## Test 5: API Endpoints (Layer 5)

### Test Health Check

```bash
# Check API health
curl http://localhost:8050/api/query/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "skills_loaded": true
}
```

**Validation**:
- ✅ Status is healthy
- ✅ Agent is initialized
- ✅ Skills are loaded

### Test Query Endpoint (Without ANTHROPIC_API_KEY)

```bash
# Test query endpoint without API key (will fail gracefully)
curl -X POST http://localhost:8050/api/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Test query",
    "include_context": false
  }'
```

**Expected Response** (without API key):
```json
{
  "detail": "ANTHROPIC_API_KEY environment variable not set"
}
```

**Validation**:
- ✅ API handles missing key gracefully
- ✅ Error message is clear

### Test Query Endpoint (With ANTHROPIC_API_KEY)

**Skip this if ANTHROPIC_API_KEY is not set.**

```bash
# Test actual query through API
curl -X POST http://localhost:8050/api/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is 2+2? Respond with just the number.",
    "include_context": false
  }'
```

**Expected Response** (if API key is set):
```json
{
  "response": "4",
  "session_id": null
}
```

**Validation** (if API key is set):
- ✅ Query succeeds
- ✅ Response is correct
- ✅ No session_id (as expected)

**✅ Layer 5 Complete**: API Endpoints work!

---

## Test 6: End-to-End Integration Test

This test validates the complete flow from API request through all layers to Claude and back.

**⚠️ Requires ANTHROPIC_API_KEY**

### Complete Integration Flow

```bash
# Step 1: Create a session
SESSION_RESPONSE=$(curl -s -X POST http://localhost:8050/api/context/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "integration-test"}')

SESSION_ID=$(echo $SESSION_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['session_id'])")

echo "Created session: $SESSION_ID"

# Step 2: Capture meeting data
curl -s -X POST http://localhost:8050/api/context/captures \
  -H "Content-Type: application/json" \
  -d "{
    \"data\": {
      \"meeting_transcript\": \"Alice: We should approve FX Options. Bob: I agree. Charlie: Approved. Alice: John, please update the product list by Nov 1.\",
      \"attendees\": [\"Alice\", \"Bob\", \"Charlie\", \"John\"],
      \"meeting_date\": \"2025-10-23\"
    },
    \"capture_type\": \"meeting\"
  }" > /dev/null

echo "Captured meeting data"

# Step 3: Query Claude with context and skill
curl -X POST http://localhost:8050/api/query/ \
  -H "Content-Type: application/json" \
  -d "{
    \"query\": \"Extract the decision and action item from this meeting.\",
    \"session_id\": \"$SESSION_ID\",
    \"include_context\": true,
    \"skill_name\": \"meeting-minutes-capture\"
  }"

echo ""
echo "Integration test complete!"
```

**Expected Flow**:
1. ✅ Session created with UUID
2. ✅ Meeting data captured
3. ✅ Claude query includes:
   - Session context (meeting data)
   - Skill instructions (meeting-minutes-capture)
   - Knowledge documents (action item standards)
4. ✅ Claude extracts structured information
5. ✅ Response follows action item standards

**Expected Response** (if API key is set):
```json
{
  "response": "**Decision:**\nApproved FX Options product\n\n**Action Item:**\n- **Task**: Update product list to include FX Options\n- **Owner**: John\n- **Due Date**: 2025-11-01\n- **Context**: Following decision to approve FX Options product\n- **Dependencies**: None\n",
  "session_id": "uuid-here"
}
```

**Validation**:
- ✅ Decision is extracted correctly
- ✅ Action item has all 5 required elements (WHAT, WHO, WHEN, WHY, Dependencies)
- ✅ Follows standards from action-items-standards.md
- ✅ Session ID is preserved

**✅ End-to-End Integration Complete**: All layers work together!

---

## Test Results Summary

### Layer Test Results

| Layer | Test | Status | Notes |
|-------|------|--------|-------|
| **Layer 1** | Context Manager | ✅ | Sessions, captures, consultation |
| **Layer 2** | Skills Framework | ✅ | Loading, listing, progressive disclosure |
| **Layer 3** | Knowledge Layer | ✅ | All 3 knowledge docs load |
| **Layer 4** | Claude Client | ⏭️ / ✅ | Depends on ANTHROPIC_API_KEY |
| **Layer 5** | API Endpoints | ✅ | All endpoints respond |
| **Integration** | End-to-End | ⏭️ / ✅ | Depends on ANTHROPIC_API_KEY |

### Without ANTHROPIC_API_KEY

If you don't have the API key set:
- ✅ Layers 1-3 fully tested and working
- ✅ Layer 4-5 architecture validated
- ⏭️ Claude integration deferred to production

**Status**: **Architecture Complete** - Ready for production with API key

### With ANTHROPIC_API_KEY

If you have the API key:
- ✅ All 5 layers fully tested
- ✅ End-to-end integration verified
- ✅ Knowledge enhancement confirmed working

**Status**: **Fully Tested** - Production ready

---

## Common Issues and Solutions

### Issue 1: "Knowledge file not found"

**Symptom**: Knowledge loading fails
**Cause**: Knowledge files not in Docker container
**Solution**:
```bash
# Rebuild containers to include knowledge files
docker-compose down
docker-compose up --build
```

### Issue 2: "ANTHROPIC_API_KEY not set"

**Symptom**: Claude queries fail
**Cause**: Environment variable not configured
**Solution**:
```bash
# Add to backend/.env file
echo "ANTHROPIC_API_KEY=your-key-here" >> backend/.env

# Restart containers
docker-compose restart backend
```

### Issue 3: "Skill not found: change-agent/meeting-minutes-capture"

**Symptom**: Skill loading fails
**Cause**: Skill directory structure mismatch
**Solution**:
```bash
# Verify skill exists in container
docker exec risk-agents-backend ls -la .claude/skills/change-agent/

# Should show meeting-minutes-capture directory
```

### Issue 4: "API endpoint returns 500"

**Symptom**: API calls fail
**Cause**: Backend initialization error
**Solution**:
```bash
# Check backend logs
docker logs risk-agents-backend

# Look for initialization errors
# Restart if needed
docker-compose restart backend
```

---

## Performance Validation

### Expected Performance Metrics

| Operation | Target Time | Acceptable Range |
|-----------|-------------|------------------|
| Session creation | < 50ms | 10-100ms |
| Capture data | < 50ms | 10-100ms |
| List skills | < 100ms | 50-200ms |
| Load skill details | < 200ms | 100-500ms |
| Load knowledge | < 100ms | 50-300ms |
| Claude query (no skill) | 1-3 seconds | 1-5 seconds |
| Claude query (with skill) | 2-5 seconds | 2-10 seconds |

**Note**: Claude query times depend on:
- Response length
- System prompt complexity
- API latency

---

## Next Steps

After completing these tests:

1. **Review Test Results**: Document any failures or issues
2. **Update Module 2 Progress**: Mark Module 2 as 100% complete
3. **Plan Module 3**: Frontend integration (if proceeding)
4. **Production Readiness**: Add ANTHROPIC_API_KEY for production deployment

---

## Module 2 Completion Checklist

- [ ] Layer 1 (Context Manager) tests pass
- [ ] Layer 2 (Skills Framework) tests pass
- [ ] Layer 3 (Knowledge Layer) tests pass
- [ ] Layer 4 (Claude Client) architecture validated
- [ ] Layer 5 (API Endpoints) tests pass
- [ ] Integration test architecture validated (or fully tested with API key)
- [ ] Performance is acceptable
- [ ] No critical errors in logs
- [ ] Documentation is complete
- [ ] Module 2 marked as 100% complete

**When all items are checked**: Module 2 is complete! 🎉

---

**Module 2 Progress**: Complete pending test execution
**Next Module**: Module 3 - Frontend Integration (or production deployment)
