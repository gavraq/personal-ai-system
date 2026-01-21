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
