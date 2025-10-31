"""
Knowledge API Routes
Provides access to the knowledge base with taxonomy navigation and search
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path

from agent import KnowledgeManager
from api.dependencies import get_optional_user
from api.auth import User

router = APIRouter()

# Initialize components (will be set on startup)
knowledge_manager: Optional[KnowledgeManager] = None


def initialize_knowledge_routes(knowledge_dir: Path) -> None:
    """
    Initialize knowledge routes with knowledge directory path

    Args:
        knowledge_dir: Path to backend/knowledge directory
    """
    global knowledge_manager
    knowledge_manager = KnowledgeManager(knowledge_dir=knowledge_dir)


# ==================== Pydantic Models ====================

class TaxonomyResponse(BaseModel):
    """Complete knowledge base taxonomy structure"""
    domains: List[Dict[str, Any]] = Field(description="List of domain nodes with nested structure")
    total_documents: int = Field(description="Total number of documents")
    total_categories: int = Field(description="Total number of categories")
    total_domains: int = Field(description="Total number of domains")

    class Config:
        json_schema_extra = {
            "example": {
                "domains": [
                    {
                        "name": "change-agent",
                        "type": "domain",
                        "path": "change-agent",
                        "document_count": 4,
                        "children": [
                            {
                                "name": "meeting-management",
                                "type": "category",
                                "path": "change-agent/meeting-management",
                                "document_count": 3,
                                "children": [
                                    {"name": "meeting-types", "type": "document", "path": "change-agent/meeting-management/meeting-types.md"}
                                ]
                            }
                        ]
                    }
                ],
                "total_documents": 4,
                "total_categories": 3,
                "total_domains": 1
            }
        }


class DomainInfo(BaseModel):
    """Domain information"""
    name: str = Field(description="Domain name")
    path: str = Field(description="Domain path")
    categories: int = Field(description="Number of categories in domain")
    documents: int = Field(description="Number of documents in domain")


class DomainListResponse(BaseModel):
    """List of domains"""
    domains: List[DomainInfo]
    count: int


class CategoryInfo(BaseModel):
    """Category information"""
    name: str = Field(description="Category name")
    path: str = Field(description="Category path (domain/category)")
    documents: int = Field(description="Number of documents in category")


class CategoryListResponse(BaseModel):
    """List of categories in a domain"""
    domain: str
    categories: List[CategoryInfo]
    count: int


class DocumentInfo(BaseModel):
    """Document metadata"""
    name: str = Field(description="Document name (without extension)")
    filename: str = Field(description="Document filename (with extension)")
    title: str = Field(description="Document title")
    path: str = Field(description="Full document path")
    size_bytes: int = Field(description="File size in bytes")


class DocumentListResponse(BaseModel):
    """List of documents in a category"""
    domain: str
    category: str
    documents: List[DocumentInfo]
    count: int


class DocumentContent(BaseModel):
    """Full document content with YAML frontmatter metadata"""
    domain: str
    category: str
    filename: str
    title: str
    content: str = Field(description="Full markdown content (without frontmatter)")
    path: str
    cross_references: List[str] = Field(description="List of cross-referenced documents")
    size_bytes: int

    # YAML frontmatter fields (optional)
    metadata: Dict[str, Any] = Field(default={}, description="Raw YAML frontmatter metadata")
    slug: Optional[str] = Field(default=None, description="Document slug")
    description: Optional[str] = Field(default=None, description="Document description")
    artefact_type: Optional[str] = Field(default=None, description="Artefact type (policy, framework, methodology, etc.)")
    risk_domain: Optional[str] = Field(default=None, description="Risk domain")
    owner: Optional[str] = Field(default=None, description="Document owner")
    approval_date: Optional[str] = Field(default=None, description="Approval date")
    version: Optional[str] = Field(default=None, description="Document version")
    tags: List[str] = Field(default=[], description="Document tags")
    related_artefacts: Dict[str, List[str]] = Field(default={}, description="Related artefacts by type")
    related_skills: List[str] = Field(default=[], description="Related skills")
    difficulty: Optional[str] = Field(default=None, description="Difficulty level")
    reading_time: Optional[str] = Field(default=None, description="Estimated reading time")


class SearchRequest(BaseModel):
    """Search request parameters"""
    query: str = Field(description="Search query text", min_length=1)
    domain: Optional[str] = Field(default=None, description="Optional domain to limit search")
    case_sensitive: bool = Field(default=False, description="Whether to perform case-sensitive search")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "decision",
                "domain": "change-agent",
                "case_sensitive": False
            }
        }


class SearchMatch(BaseModel):
    """Single search match"""
    line_number: int
    text: str


class SearchResult(BaseModel):
    """Search result for a single document"""
    domain: str
    category: str
    document: str
    title: str
    path: str
    matches: List[SearchMatch] = Field(description="First 10 matching lines")
    match_count: int = Field(description="Total number of matches in document")
    total_matches: int


class SearchResponse(BaseModel):
    """Search results"""
    query: str
    domain: Optional[str]
    case_sensitive: bool
    results: List[SearchResult]
    total_results: int = Field(description="Number of documents with matches")
    total_matches: int = Field(description="Total number of matches across all documents")


class HealthResponse(BaseModel):
    """Knowledge API health check"""
    status: str
    knowledge_base_loaded: bool
    total_domains: int
    total_categories: int
    total_documents: int


# ==================== API Endpoints ====================

@router.get("/taxonomy", response_model=TaxonomyResponse)
async def get_taxonomy(
    current_user: Optional[User] = Depends(get_optional_user)
) -> TaxonomyResponse:
    """
    Get the complete knowledge base taxonomy structure

    Returns a tree structure showing all domains, categories, and documents.
    This endpoint provides a navigable hierarchy of the entire knowledge base.

    **Example Response**:
    ```json
    {
      "domains": [{
        "name": "change-agent",
        "type": "domain",
        "path": "change-agent",
        "document_count": 4,
        "children": [...]
      }],
      "total_documents": 4,
      "total_categories": 3,
      "total_domains": 1
    }
    ```
    """
    try:
        taxonomy = knowledge_manager.get_taxonomy()
        return TaxonomyResponse(**taxonomy)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get taxonomy: {str(e)}")


@router.get("/domains", response_model=DomainListResponse)
async def list_domains(
    current_user: Optional[User] = Depends(get_optional_user)
) -> DomainListResponse:
    """
    List all domains in the knowledge base

    Returns a flat list of domains with metadata (category count, document count).

    **Example Response**:
    ```json
    {
      "domains": [{
        "name": "change-agent",
        "path": "change-agent",
        "categories": 3,
        "documents": 4
      }],
      "count": 1
    }
    ```
    """
    try:
        domains = knowledge_manager.list_domains()
        return DomainListResponse(domains=domains, count=len(domains))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list domains: {str(e)}")


@router.get("/{domain}/categories", response_model=CategoryListResponse)
async def list_categories(
    domain: str,
    current_user: Optional[User] = Depends(get_optional_user)
) -> CategoryListResponse:
    """
    List all categories in a domain

    **Path Parameters**:
    - `domain`: Domain name (e.g., "change-agent")

    **Example Response**:
    ```json
    {
      "domain": "change-agent",
      "categories": [{
        "name": "meeting-management",
        "path": "change-agent/meeting-management",
        "documents": 3
      }],
      "count": 1
    }
    ```
    """
    try:
        categories = knowledge_manager.list_categories(domain=domain)
        return CategoryListResponse(domain=domain, categories=categories, count=len(categories))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list categories: {str(e)}")


@router.get("/{domain}/{category}/documents", response_model=DocumentListResponse)
async def list_documents(
    domain: str,
    category: str,
    current_user: Optional[User] = Depends(get_optional_user)
) -> DocumentListResponse:
    """
    List all documents in a category

    **Path Parameters**:
    - `domain`: Domain name (e.g., "change-agent")
    - `category`: Category name (e.g., "meeting-management")

    **Example Response**:
    ```json
    {
      "domain": "change-agent",
      "category": "meeting-management",
      "documents": [{
        "name": "meeting-types",
        "filename": "meeting-types.md",
        "title": "Meeting Types Knowledge",
        "path": "change-agent/meeting-management/meeting-types.md",
        "size_bytes": 12345
      }],
      "count": 1
    }
    ```
    """
    try:
        documents = knowledge_manager.list_documents(domain=domain, category=category)
        return DocumentListResponse(
            domain=domain,
            category=category,
            documents=documents,
            count=len(documents)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.get("/{domain}/{category}/{document}", response_model=DocumentContent)
async def get_document(
    domain: str,
    category: str,
    document: str,
    current_user: Optional[User] = Depends(get_optional_user)
) -> DocumentContent:
    """
    Get a specific knowledge document

    **Path Parameters**:
    - `domain`: Domain name (e.g., "change-agent")
    - `category`: Category name (e.g., "meeting-management")
    - `document`: Document name (with or without .md extension)

    Returns the full document content including:
    - Full markdown text
    - Cross-references to other documents
    - Document metadata

    **Example Response**:
    ```json
    {
      "domain": "change-agent",
      "category": "meeting-management",
      "filename": "meeting-types.md",
      "title": "Meeting Types Knowledge",
      "content": "# Meeting Types Knowledge\\n\\n## Purpose\\n...",
      "path": "change-agent/meeting-management/meeting-types.md",
      "cross_references": ["action-items-standards.md", "decision-capture.md"],
      "size_bytes": 12345
    }
    ```
    """
    try:
        doc = knowledge_manager.get_document(domain=domain, category=category, document=document)
        return DocumentContent(
            domain=doc.domain,
            category=doc.category,
            filename=doc.filename,
            title=doc.title,
            content=doc.content,
            path=doc.path,
            cross_references=doc.cross_references,
            size_bytes=doc.size_bytes,
            # YAML frontmatter fields
            metadata=doc.metadata,
            slug=doc.slug,
            description=doc.description,
            artefact_type=doc.artefact_type,
            risk_domain=doc.risk_domain,
            owner=doc.owner,
            approval_date=str(doc.approval_date) if doc.approval_date else None,
            version=doc.version,
            tags=doc.tags,
            related_artefacts=doc.related_artefacts,
            related_skills=doc.related_skills,
            difficulty=doc.difficulty,
            reading_time=doc.reading_time
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    request: SearchRequest,
    current_user: Optional[User] = Depends(get_optional_user)
) -> SearchResponse:
    """
    Search the knowledge base for documents containing query text

    **Request Body**:
    ```json
    {
      "query": "decision",
      "domain": "change-agent",  // optional
      "case_sensitive": false
    }
    ```

    **Response**:
    Returns all documents containing the search query, with:
    - First 10 matching lines per document
    - Total match count per document
    - Results sorted by relevance (match count)

    **Example Response**:
    ```json
    {
      "query": "decision",
      "domain": "change-agent",
      "case_sensitive": false,
      "results": [{
        "domain": "change-agent",
        "category": "meeting-management",
        "document": "meeting-types.md",
        "title": "Meeting Types Knowledge",
        "path": "change-agent/meeting-management/meeting-types.md",
        "matches": [
          {"line_number": 8, "text": "### 1. Decision-Making Meeting"},
          {"line_number": 9, "text": "**Purpose**: Make specific decisions..."}
        ],
        "match_count": 15,
        "total_matches": 15
      }],
      "total_results": 3,
      "total_matches": 42
    }
    ```
    """
    try:
        results = knowledge_manager.search(
            query=request.query,
            domain=request.domain,
            case_sensitive=request.case_sensitive
        )

        total_matches = sum(r['total_matches'] for r in results)

        return SearchResponse(
            query=request.query,
            domain=request.domain,
            case_sensitive=request.case_sensitive,
            results=results,
            total_results=len(results),
            total_matches=total_matches
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/health/status", response_model=HealthResponse)
async def knowledge_health() -> HealthResponse:
    """
    Knowledge API health check

    Returns the status of the knowledge API and knowledge base statistics.

    **Example Response**:
    ```json
    {
      "status": "healthy",
      "knowledge_base_loaded": true,
      "total_domains": 1,
      "total_categories": 3,
      "total_documents": 4
    }
    ```
    """
    try:
        taxonomy = knowledge_manager.get_taxonomy()
        return HealthResponse(
            status="healthy",
            knowledge_base_loaded=True,
            total_domains=taxonomy["total_domains"],
            total_categories=taxonomy["total_categories"],
            total_documents=taxonomy["total_documents"]
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            knowledge_base_loaded=False,
            total_domains=0,
            total_categories=0,
            total_documents=0
        )
