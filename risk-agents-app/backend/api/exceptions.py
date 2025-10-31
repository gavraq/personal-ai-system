"""
Custom Exceptions for Risk Agents API
Provides domain-specific exceptions with appropriate HTTP status codes
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class RiskAgentsException(HTTPException):
    """
    Base exception for all Risk Agents API errors

    All custom exceptions inherit from this class
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__


# Authentication Exceptions

class AuthenticationError(RiskAgentsException):
    """Raised when authentication fails"""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            error_code="AUTH_FAILED"
        )


class InvalidTokenError(RiskAgentsException):
    """Raised when JWT token is invalid"""

    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            error_code="INVALID_TOKEN"
        )


class PermissionDeniedError(RiskAgentsException):
    """Raised when user lacks required permissions"""

    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="PERMISSION_DENIED"
        )


# Resource Exceptions

class ResourceNotFoundError(RiskAgentsException):
    """Raised when a requested resource is not found"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found: {identifier}",
            error_code="RESOURCE_NOT_FOUND"
        )


class ResourceAlreadyExistsError(RiskAgentsException):
    """Raised when attempting to create a resource that already exists"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{resource} already exists: {identifier}",
            error_code="RESOURCE_EXISTS"
        )


# Skill Exceptions

class SkillNotFoundError(ResourceNotFoundError):
    """Raised when a skill is not found"""

    def __init__(self, skill_name: str):
        super().__init__("Skill", skill_name)
        self.error_code = "SKILL_NOT_FOUND"


class SkillExecutionError(RiskAgentsException):
    """Raised when skill execution fails"""

    def __init__(self, skill_name: str, reason: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Skill execution failed for '{skill_name}': {reason}",
            error_code="SKILL_EXECUTION_FAILED"
        )


class InvalidSkillParametersError(RiskAgentsException):
    """Raised when skill parameters are invalid"""

    def __init__(self, skill_name: str, missing_params: list = None, invalid_params: list = None):
        errors = []
        if missing_params:
            errors.append(f"missing: {', '.join(missing_params)}")
        if invalid_params:
            errors.append(f"invalid: {', '.join(invalid_params)}")

        detail = f"Invalid parameters for skill '{skill_name}': {'; '.join(errors)}"

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="INVALID_SKILL_PARAMS"
        )


# Context Exceptions

class SessionNotFoundError(ResourceNotFoundError):
    """Raised when a session is not found"""

    def __init__(self, session_id: str):
        super().__init__("Session", session_id)
        self.error_code = "SESSION_NOT_FOUND"


class InvalidSessionError(RiskAgentsException):
    """Raised when session data is invalid"""

    def __init__(self, detail: str = "Invalid session data"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INVALID_SESSION"
        )


# Knowledge Exceptions

class KnowledgeNotFoundError(ResourceNotFoundError):
    """Raised when knowledge document is not found"""

    def __init__(self, path: str):
        super().__init__("Knowledge document", path)
        self.error_code = "KNOWLEDGE_NOT_FOUND"


class InvalidTaxonomyError(RiskAgentsException):
    """Raised when taxonomy path is invalid"""

    def __init__(self, path: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid taxonomy path: {path}",
            error_code="INVALID_TAXONOMY"
        )


# Query Exceptions

class InvalidQueryError(RiskAgentsException):
    """Raised when query is invalid"""

    def __init__(self, detail: str = "Invalid query"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INVALID_QUERY"
        )


class QueryExecutionError(RiskAgentsException):
    """Raised when query execution fails"""

    def __init__(self, reason: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {reason}",
            error_code="QUERY_EXECUTION_FAILED"
        )


class ClaudeAPIError(RiskAgentsException):
    """Raised when Claude API call fails"""

    def __init__(self, reason: str):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Claude API error: {reason}",
            error_code="CLAUDE_API_ERROR"
        )


# Rate Limiting Exceptions

class RateLimitExceededError(RiskAgentsException):
    """Raised when rate limit is exceeded"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds",
            headers={"Retry-After": str(retry_after)},
            error_code="RATE_LIMIT_EXCEEDED"
        )


# Validation Exceptions

class ValidationError(RiskAgentsException):
    """Raised when request validation fails"""

    def __init__(self, detail: str, field: str = None):
        error_detail = f"Validation error"
        if field:
            error_detail += f" for field '{field}'"
        error_detail += f": {detail}"

        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_detail,
            error_code="VALIDATION_ERROR"
        )


# Configuration Exceptions

class ConfigurationError(RiskAgentsException):
    """Raised when configuration is invalid or missing"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {detail}",
            error_code="CONFIGURATION_ERROR"
        )


class MissingAPIKeyError(ConfigurationError):
    """Raised when API key is missing"""

    def __init__(self):
        super().__init__("ANTHROPIC_API_KEY not configured")
        self.error_code = "MISSING_API_KEY"


# Exception Handlers

def create_error_response(
    request_id: str,
    error_code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized error response

    Args:
        request_id: Request ID for tracking
        error_code: Error code for categorization
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details

    Returns:
        dict: Standardized error response
    """
    response = {
        "error": {
            "code": error_code,
            "message": message,
            "status": status_code,
            "request_id": request_id
        }
    }

    if details:
        response["error"]["details"] = details

    return response
