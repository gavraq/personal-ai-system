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


class TestDealOverviewCards:
    """Tests for feat-5: Deal Overview Cards - file_count and sorting"""

    def test_deal_response_includes_file_count(self, client, test_db):
        """Deal response includes file_count field"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin_fc1@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_fc1@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "File Count Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert create_response.status_code == 201
        data = create_response.json()
        assert "file_count" in data
        assert data["file_count"] == 0

    def test_deal_list_sorted_by_last_activity(self, client, test_db):
        """Deal list is sorted by last activity (updated_at, then created_at)"""
        from app.core.database import get_db
        import time

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin_sort@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_sort@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create first deal (older)
        create_response1 = client.post(
            "/api/deals",
            json={"title": "First Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal1_id = create_response1.json()["id"]

        # Small delay to ensure different timestamps
        time.sleep(0.1)

        # Create second deal (newer)
        create_response2 = client.post(
            "/api/deals",
            json={"title": "Second Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal2_id = create_response2.json()["id"]

        # List deals - should show second deal first (most recent)
        list_response = client.get(
            "/api/deals",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert list_response.status_code == 200
        deals = list_response.json()["deals"]
        assert len(deals) >= 2
        # Second deal should be first (most recently created)
        assert deals[0]["id"] == deal2_id

    def test_dashboard_loads_with_deal_cards(self, client, test_db):
        """Dashboard API returns deals with all required fields for cards"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin_dash@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_dash@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        client.post(
            "/api/deals",
            json={"title": "Dashboard Test Deal", "description": "Test description"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # List deals (dashboard uses same endpoint)
        list_response = client.get(
            "/api/deals?page=1&page_size=12",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert list_response.status_code == 200
        data = list_response.json()
        assert "deals" in data
        assert "total" in data
        assert len(data["deals"]) > 0

        # Verify deal card fields
        deal = data["deals"][0]
        assert "id" in deal
        assert "title" in deal
        assert "status" in deal
        assert "file_count" in deal
        assert "created_at" in deal
        assert "updated_at" in deal

    def test_only_assigned_deals_visible_for_viewer(self, client, test_db):
        """Viewer can only see deals they are assigned to (permission filtering)"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_perm@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create viewer
        viewer = User(
            email="viewer_perm@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()
        db.refresh(viewer)

        # Login as admin
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_perm@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        # Create deal (viewer NOT assigned)
        client.post(
            "/api/deals",
            json={"title": "Admin Only Deal"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Login as viewer
        viewer_login = client.post(
            "/api/auth/login",
            json={"email": "viewer_perm@test.com", "password": "password123"}
        )
        viewer_token = viewer_login.json()["access_token"]

        # Viewer lists deals - should not see admin's deal
        list_response = client.get(
            "/api/deals",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert list_response.status_code == 200
        deals = list_response.json()["deals"]
        # Viewer should not see the admin-only deal
        deal_titles = [d["title"] for d in deals]
        assert "Admin Only Deal" not in deal_titles


class TestRoleBasedAccessControl:
    """Tests for feat-19: Role-Based Access Control

    Role hierarchy: Admin > Partner > Viewer
    - Viewers can only read deals they're members of
    - Partners can read/write deals they're members of
    - Admins can do everything
    """

    def test_viewer_cannot_update_deal_returns_403(self, client, test_db):
        """Viewer member cannot update deal - returns 403"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin who creates the deal
        admin = User(
            email="admin_rbac1@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create viewer
        viewer = User(
            email="viewer_rbac1@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()
        db.refresh(viewer)

        # Login as admin and create deal
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_rbac1@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "RBAC Test Deal"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        # Add viewer as member
        client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(viewer.id)},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Login as viewer
        viewer_login = client.post(
            "/api/auth/login",
            json={"email": "viewer_rbac1@test.com", "password": "password123"}
        )
        viewer_token = viewer_login.json()["access_token"]

        # Viewer can READ the deal
        read_response = client.get(
            f"/api/deals/{deal_id}",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert read_response.status_code == 200

        # Viewer CANNOT UPDATE the deal
        update_response = client.put(
            f"/api/deals/{deal_id}",
            json={"title": "Viewer Modified Title"},
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert update_response.status_code == 403
        assert "partner" in update_response.json()["detail"].lower() or "admin" in update_response.json()["detail"].lower()

    def test_viewer_cannot_add_deal_members_returns_403(self, client, test_db):
        """Viewer member cannot add other members - returns 403"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_rbac2@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create viewer (will be added as member)
        viewer = User(
            email="viewer_rbac2@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)

        # Create another user to try to add
        other_user = User(
            email="other_rbac2@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(other_user)
        db.commit()
        db.refresh(viewer)
        db.refresh(other_user)

        # Admin creates deal and adds viewer
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_rbac2@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Member Management Test"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(viewer.id)},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Login as viewer
        viewer_login = client.post(
            "/api/auth/login",
            json={"email": "viewer_rbac2@test.com", "password": "password123"}
        )
        viewer_token = viewer_login.json()["access_token"]

        # Viewer tries to add another member - should fail
        add_response = client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(other_user.id)},
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert add_response.status_code == 403
        assert "partner" in add_response.json()["detail"].lower() or "admin" in add_response.json()["detail"].lower()

    def test_viewer_cannot_remove_deal_members_returns_403(self, client, test_db):
        """Viewer member cannot remove other members - returns 403"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_rbac3@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create viewer
        viewer = User(
            email="viewer_rbac3@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)

        # Create another user (will be added and viewer will try to remove)
        other_user = User(
            email="other_rbac3@test.com",
            password_hash=get_password_hash("password123"),
            role="partner"
        )
        db.add(other_user)
        db.commit()
        db.refresh(viewer)
        db.refresh(other_user)

        # Admin creates deal and adds both users
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_rbac3@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Remove Member Test"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(viewer.id)},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(other_user.id)},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Login as viewer
        viewer_login = client.post(
            "/api/auth/login",
            json={"email": "viewer_rbac3@test.com", "password": "password123"}
        )
        viewer_token = viewer_login.json()["access_token"]

        # Viewer tries to remove another member - should fail
        remove_response = client.delete(
            f"/api/deals/{deal_id}/members/{other_user.id}",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert remove_response.status_code == 403

    def test_partner_can_update_deal(self, client, test_db):
        """Partner member CAN update deal they're a member of"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_rbac4@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create partner
        partner = User(
            email="partner_rbac4@test.com",
            password_hash=get_password_hash("password123"),
            role="partner"
        )
        db.add(partner)
        db.commit()
        db.refresh(partner)

        # Admin creates deal and adds partner
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_rbac4@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Partner Update Test"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(partner.id)},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Login as partner
        partner_login = client.post(
            "/api/auth/login",
            json={"email": "partner_rbac4@test.com", "password": "password123"}
        )
        partner_token = partner_login.json()["access_token"]

        # Partner CAN update the deal
        update_response = client.put(
            f"/api/deals/{deal_id}",
            json={"title": "Partner Modified Title"},
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Partner Modified Title"

    def test_partner_can_manage_deal_members(self, client, test_db):
        """Partner member CAN add/remove members from deal"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_rbac5@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create partner
        partner = User(
            email="partner_rbac5@test.com",
            password_hash=get_password_hash("password123"),
            role="partner"
        )
        db.add(partner)

        # Create viewer to add
        viewer = User(
            email="viewer_rbac5@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()
        db.refresh(partner)
        db.refresh(viewer)

        # Admin creates deal and adds partner
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_rbac5@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Partner Member Test"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(partner.id)},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Login as partner
        partner_login = client.post(
            "/api/auth/login",
            json={"email": "partner_rbac5@test.com", "password": "password123"}
        )
        partner_token = partner_login.json()["access_token"]

        # Partner CAN add a member
        add_response = client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(viewer.id)},
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        assert add_response.status_code == 201

        # Partner CAN remove the member
        remove_response = client.delete(
            f"/api/deals/{deal_id}/members/{viewer.id}",
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        assert remove_response.status_code == 204

    def test_admin_can_access_all_deals(self, client, test_db):
        """Admin can access all deals regardless of membership"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create two admins
        admin1 = User(
            email="admin1_rbac@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin1)

        admin2 = User(
            email="admin2_rbac@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin2)
        db.commit()

        # Admin1 creates deal
        admin1_login = client.post(
            "/api/auth/login",
            json={"email": "admin1_rbac@test.com", "password": "password123"}
        )
        admin1_token = admin1_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Admin1's Deal"},
            headers={"Authorization": f"Bearer {admin1_token}"}
        )
        deal_id = create_response.json()["id"]

        # Admin2 (not a member) CAN access the deal
        admin2_login = client.post(
            "/api/auth/login",
            json={"email": "admin2_rbac@test.com", "password": "password123"}
        )
        admin2_token = admin2_login.json()["access_token"]

        get_response = client.get(
            f"/api/deals/{deal_id}",
            headers={"Authorization": f"Bearer {admin2_token}"}
        )
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Admin1's Deal"

    def test_ui_reflects_role_buttons_hidden_for_viewer(self, client, test_db):
        """API returns user role info so UI can hide buttons appropriately

        While this tests the API (not UI), it verifies that the /auth/me
        endpoint returns role information that the UI can use.
        """
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create viewer
        viewer = User(
            email="viewer_ui@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()

        # Login as viewer
        viewer_login = client.post(
            "/api/auth/login",
            json={"email": "viewer_ui@test.com", "password": "password123"}
        )
        viewer_token = viewer_login.json()["access_token"]

        # Get current user info
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert me_response.status_code == 200
        user_data = me_response.json()
        assert "role" in user_data
        assert user_data["role"] == "viewer"


class TestDealLevelPermissions:
    """Tests for feat-20: Deal-Level Permissions

    Tests for:
    - Unassigned user cannot access deal (403)
    - Admin can access all deals
    - Deal-level role override works (e.g., Partner on one deal, Viewer on another)
    """

    def test_unassigned_user_cannot_access_deal_returns_403(self, client, test_db):
        """Unassigned user (not a deal member) cannot access deal - returns 403"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin who creates the deal
        admin = User(
            email="admin_dlp1@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create partner who is NOT a member of the deal
        unassigned_partner = User(
            email="unassigned_dlp1@test.com",
            password_hash=get_password_hash("password123"),
            role="partner"
        )
        db.add(unassigned_partner)
        db.commit()

        # Admin creates deal
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_dlp1@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Private Deal for DLP Test"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        # Login as unassigned partner
        partner_login = client.post(
            "/api/auth/login",
            json={"email": "unassigned_dlp1@test.com", "password": "password123"}
        )
        partner_token = partner_login.json()["access_token"]

        # Unassigned partner tries to access deal - should get 403
        get_response = client.get(
            f"/api/deals/{deal_id}",
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        assert get_response.status_code == 403
        assert "access" in get_response.json()["detail"].lower()

        # Try to update - should also get 403
        update_response = client.put(
            f"/api/deals/{deal_id}",
            json={"title": "Hacked Title"},
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        assert update_response.status_code == 403

        # Try to list members - should also get 403
        members_response = client.get(
            f"/api/deals/{deal_id}/members",
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        assert members_response.status_code == 403

    def test_admin_can_access_all_deals_regardless_of_membership(self, client, test_db):
        """Admin can access all deals even when not a member"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create partner who creates the deal
        partner = User(
            email="partner_dlp2@test.com",
            password_hash=get_password_hash("password123"),
            role="partner"
        )
        db.add(partner)

        # Create admin who is NOT a member of the deal
        admin = User(
            email="admin_dlp2@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Partner creates deal
        partner_login = client.post(
            "/api/auth/login",
            json={"email": "partner_dlp2@test.com", "password": "password123"}
        )
        partner_token = partner_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Partner's Private Deal"},
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        deal_id = create_response.json()["id"]

        # Login as admin (not a member of this deal)
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_dlp2@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        # Admin CAN access the deal
        get_response = client.get(
            f"/api/deals/{deal_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Partner's Private Deal"

        # Admin CAN update the deal
        update_response = client.put(
            f"/api/deals/{deal_id}",
            json={"title": "Admin Modified Title"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Admin Modified Title"

        # Admin CAN list members
        members_response = client.get(
            f"/api/deals/{deal_id}/members",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert members_response.status_code == 200

        # Admin CAN delete the deal
        delete_response = client.delete(
            f"/api/deals/{deal_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert delete_response.status_code == 204

    def test_deal_level_role_override_works(self, client, test_db):
        """Deal-level role override allows user to have different roles on different deals

        Example: A user is a Partner globally but is added as a Viewer on a specific deal.
        They should only be able to read (not write) on that deal.
        """
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_dlp3@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create partner user (global role is partner)
        partner = User(
            email="partner_dlp3@test.com",
            password_hash=get_password_hash("password123"),
            role="partner"
        )
        db.add(partner)
        db.commit()
        db.refresh(partner)

        # Admin creates two deals
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_dlp3@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        # Deal 1: Partner added with no role override (uses global role)
        create_response1 = client.post(
            "/api/deals",
            json={"title": "Deal 1 - Normal Partner Role"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal1_id = create_response1.json()["id"]

        client.post(
            f"/api/deals/{deal1_id}/members",
            json={"user_id": str(partner.id)},  # No role_override
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Deal 2: Partner added with viewer role override
        create_response2 = client.post(
            "/api/deals",
            json={"title": "Deal 2 - Viewer Override"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal2_id = create_response2.json()["id"]

        client.post(
            f"/api/deals/{deal2_id}/members",
            json={"user_id": str(partner.id), "role_override": "viewer"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Login as partner
        partner_login = client.post(
            "/api/auth/login",
            json={"email": "partner_dlp3@test.com", "password": "password123"}
        )
        partner_token = partner_login.json()["access_token"]

        # On Deal 1: Partner CAN update (uses global partner role)
        update_response1 = client.put(
            f"/api/deals/{deal1_id}",
            json={"title": "Deal 1 - Partner Modified"},
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        assert update_response1.status_code == 200
        assert update_response1.json()["title"] == "Deal 1 - Partner Modified"

        # On Deal 2: Partner CANNOT update (role override is viewer)
        update_response2 = client.put(
            f"/api/deals/{deal2_id}",
            json={"title": "Deal 2 - Should Fail"},
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        assert update_response2.status_code == 403

        # On Deal 2: Partner CAN read (viewer can read)
        read_response2 = client.get(
            f"/api/deals/{deal2_id}",
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        assert read_response2.status_code == 200
        assert read_response2.json()["title"] == "Deal 2 - Viewer Override"

    def test_viewer_with_partner_override_can_write(self, client, test_db):
        """A global Viewer with Partner override on a deal CAN write to that deal"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_dlp4@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create viewer user (global role is viewer)
        viewer = User(
            email="viewer_dlp4@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()
        db.refresh(viewer)

        # Admin creates deal and adds viewer with partner role override
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_dlp4@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Deal with Elevated Viewer"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        # Add viewer with partner role override
        client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(viewer.id), "role_override": "partner"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Login as viewer
        viewer_login = client.post(
            "/api/auth/login",
            json={"email": "viewer_dlp4@test.com", "password": "password123"}
        )
        viewer_token = viewer_login.json()["access_token"]

        # Viewer with partner override CAN update the deal
        update_response = client.put(
            f"/api/deals/{deal_id}",
            json={"title": "Viewer Modified via Override"},
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Viewer Modified via Override"

    def test_unassigned_user_cannot_access_deal_files_returns_403(self, client, test_db):
        """Unassigned user cannot access files for a deal they're not a member of"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin who creates the deal
        admin = User(
            email="admin_dlp5@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create partner who is NOT a member
        unassigned_partner = User(
            email="unassigned_dlp5@test.com",
            password_hash=get_password_hash("password123"),
            role="partner"
        )
        db.add(unassigned_partner)
        db.commit()

        # Admin creates deal
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_dlp5@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Deal with Files Test"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        # Login as unassigned partner
        partner_login = client.post(
            "/api/auth/login",
            json={"email": "unassigned_dlp5@test.com", "password": "password123"}
        )
        partner_token = partner_login.json()["access_token"]

        # Try to list files - should get 403
        files_response = client.get(
            f"/api/deals/{deal_id}/files",
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        assert files_response.status_code == 403

        # Try to link a file - should get 403
        link_response = client.post(
            f"/api/deals/{deal_id}/files/link",
            json={
                "drive_file_id": "fake_drive_id",
                "name": "test.pdf"
            },
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        assert link_response.status_code == 403

    def test_unassigned_user_cannot_access_deal_activity_returns_403(self, client, test_db):
        """Unassigned user cannot access activity for a deal they're not a member of"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin who creates the deal
        admin = User(
            email="admin_dlp6@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create partner who is NOT a member
        unassigned_partner = User(
            email="unassigned_dlp6@test.com",
            password_hash=get_password_hash("password123"),
            role="partner"
        )
        db.add(unassigned_partner)
        db.commit()

        # Admin creates deal
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_dlp6@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        create_response = client.post(
            "/api/deals",
            json={"title": "Deal Activity Test"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        # Login as unassigned partner
        partner_login = client.post(
            "/api/auth/login",
            json={"email": "unassigned_dlp6@test.com", "password": "password123"}
        )
        partner_token = partner_login.json()["access_token"]

        # Try to get deal activity - should get 403
        activity_response = client.get(
            f"/api/activity/deal/{deal_id}",
            headers={"Authorization": f"Bearer {partner_token}"}
        )
        assert activity_response.status_code == 403
