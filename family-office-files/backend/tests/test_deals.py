"""
Tests for deal management endpoints (feat-9, feat-10, feat-11, feat-12)
"""
import pytest
from passlib.context import CryptContext

from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


class TestCreateDeal:
    """Tests for feat-9: Create Deal"""

    def test_create_deal_with_valid_data_returns_201(self, client, test_db):
        """Create deal with valid data returns 201"""
        # Create admin user
        from sqlalchemy.orm import Session
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        response = client.post(
            "/api/deals",
            json={"title": "Test Deal", "description": "A test deal"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Deal"
        assert data["description"] == "A test deal"
        assert data["status"] == "draft"
        assert "id" in data
        assert data["created_by"] == str(admin.id)

    def test_create_deal_without_title_returns_422(self, client, test_db):
        """Create deal without title returns 422"""
        # Create admin user
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin2@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin2@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Try to create deal without title
        response = client.post(
            "/api/deals",
            json={"description": "No title deal"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 422
        assert "title" in str(response.json())

    def test_viewer_cannot_create_deal_returns_403(self, client, test_db):
        """Viewer cannot create deal - returns 403"""
        # Create viewer user
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        viewer = User(
            email="viewer@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()

        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={"email": "viewer@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Try to create deal
        response = client.post(
            "/api/deals",
            json={"title": "Viewer Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "admins and partners" in response.json()["detail"].lower()

    def test_partner_can_create_deal(self, client, test_db):
        """Partner can create deal"""
        # Create partner user
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        partner = User(
            email="partner@test.com",
            password_hash=get_password_hash("password123"),
            role="partner"
        )
        db.add(partner)
        db.commit()
        db.refresh(partner)

        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={"email": "partner@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        response = client.post(
            "/api/deals",
            json={"title": "Partner Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        assert response.json()["title"] == "Partner Deal"

    def test_creator_is_auto_assigned_as_member(self, client, test_db):
        """Creator is automatically assigned as deal member"""
        # Create admin user
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin3@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        # Login to get token
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin3@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Auto-member Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Check members
        members_response = client.get(
            f"/api/deals/{deal_id}/members",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert members_response.status_code == 200
        members = members_response.json()["members"]
        assert len(members) == 1
        assert members[0]["user_id"] == str(admin.id)


class TestEditDeal:
    """Tests for feat-10: Edit Deal Metadata"""

    def test_edit_deal_title_persists(self, client, test_db):
        """Edit deal title persists on refresh"""
        # Create admin user and deal
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin4@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin4@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Original Title"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Update title
        update_response = client.put(
            f"/api/deals/{deal_id}",
            json={"title": "Updated Title"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Title"

        # Verify persistence
        get_response = client.get(
            f"/api/deals/{deal_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert get_response.json()["title"] == "Updated Title"

    def test_non_member_cannot_edit_deal_returns_403(self, client, test_db):
        """Non-member cannot edit deal - returns 403"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin who creates the deal
        admin = User(
            email="admin5@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create another user who is not a member
        other_partner = User(
            email="other@test.com",
            password_hash=get_password_hash("password123"),
            role="partner"
        )
        db.add(other_partner)
        db.commit()

        # Login as admin and create deal
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin5@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Admin's Deal"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        # Login as other partner
        partner_login = client.post(
            "/api/auth/login",
            json={"email": "other@test.com", "password": "password123"}
        )
        partner_token = partner_login.json()["access_token"]

        # Try to edit the deal
        response = client.put(
            f"/api/deals/{deal_id}",
            json={"title": "Hacked Title"},
            headers={"Authorization": f"Bearer {partner_token}"}
        )

        assert response.status_code == 403


class TestDealPermissions:
    """Tests for feat-11: Deal Permissions"""

    def test_add_member_grants_deal_access(self, client, test_db):
        """Adding member grants deal access"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin who creates the deal
        admin = User(
            email="admin6@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create viewer to add
        viewer = User(
            email="viewer2@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()
        db.refresh(viewer)

        # Login as admin and create deal
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin6@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Shared Deal"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        # Login as viewer - should not be able to access
        viewer_login = client.post(
            "/api/auth/login",
            json={"email": "viewer2@test.com", "password": "password123"}
        )
        viewer_token = viewer_login.json()["access_token"]

        # Verify no access initially
        initial_access = client.get(
            f"/api/deals/{deal_id}",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert initial_access.status_code == 403

        # Admin adds viewer as member
        add_response = client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(viewer.id)},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert add_response.status_code == 201

        # Viewer should now have access
        final_access = client.get(
            f"/api/deals/{deal_id}",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert final_access.status_code == 200

    def test_remove_member_revokes_access(self, client, test_db):
        """Removing member revokes deal access"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin who creates the deal
        admin = User(
            email="admin7@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create viewer to add/remove
        viewer = User(
            email="viewer3@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()
        db.refresh(viewer)

        # Login as admin and create deal
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin7@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Unshared Deal"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        # Add viewer as member
        client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(viewer.id)},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Login as viewer - should have access
        viewer_login = client.post(
            "/api/auth/login",
            json={"email": "viewer3@test.com", "password": "password123"}
        )
        viewer_token = viewer_login.json()["access_token"]

        # Verify access
        access_check = client.get(
            f"/api/deals/{deal_id}",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert access_check.status_code == 200

        # Remove viewer
        remove_response = client.delete(
            f"/api/deals/{deal_id}/members/{viewer.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert remove_response.status_code == 204

        # Verify access revoked
        revoked_check = client.get(
            f"/api/deals/{deal_id}",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert revoked_check.status_code == 403

    def test_non_member_cannot_access_deal_returns_403(self, client, test_db):
        """Non-member cannot access deal - returns 403"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin who creates the deal
        admin = User(
            email="admin8@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create viewer who is not a member
        viewer = User(
            email="viewer4@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()

        # Login as admin and create deal
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin8@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Private Deal"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        # Login as viewer
        viewer_login = client.post(
            "/api/auth/login",
            json={"email": "viewer4@test.com", "password": "password123"}
        )
        viewer_token = viewer_login.json()["access_token"]

        # Try to access the deal
        response = client.get(
            f"/api/deals/{deal_id}",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert response.status_code == 403


class TestDealStatusWorkflow:
    """Tests for feat-12: Deal Status Workflow"""

    def test_change_status_draft_to_active(self, client, test_db):
        """Change status from Draft to Active"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin9@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin9@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal (starts as draft)
        create_response = client.post(
            "/api/deals",
            json={"title": "Draft Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]
        assert create_response.json()["status"] == "draft"

        # Change to active
        update_response = client.put(
            f"/api/deals/{deal_id}",
            json={"status": "active"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert update_response.status_code == 200
        assert update_response.json()["status"] == "active"

    def test_invalid_status_transition_returns_400(self, client, test_db):
        """Invalid status transition (draft→closed) returns 400"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin10@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin10@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal (starts as draft)
        create_response = client.post(
            "/api/deals",
            json={"title": "Skip Draft Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Try to skip to closed (should fail)
        update_response = client.put(
            f"/api/deals/{deal_id}",
            json={"status": "closed"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert update_response.status_code == 400
        assert "invalid status transition" in update_response.json()["detail"].lower()

    def test_closed_deal_is_read_only(self, client, test_db):
        """Closed deal cannot be edited"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin11@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin11@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "To Be Closed"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Move to active then closed
        client.put(
            f"/api/deals/{deal_id}",
            json={"status": "active"},
            headers={"Authorization": f"Bearer {token}"}
        )
        client.put(
            f"/api/deals/{deal_id}",
            json={"status": "closed"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Try to edit closed deal
        edit_response = client.put(
            f"/api/deals/{deal_id}",
            json={"title": "Modified Title"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert edit_response.status_code == 403
        assert "closed" in edit_response.json()["detail"].lower()
