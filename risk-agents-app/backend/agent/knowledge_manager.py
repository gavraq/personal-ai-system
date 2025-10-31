"""
Risk Agents Knowledge Manager
Manages knowledge base access, search, and taxonomy navigation
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import yaml
from dataclasses import dataclass, field


@dataclass
class KnowledgeDocument:
    """Represents a knowledge document in the knowledge base"""
    domain: str
    category: str
    filename: str
    title: str
    content: str
    path: str
    cross_references: List[str]  # [[domain/category/doc.md]] references
    size_bytes: int

    # YAML frontmatter fields (optional)
    metadata: Dict[str, Any] = field(default_factory=dict)
    slug: Optional[str] = None
    description: Optional[str] = None
    artefact_type: Optional[str] = None
    risk_domain: Optional[str] = None
    owner: Optional[str] = None
    approval_date: Optional[str] = None
    version: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    related_artefacts: Dict[str, List[str]] = field(default_factory=dict)
    related_skills: List[str] = field(default_factory=list)
    difficulty: Optional[str] = None
    reading_time: Optional[str] = None


@dataclass
class TaxonomyNode:
    """Represents a node in the knowledge taxonomy"""
    name: str
    type: str  # "domain", "category", or "document"
    path: str
    children: Optional[List['TaxonomyNode']] = None
    document_count: Optional[int] = None


class KnowledgeManager:
    """
    Manages the knowledge base with taxonomy navigation and search capabilities

    The knowledge base is organized as:
    knowledge/
    └── {domain}/           # Domain (e.g., change-agent, market-risk)
        └── {category}/     # Category (e.g., meeting-management)
            └── {doc}.md    # Document
    """

    def __init__(self, knowledge_dir: Path):
        """
        Initialize the Knowledge Manager

        Args:
            knowledge_dir: Path to backend/knowledge directory
        """
        self.knowledge_dir = knowledge_dir

        if not self.knowledge_dir.exists():
            raise ValueError(f"Knowledge directory does not exist: {knowledge_dir}")

    def _parse_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """
        Parse YAML frontmatter from markdown content

        Args:
            content: Full markdown content

        Returns:
            Tuple of (metadata dict, content without frontmatter)
        """
        # Check if content starts with ---
        if not content.startswith('---'):
            return {}, content

        # Find the closing ---
        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content

        try:
            # Parse YAML frontmatter
            frontmatter_text = parts[1].strip()
            metadata = yaml.safe_load(frontmatter_text) or {}

            # Content is everything after the second ---
            content_without_frontmatter = parts[2].strip()

            return metadata, content_without_frontmatter
        except yaml.YAMLError:
            # If YAML parsing fails, return empty metadata
            return {}, content

    def get_taxonomy(self) -> Dict[str, Any]:
        """
        Get the complete knowledge base taxonomy structure

        Returns:
            Dictionary representation of taxonomy tree with:
            - domains: List of domain nodes
            - total_documents: Total document count
            - total_categories: Total category count
        """
        domains = []
        total_documents = 0
        total_categories = 0

        # Iterate through domain directories
        for domain_path in sorted(self.knowledge_dir.iterdir()):
            if not domain_path.is_dir() or domain_path.name.startswith('.'):
                continue

            domain_name = domain_path.name
            categories = []
            domain_doc_count = 0

            # Iterate through category directories
            for category_path in sorted(domain_path.iterdir()):
                if not category_path.is_dir() or category_path.name.startswith('.'):
                    continue

                category_name = category_path.name
                documents = []

                # Iterate through documents
                for doc_path in sorted(category_path.glob("*.md")):
                    documents.append(TaxonomyNode(
                        name=doc_path.stem,
                        type="document",
                        path=f"{domain_name}/{category_name}/{doc_path.name}"
                    ))
                    domain_doc_count += 1
                    total_documents += 1

                if documents:
                    categories.append(TaxonomyNode(
                        name=category_name,
                        type="category",
                        path=f"{domain_name}/{category_name}",
                        children=documents,
                        document_count=len(documents)
                    ))
                    total_categories += 1

            if categories:
                domains.append(TaxonomyNode(
                    name=domain_name,
                    type="domain",
                    path=domain_name,
                    children=categories,
                    document_count=domain_doc_count
                ))

        return {
            "domains": [self._taxonomy_node_to_dict(d) for d in domains],
            "total_documents": total_documents,
            "total_categories": total_categories,
            "total_domains": len(domains)
        }

    def _taxonomy_node_to_dict(self, node: TaxonomyNode) -> Dict[str, Any]:
        """Convert TaxonomyNode to dictionary"""
        result = {
            "name": node.name,
            "type": node.type,
            "path": node.path
        }

        if node.document_count is not None:
            result["document_count"] = node.document_count

        if node.children:
            result["children"] = [self._taxonomy_node_to_dict(child) for child in node.children]

        return result

    def list_domains(self) -> List[Dict[str, Any]]:
        """
        List all domains in the knowledge base

        Returns:
            List of domain information dictionaries
        """
        domains = []

        for domain_path in sorted(self.knowledge_dir.iterdir()):
            if not domain_path.is_dir() or domain_path.name.startswith('.'):
                continue

            # Count categories and documents
            category_count = 0
            document_count = 0

            for category_path in domain_path.iterdir():
                if category_path.is_dir() and not category_path.name.startswith('.'):
                    category_count += 1
                    document_count += len(list(category_path.glob("*.md")))

            domains.append({
                "name": domain_path.name,
                "path": domain_path.name,
                "categories": category_count,
                "documents": document_count
            })

        return domains

    def list_categories(self, domain: str) -> List[Dict[str, Any]]:
        """
        List all categories in a domain

        Args:
            domain: Domain name

        Returns:
            List of category information dictionaries
        """
        domain_path = self.knowledge_dir / domain

        if not domain_path.exists():
            raise ValueError(f"Domain not found: {domain}")

        categories = []

        for category_path in sorted(domain_path.iterdir()):
            if not category_path.is_dir() or category_path.name.startswith('.'):
                continue

            document_count = len(list(category_path.glob("*.md")))

            categories.append({
                "name": category_path.name,
                "path": f"{domain}/{category_path.name}",
                "documents": document_count
            })

        return categories

    def list_documents(self, domain: str, category: str) -> List[Dict[str, Any]]:
        """
        List all documents in a category

        Args:
            domain: Domain name
            category: Category name

        Returns:
            List of document information dictionaries
        """
        category_path = self.knowledge_dir / domain / category

        if not category_path.exists():
            raise ValueError(f"Category not found: {domain}/{category}")

        documents = []

        for doc_path in sorted(category_path.glob("*.md")):
            # Read first line for title (if it's a heading)
            title = doc_path.stem
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('# '):
                        title = first_line[2:].strip()
            except:
                pass

            documents.append({
                "name": doc_path.stem,
                "filename": doc_path.name,
                "title": title,
                "path": f"{domain}/{category}/{doc_path.name}",
                "size_bytes": doc_path.stat().st_size
            })

        return documents

    def get_document(self, domain: str, category: str, document: str) -> KnowledgeDocument:
        """
        Get a specific knowledge document

        Args:
            domain: Domain name
            category: Category name
            document: Document filename (with or without .md extension)

        Returns:
            KnowledgeDocument object with metadata from YAML frontmatter if present
        """
        # Add .md extension if not present
        if not document.endswith('.md'):
            document = f"{document}.md"

        doc_path = self.knowledge_dir / domain / category / document

        if not doc_path.exists():
            raise ValueError(f"Document not found: {domain}/{category}/{document}")

        # Read document content
        with open(doc_path, 'r', encoding='utf-8') as f:
            full_content = f.read()

        # Parse YAML frontmatter
        metadata, content = self._parse_frontmatter(full_content)

        # Extract title - prefer metadata, fallback to first heading, then filename
        title = metadata.get('title', doc_path.stem)
        if not metadata.get('title'):
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()

        # Extract cross-references [[domain/category/doc.md]]
        cross_refs = re.findall(r'\[\[([^\]]+)\]\]', content)

        return KnowledgeDocument(
            domain=domain,
            category=category,
            filename=document,
            title=title,
            content=content,  # Content without frontmatter
            path=f"{domain}/{category}/{document}",
            cross_references=cross_refs,
            size_bytes=doc_path.stat().st_size,
            # YAML frontmatter fields
            metadata=metadata,
            slug=metadata.get('slug'),
            description=metadata.get('description'),
            artefact_type=metadata.get('artefact_type'),
            risk_domain=metadata.get('risk_domain'),
            owner=metadata.get('owner'),
            approval_date=metadata.get('approval_date'),
            version=metadata.get('version'),
            tags=metadata.get('tags', []),
            related_artefacts=metadata.get('related_artefacts', {}),
            related_skills=metadata.get('related_skills', []),
            difficulty=metadata.get('difficulty'),
            reading_time=metadata.get('reading_time')
        )

    def search(
        self,
        query: str,
        domain: Optional[str] = None,
        case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for documents containing the query text

        Args:
            query: Search query string
            domain: Optional domain to limit search to
            case_sensitive: Whether to perform case-sensitive search

        Returns:
            List of search result dictionaries with:
            - domain, category, document, title, path
            - matches: List of matching lines with line numbers
            - match_count: Number of matches found
        """
        results = []
        search_pattern = query if case_sensitive else query.lower()

        # Determine search scope
        search_dirs = []
        if domain:
            domain_path = self.knowledge_dir / domain
            if domain_path.exists():
                search_dirs.append(domain_path)
        else:
            search_dirs = [d for d in self.knowledge_dir.iterdir()
                          if d.is_dir() and not d.name.startswith('.')]

        # Search through all documents
        for domain_path in search_dirs:
            domain_name = domain_path.name

            for category_path in domain_path.iterdir():
                if not category_path.is_dir() or category_path.name.startswith('.'):
                    continue

                category_name = category_path.name

                for doc_path in category_path.glob("*.md"):
                    matches = []
                    match_count = 0

                    with open(doc_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    # Search each line
                    for line_num, line in enumerate(lines, start=1):
                        search_line = line if case_sensitive else line.lower()
                        if search_pattern in search_line:
                            matches.append({
                                "line_number": line_num,
                                "text": line.strip()
                            })
                            match_count += 1

                    # If matches found, add to results
                    if matches:
                        # Get title from first heading
                        title = doc_path.stem
                        title_match = re.search(r'^#\s+(.+)$', ''.join(lines), re.MULTILINE)
                        if title_match:
                            title = title_match.group(1).strip()

                        results.append({
                            "domain": domain_name,
                            "category": category_name,
                            "document": doc_path.name,
                            "title": title,
                            "path": f"{domain_name}/{category_name}/{doc_path.name}",
                            "matches": matches[:10],  # Limit to first 10 matches per doc
                            "match_count": match_count,
                            "total_matches": match_count
                        })

        # Sort by match count (descending)
        results.sort(key=lambda x: x['match_count'], reverse=True)

        return results
