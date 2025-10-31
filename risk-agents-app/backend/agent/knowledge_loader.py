"""
Knowledge Loader

Loads and manages knowledge documents from the /knowledge directory.
Knowledge documents are Markdown files with YAML frontmatter containing:
- Domain-organized content (change-agent, credit-risk, etc.)
- Category-based structure (meeting-management, project-management, etc.)
- Metadata and taxonomy information
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeDocument:
    """Represents a single knowledge document"""

    # Required metadata
    title: str
    domain: str
    category: str
    slug: str
    description: str

    # Content
    content: str  # Markdown content without frontmatter

    # Optional metadata
    tags: List[str] = field(default_factory=list)
    related_skills: List[str] = field(default_factory=list)
    related_documents: List[str] = field(default_factory=list)
    author: Optional[str] = None
    last_updated: Optional[str] = None
    difficulty: Optional[str] = None
    reading_time: Optional[str] = None

    # File information
    file_path: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses"""
        return {
            "metadata": {
                "title": self.title,
                "domain": self.domain,
                "category": self.category,
                "slug": self.slug,
                "description": self.description,
                "tags": self.tags,
                "related_skills": self.related_skills,
                "related_documents": self.related_documents,
                "author": self.author,
                "last_updated": self.last_updated,
                "difficulty": self.difficulty,
                "reading_time": self.reading_time,
            },
            "content": self.content,
            "path": f"{self.domain}/{self.category}/{self.slug}"
        }


class KnowledgeLoader:
    """Loads and manages knowledge documents from file system"""

    def __init__(self, knowledge_dir: Optional[str] = None):
        """
        Initialize knowledge loader

        Args:
            knowledge_dir: Path to knowledge directory (default: backend/knowledge)
        """
        if knowledge_dir is None:
            # Default to backend/knowledge directory
            backend_dir = Path(__file__).parent.parent
            knowledge_dir = str(backend_dir / "knowledge")

        self.knowledge_dir = Path(knowledge_dir)
        self._documents: Dict[str, KnowledgeDocument] = {}
        self._loaded = False

        logger.info(f"Knowledge loader initialized with directory: {self.knowledge_dir}")

    def load_all(self) -> Dict[str, KnowledgeDocument]:
        """
        Load all knowledge documents from the knowledge directory

        Returns:
            Dictionary mapping path (domain/category/slug) to KnowledgeDocument
        """
        self._documents.clear()

        if not self.knowledge_dir.exists():
            logger.warning(f"Knowledge directory does not exist: {self.knowledge_dir}")
            return self._documents

        # Walk through all .md files in knowledge directory
        for md_file in self.knowledge_dir.rglob("*.md"):
            # Skip template file
            if md_file.name == "KNOWLEDGE_TEMPLATE.md":
                continue

            try:
                doc = self._load_document(md_file)
                if doc:
                    path = f"{doc.domain}/{doc.category}/{doc.slug}"
                    self._documents[path] = doc
                    logger.debug(f"Loaded knowledge document: {path}")
            except Exception as e:
                logger.error(f"Error loading knowledge document {md_file}: {e}")

        self._loaded = True
        logger.info(f"Loaded {len(self._documents)} knowledge documents")
        return self._documents

    def _load_document(self, file_path: Path) -> Optional[KnowledgeDocument]:
        """
        Load a single knowledge document from file

        Args:
            file_path: Path to the Markdown file

        Returns:
            KnowledgeDocument or None if parsing fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split frontmatter and content
            if not content.startswith('---'):
                logger.warning(f"Document missing frontmatter: {file_path}")
                return None

            parts = content.split('---', 2)
            if len(parts) < 3:
                logger.warning(f"Invalid frontmatter format: {file_path}")
                return None

            # Parse YAML frontmatter
            frontmatter_str = parts[1]
            markdown_content = parts[2].strip()

            try:
                metadata = yaml.safe_load(frontmatter_str)
            except yaml.YAMLError as e:
                logger.error(f"YAML parsing error in {file_path}: {e}")
                return None

            # Validate required fields
            required_fields = ['title', 'domain', 'category', 'slug', 'description']
            for field in required_fields:
                if field not in metadata:
                    logger.warning(f"Missing required field '{field}' in {file_path}")
                    return None

            # Create KnowledgeDocument
            doc = KnowledgeDocument(
                title=metadata['title'],
                domain=metadata['domain'],
                category=metadata['category'],
                slug=metadata['slug'],
                description=metadata['description'],
                content=markdown_content,
                tags=metadata.get('tags', []),
                related_skills=metadata.get('related_skills', []),
                related_documents=metadata.get('related_documents', []),
                author=metadata.get('author'),
                last_updated=metadata.get('last_updated'),
                difficulty=metadata.get('difficulty'),
                reading_time=metadata.get('reading_time'),
                file_path=str(file_path)
            )

            return doc

        except Exception as e:
            logger.error(f"Unexpected error loading {file_path}: {e}")
            return None

    def get_all(self) -> List[KnowledgeDocument]:
        """
        Get all knowledge documents

        Returns:
            List of all KnowledgeDocument objects
        """
        if not self._loaded:
            self.load_all()
        return list(self._documents.values())

    def get_by_path(self, domain: str, category: str, slug: str) -> Optional[KnowledgeDocument]:
        """
        Get a specific knowledge document by path

        Args:
            domain: Domain (e.g., "change-agent")
            category: Category (e.g., "meeting-management")
            slug: Document slug (e.g., "effective-meetings")

        Returns:
            KnowledgeDocument or None if not found
        """
        if not self._loaded:
            self.load_all()

        path = f"{domain}/{category}/{slug}"
        return self._documents.get(path)

    def get_by_domain(self, domain: str) -> List[KnowledgeDocument]:
        """
        Get all documents in a specific domain

        Args:
            domain: Domain name (e.g., "change-agent")

        Returns:
            List of KnowledgeDocument objects
        """
        if not self._loaded:
            self.load_all()

        return [doc for doc in self._documents.values() if doc.domain == domain]

    def get_by_category(self, domain: str, category: str) -> List[KnowledgeDocument]:
        """
        Get all documents in a specific category within a domain

        Args:
            domain: Domain name
            category: Category name

        Returns:
            List of KnowledgeDocument objects
        """
        if not self._loaded:
            self.load_all()

        return [
            doc for doc in self._documents.values()
            if doc.domain == domain and doc.category == category
        ]

    def get_domains(self) -> List[str]:
        """
        Get list of all available domains

        Returns:
            Sorted list of unique domain names
        """
        if not self._loaded:
            self.load_all()

        domains = set(doc.domain for doc in self._documents.values())
        return sorted(domains)

    def get_categories(self, domain: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get categories, optionally filtered by domain

        Args:
            domain: Optional domain to filter by

        Returns:
            Dictionary mapping domain to list of categories
        """
        if not self._loaded:
            self.load_all()

        categories: Dict[str, List[str]] = {}

        for doc in self._documents.values():
            if domain and doc.domain != domain:
                continue

            if doc.domain not in categories:
                categories[doc.domain] = []

            if doc.category not in categories[doc.domain]:
                categories[doc.domain].append(doc.category)

        # Sort categories within each domain
        for domain_key in categories:
            categories[domain_key] = sorted(categories[domain_key])

        return categories

    def search(self, query: str, domain: Optional[str] = None) -> List[KnowledgeDocument]:
        """
        Search knowledge documents by query string

        Searches in:
        - Title
        - Description
        - Tags
        - Content (case-insensitive)

        Args:
            query: Search query string
            domain: Optional domain to filter by

        Returns:
            List of matching KnowledgeDocument objects
        """
        if not self._loaded:
            self.load_all()

        query_lower = query.lower()
        results = []

        for doc in self._documents.values():
            # Filter by domain if specified
            if domain and doc.domain != domain:
                continue

            # Search in various fields
            if (
                query_lower in doc.title.lower() or
                query_lower in doc.description.lower() or
                any(query_lower in tag.lower() for tag in doc.tags) or
                query_lower in doc.content.lower()
            ):
                results.append(doc)

        return results

    def get_related_to_skill(self, skill_slug: str) -> List[KnowledgeDocument]:
        """
        Get knowledge documents related to a specific skill

        Args:
            skill_slug: Skill slug (e.g., "meeting-minutes-capture")

        Returns:
            List of related KnowledgeDocument objects
        """
        if not self._loaded:
            self.load_all()

        return [
            doc for doc in self._documents.values()
            if skill_slug in doc.related_skills
        ]

    def reload(self) -> Dict[str, KnowledgeDocument]:
        """
        Reload all knowledge documents from file system

        Returns:
            Dictionary of loaded documents
        """
        logger.info("Reloading knowledge documents")
        return self.load_all()


# Global knowledge loader instance
_knowledge_loader: Optional[KnowledgeLoader] = None


def get_knowledge_loader() -> KnowledgeLoader:
    """
    Get the global knowledge loader instance (singleton pattern)

    Returns:
        KnowledgeLoader instance
    """
    global _knowledge_loader
    if _knowledge_loader is None:
        _knowledge_loader = KnowledgeLoader()
        _knowledge_loader.load_all()
    return _knowledge_loader
