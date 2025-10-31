"""
Skills Routes - Skills Framework Management Endpoints
Handles browsing, filtering, retrieving skill information, and skill execution (Module 3.4)
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import uuid

from agent import SkillsLoader, SkillMetadata, RiskAgentClient
from api.dependencies import get_optional_user
from api.auth import User

# Create router
router = APIRouter(prefix="/skills", tags=["skills"])

# Initialize components (will be set on startup)
skills_loader: Optional[SkillsLoader] = None
agent_client: Optional[RiskAgentClient] = None

# Skill execution tracking (Module 3.4 - in-memory, replace with DB in production)
# Structure: {execution_id: SkillExecutionEntry}
skill_executions: Dict[str, Dict[str, Any]] = {}

# Skill analytics tracking (Module 3.4)
skill_analytics = {
    "total_executions": 0,
    "successful_executions": 0,
    "failed_executions": 0,
    "executions_by_skill": defaultdict(int),
    "executions_by_domain": defaultdict(int),
    "average_execution_time": 0.0,
    "executions_by_hour": defaultdict(int)
}


# Response Models
class SkillMetadataResponse(BaseModel):
    """Skill metadata response"""
    name: str
    description: str
    domain: str
    category: str
    taxonomy: str
    parameters: List[str]
    output_format: str
    estimated_duration: str
    is_flat_structure: bool

    class Config:
        json_schema_extra = {
            "example": {
                "name": "meeting-minutes-capture",
                "description": "Capture meeting minutes from transcripts",
                "domain": "change-agent",
                "category": "meeting-management",
                "taxonomy": "change-agent/meeting-management",
                "parameters": ["meeting_transcript", "meeting_date"],
                "output_format": "structured_markdown",
                "estimated_duration": "2-3 minutes",
                "is_flat_structure": False
            }
        }


class SkillDetailsResponse(BaseModel):
    """Complete skill details including content"""
    metadata: SkillMetadataResponse
    content: str
    instructions: List[str]
    resources: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "name": "meeting-minutes-capture",
                    "description": "Capture meeting minutes from transcripts",
                    "domain": "change-agent",
                    "category": "meeting-management",
                    "taxonomy": "change-agent/meeting-management",
                    "parameters": ["meeting_transcript", "meeting_date"],
                    "output_format": "structured_markdown",
                    "estimated_duration": "2-3 minutes",
                    "is_flat_structure": False
                },
                "content": "# Meeting Minutes Capture Skill\n\n## Purpose\n...",
                "instructions": ["capture.md", "extract-actions.md"],
                "resources": ["meeting-template.md", "examples.md"]
            }
        }


class SkillInstructionResponse(BaseModel):
    """Skill instruction content"""
    skill_path: str
    instruction_file: str
    content: str


class SkillResourceResponse(BaseModel):
    """Skill resource content"""
    skill_path: str
    resource_file: str
    content: str


# Module 3.4: New Pydantic Models for Skill Execution

class SkillExecutionRequest(BaseModel):
    """Request to execute a skill"""
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Skill-specific parameters"
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for context persistence"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "parameters": {
                    "meeting_transcript": "...",
                    "meeting_date": "2025-10-24"
                },
                "session_id": "session-123"
            }
        }


class SkillExecutionResponse(BaseModel):
    """Response from skill execution"""
    execution_id: str
    skill_path: str
    result: str
    success: bool
    execution_time: float
    timestamp: datetime
    session_id: Optional[str]

    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "exec-123e4567-e89b-12d3-a456-426614174000",
                "skill_path": "change-agent/meeting-minutes",
                "result": "# Meeting Minutes\n\n...",
                "success": True,
                "execution_time": 2.345,
                "timestamp": "2025-10-24T10:30:00",
                "session_id": "session-123"
            }
        }


class SkillExecutionEntry(BaseModel):
    """Single skill execution history entry"""
    execution_id: str
    skill_path: str
    skill_domain: str
    parameters: Dict[str, Any]
    result: str
    success: bool
    error: Optional[str]
    execution_time: float
    timestamp: datetime
    session_id: Optional[str]
    user_id: Optional[str]


class SkillMetricsResponse(BaseModel):
    """Metrics for a specific skill"""
    skill_path: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    average_execution_time: float
    recent_executions: List[Dict[str, Any]]

    class Config:
        json_schema_extra = {
            "example": {
                "skill_path": "change-agent/meeting-minutes",
                "total_executions": 45,
                "successful_executions": 43,
                "failed_executions": 2,
                "success_rate": 0.956,
                "average_execution_time": 2.345,
                "recent_executions": [
                    {
                        "execution_id": "exec-123",
                        "timestamp": "2025-10-24T10:30:00",
                        "success": True,
                        "execution_time": 2.1
                    }
                ]
            }
        }


class SkillAnalyticsResponse(BaseModel):
    """Global skill execution analytics"""
    total_executions: int
    successful_executions: int
    failed_executions: int
    overall_success_rate: float
    average_execution_time: float
    most_used_skills: List[Dict[str, Any]]
    executions_by_domain: Dict[str, int]
    executions_by_hour: Dict[str, int]

    class Config:
        json_schema_extra = {
            "example": {
                "total_executions": 234,
                "successful_executions": 220,
                "failed_executions": 14,
                "overall_success_rate": 0.940,
                "average_execution_time": 2.5,
                "most_used_skills": [
                    {"skill": "change-agent/meeting-minutes", "count": 45},
                    {"skill": "risk-agent/dependency-analysis", "count": 38}
                ],
                "executions_by_domain": {
                    "change-agent": 120,
                    "risk-agent": 114
                },
                "executions_by_hour": {
                    "2025-10-24T09": 12,
                    "2025-10-24T10": 34
                }
            }
        }


# Initialize function (called from api_server.py startup)
def initialize_skills_routes(skills_dir: Path, client: Optional[RiskAgentClient] = None):
    """
    Initialize skills routes with skills loader and agent client

    Args:
        skills_dir: Path to skills directory
        client: Optional RiskAgentClient for skill execution (Module 3.4)
    """
    global skills_loader, agent_client
    skills_loader = SkillsLoader(skills_dir=skills_dir)
    agent_client = client
    print("✅ Skills routes initialized")


@router.get("/", response_model=List[SkillMetadataResponse])
async def list_skills(
    domain: Optional[str] = None,
    category: Optional[str] = None
) -> List[SkillMetadataResponse]:
    """
    List all available skills with optional filtering

    This endpoint returns metadata for all skills without loading
    full content (progressive disclosure layer 1).

    Args:
        domain: Optional domain filter (e.g., "change-agent")
        category: Optional category filter (e.g., "meeting-management")

    Returns:
        List of skill metadata

    Raises:
        HTTPException: If skills loader not initialized
    """
    if skills_loader is None:
        raise HTTPException(
            status_code=500,
            detail="Skills loader not initialized"
        )

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


@router.get("/domains", response_model=List[str])
async def list_domains() -> List[str]:
    """
    List all skill domains

    Returns:
        List of domain names

    Raises:
        HTTPException: If skills loader not initialized
    """
    if skills_loader is None:
        raise HTTPException(
            status_code=500,
            detail="Skills loader not initialized"
        )

    try:
        return skills_loader.list_domains()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list domains: {str(e)}"
        )


@router.get("/categories", response_model=List[str])
async def list_categories(domain: Optional[str] = None) -> List[str]:
    """
    List all skill categories, optionally filtered by domain

    Args:
        domain: Optional domain filter

    Returns:
        List of category names

    Raises:
        HTTPException: If skills loader not initialized
    """
    if skills_loader is None:
        raise HTTPException(
            status_code=500,
            detail="Skills loader not initialized"
        )

    try:
        return skills_loader.list_categories(domain=domain)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list categories: {str(e)}"
        )


# Module 3.4: Health and Analytics endpoints (BEFORE catch-all to avoid routing conflicts)

@router.get("/health/status")
async def skills_health():
    """
    Check skills service health (Enhanced with Module 3.4 stats)

    Returns:
        dict: Health status including loader initialization and execution stats
    """
    loader_initialized = skills_loader is not None
    agent_initialized = agent_client is not None

    skill_count = 0
    if loader_initialized:
        try:
            skill_count = len(skills_loader.list_skills())
        except:
            pass

    return {
        "status": "healthy" if (loader_initialized and agent_initialized) else "degraded",
        "loader_initialized": loader_initialized,
        "agent_client_initialized": agent_initialized,
        "skills_available": skill_count,
        "ready": loader_initialized and agent_initialized,
        # Module 3.4 stats
        "total_executions": skill_analytics["total_executions"],
        "successful_executions": skill_analytics["successful_executions"],
        "failed_executions": skill_analytics["failed_executions"]
    }


@router.get("/analytics/global", response_model=SkillAnalyticsResponse)
async def get_global_skill_analytics() -> SkillAnalyticsResponse:
    """
    Get global skill execution analytics across all skills

    Returns:
        Global analytics including most-used skills, success rates, and domain breakdown
    """
    total_executions = skill_analytics["total_executions"]
    successful_executions = skill_analytics["successful_executions"]
    failed_executions = skill_analytics["failed_executions"]

    overall_success_rate = (
        successful_executions / total_executions if total_executions > 0 else 0.0
    )

    # Get most-used skills (top 10)
    most_used_skills = sorted(
        skill_analytics["executions_by_skill"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    most_used_skills_formatted = [
        {"skill": skill, "count": count}
        for skill, count in most_used_skills
    ]

    return SkillAnalyticsResponse(
        total_executions=total_executions,
        successful_executions=successful_executions,
        failed_executions=failed_executions,
        overall_success_rate=round(overall_success_rate, 3),
        average_execution_time=round(skill_analytics["average_execution_time"], 3),
        most_used_skills=most_used_skills_formatted,
        executions_by_domain=dict(skill_analytics["executions_by_domain"]),
        executions_by_hour=dict(skill_analytics["executions_by_hour"])
    )

# Specific skill path endpoints (MUST come before catch-all /{skill_path:path})

@router.get("/{skill_path:path}/instructions/{instruction_file}", response_model=SkillInstructionResponse)
async def get_skill_instruction(skill_path: str, instruction_file: str) -> SkillInstructionResponse:
    """
    Get specific instruction file content

    This endpoint loads instruction content on-demand (progressive disclosure layer 2).

    Args:
        skill_path: Skill path (nested: "domain/skill-name" or flat: "skill-name")
        instruction_file: Instruction filename (e.g., "capture.md")

    Returns:
        Instruction content

    Raises:
        HTTPException: If instruction file not found or loader not initialized
    """
    if skills_loader is None:
        raise HTTPException(
            status_code=500,
            detail="Skills loader not initialized"
        )

    try:
        content = skills_loader.load_skill_instructions(skill_path, instruction_file)

        return SkillInstructionResponse(
            skill_path=skill_path,
            instruction_file=instruction_file,
            content=content
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Instruction file not found: {skill_path}/instructions/{instruction_file}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load instruction: {str(e)}"
        )


@router.get("/{skill_path:path}/resources/{resource_file}", response_model=SkillResourceResponse)
async def get_skill_resource(skill_path: str, resource_file: str) -> SkillResourceResponse:
    """
    Get specific resource file content

    This endpoint loads resource content on-demand (progressive disclosure layer 3).

    Args:
        skill_path: Skill path (nested: "domain/skill-name" or flat: "skill-name")
        resource_file: Resource filename (e.g., "meeting-template.md")

    Returns:
        Resource content

    Raises:
        HTTPException: If resource file not found or loader not initialized
    """
    if skills_loader is None:
        raise HTTPException(
            status_code=500,
            detail="Skills loader not initialized"
        )

    try:
        content = skills_loader.load_skill_resources(skill_path, resource_file)

        return SkillResourceResponse(
            skill_path=skill_path,
            resource_file=resource_file,
            content=content
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Resource file not found: {skill_path}/resources/{resource_file}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load resource: {str(e)}"
        )


# Module 3.4: Skill Execution Endpoint

@router.post("/{skill_path:path}/execute", response_model=SkillExecutionResponse)
async def execute_skill(
    skill_path: str,
    request: SkillExecutionRequest,
    current_user: Optional[User] = Depends(get_optional_user)
) -> SkillExecutionResponse:
    """
    Execute a skill with the provided parameters

    This endpoint uses the AgentClient to execute skills dynamically.

    Args:
        skill_path: Skill path (nested: "domain/skill-name" or flat: "skill-name")
        request: Execution request with parameters and optional session_id
        current_user: Optional authenticated user

    Returns:
        Skill execution result

    Raises:
        HTTPException: If skill not found, execution fails, or services not initialized
    """
    if skills_loader is None:
        raise HTTPException(
            status_code=500,
            detail="Skills loader not initialized"
        )

    if agent_client is None:
        raise HTTPException(
            status_code=500,
            detail="Agent client not initialized - skill execution not available"
        )

    # Generate execution ID and track start time
    execution_id = f"exec-{uuid.uuid4()}"
    start_time = datetime.now()

    try:
        # Load skill metadata to get domain
        metadata = skills_loader.load_skill_metadata(skill_path)

        # Build skill execution prompt
        # In a real implementation, this would use the skill's instructions
        # and apply the parameters. For now, we'll create a simple prompt.
        skill_prompt = f"""Execute the skill: {metadata.name}

Domain: {metadata.domain}
Description: {metadata.description}

Parameters:
{chr(10).join(f"- {k}: {v}" for k, v in request.parameters.items())}

Please execute this skill and return the result in the expected format: {metadata.output_format}
"""

        # Execute using agent client
        result = agent_client.query(
            user_message=skill_prompt
        )

        # Calculate execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        # Track successful execution
        skill_executions[execution_id] = {
            "execution_id": execution_id,
            "skill_path": skill_path,
            "skill_domain": metadata.domain,
            "parameters": request.parameters,
            "result": result,
            "success": True,
            "error": None,
            "execution_time": execution_time,
            "timestamp": start_time,
            "session_id": request.session_id,
            "user_id": current_user.user_id if current_user else None
        }

        # Update analytics
        skill_analytics["total_executions"] += 1
        skill_analytics["successful_executions"] += 1
        skill_analytics["executions_by_skill"][skill_path] += 1
        skill_analytics["executions_by_domain"][metadata.domain] += 1

        # Update average execution time (incremental averaging)
        total_execs = skill_analytics["total_executions"]
        current_avg = skill_analytics["average_execution_time"]
        skill_analytics["average_execution_time"] = (
            (current_avg * (total_execs - 1) + execution_time) / total_execs
        )

        # Track executions by hour
        hour_key = start_time.strftime("%Y-%m-%dT%H")
        skill_analytics["executions_by_hour"][hour_key] += 1

        return SkillExecutionResponse(
            execution_id=execution_id,
            skill_path=skill_path,
            result=result,
            success=True,
            execution_time=execution_time,
            timestamp=start_time,
            session_id=request.session_id
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Skill not found: {skill_path}"
        )
    except Exception as e:
        # Track failed execution
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()

        skill_executions[execution_id] = {
            "execution_id": execution_id,
            "skill_path": skill_path,
            "skill_domain": metadata.domain if 'metadata' in locals() else "unknown",
            "parameters": request.parameters,
            "result": "",
            "success": False,
            "error": str(e),
            "execution_time": execution_time,
            "timestamp": start_time,
            "session_id": request.session_id,
            "user_id": current_user.user_id if current_user else None
        }

        # Update analytics
        skill_analytics["total_executions"] += 1
        skill_analytics["failed_executions"] += 1

        raise HTTPException(
            status_code=500,
            detail=f"Skill execution failed: {str(e)}"
        )


# Module 3.4: Skill Metrics Endpoint

@router.get("/{skill_path:path}/metrics", response_model=SkillMetricsResponse)
async def get_skill_metrics(skill_path: str) -> SkillMetricsResponse:
    """
    Get execution metrics for a specific skill

    Args:
        skill_path: Skill path (nested: "domain/skill-name" or flat: "skill-name")

    Returns:
        Skill metrics including execution count, success rate, and recent executions

    Raises:
        HTTPException: If skill not found
    """
    if skills_loader is None:
        raise HTTPException(
            status_code=500,
            detail="Skills loader not initialized"
        )

    try:
        # Verify skill exists
        metadata = skills_loader.load_skill_metadata(skill_path)

        # Filter executions for this skill
        skill_execs = [
            exec_data for exec_data in skill_executions.values()
            if exec_data["skill_path"] == skill_path
        ]

        total_executions = len(skill_execs)
        successful_executions = sum(1 for e in skill_execs if e["success"])
        failed_executions = total_executions - successful_executions
        success_rate = successful_executions / total_executions if total_executions > 0 else 0.0

        # Calculate average execution time
        if total_executions > 0:
            average_execution_time = sum(e["execution_time"] for e in skill_execs) / total_executions
        else:
            average_execution_time = 0.0

        # Get recent executions (last 10)
        recent_executions = sorted(
            skill_execs,
            key=lambda x: x["timestamp"],
            reverse=True
        )[:10]

        recent_executions_formatted = [
            {
                "execution_id": e["execution_id"],
                "timestamp": e["timestamp"].isoformat(),
                "success": e["success"],
                "execution_time": round(e["execution_time"], 3)
            }
            for e in recent_executions
        ]

        return SkillMetricsResponse(
            skill_path=skill_path,
            total_executions=total_executions,
            successful_executions=successful_executions,
            failed_executions=failed_executions,
            success_rate=round(success_rate, 3),
            average_execution_time=round(average_execution_time, 3),
            recent_executions=recent_executions_formatted
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Skill not found: {skill_path}"
        )


# Catch-all endpoint (MUST be LAST to avoid catching more specific routes above)

@router.get("/{skill_path:path}", response_model=SkillDetailsResponse)
async def get_skill_details(skill_path: str) -> SkillDetailsResponse:
    """
    Get complete skill details including metadata, content, and available files

    This endpoint returns comprehensive skill information (progressive disclosure layers 1-2).

    IMPORTANT: This catch-all endpoint must be defined LAST to ensure more specific
    routes like /instructions, /resources, /metrics, /execute are matched first.

    Args:
        skill_path: Skill path (nested: "domain/skill-name" or flat: "skill-name")

    Returns:
        Complete skill details

    Raises:
        HTTPException: If skill not found or loader not initialized
    """
    if skills_loader is None:
        raise HTTPException(
            status_code=500,
            detail="Skills loader not initialized"
        )

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
