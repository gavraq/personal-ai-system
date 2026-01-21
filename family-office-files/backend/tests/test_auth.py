"""
Tests for authentication endpoints
"""
import pytest


class TestRegister:
    """Tests for POST /api/auth/register"""

    def test_register_valid_credentials_returns_201(self, client):
        """Register with valid credentials returns 201"""
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "securepassword123"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "viewer"
        assert "id" in data
        assert "created_at" in data
        # Password should not be in response
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_existing_email_returns_409(self, client):
        """Register with existing email returns 409"""
        # First registration
        client.post(
            "/api/auth/register",
            json={"email": "duplicate@example.com", "password": "securepassword123"}
        )

        # Second registration with same email
        response = client.post(
            "/api/auth/register",
            json={"email": "duplicate@example.com", "password": "differentpassword"}
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    def test_register_weak_password_returns_400(self, client):
        """Register with weak password (< 8 chars) returns 400"""
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com", "password": "short"}
        )

        assert response.status_code == 422  # Pydantic validation error
        detail = response.json()["detail"]
        # Check that password length error is in validation errors
        assert any("password" in str(error).lower() for error in detail)

    def test_register_invalid_email_returns_422(self, client):
        """Register with invalid email format returns 422"""
        response = client.post(
            "/api/auth/register",
            json={"email": "not-an-email", "password": "securepassword123"}
        )

        assert response.status_code == 422

    def test_register_missing_password_returns_422(self, client):
        """Register without password returns 422"""
        response = client.post(
            "/api/auth/register",
            json={"email": "test@example.com"}
        )

        assert response.status_code == 422

    def test_register_missing_email_returns_422(self, client):
        """Register without email returns 422"""
        response = client.post(
            "/api/auth/register",
            json={"password": "securepassword123"}
        )

        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/auth/login"""

    def test_login_valid_credentials_returns_jwt(self, client):
        """Login with valid credentials returns JWT tokens"""
        # First register a user
        client.post(
            "/api/auth/register",
            json={"email": "login@example.com", "password": "securepassword123"}
        )

        # Then login
        response = client.post(
            "/api/auth/login",
            json={"email": "login@example.com", "password": "securepassword123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        # Tokens should be non-empty strings
        assert len(data["access_token"]) > 0
        assert len(data["refresh_token"]) > 0

    def test_login_invalid_password_returns_401(self, client):
        """Login with invalid password returns 401"""
        # First register a user
        client.post(
            "/api/auth/register",
            json={"email": "wrongpass@example.com", "password": "securepassword123"}
        )

        # Then login with wrong password
        response = client.post(
            "/api/auth/login",
            json={"email": "wrongpass@example.com", "password": "wrongpassword"}
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_nonexistent_user_returns_401(self, client):
        """Login with non-existent user returns 401"""
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "somepassword"}
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]


class TestProtectedRoutes:
    """Tests for protected routes requiring authentication"""

    def test_access_protected_route_without_token_returns_401(self, client):
        """Access protected route without token returns 401"""
        response = client.get("/api/auth/me")

        assert response.status_code == 403  # HTTPBearer returns 403 when no credentials

    def test_access_protected_route_with_invalid_token_returns_401(self, client):
        """Access protected route with invalid token returns 401"""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token-here"}
        )

        assert response.status_code == 401

    def test_access_protected_route_with_valid_token_returns_user(self, client):
        """Access protected route with valid token returns user data"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"email": "protected@example.com", "password": "securepassword123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"email": "protected@example.com", "password": "securepassword123"}
        )
        access_token = login_response.json()["access_token"]

        # Access protected route
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "protected@example.com"
        assert data["role"] == "viewer"


class TestTokenRefresh:
    """Tests for POST /api/auth/refresh"""

    def test_token_refresh_returns_new_access_token(self, client):
        """Token refresh with valid refresh token returns new access token"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"email": "refresh@example.com", "password": "securepassword123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"email": "refresh@example.com", "password": "securepassword123"}
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh the token
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_token_refresh_with_invalid_token_returns_401(self, client):
        """Token refresh with invalid token returns 401"""
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": "invalid-refresh-token"}
        )

        assert response.status_code == 401

    def test_token_refresh_with_access_token_returns_401(self, client):
        """Token refresh using access token instead of refresh token returns 401"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"email": "wrongtoken@example.com", "password": "securepassword123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"email": "wrongtoken@example.com", "password": "securepassword123"}
        )
        access_token = login_response.json()["access_token"]

        # Try to refresh using access token (should fail)
        response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": access_token}
        )

        assert response.status_code == 401


class TestLogout:
    """Tests for POST /api/auth/logout"""

    def test_logout_with_valid_token_returns_success(self, client):
        """Logout with valid token returns success message"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"email": "logout@example.com", "password": "securepassword123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"email": "logout@example.com", "password": "securepassword123"}
        )
        access_token = login_response.json()["access_token"]

        # Logout
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]

    def test_logout_without_token_returns_401(self, client):
        """Logout without token returns 401"""
        response = client.post("/api/auth/logout")

        assert response.status_code == 403  # HTTPBearer returns 403 when no credentials


class TestSessionManagement:
    """Tests for session management (feat-4) - token blacklist functionality"""

    def test_logout_invalidates_access_token(self, client):
        """After logout, the access token should be blacklisted and rejected"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"email": "session@example.com", "password": "securepassword123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"email": "session@example.com", "password": "securepassword123"}
        )
        access_token = login_response.json()["access_token"]

        # Verify token works before logout
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me_response.status_code == 200

        # Logout
        logout_response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert logout_response.status_code == 200

        # Try to use the same token after logout - should fail
        me_response_after = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert me_response_after.status_code == 401

    def test_logout_with_refresh_token_invalidates_both(self, client):
        """Logout with refresh token provided should blacklist both tokens"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"email": "bothtoken@example.com", "password": "securepassword123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"email": "bothtoken@example.com", "password": "securepassword123"}
        )
        tokens = login_response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # Logout with refresh token
        logout_response = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
            json={"refresh_token": refresh_token}
        )
        assert logout_response.status_code == 200

        # Try to refresh with the blacklisted refresh token - should fail
        refresh_response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 401

    def test_new_login_after_logout_gets_valid_tokens(self, client):
        """After logout, user can login again and get new valid tokens"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"email": "relogin@example.com", "password": "securepassword123"}
        )
        login_response1 = client.post(
            "/api/auth/login",
            json={"email": "relogin@example.com", "password": "securepassword123"}
        )
        access_token1 = login_response1.json()["access_token"]

        # Logout
        client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {access_token1}"}
        )

        # Login again
        login_response2 = client.post(
            "/api/auth/login",
            json={"email": "relogin@example.com", "password": "securepassword123"}
        )
        access_token2 = login_response2.json()["access_token"]

        # New token should work
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token2}"}
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "relogin@example.com"

    def test_refresh_token_generates_new_valid_tokens(self, client):
        """Token refresh should return new tokens that work"""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"email": "refreshnew@example.com", "password": "securepassword123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"email": "refreshnew@example.com", "password": "securepassword123"}
        )
        tokens = login_response.json()
        original_access = tokens["access_token"]
        original_refresh = tokens["refresh_token"]

        # Refresh tokens
        refresh_response = client.post(
            "/api/auth/refresh",
            json={"refresh_token": original_refresh}
        )
        assert refresh_response.status_code == 200

        new_tokens = refresh_response.json()
        new_access = new_tokens["access_token"]

        # New access token should work
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {new_access}"}
        )
        assert me_response.status_code == 200

        # New token should be different from original
        assert new_access != original_access
