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

    def test_list_files_sort_by_date_desc(self, client, test_db):
        """Files are sorted by date descending by default"""
        from app.core.database import get_db
        from datetime import datetime, timedelta

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        # Create files with different timestamps
        file1 = File(
            deal_id=deal.id,
            name="OldFile.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_1",
            uploaded_by=user.id
        )
        db.add(file1)
        db.commit()

        # Add newer file
        file2 = File(
            deal_id=deal.id,
            name="NewFile.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_2",
            uploaded_by=user.id
        )
        db.add(file2)
        db.commit()

        token = login_user(client, "partner@test.com")

        response = client.get(
            f"/api/deals/{deal.id}/files?sort_by=date&sort_order=desc",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        # Newest file should be first
        assert data["files"][0]["name"] == "NewFile.pdf"
        assert data["files"][1]["name"] == "OldFile.pdf"

    def test_list_files_sort_by_name_asc(self, client, test_db):
        """Can sort files by name ascending"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        # Create files with different names
        file1 = File(
            deal_id=deal.id,
            name="Zebra.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_1",
            uploaded_by=user.id
        )
        file2 = File(
            deal_id=deal.id,
            name="Alpha.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_2",
            uploaded_by=user.id
        )
        file3 = File(
            deal_id=deal.id,
            name="Beta.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_3",
            uploaded_by=user.id
        )
        db.add_all([file1, file2, file3])
        db.commit()

        token = login_user(client, "partner@test.com")

        response = client.get(
            f"/api/deals/{deal.id}/files?sort_by=name&sort_order=asc",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        names = [f["name"] for f in data["files"]]
        assert names == ["Alpha.pdf", "Beta.pdf", "Zebra.pdf"]

    def test_list_files_search_by_filename(self, client, test_db):
        """Can search files by filename (case-insensitive)"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        # Create files with different names
        file1 = File(
            deal_id=deal.id,
            name="Contract_Draft.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_1",
            uploaded_by=user.id
        )
        file2 = File(
            deal_id=deal.id,
            name="Financial_Report.xlsx",
            source=FileSource.GCS,
            source_id="gcs/path/file.xlsx",
            uploaded_by=user.id
        )
        file3 = File(
            deal_id=deal.id,
            name="contract_final.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_3",
            uploaded_by=user.id
        )
        db.add_all([file1, file2, file3])
        db.commit()

        token = login_user(client, "partner@test.com")

        # Search for "contract" (case-insensitive)
        response = client.get(
            f"/api/deals/{deal.id}/files?search=contract",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        names = [f["name"] for f in data["files"]]
        assert "Contract_Draft.pdf" in names
        assert "contract_final.pdf" in names
        assert "Financial_Report.xlsx" not in names

    def test_list_files_search_no_results(self, client, test_db):
        """Search returns empty list when no matches"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        file1 = File(
            deal_id=deal.id,
            name="Document.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_1",
            uploaded_by=user.id
        )
        db.add(file1)
        db.commit()

        token = login_user(client, "partner@test.com")

        response = client.get(
            f"/api/deals/{deal.id}/files?search=nonexistent",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["files"] == []

    def test_list_files_combined_filter_sort_search(self, client, test_db):
        """Can combine source filter, sort, and search"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        # Create mixed files
        file1 = File(
            deal_id=deal.id,
            name="Report_2023.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_1",
            uploaded_by=user.id
        )
        file2 = File(
            deal_id=deal.id,
            name="Report_2024.pdf",
            source=FileSource.GCS,
            source_id="gcs/path/file.pdf",
            uploaded_by=user.id
        )
        file3 = File(
            deal_id=deal.id,
            name="Report_2022.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_3",
            uploaded_by=user.id
        )
        file4 = File(
            deal_id=deal.id,
            name="Contract.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_4",
            uploaded_by=user.id
        )
        db.add_all([file1, file2, file3, file4])
        db.commit()

        token = login_user(client, "partner@test.com")

        # Search for "report", filter by drive, sort by name ascending
        response = client.get(
            f"/api/deals/{deal.id}/files?search=report&source=drive&sort_by=name&sort_order=asc",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        names = [f["name"] for f in data["files"]]
        # Should be sorted alphabetically and only include drive files matching "report"
        assert names == ["Report_2022.pdf", "Report_2023.pdf"]


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


class TestUploadFile:
    """Tests for feat-15: Direct file upload to GCS"""

    def test_upload_valid_file_success(self, client, test_db, mocker):
        """Partner can upload valid file"""
        from app.core.database import get_db
        from app.core.storage import StorageService
        from io import BytesIO
        from unittest.mock import AsyncMock

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service with AsyncMock for async methods
        mock_storage = mocker.MagicMock(spec=StorageService)
        mock_storage.validate_file_size.return_value = (True, None)
        mock_storage.validate_mime_type.return_value = (True, None)
        mock_storage.upload_file = AsyncMock(return_value="deals/deal-id/file-id/test.pdf")

        # Override storage dependency
        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        token = login_user(client, "partner@test.com")

        # Create a test file
        file_content = b"test file content"
        response = client.post(
            f"/api/deals/{deal.id}/files/upload",
            files={"file": ("test.pdf", BytesIO(file_content), "application/pdf")},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test.pdf"
        assert data["mime_type"] == "application/pdf"
        assert data["size_bytes"] == len(file_content)
        assert data["source"] == "gcs"

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_upload_oversized_file_returns_413(self, client, test_db, mocker):
        """Upload file exceeding max size returns 413"""
        from app.core.database import get_db
        from app.core.storage import StorageService
        from io import BytesIO

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service to reject file size
        mock_storage = mocker.MagicMock(spec=StorageService)
        mock_storage.validate_file_size.return_value = (False, "File size exceeds maximum allowed (100MB)")
        mock_storage.validate_mime_type.return_value = (True, None)

        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        token = login_user(client, "partner@test.com")

        # Create a test file
        file_content = b"x" * 1000  # Small file, but mock will reject
        response = client.post(
            f"/api/deals/{deal.id}/files/upload",
            files={"file": ("large.pdf", BytesIO(file_content), "application/pdf")},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 413
        assert "exceeds maximum" in response.json()["detail"]

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_upload_invalid_mime_type_returns_415(self, client, test_db, mocker):
        """Upload file with disallowed MIME type returns 415"""
        from app.core.database import get_db
        from app.core.storage import StorageService
        from io import BytesIO

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service to reject MIME type
        mock_storage = mocker.MagicMock(spec=StorageService)
        mock_storage.validate_file_size.return_value = (True, None)
        mock_storage.validate_mime_type.return_value = (False, "File type 'application/x-executable' is not allowed")

        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        token = login_user(client, "partner@test.com")

        # Create a test file
        file_content = b"executable content"
        response = client.post(
            f"/api/deals/{deal.id}/files/upload",
            files={"file": ("malware.exe", BytesIO(file_content), "application/x-executable")},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 415
        assert "not allowed" in response.json()["detail"]

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_upload_viewer_forbidden(self, client, test_db, mocker):
        """Viewer cannot upload files (403)"""
        from app.core.database import get_db
        from app.core.storage import StorageService
        from io import BytesIO

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        viewer = create_test_user(db, "viewer@test.com", "viewer")
        member = DealMember(deal_id=deal.id, user_id=viewer.id)
        db.add(member)
        db.commit()

        token = login_user(client, "viewer@test.com")

        file_content = b"test content"
        response = client.post(
            f"/api/deals/{deal.id}/files/upload",
            files={"file": ("test.pdf", BytesIO(file_content), "application/pdf")},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "Only partners and admins" in response.json()["detail"]

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_upload_to_closed_deal_forbidden(self, client, test_db, mocker):
        """Cannot upload to closed deal"""
        from app.core.database import get_db
        from app.core.storage import StorageService
        from io import BytesIO

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user, status="closed")

        token = login_user(client, "partner@test.com")

        file_content = b"test content"
        response = client.post(
            f"/api/deals/{deal.id}/files/upload",
            files={"file": ("test.pdf", BytesIO(file_content), "application/pdf")},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "closed deal" in response.json()["detail"]

        # Clean up
        del client.app.dependency_overrides[get_storage_service]


class TestDownloadFile:
    """Tests for feat-15: Download file via signed URL"""

    def test_download_gcs_file_returns_signed_url(self, client, test_db, mocker):
        """Download GCS file returns signed URL"""
        from app.core.database import get_db
        from app.core.storage import StorageService

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        mock_storage.generate_signed_url.return_value = "https://storage.googleapis.com/signed-url"

        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        # Create a GCS file
        file = File(
            deal_id=deal.id,
            name="test.pdf",
            source=FileSource.GCS,
            source_id="deals/deal-id/file-id/test.pdf",
            mime_type="application/pdf",
            size_bytes=1024,
            uploaded_by=user.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        token = login_user(client, "partner@test.com")

        response = client.get(
            f"/api/files/{file.id}/download",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "test.pdf"
        assert "https://storage.googleapis.com" in data["download_url"]
        assert data["expires_in_minutes"] == 60

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_download_drive_file_returns_drive_url(self, client, test_db, mocker):
        """Download Drive file returns Google Drive URL"""
        from app.core.database import get_db
        from app.core.storage import StorageService

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service (shouldn't be called for Drive files)
        mock_storage = mocker.MagicMock(spec=StorageService)
        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        user = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, user)

        # Create a Drive file
        file = File(
            deal_id=deal.id,
            name="drive-doc.pdf",
            source=FileSource.DRIVE,
            source_id="abc123def456",
            mime_type="application/pdf",
            size_bytes=2048,
            uploaded_by=user.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        token = login_user(client, "partner@test.com")

        response = client.get(
            f"/api/files/{file.id}/download",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "drive-doc.pdf"
        assert "drive.google.com" in data["download_url"]
        assert "abc123def456" in data["download_url"]
        assert data["expires_in_minutes"] == 0  # Drive URLs don't expire

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_download_file_not_found(self, client, test_db, mocker):
        """Download nonexistent file returns 404"""
        from app.core.database import get_db
        from app.core.storage import StorageService
        import uuid

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        user = create_test_user(db, "partner@test.com", "partner")

        token = login_user(client, "partner@test.com")

        fake_file_id = str(uuid.uuid4())
        response = client.get(
            f"/api/files/{fake_file_id}/download",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_download_file_non_member_forbidden(self, client, test_db, mocker):
        """Non-member cannot download file"""
        from app.core.database import get_db
        from app.core.storage import StorageService

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        owner = create_test_user(db, "owner@test.com", "partner")
        deal = create_test_deal(db, owner)

        # Create a file
        file = File(
            deal_id=deal.id,
            name="secret.pdf",
            source=FileSource.GCS,
            source_id="deals/deal-id/file-id/secret.pdf",
            uploaded_by=owner.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        # Create another user who is not a member
        other_user = create_test_user(db, "other@test.com", "partner")
        token = login_user(client, "other@test.com")

        response = client.get(
            f"/api/files/{file.id}/download",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_download_viewer_can_download(self, client, test_db, mocker):
        """Viewer can download files (read-only access)"""
        from app.core.database import get_db
        from app.core.storage import StorageService

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        mock_storage.generate_signed_url.return_value = "https://storage.googleapis.com/signed-url"

        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        # Create viewer and add to deal
        viewer = create_test_user(db, "viewer@test.com", "viewer")
        member = DealMember(deal_id=deal.id, user_id=viewer.id)
        db.add(member)

        # Create a file
        file = File(
            deal_id=deal.id,
            name="viewable.pdf",
            source=FileSource.GCS,
            source_id="deals/deal-id/file-id/viewable.pdf",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        token = login_user(client, "viewer@test.com")

        response = client.get(
            f"/api/files/{file.id}/download",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "viewable.pdf"

        # Clean up
        del client.app.dependency_overrides[get_storage_service]


class TestDeleteFile:
    """Tests for feat-18: Delete file (admin only)"""

    def test_admin_can_delete_file(self, client, test_db, mocker):
        """Admin can delete a file"""
        from app.core.database import get_db
        from app.core.storage import StorageService

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        mock_storage.delete_file.return_value = True

        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        # Create a file
        file = File(
            deal_id=deal.id,
            name="deleteme.pdf",
            source=FileSource.GCS,
            source_id="deals/deal-id/file-id/deleteme.pdf",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        token = login_user(client, "admin@test.com")

        response = client.delete(
            f"/api/files/{file.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 204

        # Verify file is deleted
        deleted_file = db.query(File).filter(File.id == file.id).first()
        assert deleted_file is None

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_partner_cannot_delete_file(self, client, test_db, mocker):
        """Partner cannot delete a file (403)"""
        from app.core.database import get_db
        from app.core.storage import StorageService

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        partner = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, partner)

        # Create a file
        file = File(
            deal_id=deal.id,
            name="protected.pdf",
            source=FileSource.GCS,
            source_id="deals/deal-id/file-id/protected.pdf",
            uploaded_by=partner.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        token = login_user(client, "partner@test.com")

        response = client.delete(
            f"/api/files/{file.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "Only admins can delete files" in response.json()["detail"]

        # Verify file still exists
        existing_file = db.query(File).filter(File.id == file.id).first()
        assert existing_file is not None

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_viewer_cannot_delete_file(self, client, test_db, mocker):
        """Viewer cannot delete a file (403)"""
        from app.core.database import get_db
        from app.core.storage import StorageService

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        viewer = create_test_user(db, "viewer@test.com", "viewer")
        member = DealMember(deal_id=deal.id, user_id=viewer.id)
        db.add(member)

        # Create a file
        file = File(
            deal_id=deal.id,
            name="restricted.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_123",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        token = login_user(client, "viewer@test.com")

        response = client.delete(
            f"/api/files/{file.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "Only admins can delete files" in response.json()["detail"]

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_delete_file_not_found(self, client, test_db, mocker):
        """Delete nonexistent file returns 404"""
        from app.core.database import get_db
        from app.core.storage import StorageService
        import uuid

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        admin = create_test_user(db, "admin@test.com", "admin")
        token = login_user(client, "admin@test.com")

        fake_file_id = str(uuid.uuid4())
        response = client.delete(
            f"/api/files/{fake_file_id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_delete_file_non_member_forbidden(self, client, test_db, mocker):
        """Non-member cannot delete file even as admin role"""
        from app.core.database import get_db
        from app.core.storage import StorageService

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        # Create a deal owned by one admin
        owner = create_test_user(db, "owner@test.com", "admin")
        deal = create_test_deal(db, owner)

        # Create a file
        file = File(
            deal_id=deal.id,
            name="private.pdf",
            source=FileSource.GCS,
            source_id="deals/deal-id/file-id/private.pdf",
            uploaded_by=owner.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        # Create another admin who is not a member of the deal
        # Note: admins can access any deal by default
        other_admin = create_test_user(db, "other-admin@test.com", "admin")
        token = login_user(client, "other-admin@test.com")

        # This should succeed because admins can access any deal
        response = client.delete(
            f"/api/files/{file.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Admin should be able to delete
        assert response.status_code == 204

        # Clean up
        del client.app.dependency_overrides[get_storage_service]


class TestShareFile:
    """Tests for feat-18: Share file (admin only)"""

    def test_admin_can_share_file(self, client, test_db):
        """Admin can share a file with another user"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        # Create target user to share with
        target_user = create_test_user(db, "target@test.com", "viewer")

        # Create a file
        file = File(
            deal_id=deal.id,
            name="shareable.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_share",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        token = login_user(client, "admin@test.com")

        response = client.post(
            f"/api/files/{file.id}/share",
            json={"user_id": str(target_user.id), "permission": "view"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "File shared successfully"
        assert data["share"]["file_id"] == str(file.id)
        assert data["share"]["shared_with"] == str(target_user.id)
        assert data["share"]["permission"] == "view"

    def test_partner_cannot_share_file(self, client, test_db):
        """Partner cannot share a file (403)"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        partner = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, partner)

        target_user = create_test_user(db, "target@test.com", "viewer")

        file = File(
            deal_id=deal.id,
            name="noshare.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_noshare",
            uploaded_by=partner.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        token = login_user(client, "partner@test.com")

        response = client.post(
            f"/api/files/{file.id}/share",
            json={"user_id": str(target_user.id), "permission": "view"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "Only admins can share files" in response.json()["detail"]

    def test_viewer_cannot_share_file(self, client, test_db):
        """Viewer cannot share a file (403)"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        viewer = create_test_user(db, "viewer@test.com", "viewer")
        member = DealMember(deal_id=deal.id, user_id=viewer.id)
        db.add(member)

        target_user = create_test_user(db, "target@test.com", "partner")

        file = File(
            deal_id=deal.id,
            name="viewonly.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_viewonly",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        token = login_user(client, "viewer@test.com")

        response = client.post(
            f"/api/files/{file.id}/share",
            json={"user_id": str(target_user.id), "permission": "view"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "Only admins can share files" in response.json()["detail"]

    def test_share_file_target_user_not_found(self, client, test_db):
        """Share with nonexistent user returns 404"""
        from app.core.database import get_db
        import uuid

        db = next(client.app.dependency_overrides[get_db]())

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        file = File(
            deal_id=deal.id,
            name="shareable.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_share",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        token = login_user(client, "admin@test.com")

        fake_user_id = str(uuid.uuid4())
        response = client.post(
            f"/api/files/{file.id}/share",
            json={"user_id": fake_user_id, "permission": "view"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
        assert "Target user not found" in response.json()["detail"]

    def test_share_file_updates_existing_permission(self, client, test_db):
        """Sharing with same user updates permission"""
        from app.core.database import get_db
        from app.models.file import FileShare, FilePermission

        db = next(client.app.dependency_overrides[get_db]())

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        target_user = create_test_user(db, "target@test.com", "viewer")

        file = File(
            deal_id=deal.id,
            name="updateshare.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_update",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        # Create initial share with VIEW permission
        share = FileShare(
            file_id=file.id,
            shared_with=target_user.id,
            permission=FilePermission.VIEW
        )
        db.add(share)
        db.commit()

        token = login_user(client, "admin@test.com")

        # Update to EDIT permission
        response = client.post(
            f"/api/files/{file.id}/share",
            json={"user_id": str(target_user.id), "permission": "edit"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["share"]["permission"] == "edit"

        # Verify only one share record exists
        shares = db.query(FileShare).filter(
            FileShare.file_id == file.id,
            FileShare.shared_with == target_user.id
        ).all()
        assert len(shares) == 1
        assert shares[0].permission == FilePermission.EDIT

    def test_share_file_with_download_permission(self, client, test_db):
        """Admin can share a file with download permission"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        target_user = create_test_user(db, "target@test.com", "viewer")

        file = File(
            deal_id=deal.id,
            name="downloadable.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_dl",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        token = login_user(client, "admin@test.com")

        response = client.post(
            f"/api/files/{file.id}/share",
            json={"user_id": str(target_user.id), "permission": "download"},
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["share"]["permission"] == "download"


class TestRevokeFileShare:
    """Tests for feat-21: Revoke file share"""

    def test_admin_can_revoke_file_share(self, client, test_db):
        """Admin can revoke a file share"""
        from app.core.database import get_db
        from app.models.file import FileShare, FilePermission

        db = next(client.app.dependency_overrides[get_db]())

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        target_user = create_test_user(db, "target@test.com", "viewer")

        file = File(
            deal_id=deal.id,
            name="revokable.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_revoke",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        # Create a share
        share = FileShare(
            file_id=file.id,
            shared_with=target_user.id,
            permission=FilePermission.VIEW
        )
        db.add(share)
        db.commit()

        token = login_user(client, "admin@test.com")

        response = client.delete(
            f"/api/files/{file.id}/share/{target_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 204

        # Verify share is deleted
        deleted_share = db.query(FileShare).filter(
            FileShare.file_id == file.id,
            FileShare.shared_with == target_user.id
        ).first()
        assert deleted_share is None

    def test_partner_cannot_revoke_file_share(self, client, test_db):
        """Partner cannot revoke a file share (403)"""
        from app.core.database import get_db
        from app.models.file import FileShare, FilePermission

        db = next(client.app.dependency_overrides[get_db]())

        partner = create_test_user(db, "partner@test.com", "partner")
        deal = create_test_deal(db, partner)

        target_user = create_test_user(db, "target@test.com", "viewer")

        file = File(
            deal_id=deal.id,
            name="norevoke.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_norevoke",
            uploaded_by=partner.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        share = FileShare(
            file_id=file.id,
            shared_with=target_user.id,
            permission=FilePermission.VIEW
        )
        db.add(share)
        db.commit()

        token = login_user(client, "partner@test.com")

        response = client.delete(
            f"/api/files/{file.id}/share/{target_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "Only admins can revoke file shares" in response.json()["detail"]

    def test_revoke_nonexistent_share_returns_404(self, client, test_db):
        """Revoking a nonexistent share returns 404"""
        from app.core.database import get_db
        import uuid

        db = next(client.app.dependency_overrides[get_db]())

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        target_user = create_test_user(db, "target@test.com", "viewer")

        file = File(
            deal_id=deal.id,
            name="noshare.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_noshare",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        token = login_user(client, "admin@test.com")

        response = client.delete(
            f"/api/files/{file.id}/share/{target_user.id}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 404
        assert "File share not found" in response.json()["detail"]


class TestSharedFilesAccess:
    """Tests for feat-21: Shared files access via file_shares"""

    def test_shared_file_grants_download_access(self, client, test_db, mocker):
        """User with download share permission can download the file"""
        from app.core.database import get_db
        from app.core.storage import StorageService
        from app.models.file import FileShare, FilePermission

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        mock_storage.generate_signed_url.return_value = "https://storage.googleapis.com/signed-url"

        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        # Create a user NOT a member of the deal
        external_user = create_test_user(db, "external@test.com", "viewer")

        file = File(
            deal_id=deal.id,
            name="shared.pdf",
            source=FileSource.GCS,
            source_id="deals/deal-id/file-id/shared.pdf",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        # Share file with external user with DOWNLOAD permission
        share = FileShare(
            file_id=file.id,
            shared_with=external_user.id,
            permission=FilePermission.DOWNLOAD
        )
        db.add(share)
        db.commit()

        token = login_user(client, "external@test.com")

        # External user should be able to download
        response = client.get(
            f"/api/files/{file.id}/download",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "shared.pdf"

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_view_share_does_not_grant_download_access(self, client, test_db, mocker):
        """User with VIEW share permission cannot download the file"""
        from app.core.database import get_db
        from app.core.storage import StorageService
        from app.models.file import FileShare, FilePermission

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        # Create a user NOT a member of the deal
        external_user = create_test_user(db, "external@test.com", "viewer")

        file = File(
            deal_id=deal.id,
            name="viewonly.pdf",
            source=FileSource.GCS,
            source_id="deals/deal-id/file-id/viewonly.pdf",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        # Share file with external user with VIEW permission only
        share = FileShare(
            file_id=file.id,
            shared_with=external_user.id,
            permission=FilePermission.VIEW
        )
        db.add(share)
        db.commit()

        token = login_user(client, "external@test.com")

        # External user should NOT be able to download (VIEW only)
        response = client.get(
            f"/api/files/{file.id}/download",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 403
        assert "permission to download" in response.json()["detail"]

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_edit_share_grants_download_access(self, client, test_db, mocker):
        """User with EDIT share permission can download the file"""
        from app.core.database import get_db
        from app.core.storage import StorageService
        from app.models.file import FileShare, FilePermission

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        mock_storage.generate_signed_url.return_value = "https://storage.googleapis.com/signed-url"

        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        external_user = create_test_user(db, "external@test.com", "viewer")

        file = File(
            deal_id=deal.id,
            name="editable.pdf",
            source=FileSource.GCS,
            source_id="deals/deal-id/file-id/editable.pdf",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        # Share file with EDIT permission
        share = FileShare(
            file_id=file.id,
            shared_with=external_user.id,
            permission=FilePermission.EDIT
        )
        db.add(share)
        db.commit()

        token = login_user(client, "external@test.com")

        response = client.get(
            f"/api/files/{file.id}/download",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

        # Clean up
        del client.app.dependency_overrides[get_storage_service]

    def test_revoke_share_removes_access(self, client, test_db, mocker):
        """After revoking share, user can no longer access the file"""
        from app.core.database import get_db
        from app.core.storage import StorageService
        from app.models.file import FileShare, FilePermission

        db = next(client.app.dependency_overrides[get_db]())

        # Mock storage service
        mock_storage = mocker.MagicMock(spec=StorageService)
        mock_storage.generate_signed_url.return_value = "https://storage.googleapis.com/signed-url"

        from app.core.storage import get_storage_service
        client.app.dependency_overrides[get_storage_service] = lambda: mock_storage

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        external_user = create_test_user(db, "external@test.com", "viewer")

        file = File(
            deal_id=deal.id,
            name="revokable.pdf",
            source=FileSource.GCS,
            source_id="deals/deal-id/file-id/revokable.pdf",
            uploaded_by=admin.id
        )
        db.add(file)
        db.commit()
        db.refresh(file)

        # Share file with DOWNLOAD permission
        share = FileShare(
            file_id=file.id,
            shared_with=external_user.id,
            permission=FilePermission.DOWNLOAD
        )
        db.add(share)
        db.commit()

        external_token = login_user(client, "external@test.com")
        admin_token = login_user(client, "admin@test.com")

        # External user can download
        response = client.get(
            f"/api/files/{file.id}/download",
            headers={"Authorization": f"Bearer {external_token}"}
        )
        assert response.status_code == 200

        # Admin revokes the share
        revoke_response = client.delete(
            f"/api/files/{file.id}/share/{external_user.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert revoke_response.status_code == 204

        # External user can no longer download
        response = client.get(
            f"/api/files/{file.id}/download",
            headers={"Authorization": f"Bearer {external_token}"}
        )
        assert response.status_code == 403

        # Clean up
        del client.app.dependency_overrides[get_storage_service]


class TestListSharedFiles:
    """Tests for feat-21: List files shared with current user"""

    def test_list_shared_files_returns_shared_files(self, client, test_db):
        """List shared files returns files shared with current user"""
        from app.core.database import get_db
        from app.models.file import FileShare, FilePermission

        db = next(client.app.dependency_overrides[get_db]())

        admin = create_test_user(db, "admin@test.com", "admin")
        deal = create_test_deal(db, admin)

        recipient = create_test_user(db, "recipient@test.com", "viewer")

        # Create files
        file1 = File(
            deal_id=deal.id,
            name="shared1.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_1",
            uploaded_by=admin.id
        )
        file2 = File(
            deal_id=deal.id,
            name="shared2.pdf",
            source=FileSource.GCS,
            source_id="gcs/path/shared2.pdf",
            uploaded_by=admin.id
        )
        file3 = File(
            deal_id=deal.id,
            name="notshared.pdf",
            source=FileSource.DRIVE,
            source_id="drive_id_3",
            uploaded_by=admin.id
        )
        db.add_all([file1, file2, file3])
        db.commit()
        db.refresh(file1)
        db.refresh(file2)
        db.refresh(file3)

        # Share file1 and file2 with recipient
        share1 = FileShare(
            file_id=file1.id,
            shared_with=recipient.id,
            permission=FilePermission.VIEW
        )
        share2 = FileShare(
            file_id=file2.id,
            shared_with=recipient.id,
            permission=FilePermission.DOWNLOAD
        )
        db.add_all([share1, share2])
        db.commit()

        token = login_user(client, "recipient@test.com")

        response = client.get(
            "/api/files/shared",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

        names = [f["name"] for f in data["files"]]
        assert "shared1.pdf" in names
        assert "shared2.pdf" in names
        assert "notshared.pdf" not in names

        # Check permission is included
        for f in data["files"]:
            if f["name"] == "shared1.pdf":
                assert f["permission"] == "view"
            elif f["name"] == "shared2.pdf":
                assert f["permission"] == "download"

    def test_list_shared_files_empty_when_no_shares(self, client, test_db):
        """List shared files returns empty when user has no shares"""
        from app.core.database import get_db

        db = next(client.app.dependency_overrides[get_db]())

        user = create_test_user(db, "noshares@test.com", "viewer")

        token = login_user(client, "noshares@test.com")

        response = client.get(
            "/api/files/shared",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["files"] == []
