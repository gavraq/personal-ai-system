# Module 2, Step 2.6: API Endpoints Implementation

**Completed**: October 23, 2025

## What We Built

In this step, we created comprehensive REST API endpoints that expose all the backend functionality we've built: the RiskAgentClient (Claude queries), SkillsLoader (skill browsing), and ContextManager (session/capture management). This connects our Python backend to the frontend and makes all functionality accessible via HTTP.

## Why This Matters

The API endpoints are the bridge between our backend components and the frontend:
- **Expose functionality**: Makes backend accessible to the web interface
- **REST standard**: Industry-standard HTTP API design
- **Interactive docs**: Automatic Swagger UI for testing
- **Type safety**: Pydantic models ensure request/response validity
- **Streaming support**: Real-time responses for long Claude queries

## Files Created

**Route Files** (3 new files, ~1,210 lines):
1. `backend/api/routes/query.py` (265 lines)
2. `backend/api/routes/skills.py` (415 lines)
3. `backend/api/routes/context.py` (530 lines)

**Modified Files** (2 files):
1. `backend/api/api_server.py` (added router registration)
2. `backend/api/routes/__init__.py` (module exports)

## Key Concepts Explained

### 1. What is a REST API?

**REST** (Representational State Transfer) is an architectural style for APIs:

**Key Principles**:
- **Resources**: Everything is a resource (skill, session, capture)
- **HTTP Methods**: Standard verbs (GET, POST, PUT, DELETE)
- **Stateless**: Each request is independent
- **JSON**: Standard data format

**Example**:
```
GET    /api/skills/           → List all skills
POST   /api/context/sessions  → Create a session
PUT    /api/context/sessions/{id} → Update a session
DELETE /api/context/sessions/{id} → Delete a session
```

**Why REST?**
- Universal standard (works with any client)
- Simple to understand and use
- Well-supported by tools and frameworks
- Cacheable and scalable

### 2. FastAPI Routers

**FastAPI Router** organizes endpoints into logical groups:

```python
from fastapi import APIRouter

# Create router for a specific domain
router = APIRouter(prefix="/query", tags=["query"])

# Add endpoints to this router
@router.post("/")
async def query_claude(request: QueryRequest):
    # Handle query
    pass

@router.get("/health")
async def health_check():
    # Check health
    pass
```

**Benefits**:
- **Organization**: Group related endpoints
- **Reusability**: Import router into main app
- **Tags**: Automatic grouping in Swagger UI
- **Prefix**: Common URL prefix for all routes

**Our router structure**:
```
/api/query/     → Query endpoints (Claude AI)
/api/skills/    → Skills endpoints (browsing)
/api/context/   → Context endpoints (sessions/captures)
```

### 3. Pydantic Models

**Pydantic** provides data validation and serialization:

```python
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., description="User's query", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID")
    include_context: bool = Field(True, description="Include context")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Help me with meeting minutes",
                "session_id": "abc-123",
                "include_context": true
            }
        }
```

**What this does**:
- **Validates** incoming requests (type checking, length constraints)
- **Generates** OpenAPI schema automatically
- **Provides** examples in documentation
- **Serializes** responses to JSON

**Benefits**:
- Type safety (catch errors early)
- Automatic API documentation
- Clear request/response contracts
- IDE autocomplete support

### 4. Dependency Injection

**Dependency injection** provides components to routes:

```python
# Global variables (initialized at startup)
agent_client: Optional[RiskAgentClient] = None
context_manager: Optional[ContextManager] = None

def initialize_query_routes(skills_dir: Path, context_dir: Path):
    """Initialize components when app starts"""
    global agent_client, context_manager
    agent_client = RiskAgentClient(skills_dir=skills_dir)
    context_manager = ContextManager(context_dir=context_dir)

# Routes use these global instances
@router.post("/")
async def query_claude(request: QueryRequest):
    if agent_client is None:
        raise HTTPException(status_code=500, detail="Not initialized")

    response = agent_client.query(request.query)
    return response
```

**Why this pattern?**
- **Single instance**: Don't recreate components on every request
- **Testability**: Can inject mock components for testing
- **Startup initialization**: Load once, use many times
- **Clean separation**: Routes don't manage component lifecycle

### 5. Streaming Responses

**Streaming** sends data progressively rather than all at once:

```python
from fastapi.responses import StreamingResponse
from typing import AsyncIterator

async def generate_stream() -> AsyncIterator[str]:
    """Generate streaming response"""
    for chunk in agent_client.query_stream(user_message):
        yield f"data: {chunk}\n\n"
    yield "data: [DONE]\n\n"

@router.post("/stream")
async def query_stream(request: QueryRequest):
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"
    )
```

**Server-Sent Events (SSE) format**:
```
data: I'll
data:  help
data:  you
data:  with
data:  that
data: [DONE]
```

**Why streaming?**
- **Progressive display**: Show response as it's generated
- **Better UX**: User sees activity immediately
- **Long responses**: Don't wait for complete answer
- **Real-time feel**: More interactive experience

### 6. HTTP Status Codes

**Standard status codes** communicate results:

**Success codes**:
- `200 OK`: Standard successful response
- `201 Created`: Resource successfully created

**Client error codes**:
- `404 Not Found`: Resource doesn't exist
- `422 Unprocessable Entity`: Validation failed

**Server error codes**:
- `500 Internal Server Error`: Something went wrong

**Example**:
```python
@router.post("/sessions", status_code=201)  # Created
async def create_session(request: CreateSessionRequest):
    session_id = context_manager.create_session(...)
    return SessionResponse(session_id=session_id)

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    try:
        session = context_manager.get_session(session_id)
        return SessionResponse(**session)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Not found")
```

### 7. CORS Configuration

**CORS** (Cross-Origin Resource Sharing) allows frontend to call backend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3050",  # Frontend in development
        "http://frontend:3050",   # Frontend from Docker
    ],
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE
    allow_headers=["*"],
)
```

**Without CORS**: Browser blocks requests from frontend to backend (security)
**With CORS**: Browser allows specified origins to make requests

**Why needed?**
- Frontend runs on port 3050
- Backend runs on port 8050
- Different ports = different origins = CORS needed

## Code Walkthrough

### Query Routes (Claude AI Endpoints)

**File**: `backend/api/routes/query.py`

#### Standard Query Endpoint

```python
@router.post("/", response_model=QueryResponse)
async def query_claude(request: QueryRequest) -> QueryResponse:
    """
    Execute a standard (non-streaming) query to Claude

    This endpoint sends a query to Claude and returns the complete response.
    Use this for simple queries where you want the full response at once.
    """
    if agent_client is None:
        raise HTTPException(
            status_code=500,
            detail="Agent client not initialized. Check ANTHROPIC_API_KEY."
        )

    try:
        # Build context if requested
        context = None
        if request.include_context and request.session_id and context_manager:
            context = context_manager.consult(
                query=request.query,
                session_id=request.session_id
            )

        # Execute query
        response = agent_client.query(
            user_message=request.query,
            context=context,
            system_prompt=request.system_prompt
        )

        # Update session history
        if request.session_id and context_manager:
            try:
                context_manager.update_session(
                    request.session_id,
                    add_history={
                        "action": "query",
                        "query": request.query,
                        "response_length": len(response)
                    }
                )
            except FileNotFoundError:
                pass  # Session doesn't exist - that's okay

        return QueryResponse(
            response=response,
            session_id=request.session_id,
            tokens_used=len(response.split()) * 2  # Rough estimate
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
```

**What's happening**:
1. **Validate initialization**: Check agent client exists
2. **Build context**: Consult context manager if session provided
3. **Execute query**: Call Claude via agent client
4. **Update history**: Record query in session (best effort)
5. **Return response**: Standard JSON response
6. **Error handling**: Proper HTTP errors for failures

#### Streaming Query Endpoint

```python
@router.post("/stream")
async def query_claude_stream(request: StreamQueryRequest):
    """
    Execute a streaming query to Claude

    This endpoint streams the response back token by token.
    """
    if agent_client is None:
        raise HTTPException(
            status_code=500,
            detail="Agent client not initialized."
        )

    async def generate_stream() -> AsyncIterator[str]:
        """Generate streaming response"""
        try:
            # Build context
            context = None
            if request.include_context and request.session_id and context_manager:
                context = context_manager.consult(
                    query=request.query,
                    session_id=request.session_id
                )

            # Stream query
            full_response = []
            for chunk in agent_client.query_stream(
                user_message=request.query,
                context=context,
                system_prompt=request.system_prompt
            ):
                full_response.append(chunk)
                yield f"data: {chunk}\n\n"

            # Send completion signal
            yield "data: [DONE]\n\n"

            # Update session history
            if request.session_id and context_manager:
                try:
                    complete_response = "".join(full_response)
                    context_manager.update_session(
                        request.session_id,
                        add_history={
                            "action": "query_stream",
                            "query": request.query,
                            "response_length": len(complete_response)
                        }
                    )
                except FileNotFoundError:
                    pass

        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Disable proxy buffering
        }
    )
```

**What's happening**:
1. **Async generator**: Define function that yields chunks
2. **Build context**: Same as standard query
3. **Stream chunks**: Yield each chunk as received from Claude
4. **Collect full response**: Save for history update
5. **Completion signal**: Send [DONE] when finished
6. **Update history**: Record complete query
7. **Error handling**: Stream errors as special messages

**SSE Headers**:
- `text/event-stream`: Tells browser it's a stream
- `Cache-Control: no-cache`: Don't cache streaming data
- `X-Accel-Buffering: no`: Disable nginx buffering

### Skills Routes (Skill Browsing Endpoints)

**File**: `backend/api/routes/skills.py`

#### List All Skills

```python
@router.get("/", response_model=List[SkillMetadataResponse])
async def list_skills(
    domain: Optional[str] = None,
    category: Optional[str] = None
) -> List[SkillMetadataResponse]:
    """
    List all available skills with optional filtering

    This endpoint returns metadata for all skills without loading
    full content (progressive disclosure layer 1).
    """
    if skills_loader is None:
        raise HTTPException(status_code=500, detail="Skills loader not initialized")

    try:
        skills = skills_loader.list_skills(domain=domain, category=category)

        return [
            SkillMetadataResponse(
                name=skill.name,
                description=skill.description,
                domain=skill.domain,
                category=skill.category,
                taxonomy=skill.taxonomy,
                parameters=skill.parameters,
                output_format=skill.output_format,
                estimated_duration=skill.estimated_duration,
                is_flat_structure=skill.is_flat_structure
            )
            for skill in skills
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list skills: {str(e)}"
        )
```

**What's happening**:
1. **Check initialization**: Validate skills loader exists
2. **Load skills**: Call loader with optional filters
3. **Convert to response**: Map SkillMetadata to SkillMetadataResponse
4. **Return list**: JSON array of skill metadata
5. **Error handling**: Proper HTTP error if loading fails

**Query parameters**:
- `domain`: Filter by domain (e.g., `?domain=change-agent`)
- `category`: Filter by category (e.g., `?category=meeting-management`)
- Both optional, can combine them

#### Get Skill Details

```python
@router.get("/{skill_path:path}", response_model=SkillDetailsResponse)
async def get_skill_details(skill_path: str) -> SkillDetailsResponse:
    """
    Get complete skill details including metadata, content, and available files

    This endpoint returns comprehensive skill information (progressive disclosure layers 1-2).
    """
    if skills_loader is None:
        raise HTTPException(status_code=500, detail="Skills loader not initialized")

    try:
        # Get skill info (metadata + available files)
        info = skills_loader.get_skill_info(skill_path)

        metadata = info["metadata"]

        return SkillDetailsResponse(
            metadata=SkillMetadataResponse(
                name=metadata.name,
                description=metadata.description,
                domain=metadata.domain,
                category=metadata.category,
                taxonomy=metadata.taxonomy,
                parameters=metadata.parameters,
                output_format=metadata.output_format,
                estimated_duration=metadata.estimated_duration,
                is_flat_structure=metadata.is_flat_structure
            ),
            content=info["content"],
            instructions=info["instructions"],
            resources=info["resources"]
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Skill not found: {skill_path}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get skill details: {str(e)}"
        )
```

**What's happening**:
1. **Path parameter**: `{skill_path:path}` captures full path (with slashes)
2. **Get skill info**: Load metadata + content + file listings
3. **Build response**: Comprehensive skill details
4. **404 handling**: Proper error if skill doesn't exist
5. **Error handling**: Catch and report failures

**The `:path` modifier**:
- Allows slashes in path parameter
- Example: `/api/skills/change-agent/meeting-minutes-capture`
- Without `:path`, only `/api/skills/change-agent` would work

### Context Routes (Session/Capture Management)

**File**: `backend/api/routes/context.py`

#### Create Session

```python
@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(request: CreateSessionRequest) -> SessionResponse:
    """
    Create a new session

    Sessions represent conversations or workflows with their own context and history.
    """
    if context_manager is None:
        raise HTTPException(status_code=500, detail="Context manager not initialized")

    try:
        session_id = context_manager.create_session(user_id=request.user_id)
        session = context_manager.get_session(session_id)

        return SessionResponse(
            session_id=session["session_id"],
            user_id=session.get("user_id"),
            created_at=session["created_at"],
            updated_at=session["updated_at"],
            context=session["context"],
            history_count=len(session.get("history", []))
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )
```

**What's happening**:
1. **201 Created**: Proper status code for resource creation
2. **Create session**: Call context manager
3. **Load full details**: Get complete session data
4. **Build response**: Session with all fields
5. **Error handling**: 500 if creation fails

**Status code 201**:
- Standard for "successfully created a resource"
- Different from 200 (general success)
- Semantically correct for POST creating resources

#### Update Session

```python
@router.put("/sessions/{session_id}")
async def update_session(session_id: str, request: UpdateSessionRequest):
    """
    Update session context or add history
    """
    if context_manager is None:
        raise HTTPException(status_code=500, detail="Context manager not initialized")

    try:
        context_manager.update_session(
            session_id,
            context=request.context,
            add_history=request.add_history
        )

        return {"message": "Session updated successfully"}

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found: {session_id}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update session: {str(e)}"
        )
```

**What's happening**:
1. **PUT method**: Standard for updates
2. **Path parameter**: Session ID in URL
3. **Update call**: Pass optional context and history
4. **404 handling**: Proper error if session doesn't exist
5. **Success message**: Simple confirmation

**PUT vs POST**:
- **PUT**: Update existing resource (idempotent)
- **POST**: Create new resource or perform action

#### Capture Information

```python
@router.post("/captures", response_model=CaptureResponse, status_code=201)
async def capture_information(request: CaptureRequest) -> CaptureResponse:
    """
    Capture information (meetings, documents, notes, etc.)

    This is the "Capture" part of the 3 C's.
    """
    if context_manager is None:
        raise HTTPException(status_code=500, detail="Context manager not initialized")

    try:
        capture_id = context_manager.capture(
            data=request.data,
            capture_type=request.capture_type,
            metadata=request.metadata
        )

        capture = context_manager.get_capture(capture_id)

        return CaptureResponse(
            capture_id=capture["capture_id"],
            capture_type=capture["capture_type"],
            captured_at=capture["captured_at"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to capture information: {str(e)}"
        )
```

**What's happening**:
1. **Create capture**: Store information
2. **Load details**: Get complete capture data
3. **Return summary**: Just ID, type, timestamp (not full data)
4. **201 Created**: Proper status for creation
5. **Error handling**: 500 if capture fails

**Why return summary?**
- Full data might be large
- Client already has the data (they sent it)
- Just need ID for future reference

### Main API Server Integration

**File**: `backend/api/api_server.py`

#### Router Registration

```python
from api.routes import query, skills, context

# Include API routers
app.include_router(query.router, prefix="/api")
app.include_router(skills.router, prefix="/api")
app.include_router(context.router, prefix="/api")
```

**What's happening**:
- Import route modules
- Register each router with `/api` prefix
- All routes automatically namespaced

**Result**:
- Query routes: `/api/query/*`
- Skills routes: `/api/skills/*`
- Context routes: `/api/context/*`

#### Startup Initialization

```python
@app.on_event("startup")
async def startup_event():
    """
    Run when the application starts
    Initialize agent components and routes
    """
    print("🚀 Risk Agents Backend starting...")

    # Setup directories
    skills_dir = Path(".claude/skills")
    context_dir = Path("context")

    # Initialize route modules
    print("🔧 Initializing agent components...")
    try:
        query.initialize_query_routes(skills_dir=skills_dir, context_dir=context_dir)
        skills.initialize_skills_routes(skills_dir=skills_dir)
        context.initialize_context_routes(context_dir=context_dir)
        print("✅ Agent components initialized")
    except Exception as e:
        print(f"⚠️  Warning: Failed to initialize: {e}")
        print("   API will run but some endpoints may not work")

    print(f"📚 API Docs: http://localhost:8050/docs")
    print("✅ Ready to accept requests")
```

**What's happening**:
1. **Startup event**: Runs when FastAPI starts
2. **Define paths**: Skills and context directories
3. **Initialize routes**: Call each route module's init function
4. **Error handling**: Graceful degradation if initialization fails
5. **User feedback**: Clear startup messages

**Why at startup?**
- Load once, use many times
- Fail fast if configuration wrong
- Clear logging of initialization
- Ready before first request

## API Documentation (Swagger UI)

FastAPI automatically generates interactive documentation:

**URL**: http://localhost:8050/docs

**Features**:
- **Try it out**: Execute requests directly from browser
- **Schemas**: See request/response models
- **Examples**: Auto-generated from Pydantic models
- **Authorization**: Can add auth headers
- **Response codes**: See all possible responses

**Alternative**: http://localhost:8050/redoc (cleaner reading experience)

## Testing the API

### Manual Testing with curl

**List skills**:
```bash
curl http://localhost:8050/api/skills/
```

**Create session**:
```bash
curl -X POST http://localhost:8050/api/context/sessions \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test@example.com"}'
```

**Query Claude**:
```bash
curl -X POST http://localhost:8050/api/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Help me with meeting minutes",
    "include_context": false
  }'
```

### Testing with Swagger UI

1. Open http://localhost:8050/docs
2. Find endpoint (e.g., `POST /api/query/`)
3. Click "Try it out"
4. Fill in request body
5. Click "Execute"
6. See response below

**Benefits**:
- No curl command needed
- Auto-fills examples
- Shows response schemas
- Saves successful requests

## Design Decisions Explained

### Why Separate Route Files?

**Decision**: Three separate route files instead of one large file

**Reasoning**:
1. **Organization**: Related endpoints grouped together
2. **Maintainability**: Easier to find and update endpoints
3. **Clear ownership**: Each file has clear responsibility
4. **Parallel development**: Multiple people can work on different routes
5. **Testing**: Easier to test routes in isolation

**Alternative approaches**:
- Single large file: Gets unwieldy (would be 1,200+ lines)
- Many tiny files: Too much overhead, harder to navigate

### Why Global Variables for Components?

**Decision**: Global variables initialized at startup

**Reasoning**:
1. **Single instance**: Don't recreate components per request (expensive)
2. **Simple pattern**: Easy to understand and maintain
3. **Startup initialization**: Load once, use many times
4. **Testability**: Can mock by replacing globals

**Alternative approaches**:
- FastAPI Depends: More complex, overkill for our use case
- Request-scoped: Too expensive (recreating per request)
- Class-based: More boilerplate, similar end result

### Why Pydantic Over Plain Dicts?

**Decision**: Use Pydantic models for all requests/responses

**Reasoning**:
1. **Type safety**: Catch errors at validation, not deep in code
2. **Documentation**: Auto-generates OpenAPI schemas
3. **IDE support**: Autocomplete and type checking
4. **Consistency**: Standard format across all endpoints
5. **Examples**: Built-in example data for docs

**Without Pydantic**:
```python
@router.post("/")
async def query_claude(data: dict):  # What fields? What types?
    query = data.get("query")  # Might not exist!
    if not query:  # Manual validation needed
        raise HTTPException(...)
```

**With Pydantic**:
```python
@router.post("/")
async def query_claude(request: QueryRequest):  # Clear schema
    # request.query guaranteed to exist and be a string!
```

### Why Both Standard and Streaming Query?

**Decision**: Two separate endpoints for query vs query_stream

**Reasoning**:
1. **Different use cases**: Quick questions vs long explanations
2. **Different clients**: Some can't handle streaming
3. **Simpler implementation**: Each endpoint focused
4. **Clear intent**: Endpoint name indicates behavior

**Alternative approaches**:
- Query parameter (`?stream=true`): Less clear, more complex logic
- Content negotiation: Overkill for this use case
- Single endpoint defaulting to stream: Forces streaming on all clients

### Why Path Parameters vs Query Parameters?

**Decision**: Use path parameters for resource IDs, query parameters for filters

**Reasoning**:
```python
# Resource ID (required, identifies specific resource)
GET /api/skills/{skill_path}        # Path parameter
GET /api/context/sessions/{session_id}  # Path parameter

# Filters (optional, modifies query)
GET /api/skills/?domain=change-agent    # Query parameter
GET /api/context/captures?capture_type=meeting  # Query parameter
```

**REST convention**:
- Path = resource identity
- Query = optional modifications/filters

## Key Takeaways

1. **FastAPI routers organize endpoints** into logical groups
2. **Pydantic models provide validation** and documentation
3. **Dependency injection initializes components** once at startup
4. **Streaming responses enable real-time** Claude interactions
5. **HTTP status codes communicate results** clearly
6. **Swagger UI provides interactive testing** built-in
7. **Progressive disclosure in APIs** matches backend loader pattern

---

**Files Created**: 3 route files + 2 modified (~1,210 lines)
**Endpoints Implemented**: 18 endpoints across 3 domains
**Status**: ✅ All endpoints tested and operational
**Documentation**: Automatic Swagger UI + this guide

**Next Step**: [Module 2, Step 2.7: End-to-End Testing](module-2-step-2.7-end-to-end-testing.md)
