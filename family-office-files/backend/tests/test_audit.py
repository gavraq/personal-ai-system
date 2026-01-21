"""
Tests for audit log functionality (feat-22: Permission Audit Log)
"""
import pytest
from sqlalchemy import text
from uuid import uuid4


class TestAuditLogEndpoints:
    """Tests for GET /api/audit endpoints (Admin only)"""

    def _create_admin_user(self, client, db_override):
        """Helper to create and authenticate an admin user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "admin@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]

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

    def _create_viewer_user(self, client):
        """Helper to create a viewer user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "viewer@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]
        login_response = client.post(
            "/api/auth/login",
            json={"email": "viewer@example.com", "password": "securepassword123"}
        )
        return user_id, login_response.json()["access_token"]

    def test_admin_can_view_audit_log(self, client, test_db):
        """Admin can access the audit log endpoint"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)

        response = client.get(
            "/api/audit",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    def test_viewer_cannot_view_audit_log(self, client, test_db):
        """Viewer cannot access the audit log (403)"""
        from tests.conftest import override_get_db

        # Create admin first (needed for setup)
        self._create_admin_user(client, override_get_db)
        viewer_id, viewer_token = self._create_viewer_user(client)

        response = client.get(
            "/api/audit",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]

    def test_audit_log_without_auth_returns_403(self, client, test_db):
        """Audit log endpoint without authentication returns 403"""
        response = client.get("/api/audit")
        assert response.status_code == 403


class TestRoleChangeCreatesAuditEntry:
    """Tests that role changes create audit entries"""

    def _create_admin_user(self, client, db_override):
        """Helper to create and authenticate an admin user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "admin@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]

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

    def _create_viewer_user(self, client):
        """Helper to create a viewer user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "viewer@example.com", "password": "securepassword123"}
        )
        return response.json()["id"]

    def test_role_change_creates_audit_entry(self, client, test_db):
        """Role change creates an audit entry"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        viewer_id = self._create_viewer_user(client)

        # Change viewer's role to partner
        response = client.put(
            f"/api/users/{viewer_id}/role",
            json={"role": "partner"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200

        # Check audit log for the role_change entry
        response = client.get(
            "/api/audit?action=role_change",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

        # Find the role_change entry for this user
        role_change_entries = [e for e in data["entries"] if e["action"] == "role_change" and e["entity_id"] == viewer_id]
        assert len(role_change_entries) >= 1

        entry = role_change_entries[0]
        assert entry["actor_id"] == admin_id
        assert entry["entity_type"] == "user"
        assert entry["old_value"]["role"] == "viewer"
        assert entry["new_value"]["role"] == "partner"


class TestMembershipChangesCreateAuditEntries:
    """Tests that deal membership changes create audit entries"""

    def _create_admin_user(self, client, db_override):
        """Helper to create and authenticate an admin user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "admin@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]

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

    def _create_partner_user(self, client, db_override):
        """Helper to create and authenticate a partner user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "partner@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]

        db_gen = db_override()
        db = next(db_gen)
        db.execute(text(f"UPDATE users SET role = 'partner' WHERE id = '{user_id}'"))
        db.commit()
        db_gen.close()

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

    def test_member_add_creates_audit_entry(self, client, test_db):
        """Adding a deal member creates an audit entry"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        viewer_id = self._create_viewer_user(client)

        # Create a deal
        deal_response = client.post(
            "/api/deals",
            json={"title": "Test Deal", "description": "Test"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = deal_response.json()["id"]

        # Add viewer as a member
        response = client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": viewer_id},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201

        # Check audit log for the member_add entry
        response = client.get(
            "/api/audit?action=member_add",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

        # Find the member_add entry
        member_add_entries = [e for e in data["entries"] if e["action"] == "member_add" and e["entity_id"] == deal_id]
        assert len(member_add_entries) >= 1

        entry = member_add_entries[0]
        assert entry["actor_id"] == admin_id
        assert entry["entity_type"] == "deal_member"
        assert entry["new_value"]["user_id"] == viewer_id

    def test_member_remove_creates_audit_entry(self, client, test_db):
        """Removing a deal member creates an audit entry"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        viewer_id = self._create_viewer_user(client)

        # Create a deal
        deal_response = client.post(
            "/api/deals",
            json={"title": "Test Deal", "description": "Test"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = deal_response.json()["id"]

        # Add viewer as a member
        client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": viewer_id},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Remove viewer from deal
        response = client.delete(
            f"/api/deals/{deal_id}/members/{viewer_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204

        # Check audit log for the member_remove entry
        response = client.get(
            "/api/audit?action=member_remove",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

        # Find the member_remove entry
        member_remove_entries = [e for e in data["entries"] if e["action"] == "member_remove" and e["entity_id"] == deal_id]
        assert len(member_remove_entries) >= 1

        entry = member_remove_entries[0]
        assert entry["actor_id"] == admin_id
        assert entry["entity_type"] == "deal_member"
        assert entry["old_value"]["user_id"] == viewer_id


class TestFileSharesCreateAuditEntries:
    """Tests that file share operations create audit entries"""

    def _create_admin_user(self, client, db_override):
        """Helper to create and authenticate an admin user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "admin@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]

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

    def _create_viewer_user(self, client):
        """Helper to create a viewer user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "viewer@example.com", "password": "securepassword123"}
        )
        return response.json()["id"]

    def _create_deal_with_file(self, client, admin_token, db_override):
        """Helper to create a deal with a linked file"""
        # Create a deal
        deal_response = client.post(
            "/api/deals",
            json={"title": "Test Deal", "description": "Test"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = deal_response.json()["id"]

        # Link a Google Drive file
        file_response = client.post(
            "/api/files/link",
            json={
                "deal_id": deal_id,
                "drive_file_id": "test-drive-file-id-123",
                "name": "Test Document.pdf",
                "mime_type": "application/pdf",
                "web_view_link": "https://drive.google.com/file/d/test/view",
                "web_content_link": "https://drive.google.com/uc?id=test"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        if file_response.status_code != 201:
            # Fall back to creating file directly in database
            from tests.conftest import override_get_db
            from app.models.file import File, FileSource

            db_gen = db_override()
            db = next(db_gen)

            file = File(
                name="Test Document.pdf",
                deal_id=deal_id,
                source=FileSource.GOOGLE_DRIVE,
                google_drive_file_id="test-drive-file-id-123",
                mime_type="application/pdf"
            )
            db.add(file)
            db.commit()
            file_id = str(file.id)
            db_gen.close()
            return deal_id, file_id

        return deal_id, file_response.json()["id"]

    def test_file_share_creates_audit_entry(self, client, test_db):
        """Sharing a file creates an audit entry"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        viewer_id = self._create_viewer_user(client)

        # Create deal with file
        deal_id, file_id = self._create_deal_with_file(client, admin_token, override_get_db)

        # Share file with viewer
        response = client.post(
            f"/api/files/{file_id}/share",
            json={"user_id": viewer_id, "permission": "view"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201

        # Check audit log for the file_share entry
        response = client.get(
            "/api/audit?action=file_share",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

        # Find the file_share entry
        file_share_entries = [e for e in data["entries"] if e["action"] == "file_share" and e["entity_id"] == file_id]
        assert len(file_share_entries) >= 1

        entry = file_share_entries[0]
        assert entry["actor_id"] == admin_id
        assert entry["entity_type"] == "file_share"
        assert entry["new_value"]["shared_with_user_id"] == viewer_id
        assert entry["new_value"]["permission"] == "view"

    def test_file_unshare_creates_audit_entry(self, client, test_db):
        """Revoking a file share creates an audit entry"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        viewer_id = self._create_viewer_user(client)

        # Create deal with file
        deal_id, file_id = self._create_deal_with_file(client, admin_token, override_get_db)

        # Share file with viewer
        client.post(
            f"/api/files/{file_id}/share",
            json={"user_id": viewer_id, "permission": "view"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Revoke the share
        response = client.delete(
            f"/api/files/{file_id}/share/{viewer_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 204

        # Check audit log for the file_unshare entry
        response = client.get(
            "/api/audit?action=file_unshare",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

        # Find the file_unshare entry
        file_unshare_entries = [e for e in data["entries"] if e["action"] == "file_unshare" and e["entity_id"] == file_id]
        assert len(file_unshare_entries) >= 1

        entry = file_unshare_entries[0]
        assert entry["actor_id"] == admin_id
        assert entry["entity_type"] == "file_share"
        assert entry["old_value"]["shared_with_user_id"] == viewer_id


class TestAuditLogFiltering:
    """Tests for audit log filtering functionality"""

    def _create_admin_user(self, client, db_override):
        """Helper to create and authenticate an admin user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "admin@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]

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

    def _create_viewer_user(self, client):
        """Helper to create a viewer user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "viewer@example.com", "password": "securepassword123"}
        )
        return response.json()["id"]

    def test_filter_by_action_type(self, client, test_db):
        """Can filter audit entries by action type"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        viewer_id = self._create_viewer_user(client)

        # Create a role_change entry
        client.put(
            f"/api/users/{viewer_id}/role",
            json={"role": "partner"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Filter by role_change
        response = client.get(
            "/api/audit?action=role_change",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        for entry in data["entries"]:
            assert entry["action"] == "role_change"

    def test_filter_by_entity_type(self, client, test_db):
        """Can filter audit entries by entity type"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        viewer_id = self._create_viewer_user(client)

        # Create a role_change entry (entity_type = user)
        client.put(
            f"/api/users/{viewer_id}/role",
            json={"role": "partner"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Filter by entity_type=user
        response = client.get(
            "/api/audit?entity_type=user",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        for entry in data["entries"]:
            assert entry["entity_type"] == "user"

    def test_filter_by_actor_id(self, client, test_db):
        """Can filter audit entries by actor ID"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)
        viewer_id = self._create_viewer_user(client)

        # Create a role_change entry
        client.put(
            f"/api/users/{viewer_id}/role",
            json={"role": "partner"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Filter by actor_id
        response = client.get(
            f"/api/audit?actor_id={admin_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        for entry in data["entries"]:
            assert entry["actor_id"] == admin_id

    def test_pagination_works(self, client, test_db):
        """Audit log pagination works correctly"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)

        # Create multiple viewers and change their roles to create audit entries
        for i in range(5):
            response = client.post(
                "/api/auth/register",
                json={"email": f"viewer{i}@example.com", "password": "securepassword123"}
            )
            viewer_id = response.json()["id"]
            client.put(
                f"/api/users/{viewer_id}/role",
                json={"role": "partner"},
                headers={"Authorization": f"Bearer {admin_token}"}
            )

        # Get first page with page_size=2
        response = client.get(
            "/api/audit?page=1&page_size=2",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["entries"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total"] >= 5


class TestAuditEntriesAreImmutable:
    """Tests that audit entries cannot be modified"""

    def _create_admin_user(self, client, db_override):
        """Helper to create and authenticate an admin user"""
        response = client.post(
            "/api/auth/register",
            json={"email": "admin@example.com", "password": "securepassword123"}
        )
        user_id = response.json()["id"]

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

    def test_no_update_endpoint_exists(self, client, test_db):
        """No PUT/PATCH endpoint exists for audit entries"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)

        # Try to update an audit entry (should return 405 Method Not Allowed)
        fake_entry_id = str(uuid4())
        response = client.put(
            f"/api/audit/{fake_entry_id}",
            json={"action": "modified"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 405

    def test_no_delete_endpoint_exists(self, client, test_db):
        """No DELETE endpoint exists for audit entries"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)

        # Try to delete an audit entry (should return 405 Method Not Allowed)
        fake_entry_id = str(uuid4())
        response = client.delete(
            f"/api/audit/{fake_entry_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 405

    def test_get_single_entry_works(self, client, test_db):
        """Can get a single audit entry by ID (read-only)"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)

        # Create a viewer and change role to create an audit entry
        response = client.post(
            "/api/auth/register",
            json={"email": "viewer@example.com", "password": "securepassword123"}
        )
        viewer_id = response.json()["id"]
        client.put(
            f"/api/users/{viewer_id}/role",
            json={"role": "partner"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Get the audit entry
        list_response = client.get(
            "/api/audit?action=role_change",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        entry_id = list_response.json()["entries"][0]["id"]

        # Get single entry
        response = client.get(
            f"/api/audit/{entry_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == entry_id
        assert data["action"] == "role_change"

    def test_get_nonexistent_entry_returns_404(self, client, test_db):
        """Getting a nonexistent audit entry returns 404"""
        from tests.conftest import override_get_db

        admin_id, admin_token = self._create_admin_user(client, override_get_db)

        fake_entry_id = str(uuid4())
        response = client.get(
            f"/api/audit/{fake_entry_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404
