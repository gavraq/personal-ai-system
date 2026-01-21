"""
Document Analysis Agent for AI-powered document understanding

This agent provides document analysis capabilities including:
- PDF, DOCX, TXT, and image analysis
- OCR support via Claude vision for scanned documents
- Summary, key points, entities, and recommendations extraction
- Source citations linked to original file
"""
import base64
import io
import logging
from typing import Any, Optional
from uuid import UUID

import httpx
from anthropic import AsyncAnthropic
from sqlalchemy.orm import Session

from .base import BaseAgent
from ..core.config import get_settings
from ..core.storage import get_storage_service
from ..models.agent import AgentType
from ..models.file import File, FileSource

logger = logging.getLogger(__name__)


class DocumentAnalysisOutput:
    """Structure for document analysis output"""

    def __init__(
        self,
        summary: str,
        key_points: list[str],
        entities: list[dict],
        recommendations: list[str],
        source_file_id: str | None = None,
        source_file_name: str | None = None,
    ):
        self.summary = summary
        self.key_points = key_points
        self.entities = entities
        self.recommendations = recommendations
        self.source_file_id = source_file_id
        self.source_file_name = source_file_name

    def to_dict(self) -> dict:
        return {
            "summary": self.summary,
            "key_points": self.key_points,
            "entities": self.entities,
            "recommendations": self.recommendations,
            "source_file_id": self.source_file_id,
            "source_file_name": self.source_file_name,
        }


class DocumentAnalysisAgent(BaseAgent):
    """
    Document Analysis Agent for extracting insights from documents.

    Input: file_id reference to analyze
    Output: summary, key_points, entities, recommendations
    Supports: PDF, DOCX, TXT, images (with OCR via Claude vision)
    """

    SYSTEM_PROMPT = """You are a professional document analyst. Your task is to analyze documents and extract key insights.

Provide your analysis in the following JSON structure:
{
    "summary": "A comprehensive summary of the document (2-3 paragraphs)",
    "key_points": [
        "Key point 1",
        "Key point 2",
        "Key point 3"
    ],
    "entities": [
        {"name": "Entity name", "type": "person/company/date/monetary/location/other", "context": "Brief context"}
    ],
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2"
    ]
}

Important guidelines:
- Provide accurate, factual analysis based on the document content
- Extract all significant entities (people, companies, dates, monetary values, locations)
- Identify at least 3-5 key points from the document
- Provide actionable recommendations based on the document's content
- If the document is unclear or partially readable, note this in the summary
- For financial documents, pay special attention to monetary figures and dates
- For legal documents, highlight key terms and obligations
- For technical documents, focus on specifications and requirements"""

    # Supported MIME types and their handling
    TEXT_MIME_TYPES = {
        "text/plain",
        "text/csv",
        "application/json",
    }

    DOCUMENT_MIME_TYPES = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    IMAGE_MIME_TYPES = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
    }

    @property
    def agent_type(self) -> AgentType:
        return AgentType.DOCUMENT_ANALYSIS

    async def execute(self, input_data: dict) -> dict:
        """
        Execute document analysis using Claude API.

        Args:
            input_data: Dict containing:
                - file_id: UUID of the file to analyze
                - context: Optional additional context

        Returns:
            Dict with summary, key_points, entities, recommendations
        """
        file_id = input_data.get("file_id")
        context = input_data.get("context", {})

        if not file_id:
            raise ValueError("file_id is required for document analysis")

        # Get file record from database
        file_record = self.db.query(File).filter(File.id == file_id).first()
        if not file_record:
            raise ValueError(f"File not found: {file_id}")

        # Get file content based on source type
        file_content, is_image = await self._get_file_content(file_record)

        if not file_content:
            raise ValueError("Failed to retrieve file content")

        # Build the analysis request
        return await self._analyze_document(
            file_content=file_content,
            file_record=file_record,
            is_image=is_image,
            context=context,
        )

    async def _get_file_content(self, file_record: File) -> tuple[bytes | str | None, bool]:
        """
        Retrieve file content based on source type.

        Args:
            file_record: File model record

        Returns:
            Tuple of (content, is_image)
        """
        is_image = file_record.mime_type in self.IMAGE_MIME_TYPES

        if file_record.source == FileSource.GCS:
            return await self._get_gcs_content(file_record), is_image
        elif file_record.source == FileSource.DRIVE:
            return await self._get_drive_content(file_record), is_image
        else:
            raise ValueError(f"Unsupported file source: {file_record.source}")

    async def _get_gcs_content(self, file_record: File) -> bytes | None:
        """
        Download file content from GCS.

        Args:
            file_record: File model with GCS source

        Returns:
            File content as bytes
        """
        storage = get_storage_service()

        if not file_record.source_id:
            raise ValueError("File has no GCS path")

        try:
            # Get the blob directly and download
            blob = storage.bucket.blob(file_record.source_id)
            content = blob.download_as_bytes()
            return content
        except Exception as e:
            logger.error(f"Failed to download file from GCS: {e}")
            raise ValueError(f"Failed to download file from storage: {e}")

    async def _get_drive_content(self, file_record: File) -> bytes | None:
        """
        Download file content from Google Drive.

        Args:
            file_record: File model with Drive source

        Returns:
            File content as bytes
        """
        from ..routers.integrations import get_valid_access_token

        if not file_record.source_id:
            raise ValueError("File has no Drive file ID")

        # Get access token for the file uploader
        access_token = await get_valid_access_token(file_record.uploaded_by, self.db)
        if not access_token:
            raise ValueError("No valid Google access token available")

        try:
            async with httpx.AsyncClient() as client:
                # Download file from Drive
                response = await client.get(
                    f"https://www.googleapis.com/drive/v3/files/{file_record.source_id}?alt=media",
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=60.0,
                )
                if response.status_code != 200:
                    raise ValueError(f"Failed to download from Drive: {response.status_code}")
                return response.content
        except Exception as e:
            logger.error(f"Failed to download file from Drive: {e}")
            raise ValueError(f"Failed to download file from Drive: {e}")

    async def _analyze_document(
        self,
        file_content: bytes,
        file_record: File,
        is_image: bool,
        context: dict,
    ) -> dict:
        """
        Analyze document content using Claude API.

        Args:
            file_content: Raw file content
            file_record: File metadata
            is_image: Whether to use vision API
            context: Additional context

        Returns:
            Structured analysis output
        """
        # Check for API key
        if not self.settings.anthropic_api_key:
            logger.warning("No Anthropic API key configured, using mock response")
            return self._generate_mock_response(file_record)

        try:
            client = AsyncAnthropic(api_key=self.settings.anthropic_api_key)

            # Build message content based on file type
            if is_image or file_record.mime_type == "application/pdf":
                # Use vision API for images and PDFs
                message_content = self._build_vision_content(file_content, file_record)
            else:
                # Extract text for text-based documents
                text_content = self._extract_text_content(file_content, file_record)
                message_content = [
                    {
                        "type": "text",
                        "text": f"Please analyze the following document:\n\n{text_content}",
                    }
                ]

            # Add context if provided
            if context:
                context_str = f"\n\nAdditional context: {context}"
                if isinstance(message_content[-1], dict) and message_content[-1].get("type") == "text":
                    message_content[-1]["text"] += context_str
                else:
                    message_content.append({"type": "text", "text": context_str})

            # Call Claude API
            message = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=self.SYSTEM_PROMPT,
                messages=[{"role": "user", "content": message_content}],
            )

            # Parse the response
            response_text = message.content[0].text
            parsed_output = self._parse_response(response_text, file_record)

            return parsed_output

        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            if "api_key" in str(e).lower() or "authentication" in str(e).lower():
                return self._generate_mock_response(file_record)
            raise

    def _build_vision_content(self, file_content: bytes, file_record: File) -> list[dict]:
        """
        Build vision API content for images and PDFs.

        Args:
            file_content: Raw file bytes
            file_record: File metadata

        Returns:
            List of content blocks for Claude API
        """
        # Encode content as base64
        encoded = base64.standard_b64encode(file_content).decode("utf-8")

        # Determine media type
        media_type = file_record.mime_type
        if media_type == "application/pdf":
            media_type = "application/pdf"

        return [
            {
                "type": "document" if file_record.mime_type == "application/pdf" else "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": encoded,
                },
            },
            {
                "type": "text",
                "text": f"Please analyze this document: {file_record.name}",
            },
        ]

    def _extract_text_content(self, file_content: bytes, file_record: File) -> str:
        """
        Extract text content from document.

        Args:
            file_content: Raw file bytes
            file_record: File metadata

        Returns:
            Extracted text content
        """
        mime_type = file_record.mime_type

        # Plain text files
        if mime_type in self.TEXT_MIME_TYPES:
            return file_content.decode("utf-8", errors="replace")

        # Word documents (basic extraction)
        if mime_type in {
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }:
            try:
                from docx import Document

                doc = Document(io.BytesIO(file_content))
                return "\n".join(para.text for para in doc.paragraphs)
            except ImportError:
                logger.warning("python-docx not installed, treating as binary")
                return f"[Document: {file_record.name} - DOCX extraction requires python-docx]"
            except Exception as e:
                logger.error(f"Failed to extract DOCX content: {e}")
                return f"[Failed to extract content from: {file_record.name}]"

        # Fallback for unsupported types
        return f"[Unsupported document type: {mime_type}]"

    def _parse_response(self, response_text: str, file_record: File) -> dict:
        """
        Parse Claude's response into structured output.

        Args:
            response_text: Raw text response from Claude
            file_record: Source file metadata

        Returns:
            Structured dict with analysis data
        """
        import json
        import re

        # Try to extract JSON from the response
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response_text)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_start = response_text.find("{")
            json_end = response_text.rfind("}")
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start : json_end + 1]
            else:
                # Couldn't find JSON, return text as summary
                return {
                    "summary": response_text[:1000],
                    "key_points": ["See full summary for details"],
                    "entities": [],
                    "recommendations": [],
                    "source_file_id": str(file_record.id),
                    "source_file_name": file_record.name,
                }

        try:
            data = json.loads(json_str)

            output = {
                "summary": data.get("summary", ""),
                "key_points": data.get("key_points", []),
                "entities": data.get("entities", []),
                "recommendations": data.get("recommendations", []),
                "source_file_id": str(file_record.id),
                "source_file_name": file_record.name,
            }

            return output

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from Claude response")
            return {
                "summary": response_text[:1000],
                "key_points": ["See full summary for details"],
                "entities": [],
                "recommendations": [],
                "source_file_id": str(file_record.id),
                "source_file_name": file_record.name,
            }

    def _generate_mock_response(self, file_record: File) -> dict:
        """
        Generate a mock response when API is not available.

        Args:
            file_record: Source file metadata

        Returns:
            Mock structured response
        """
        return {
            "summary": f"Document analysis for: {file_record.name}. This is a mock response - configure ANTHROPIC_API_KEY for real analysis. The document appears to be a {file_record.mime_type} file of approximately {file_record.size_bytes or 'unknown'} bytes.",
            "key_points": [
                "Mock key point 1: Document uploaded successfully",
                "Mock key point 2: Analysis requires API key configuration",
                "Mock key point 3: File metadata captured and linked",
            ],
            "entities": [
                {"name": file_record.name, "type": "document", "context": "Source file"},
                {"name": str(file_record.deal_id), "type": "reference", "context": "Associated deal"},
            ],
            "recommendations": [
                "Configure ANTHROPIC_API_KEY for real document analysis",
                "Review document manually pending API configuration",
            ],
            "source_file_id": str(file_record.id),
            "source_file_name": file_record.name,
        }
