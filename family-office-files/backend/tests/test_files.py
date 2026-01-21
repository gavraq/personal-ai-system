"""
Tests for file management endpoints (feat-14, feat-15, feat-16)
"""
import pytest
from passlib.context import CryptContext

from app.models.user import User
from app.models.deal import Deal, DealMember
from app.models.file import File, FileSource

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def create_test_user(db, email: str, role: str = "admin") -> User:
    """Create a test user"""
    user = User(
        email=email,
        password_hash=get_password_hash("password123"),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_deal(db, user: User, status: str = "active") -> Deal:
    """Create a test deal with user as member"""
    deal = Deal(
        title="Test Deal",
        description="A test deal",
        status=status,
        created_by=user.id
    )
    db.add(deal)
    db.commit()
    db.refresh(deal)

    # Add user as member
    member = DealMember(
        deal_id=deal.id,
        user_id=user.id
    )
    db.add(member)
    db.commit()

    return deal


def login_user(client, email: str, password: str = "password123") -> str:
    """Login and return access token"""
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password}
    )
    return response.json()["access_token"]


class TestLinkDriveFile:
    """Tests for feat-14: Link Drive file to deal"""

    def test_link_drive_file_success(self, client, test_db):
        """Partner can link Drive file to deal"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create user and deal
        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        token = login_user(client, "partner@test.com")

        # Link a Drive file
        response = client.post(
            f"/api/deals/{deal.id}/files/link",
            json={
                "drive_file_id": "1234567890abcdef",
                "name": "Test Document.pdf",
                "mime_type": "application/pdf",
                "size_bytes": 1024
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Document.pdf"
        assert data["mime_type"] == "application/pdf"
        assert data["size_bytes"] == 1024
        assert data["source"] == "drive"
        assert data["source_id"] == "1234567890abcdef"

    def test_link_drive_file_admin_success(self, client, test_db):
        """Admin can link Drive file to deal"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, user)

        token = login_user(client, "admin@test.com")

        response = client.post(
            f"/api/deals/{deal.id}/files/link",
            json={
                "drive_file_id": "abc123",
                "name": "Admin Document.docx",
                "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Admin Document.docx"
        assert data["source"] == "drive"

    def test_link_drive_file_viewer_forbidden(self, client, test_db):
        """Viewer cannot link Drive file (403)"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create admin who owns the deal
        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        # Create viewer
        viewer = create_test_user(db, "viewer@test.com", "viewer")

        # Add viewer to deal
        member = DealMember(deal_id=deal.id, user_id=viewer.id)
        db.add(member)
        db.commit()

        token = login_user(client, "viewer@test.com")

        response = client.post(
            f"/api/deals/{deal.id}/files/link",
            json={
                "drive_file_id": "viewerfile123",
                "name": "Viewer Attempt.pdf"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "Only partners and admins" in response.json()["detail"]

    def test_link_drive_file_duplicate_conflict(self, client, test_db):
        """Linking same Drive file twice returns 409"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        token = login_user(client, "partner@test.com")

        # Link first time
        response1 = client.post(
            f"/api/deals/{deal.id}/files/link",
            json={
                "drive_file_id": "duplicate123",
                "name": "Document.pdf"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response1.status_code == 201

        # Try to link same file again
        response2 = client.post(
            f"/api/deals/{deal.id}/files/link",
            json={
                "drive_file_id": "duplicate123",
                "name": "Document.pdf"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response2.status_code == 409
        assert "already linked" in response2.json()["detail"]

    def test_link_drive_file_closed_deal_forbidden(self, client, test_db):
        """Cannot link files to closed deal"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user, status="closed")

        token = login_user(client, "partner@test.com")

        response = client.post(
            f"/api/deals/{deal.id}/files/link",
            json={
                "drive_file_id": "closedfile123",
                "name": "Closed Deal File.pdf"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "closed deal" in response.json()["detail"]

    def test_link_drive_file_not_member_forbidden(self, client, test_db):
        """Non-member cannot link files"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        # Create deal owner
        owner = create_test_user(db, "owner@test.com", "partner")
        deal = create_test_deal(db, owner)

        # Create another user who is not a member
        other_user = create_test_user(db, "other@test.com", "partner")

        token = login_user(client, "other@test.com")

        response = client.post(
            f"/api/deals/{deal.id}/files/link",
            json={
                "drive_file_id": "otherfile123",
                "name": "Other User File.pdf"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403

    def test_link_drive_file_deal_not_found(self, client, test_db):
        """Linking to nonexistent deal returns 404"""
        from app.core.database import get_db
        import uuid

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "partner@test.com", "partner")
        token = login_user(client, "partner@test.com")

        fake_deal_id = str(uuid.uuid4())
        response = client.post(
            f"/api/deals/{fake_deal_id}/files/link",
            json={
                "drive_file_id": "file123",
                "name": "Document.pdf"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404


class TestListDealFiles:
    """Tests for feat-14/16: List files per deal"""

    def test_list_files_returns_linked_files(self, client, test_db):
        """List returns all linked Drive files"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        # Create some files directly in DB
        file1 = File(
            deal_id=deal.id,
            name="File1.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_1",
            mime_type="application/pdf",
            size_bytes=1000,
            uploaded_by=user.id
        )
        file2 = File(
            deal_id=deal.id,
            name="File2.docx",
            source=FileSource.DRIVE,
            source_id="drive_id_2",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            size_bytes=2000,
            uploaded_by=user.id
        )
        db.add_all([file1, file2])
        db.commit()

        token = login_user(client, "partner@test.com")

        response = client.get(
            f"/api/deals/{deal.id}/files",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["files"]) == 2

        names = [f["name"] for f in data["files"]]
        assert "File1.pdf" in names
        assert "File2.docx" in names

    def test_list_files_filter_by_source(self, client, test_db):
        """Can filter files by source"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        # Create drive and gcs files
        drive_file = File(
            deal_id=deal.id,
            name="DriveFile.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id",
            uploaded_by=user.id
        )
        gcs_file = File(
            deal_id=deal.id,
            name="GCSFile.pdf",
            source=FileSource.GCS,
            source_id="gcs/path/file.pdf",
            uploaded_by=user.id
        )
        db.add_all([drive_file, gcs_file])
        db.commit()

        token = login_user(client, "partner@test.com")

        # Filter by drive
        response = client.get(
            f"/api/deals/{deal.id}/files?source=drive",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["files"][0]["name"] == "DriveFile.pdf"

    def test_list_files_viewer_can_view(self, client, test_db):
        """Viewer can list files (read-only access)"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        # Create viewer and add to deal
        viewer = create_test_user(db, "viewer@test.com", "viewer")
        member = DealMember(deal_id=deal.id, user_id=viewer.id)
        db.add(member)

        # Add a file
        file = File(
            deal_id=deal.id,
            name="ViewableFile.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()

        token = login_user(client, "viewer@test.com")

        response = client.get(
            f"/api/deals/{deal.id}/files",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["files"][0]["name"] == "ViewableFile.pdf"

    def test_list_files_non_member_forbidden(self, client, test_db):
        """Non-member cannot list files"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        owner = create_test_user(db, "owner@test.com", "partner")
        deal = create_test_deal(db, owner)

        other_user = create_test_user(db, "other@test.com", "partner")

        token = login_user(client, "other@test.com")

        response = client.get(
            f"/api/deals/{deal.id}/files",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403


class TestSelectMultipleFiles:
    """Tests for feat-14: Select multiple files"""

    def test_link_multiple_files_sequentially(self, client, test_db):
        """Can link multiple Drive files to same deal"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        token = login_user(client, "partner@test.com")

        # Link multiple files
        files_to_link = [
            {"drive_file_id": "file1", "name": "Document1.pdf"},
            {"drive_file_id": "file2", "name": "Document2.pdf"},
            {"drive_file_id": "file3", "name": "Document3.pdf"},
        ]

        for file_data in files_to_link:
            response = client.post(
                f"/api/deals/{deal.id}/files/link",
                json=file_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 201

        # Verify all files are linked
        list_response = client.get(
            f"/api/deals/{deal.id}/files",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert list_response.status_code == 200
        data = list_response.json()
        assert data["total"] == 3
