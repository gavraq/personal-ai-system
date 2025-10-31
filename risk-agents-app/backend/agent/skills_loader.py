"""
Skills Loader with Progressive Disclosure
Loads skills using the Skills Framework pattern with lazy loading

Supports both:
1. Standard Claude structure: .claude/skills/skill-name/ with reference.md, examples.md
2. Enhanced structure: .claude/skills/domain/skill-name/ with instructions/, resources/

This hybrid approach provides backward compatibility with Claude's standard
while enabling better organization for large skill collections (100+ skills).
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
import yaml


@dataclass
class SkillMetadata:
    """
    Skill metadata extracted from YAML frontmatter in SKILL.md

    This is the first level of progressive disclosure - lightweight metadata
    that can be loaded quickly for browsing and filtering skills.

    Supports both standard Claude fields (name, description) and enhanced
    fields (domain, category, taxonomy) for better organization.
    """
    name: str                      # Required: skill identifier
    description: str               # Required: what the skill does and when to use it
    domain: str                    # Enhanced: organizational domain (optional in standard Claude)
    category: str                  # Enhanced: skill category (optional in standard Claude)
    taxonomy: str                  # Enhanced: full taxonomy path (optional in standard Claude)
    parameters: List[str]          # Enhanced: expected inputs (optional in standard Claude)
    output_format: str             # Enhanced: expected output format (optional in standard Claude)
    estimated_duration: str        # Enhanced: execution time estimate (optional in standard Claude)
    skill_path: Path              # Full path to skill directory
    is_flat_structure: bool = False  # True if using flat Claude structure, False if nested

    def __repr__(self) -> str:
        if self.is_flat_structure:
            return f"<Skill: {self.name}>"
        return f"<Skill: {self.domain}/{self.name}>"


class SkillsLoader:
    """
    Progressive Disclosure Skill Loader

    This class implements the Skills Framework pattern where skills are loaded
    incrementally:
    1. Metadata only (fast, for browsing)
    2. Instructions (on demand, when executing)
    3. Resources (on demand, when needed)
    4. Code helpers (on demand, if available)

    This pattern keeps memory usage low and loading fast while maintaining
    flexibility to load detailed information when needed.
    """

    def __init__(self, skills_dir: Path):
        """
        Initialize the Skills Loader

        Args:
            skills_dir: Path to .claude/skills directory
        """
        self.skills_dir = skills_dir
        self._skill_cache: Dict[str, SkillMetadata] = {}

    def load_skill_metadata(self, skill_path: str) -> SkillMetadata:
        """
        Load only YAML frontmatter from SKILL.md (Progressive disclosure step 1)

        This is fast and lightweight - perfect for browsing skills or building
        a skills registry.

        Supports both:
        - Nested structure: "domain/skill-name" (e.g., "change-agent/meeting-minutes")
        - Flat structure: "skill-name" (e.g., "meeting-minutes")

        Args:
            skill_path: Skill path (nested: "domain/skill-name" or flat: "skill-name")

        Returns:
            SkillMetadata object with basic skill information

        Raises:
            FileNotFoundError: If SKILL.md doesn't exist
            ValueError: If YAML frontmatter is invalid
        """
        # Check cache first
        if skill_path in self._skill_cache:
            return self._skill_cache[skill_path]

        # Build path to SKILL.md
        full_path = self.skills_dir / skill_path / "SKILL.md"

        if not full_path.exists():
            raise FileNotFoundError(f"Skill file not found: {full_path}")

        # Read and parse YAML frontmatter
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract YAML frontmatter (between --- markers)
        if not content.startswith('---'):
            raise ValueError(f"SKILL.md must start with YAML frontmatter: {skill_path}")

        parts = content.split('---', 2)
        if len(parts) < 3:
            raise ValueError(f"Invalid YAML frontmatter format: {skill_path}")

        yaml_content = parts[1].strip()
        metadata_dict = yaml.safe_load(yaml_content)

        # Detect structure type (flat vs nested)
        is_flat = '/' not in skill_path

        # Extract domain from skill_path if nested, or use metadata if available
        if is_flat:
            domain = metadata_dict.get('domain', 'general')
        else:
            domain = skill_path.split('/')[0]

        # Create SkillMetadata object
        # For flat structure, we use defaults for enhanced fields if not in YAML
        metadata = SkillMetadata(
            name=metadata_dict['name'],
            description=metadata_dict['description'],
            domain=domain,
            category=metadata_dict.get('category', 'general'),
            taxonomy=metadata_dict.get('taxonomy', f"{domain}/{metadata_dict.get('category', 'general')}"),
            parameters=metadata_dict.get('parameters', []),
            output_format=metadata_dict.get('output_format', 'markdown'),
            estimated_duration=metadata_dict.get('estimated_duration', 'varies'),
            skill_path=self.skills_dir / skill_path,
            is_flat_structure=is_flat
        )

        # Cache it
        self._skill_cache[skill_path] = metadata

        return metadata

    def load_skill_content(self, skill_path: str) -> str:
        """
        Load the full SKILL.md content (including markdown description)

        This loads more information than just metadata - the full skill description
        and documentation from the SKILL.md file.

        Args:
            skill_path: Skill path in format "domain/skill-name"

        Returns:
            Full markdown content from SKILL.md (excluding YAML frontmatter)
        """
        full_path = self.skills_dir / skill_path / "SKILL.md"

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract markdown content (after YAML frontmatter)
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return parts[2].strip()

        return content

    def load_skill_instructions(self, skill_path: str, instruction_file: str = "reference.md") -> str:
        """
        Load specific instruction file (Progressive disclosure step 2)

        Instructions are loaded on-demand when a skill is about to be executed.
        This keeps initial loading fast while providing detailed guidance when needed.

        Supports both:
        - Enhanced structure: instructions/capture.md, instructions/extract-actions.md
        - Standard Claude: reference.md (root level)

        Args:
            skill_path: Skill path (nested: "domain/skill-name" or flat: "skill-name")
            instruction_file: Name of instruction file (default: "reference.md")
                            For enhanced structure: "capture.md", "extract-actions.md"
                            For standard Claude: "reference.md"

        Returns:
            Content of the instruction file

        Raises:
            FileNotFoundError: If instruction file doesn't exist
        """
        skill_dir = self.skills_dir / skill_path

        # Try enhanced structure first (instructions/ directory)
        instruction_path = skill_dir / "instructions" / instruction_file
        if instruction_path.exists():
            with open(instruction_path, 'r', encoding='utf-8') as f:
                return f.read()

        # Try standard Claude structure (root level reference.md)
        root_instruction_path = skill_dir / instruction_file
        if root_instruction_path.exists():
            with open(root_instruction_path, 'r', encoding='utf-8') as f:
                return f.read()

        raise FileNotFoundError(
            f"Instruction file not found: tried {instruction_path} and {root_instruction_path}"
        )

    def list_skill_instructions(self, skill_path: str) -> List[str]:
        """
        List available instruction files for a skill

        Supports both:
        - Enhanced structure: instructions/ directory with multiple .md files
        - Standard Claude: reference.md at root level

        Args:
            skill_path: Skill path (nested: "domain/skill-name" or flat: "skill-name")

        Returns:
            List of instruction filenames
        """
        skill_dir = self.skills_dir / skill_path
        instruction_files = []

        # Check enhanced structure (instructions/ directory)
        instructions_dir = skill_dir / "instructions"
        if instructions_dir.exists() and instructions_dir.is_dir():
            instruction_files.extend([
                f.name for f in instructions_dir.iterdir()
                if f.is_file() and f.suffix == '.md'
            ])

        # Check standard Claude structure (reference.md at root)
        reference_file = skill_dir / "reference.md"
        if reference_file.exists():
            instruction_files.append("reference.md")

        return instruction_files

    def load_skill_resources(self, skill_path: str, resource_file: str = "examples.md") -> str:
        """
        Load specific resource file (Progressive disclosure step 3)

        Resources are templates, examples, or reference materials that support
        skill execution. They're loaded on-demand to keep memory usage efficient.

        Supports both:
        - Enhanced structure: resources/meeting-template.md, resources/examples.md
        - Standard Claude: examples.md, templates/ (root level)

        Args:
            skill_path: Skill path (nested: "domain/skill-name" or flat: "skill-name")
            resource_file: Name of resource file (default: "examples.md")
                          For enhanced: "meeting-template.md", "examples.md"
                          For standard: "examples.md" or "templates/xyz.md"

        Returns:
            Content of the resource file

        Raises:
            FileNotFoundError: If resource file doesn't exist
        """
        skill_dir = self.skills_dir / skill_path

        # Try enhanced structure first (resources/ directory)
        resource_path = skill_dir / "resources" / resource_file
        if resource_path.exists():
            with open(resource_path, 'r', encoding='utf-8') as f:
                return f.read()

        # Try standard Claude structure (root level or templates/ directory)
        root_resource_path = skill_dir / resource_file
        if root_resource_path.exists():
            with open(root_resource_path, 'r', encoding='utf-8') as f:
                return f.read()

        # Try templates/ directory (standard Claude)
        template_path = skill_dir / "templates" / resource_file
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()

        raise FileNotFoundError(
            f"Resource file not found: tried {resource_path}, {root_resource_path}, and {template_path}"
        )

    def list_skill_resources(self, skill_path: str) -> List[str]:
        """
        List available resource files for a skill

        Supports both:
        - Enhanced structure: resources/ directory
        - Standard Claude: examples.md, templates/, scripts/ at root level

        Args:
            skill_path: Skill path (nested: "domain/skill-name" or flat: "skill-name")

        Returns:
            List of resource filenames
        """
        skill_dir = self.skills_dir / skill_path
        resource_files = []

        # Check enhanced structure (resources/ directory)
        resources_dir = skill_dir / "resources"
        if resources_dir.exists() and resources_dir.is_dir():
            resource_files.extend([
                f.name for f in resources_dir.iterdir()
                if f.is_file()
            ])

        # Check standard Claude structure (root level files)
        for standard_file in ["examples.md", "templates", "scripts"]:
            path = skill_dir / standard_file
            if path.is_file():
                resource_files.append(standard_file)
            elif path.is_dir():
                # Add files from templates/ or scripts/ directories
                resource_files.extend([
                    f"{standard_file}/{f.name}" for f in path.iterdir()
                    if f.is_file()
                ])

        return resource_files

    def list_skills(
        self,
        domain: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[SkillMetadata]:
        """
        List all skills (metadata only) with optional filtering

        This efficiently returns metadata for all skills without loading
        full content, instructions, or resources.

        Supports both:
        - Nested structure: .claude/skills/domain/skill-name/
        - Flat structure: .claude/skills/skill-name/

        Args:
            domain: Optional domain filter (e.g., "change-agent")
            category: Optional category filter (e.g., "meeting-management")

        Returns:
            List of SkillMetadata objects
        """
        skills = []

        if not self.skills_dir.exists():
            return skills

        # Scan all directories in skills_dir
        for item in self.skills_dir.iterdir():
            if not item.is_dir() or item.name.startswith('.'):
                continue

            # Check if this is a skill (flat structure)
            if (item / "SKILL.md").exists():
                # Flat structure: .claude/skills/skill-name/
                try:
                    skill_path = item.name
                    metadata = self.load_skill_metadata(skill_path)

                    # Apply filters
                    if domain and metadata.domain != domain:
                        continue
                    if category and metadata.category != category:
                        continue

                    skills.append(metadata)
                except Exception as e:
                    print(f"Warning: Could not load skill {item.name}: {e}")
                    continue
            else:
                # Nested structure: .claude/skills/domain/skill-name/
                domain_dir = item

                # Skip if domain filter doesn't match
                if domain and domain_dir.name != domain:
                    continue

                # Scan skill directories within domain
                for skill_dir in domain_dir.iterdir():
                    if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                        continue

                    # Check if SKILL.md exists
                    if not (skill_dir / "SKILL.md").exists():
                        continue

                    # Load metadata
                    try:
                        skill_path = f"{domain_dir.name}/{skill_dir.name}"
                        metadata = self.load_skill_metadata(skill_path)

                        # Apply category filter if specified
                        if category and metadata.category != category:
                            continue

                        skills.append(metadata)
                    except Exception as e:
                        print(f"Warning: Could not load skill {skill_dir.name}: {e}")
                        continue

        return skills

    def list_domains(self) -> List[str]:
        """
        List all available skill domains

        Returns:
            List of domain names
        """
        if not self.skills_dir.exists():
            return []

        domains = []
        for domain_dir in self.skills_dir.iterdir():
            if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
                domains.append(domain_dir.name)

        return sorted(domains)

    def list_categories(self, domain: Optional[str] = None) -> List[str]:
        """
        List all categories, optionally filtered by domain

        Args:
            domain: Optional domain filter

        Returns:
            List of unique category names
        """
        skills = self.list_skills(domain=domain)
        categories = {skill.category for skill in skills}
        return sorted(categories)

    def get_skill_info(self, skill_path: str) -> Dict[str, any]:
        """
        Get comprehensive information about a skill including metadata
        and available instructions/resources

        Args:
            skill_path: Skill path in format "domain/skill-name"

        Returns:
            Dictionary with skill metadata, instructions list, and resources list
        """
        metadata = self.load_skill_metadata(skill_path)

        return {
            "metadata": metadata,
            "instructions": self.list_skill_instructions(skill_path),
            "resources": self.list_skill_resources(skill_path),
            "content": self.load_skill_content(skill_path)
        }

    # =============================================================================
    # KNOWLEDGE LAYER METHODS
    # =============================================================================

    def load_knowledge(self, domain: str, category: str, knowledge_file: str) -> str:
        """
        Load a knowledge document from the knowledge layer.

        Knowledge documents provide domain-specific reference material that
        enhances skill execution. Unlike skills (which are instructions),
        knowledge documents contain standards, best practices, and reference
        information.

        Args:
            domain: Domain name (e.g., "change-agent")
            category: Category name (e.g., "meeting-management")
            knowledge_file: Knowledge file name (e.g., "action-items-standards.md")

        Returns:
            str: Content of the knowledge document

        Raises:
            FileNotFoundError: If knowledge file doesn't exist

        Example:
            >>> loader.load_knowledge("change-agent", "meeting-management",
                                     "action-items-standards.md")
        """
        knowledge_path = Path("knowledge") / domain / category / knowledge_file

        if not knowledge_path.exists():
            raise FileNotFoundError(f"Knowledge file not found: {knowledge_path}")

        with open(knowledge_path, 'r', encoding='utf-8') as f:
            return f.read()

    def get_knowledge_files(self, domain: str, category: str) -> List[str]:
        """
        Get list of available knowledge files for a domain/category.

        Args:
            domain: Domain name (e.g., "change-agent")
            category: Category name (e.g., "meeting-management")

        Returns:
            List[str]: List of knowledge file names (e.g., ["action-items-standards.md"])

        Example:
            >>> loader.get_knowledge_files("change-agent", "meeting-management")
            ['meeting-types.md', 'action-items-standards.md', 'decision-capture.md']
        """
        knowledge_dir = Path("knowledge") / domain / category

        if not knowledge_dir.exists():
            return []

        return sorted([f.name for f in knowledge_dir.glob("*.md")])
