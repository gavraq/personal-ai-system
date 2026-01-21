"""
Google Cloud Storage operations for file management
"""
import os
from datetime import timedelta
from typing import Optional, Tuple
from uuid import UUID

from google.cloud import storage
from google.cloud.exceptions import NotFound

from .config import get_settings


class StorageService:
    """Service for Google Cloud Storage operations"""

    # Maximum file size: 100MB
    MAX_FILE_SIZE = 100 * 1024 * 1024

    # Allowed file types (MIME types)
    ALLOWED_MIME_TYPES = {
        # Documents
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain",
        "text/csv",
        # Images
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "image/svg+xml",
        # Archives
        "application/zip",
        "application/x-rar-compressed",
        "application/gzip",
    }

    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[storage.Client] = None

    @property
    def client(self) -> storage.Client:
        """Lazy initialization of GCS client"""
        if self._client is None:
            self._client = storage.Client()
        return self._client

    @property
    def bucket(self) -> storage.Bucket:
        """Get the configured GCS bucket"""
        return self.client.bucket(self.settings.gcs_bucket)

    def validate_file_size(self, size_bytes: int) -> Tuple[bool, Optional[str]]:
        """
        Validate file size against maximum allowed.

        Args:
            size_bytes: File size in bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        if size_bytes > self.MAX_FILE_SIZE:
            max_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File size exceeds maximum allowed ({max_mb:.0f}MB)"
        return True, None

    def validate_mime_type(self, mime_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file MIME type against allowlist.

        Args:
            mime_type: MIME type of the file

        Returns:
            Tuple of (is_valid, error_message)
        """
        if mime_type not in self.ALLOWED_MIME_TYPES:
            return False, f"File type '{mime_type}' is not allowed"
        return True, None

    def get_file_path(self, deal_id: UUID, file_id: UUID, filename: str) -> str:
        """
        Generate GCS path for a file.

        Path format: deals/{deal_id}/{file_id}/{filename}

        Args:
            deal_id: UUID of the deal
            file_id: UUID of the file record
            filename: Original filename

        Returns:
            GCS object path
        """
        # Sanitize filename to prevent path traversal
        safe_filename = os.path.basename(filename)
        return f"deals/{deal_id}/{file_id}/{safe_filename}"

    async def upload_file(
        self,
        deal_id: UUID,
        file_id: UUID,
        filename: str,
        content: bytes,
        mime_type: str
    ) -> str:
        """
        Upload a file to GCS.

        Args:
            deal_id: UUID of the deal
            file_id: UUID of the file record
            filename: Original filename
            content: File content as bytes
            mime_type: MIME type of the file

        Returns:
            GCS path where file was stored
        """
        gcs_path = self.get_file_path(deal_id, file_id, filename)
        blob = self.bucket.blob(gcs_path)
        blob.upload_from_string(content, content_type=mime_type)
        return gcs_path

    def generate_signed_url(
        self,
        gcs_path: str,
        expiration_minutes: int = 60,
        for_download: bool = True
    ) -> str:
        """
        Generate a signed URL for file access.

        Args:
            gcs_path: Path to the file in GCS
            expiration_minutes: URL validity period in minutes
            for_download: If True, sets Content-Disposition for download

        Returns:
            Signed URL for file access
        """
        blob = self.bucket.blob(gcs_path)

        # Set response disposition for download
        response_disposition = None
        if for_download:
            # Extract filename from path
            filename = os.path.basename(gcs_path)
            response_disposition = f'attachment; filename="{filename}"'

        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expiration_minutes),
            method="GET",
            response_disposition=response_disposition
        )
        return url

    def delete_file(self, gcs_path: str) -> bool:
        """
        Delete a file from GCS.

        Args:
            gcs_path: Path to the file in GCS

        Returns:
            True if file was deleted, False if not found
        """
        blob = self.bucket.blob(gcs_path)
        try:
            blob.delete()
            return True
        except NotFound:
            return False

    def file_exists(self, gcs_path: str) -> bool:
        """
        Check if a file exists in GCS.

        Args:
            gcs_path: Path to the file in GCS

        Returns:
            True if file exists
        """
        blob = self.bucket.blob(gcs_path)
        return blob.exists()


# Singleton instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create the storage service singleton"""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
