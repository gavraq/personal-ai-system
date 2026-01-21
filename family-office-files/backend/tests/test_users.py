"""
Tests for user management endpoints (feat-3: Role Assignment)
"""
import pytest
from sqlalchemy import text


class TestRoleAssignment:
    """Tests for PUT /api/users/{user_id}/role"""

    def _create_admin_user(self, client, db_override):
        """Helper to create and authenticate an admin user"""
        # Register user
        response = client.post(
            "/api/auth/register",
            json={"email": "admin@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]

        # Manually set user as admin in database (simulating initial admin setup)
        from app.core.database import get_db
        from app.main import app
        db_gen = db_override()
        db = next(db_gen)
        db.execute(text(f"UPDATE users SET role = 'admin' WHERE id = '{user_id}'"))
        db.commit()
        db_gen.close()

        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "securepassword123"}
        )
        return user_id, login_response.json()["access_token"]

    def _create_partner_user(self, client):
        """Helper to create and authenticate a partner user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "partner@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]

        login_response = client.post(
            "/api/auth/login",
            json={"email": "partner@example.com", "password": "securepassword123"}
        )
        return user_id, login_response.json()["access_token"]

    def _create_viewer_user(self, client):
        """Helper to create a viewer user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "viewer@example.com", "password": "securepassword123"}
        )
        return response.json()["id"]

    def test_admin_can_assign_partner_role(self, client, test_db):
        """Admin can assign Partner role to a user"""
        from tests.conftest import override_get_db

        # Create admin and viewer users
        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        viewer_id = self._create_viewer_user(client)

        # Admin assigns partner role to viewer
        response = client.put(
            f"/api/users/{viewer_id}/role",
            json={"role": "partner"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == viewer_id
        assert data["role"] == "partner"

    def test_admin_can_assign_admin_role(self, client, test_db):
        """Admin can assign Admin role to a user"""
        from tests.conftest import override_get_db

        # Create admin and viewer users
        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        viewer_id = self._create_viewer_user(client)

        # Admin assigns admin role to viewer
        response = client.put(
            f"/api/users/{viewer_id}/role",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == viewer_id
        assert data["role"] == "admin"

    def test_partner_cannot_change_roles(self, client, test_db):
        """Partner cannot change roles (403)"""
        from tests.conftest import override_get_db

        # Create admin and partner users
        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        partner_id, partner_token = self._create_partner_user(client)
        viewer_id = self._create_viewer_user(client)

        # Partner tries to change viewer's role (should fail)
        response = client.put(
            f"/api/users/{viewer_id}/role",
            json={"role": "partner"},
            headers={"Authorization": f"Bearer {partner_token}"}
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_viewer_cannot_change_roles(self, client, test_db):
        """Viewer cannot change roles (403)"""
        from tests.conftest import override_get_db

        # Create admin and viewer users
        admin_id, admin_token = self._create_admin_user(client, override_get_db)

        # Create a second viewer user and get their token
        response = client.post(
            "/api/auth/register",
            json={"email": "viewer2@example.com", "password": "securepassword123"}
        )
        viewer2_id = response.json()["id"]
        login_response = client.post(
            "/api/auth/login",
            json={"email": "viewer2@example.com", "password": "securepassword123"}
        )
        viewer2_token = login_response.json()["access_token"]

        viewer_id = self._create_viewer_user(client)

        # Viewer tries to change another user's role (should fail)
        response = client.put(
            f"/api/users/{viewer_id}/role",
            json={"role": "partner"},
            headers={"Authorization": f"Bearer {viewer2_token}"}
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_role_change_reflects_in_user_permissions(self, client, test_db):
        """Role change reflects in user permissions"""
        from tests.conftest import override_get_db

        # Create admin and viewer users
        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        viewer_id = self._create_viewer_user(client)

        # Get viewer's token
        login_response = client.post(
            "/api/auth/login",
            json={"email": "viewer@example.com", "password": "securepassword123"}
        )
        viewer_token = login_response.json()["access_token"]

        # Viewer cannot access admin endpoint initially
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert response.status_code == 403

        # Admin promotes viewer to admin
        response = client.put(
            f"/api/users/{viewer_id}/role",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

        # Now viewer (now admin) can access admin endpoint
        # Need to get a fresh token since the old one might have cached role
        login_response = client.post(
            "/api/auth/login",
            json={"email": "viewer@example.com", "password": "securepassword123"}
        )
        new_viewer_token = login_response.json()["access_token"]

        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {new_viewer_token}"}
        )
        assert response.status_code == 200

    def test_role_update_for_nonexistent_user_returns_404(self, client, test_db):
        """Role update for non-existent user returns 404"""
        from tests.conftest import override_get_db
        import uuid

        admin_id, admin_token = self._create_admin_user(client, override_get_db)

        # Try to update role for non-existent user
        fake_user_id = str(uuid.uuid4())
        response = client.put(
            f"/api/users/{fake_user_id}/role",
            json={"role": "partner"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_invalid_role_returns_422(self, client, test_db):
        """Invalid role value returns 422"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        viewer_id = self._create_viewer_user(client)

        # Try to assign invalid role
        response = client.put(
            f"/api/users/{viewer_id}/role",
            json={"role": "superuser"},  # Invalid role
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 422


class TestListUsers:
    """Tests for GET /api/users"""

    def _create_admin_user(self, client, db_override):
        """Helper to create and authenticate an admin user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "admin@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]

        from sqlalchemy import text
        db_gen = db_override()
        db = next(db_gen)
        db.execute(text(f"UPDATE users SET role = 'admin' WHERE id = '{user_id}'"))
        db.commit()
        db_gen.close()

        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "securepassword123"}
        )
        return user_id, login_response.json()["access_token"]

    def test_admin_can_list_users(self, client, test_db):
        """Admin can list all users"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)

        # Create some additional users
        client.post(
            "/api/auth/register",
            json={"email": "user1@example.com", "password": "securepassword123"}
        )
        client.post(
            "/api/auth/register",
            json={"email": "user2@example.com", "password": "securepassword123"}
        )

        # List users
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3  # admin + 2 users
        assert len(data["users"]) == 3
        assert data["page"] == 1
        assert data["page_size"] == 20

    def test_list_users_pagination(self, client, test_db):
        """List users supports pagination"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)

        # Create additional users
        for i in range(5):
            client.post(
                "/api/auth/register",
                json={"email": f"user{i}@example.com", "password": "securepassword123"}
            )

        # Get page 1 with page_size=2
        response = client.get(
            "/api/users?page=1&page_size=2",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 6  # admin + 5 users
        assert len(data["users"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2

    def test_non_admin_cannot_list_users(self, client, test_db):
        """Non-admin user cannot list users"""
        # Create a regular user
        client.post(
            "/api/auth/register",
            json={"email": "viewer@example.com", "password": "securepassword123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"email": "viewer@example.com", "password": "securepassword123"}
        )
        viewer_token = login_response.json()["access_token"]

        # Try to list users
        response = client.get(
            "/api/users",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert response.status_code == 403

    def test_list_users_without_auth_returns_403(self, client, test_db):
        """List users without authentication returns 403"""
        response = client.get("/api/users")
        assert response.status_code == 403


class TestGetUser:
    """Tests for GET /api/users/{user_id}"""

    def _create_admin_user(self, client, db_override):
        """Helper to create and authenticate an admin user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "admin@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]

        from sqlalchemy import text
        db_gen = db_override()
        db = next(db_gen)
        db.execute(text(f"UPDATE users SET role = 'admin' WHERE id = '{user_id}'"))
        db.commit()
        db_gen.close()

        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin@example.com", "password": "securepassword123"}
        )
        return user_id, login_response.json()["access_token"]

    def test_admin_can_get_user_by_id(self, client, test_db):
        """Admin can get a specific user by ID"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)

        # Create a user
        response = client.post(
            "/api/auth/register",
            json={"email": "user@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]

        # Get user by ID
        response = client.get(
            f"/api/users/{user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "user@example.com"
        assert data["role"] == "viewer"

    def test_get_nonexistent_user_returns_404(self, client, test_db):
        """Get non-existent user returns 404"""
        from tests.conftest import override_get_db
        import uuid

        admin_id, admin_token = self._create_admin_user(client, override_get_db)

        fake_user_id = str(uuid.uuid4())
        response = client.get(
            f"/api/users/{fake_user_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404
