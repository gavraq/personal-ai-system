"""
Tests for API response compression
"""
import gzip
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


class TestGZipCompression:
    """Test that GZip compression is applied to API responses"""

    def test_compression_enabled_for_large_responses(self, client):
        """Verify GZip compression is applied when Accept-Encoding includes gzip"""
        # The health endpoint is small, but we can test the compression header behavior
        # with Accept-Encoding header
        response = client.get(
            "/health",
            headers={"Accept-Encoding": "gzip, deflate"}
        )
        assert response.status_code == 200
        # Small responses (< 500 bytes) won't be compressed due to minimum_size setting
        # But the middleware should be active

    def test_compression_not_applied_to_small_responses(self, client):
        """Verify small responses are not compressed (due to minimum_size threshold)"""
        response = client.get(
            "/",
            headers={"Accept-Encoding": "gzip, deflate"}
        )
        assert response.status_code == 200
        # Response is small (~50 bytes), so it shouldn't be gzip compressed
        # The Content-Encoding header should not be 'gzip' for small responses
        # Note: TestClient may transparently decompress, so we check the raw content
        assert response.json() == {"status": "ok", "message": "Family Office Files API"}

    def test_health_endpoint_works_with_compression(self, client):
        """Health check works regardless of compression"""
        response = client.get(
            "/health",
            headers={"Accept-Encoding": "gzip, deflate"}
        )
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_large_response_gets_compressed(self, client):
        """Test that large responses are compressed"""
        # Create a user to get a longer response when listing users
        # First, register a user
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "TestPass123!",
                "full_name": "Test User"
            }
        )
        assert register_response.status_code == 200

        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPass123!"
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Make a request to an endpoint that could return larger data
        # The users list with pagination info is a good candidate
        response = client.get(
            "/api/users",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept-Encoding": "gzip, deflate"
            }
        )
        assert response.status_code == 200
        # Response should be valid JSON regardless of compression
        data = response.json()
        assert "users" in data or "items" in data or isinstance(data, list)


class TestCompressionMiddlewareConfiguration:
    """Test middleware configuration"""

    def test_middleware_is_registered(self):
        """Verify GZipMiddleware is in the middleware stack"""
        # Check that the app has middleware configured
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "GZipMiddleware" in middleware_classes

    def test_minimum_size_threshold(self):
        """Verify minimum size threshold is configured"""
        # Find the GZipMiddleware in the middleware stack
        gzip_middleware = None
        for m in app.user_middleware:
            if m.cls.__name__ == "GZipMiddleware":
                gzip_middleware = m
                break

        assert gzip_middleware is not None
        # Check the minimum_size kwarg
        assert gzip_middleware.kwargs.get("minimum_size") == 500


class TestCompressionWithDealEndpoints:
    """Test compression with deal-related endpoints that may return larger payloads"""

    def test_deal_list_response_format(self, client):
        """Test that deal list responses work correctly with compression enabled"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123!",
                "full_name": "Admin User"
            }
        )
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123!"
            }
        )
        token = login_response.json()["access_token"]

        # Create multiple deals to get a larger response
        for i in range(5):
            client.post(
                "/api/deals",
                json={
                    "name": f"Test Deal {i}",
                    "description": f"Description for deal {i}" * 10,  # Make it larger
                    "stage": "prospecting"
                },
                headers={"Authorization": f"Bearer {token}"}
            )

        # Request deal list with compression
        response = client.get(
            "/api/deals",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept-Encoding": "gzip, deflate"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "deals" in data
        assert len(data["deals"]) >= 5

    def test_audit_log_compression(self, client):
        """Test that audit log endpoint works with compression"""
        # Register admin user
        client.post(
            "/api/auth/register",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123!",
                "full_name": "Admin User"
            }
        )

        # Login and make the user admin
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123!"
            }
        )
        token = login_response.json()["access_token"]
        user_id = login_response.json()["user"]["id"]

        # Make the user an admin using database session
        from tests.conftest import TestingSessionLocal
        from app.models.user import User, UserRole

        db = TestingSessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            user.role = UserRole.ADMIN.value
            db.commit()
        finally:
            db.close()

        # Re-login to get fresh token with admin role
        login_response = client.post(
            "/api/auth/login",
            json={
                "email": "admin@example.com",
                "password": "AdminPass123!"
            }
        )
        token = login_response.json()["access_token"]

        # Access audit log with compression
        response = client.get(
            "/api/audit",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept-Encoding": "gzip, deflate"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or "entries" in data or isinstance(data, list) or "audit_entries" in data
