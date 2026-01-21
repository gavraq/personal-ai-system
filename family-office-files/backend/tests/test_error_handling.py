"""
Tests for global error handling and consistent error response format.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.exceptions import (
    AppException,
    ErrorCode,
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ValidationException,
    ConflictException,
)


class TestErrorResponseFormat:
    """Test that all error responses follow the consistent format: {error, message, details}"""

    def test_validation_error_format(self, client: TestClient):
        """Test validation errors return correct format"""
        # Send invalid registration data (empty email)
        response = client.post(
            "/api/auth/register",
            json={"email": "", "password": "short"}
        )

        assert response.status_code == 422
        data = response.json()

        # Check standard error format
        assert "error" in data
        assert "message" in data
        assert data["error"] == "VALIDATION_ERROR"
        assert data["message"] == "Request validation failed"

        # Should have validation details
        assert "details" in data
        assert "validation_errors" in data["details"]

    def test_404_not_found_format(self, client: TestClient):
        """Test 404 errors return correct format"""
        # Try to get a non-existent deal (first need to auth)
        # Register and login
        client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "password123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Try to get non-existent deal
        response = client.get(
            "/api/deals/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
        data = response.json()

        assert "error" in data
        assert "message" in data
        assert data["error"] == "NOT_FOUND"

    def test_401_unauthorized_format(self, client: TestClient):
        """Test 401 errors return correct format"""
        # Try to access protected endpoint without token
        response = client.get("/api/auth/me")

        assert response.status_code in [401, 403]  # FastAPI security may return either
        data = response.json()

        assert "error" in data
        assert "message" in data

    def test_invalid_credentials_format(self, client: TestClient):
        """Test invalid login returns correct format"""
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrongpassword"}
        )

        assert response.status_code == 401
        data = response.json()

        assert "error" in data
        assert "message" in data
        assert data["error"] == "UNAUTHORIZED"

    def test_409_conflict_format(self, client: TestClient):
        """Test 409 conflict errors return correct format"""
        # Register a user
        client.post(
            "/api/auth/register",
            json={"email": "existing@example.com", "password": "password123"}
        )

        # Try to register with same email
        response = client.post(
            "/api/auth/register",
            json={"email": "existing@example.com", "password": "password456"}
        )

        assert response.status_code == 409
        data = response.json()

        assert "error" in data
        assert "message" in data


class TestAppExceptions:
    """Test custom AppException classes"""

    def test_not_found_exception(self):
        """Test NotFoundException creates correct exception"""
        exc = NotFoundException(message="User not found")

        assert exc.status_code == 404
        assert exc.error == "NOT_FOUND"
        assert exc.message == "User not found"

    def test_unauthorized_exception(self):
        """Test UnauthorizedException creates correct exception"""
        exc = UnauthorizedException(message="Token expired")

        assert exc.status_code == 401
        assert exc.error == "UNAUTHORIZED"
        assert exc.message == "Token expired"

    def test_forbidden_exception(self):
        """Test ForbiddenException creates correct exception"""
        exc = ForbiddenException(message="Admin access required")

        assert exc.status_code == 403
        assert exc.error == "FORBIDDEN"
        assert exc.message == "Admin access required"

    def test_validation_exception(self):
        """Test ValidationException creates correct exception"""
        exc = ValidationException(
            message="Invalid email format",
            details={"field": "email", "value": "not-an-email"}
        )

        assert exc.status_code == 400
        assert exc.error == "VALIDATION_ERROR"
        assert exc.message == "Invalid email format"
        assert exc.details == {"field": "email", "value": "not-an-email"}

    def test_conflict_exception(self):
        """Test ConflictException creates correct exception"""
        exc = ConflictException(message="Email already exists")

        assert exc.status_code == 409
        assert exc.error == "CONFLICT"
        assert exc.message == "Email already exists"

    def test_custom_app_exception(self):
        """Test custom AppException with all parameters"""
        exc = AppException(
            status_code=418,
            error="TEAPOT",
            message="I'm a teapot",
            details={"brew_type": "Earl Grey"}
        )

        assert exc.status_code == 418
        assert exc.error == "TEAPOT"
        assert exc.message == "I'm a teapot"
        assert exc.details == {"brew_type": "Earl Grey"}


class TestErrorCodes:
    """Test ErrorCode enum values"""

    def test_auth_error_codes(self):
        """Test authentication error codes exist"""
        assert ErrorCode.UNAUTHORIZED.value == "UNAUTHORIZED"
        assert ErrorCode.INVALID_TOKEN.value == "INVALID_TOKEN"
        assert ErrorCode.TOKEN_EXPIRED.value == "TOKEN_EXPIRED"

    def test_permission_error_codes(self):
        """Test permission error codes exist"""
        assert ErrorCode.FORBIDDEN.value == "FORBIDDEN"
        assert ErrorCode.INSUFFICIENT_PERMISSIONS.value == "INSUFFICIENT_PERMISSIONS"

    def test_not_found_error_codes(self):
        """Test not found error codes exist"""
        assert ErrorCode.NOT_FOUND.value == "NOT_FOUND"
        assert ErrorCode.RESOURCE_NOT_FOUND.value == "RESOURCE_NOT_FOUND"

    def test_validation_error_codes(self):
        """Test validation error codes exist"""
        assert ErrorCode.VALIDATION_ERROR.value == "VALIDATION_ERROR"
        assert ErrorCode.BAD_REQUEST.value == "BAD_REQUEST"
        assert ErrorCode.INVALID_INPUT.value == "INVALID_INPUT"

    def test_server_error_codes(self):
        """Test server error codes exist"""
        assert ErrorCode.INTERNAL_ERROR.value == "INTERNAL_ERROR"
        assert ErrorCode.DATABASE_ERROR.value == "DATABASE_ERROR"
        assert ErrorCode.EXTERNAL_SERVICE_ERROR.value == "EXTERNAL_SERVICE_ERROR"


class TestGlobalExceptionHandler:
    """Test that global exception handlers work correctly"""

    def test_validation_error_includes_field_details(self, client: TestClient):
        """Test that validation errors include field-level details"""
        # Missing required field
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com"}  # Missing password
        )

        assert response.status_code == 422
        data = response.json()

        assert data["error"] == "VALIDATION_ERROR"
        assert "details" in data
        assert "validation_errors" in data["details"]

        # Check we have validation error for password
        errors = data["details"]["validation_errors"]
        assert len(errors) > 0
        password_error = next((e for e in errors if "password" in e["field"].lower()), None)
        assert password_error is not None

    def test_malformed_json_returns_validation_error(self, client: TestClient):
        """Test that malformed JSON returns a proper error response"""
        response = client.post(
            "/api/auth/register",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )

        # Should return 422 for malformed request
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "message" in data
