"""
Tests for activity feed endpoints (feat-6: Recent Activity Feed)
"""
import pytest
import time
from passlib.context import CryptContext

from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


class TestActivityFeed:
    """Tests for feat-6: Recent Activity Feed"""

    def test_activity_logged_on_deal_create(self, client, test_db):
        """Activity is logged when a deal is created"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin_act1@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_act1@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Activity Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert create_response.status_code == 201
        deal_id = create_response.json()["id"]

        # Check activity feed
        activity_response = client.get(
            f"/api/activity/deal/{deal_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert activity_response.status_code == 200
        activities = activity_response.json()["activities"]
        assert len(activities) >= 1
        assert any(a["action"] == "deal_create" for a in activities)

    def test_activity_logged_on_file_upload(self, client, test_db):
        """Activity is logged when a file is linked"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin_act2@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_act2@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "File Activity Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Link a file
        link_response = client.post(
            f"/api/deals/{deal_id}/files/link",
            json={
                "drive_file_id": "test-drive-file-id",
                "name": "test-document.pdf"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert link_response.status_code == 201

        # Check activity feed
        activity_response = client.get(
            f"/api/activity/deal/{deal_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert activity_response.status_code == 200
        activities = activity_response.json()["activities"]
        file_link_activities = [a for a in activities if a["action"] == "file_link"]
        assert len(file_link_activities) >= 1
        assert file_link_activities[0]["details"]["file_name"] == "test-document.pdf"

    def test_activity_feed_shows_actor_email(self, client, test_db):
        """Activity feed includes actor email"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin_act3@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_act3@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Actor Email Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Check activity feed
        activity_response = client.get(
            f"/api/activity/deal/{deal_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert activity_response.status_code == 200
        activities = activity_response.json()["activities"]
        assert len(activities) >= 1
        assert activities[0]["actor_email"] == "admin_act3@test.com"

    def test_activity_feed_only_shows_accessible_deals(self, client, test_db):
        """Activity feed only shows activity from accessible deals"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_act4@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create viewer
        viewer = User(
            email="viewer_act4@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()
        db.refresh(viewer)

        # Login as admin and create deal
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_act4@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        # Create deal (viewer NOT assigned)
        create_response = client.post(
            "/api/deals",
            json={"title": "Admin Only Activity Deal"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        deal_id = create_response.json()["id"]

        # Login as viewer
        viewer_login = client.post(
            "/api/auth/login",
            json={"email": "viewer_act4@test.com", "password": "password123"}
        )
        viewer_token = viewer_login.json()["access_token"]

        # Viewer tries to access deal's activity
        activity_response = client.get(
            f"/api/activity/deal/{deal_id}",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )

        assert activity_response.status_code == 403

    def test_activity_feed_pagination(self, client, test_db):
        """Activity feed supports pagination"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin_act5@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_act5@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create multiple deals to generate activities
        for i in range(5):
            client.post(
                "/api/deals",
                json={"title": f"Pagination Test Deal {i}"},
                headers={"Authorization": f"Bearer {token}"}
            )

        # Get first page with small page size
        activity_response = client.get(
            "/api/activity?page=1&page_size=2",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert activity_response.status_code == 200
        data = activity_response.json()
        assert "activities" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert len(data["activities"]) <= 2
        assert data["total"] >= 5  # At least 5 deal_create activities

    def test_activity_includes_relative_timestamp(self, client, test_db):
        """Activity response includes timestamp for relative time display"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin_act6@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_act6@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Timestamp Test Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Check activity feed
        activity_response = client.get(
            f"/api/activity/deal/{deal_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert activity_response.status_code == 200
        activities = activity_response.json()["activities"]
        assert len(activities) >= 1
        assert "created_at" in activities[0]
        # Timestamp should be ISO format
        assert "T" in activities[0]["created_at"]

    def test_activity_logged_on_deal_update(self, client, test_db):
        """Activity is logged when a deal is updated"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())
        admin = User(
            email="admin_act7@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)
        db.commit()

        # Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_act7@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Update Activity Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Update deal status
        client.put(
            f"/api/deals/{deal_id}",
            json={"status": "active"},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Check activity feed
        activity_response = client.get(
            f"/api/activity/deal/{deal_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert activity_response.status_code == 200
        activities = activity_response.json()["activities"]
        update_activities = [a for a in activities if a["action"] == "deal_update"]
        assert len(update_activities) >= 1
        # Check that status change is recorded in details
        assert "changes" in update_activities[0]["details"]
        assert "status" in update_activities[0]["details"]["changes"]

    def test_activity_logged_on_member_add(self, client, test_db):
        """Activity is logged when a member is added"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_act8@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create viewer to add
        viewer = User(
            email="viewer_act8@test.com",
            password_hash=get_password_hash("password123"),
            role="viewer"
        )
        db.add(viewer)
        db.commit()
        db.refresh(viewer)

        # Login as admin
        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin_act8@test.com", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Create deal
        create_response = client.post(
            "/api/deals",
            json={"title": "Member Add Activity Deal"},
            headers={"Authorization": f"Bearer {token}"}
        )
        deal_id = create_response.json()["id"]

        # Add member
        client.post(
            f"/api/deals/{deal_id}/members",
            json={"user_id": str(viewer.id)},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Check activity feed
        activity_response = client.get(
            f"/api/activity/deal/{deal_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert activity_response.status_code == 200
        activities = activity_response.json()["activities"]
        member_add_activities = [a for a in activities if a["action"] == "member_add"]
        assert len(member_add_activities) >= 1
        assert member_add_activities[0]["details"]["user_email"] == "viewer_act8@test.com"

    def test_global_activity_feed_filters_by_accessible_deals(self, client, test_db):
        """Global activity feed only shows activities from accessible deals"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin
        admin = User(
            email="admin_act9@test.com",
            password_hash=get_password_hash("password123"),
            role="admin"
        )
        db.add(admin)

        # Create partner
        partner = User(
            email="partner_act9@test.com",
            password_hash=get_password_hash("password123"),
            role="partner"
        )
        db.add(partner)
        db.commit()

        # Admin creates a deal
        admin_login = client.post(
            "/api/auth/login",
            json={"email": "admin_act9@test.com", "password": "password123"}
        )
        admin_token = admin_login.json()["access_token"]

        client.post(
            "/api/deals",
            json={"title": "Admin Private Deal"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Partner creates their own deal
        partner_login = client.post(
            "/api/auth/login",
            json={"email": "partner_act9@test.com", "password": "password123"}
        )
        partner_token = partner_login.json()["access_token"]

        client.post(
            "/api/deals",
            json={"title": "Partner Deal"},
            headers={"Authorization": f"Bearer {partner_token}"}
        )

        # Partner gets global activity - should only see their own deal's activity
        activity_response = client.get(
            "/api/activity",
            headers={"Authorization": f"Bearer {partner_token}"}
        )

        assert activity_response.status_code == 200
        activities = activity_response.json()["activities"]

        # All activities should be from partner's accessible deals only
        for activity in activities:
            # Partner should not see admin's private deal activities
            assert activity["actor_email"] != "admin_act9@test.com" or activity["actor_email"] == "partner_act9@test.com"
