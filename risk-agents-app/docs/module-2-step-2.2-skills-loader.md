# Module 2, Step 2.2: Skills Loader Implementation

**Completed**: October 22, 2025

## What We Built

In this step, we created the `SkillsLoader` class - a sophisticated loader that implements progressive disclosure for the Skills Framework. This class allows Claude to efficiently access 100+ skills without loading everything into memory at once.

## Why This Matters

The `SkillsLoader` is the heart of the Skills Framework's efficiency. It:
- Implements progressive disclosure (load only what you need, when you need it)
- Manages skill metadata, instructions, and resources
- Provides filtering and browsing capabilities
- Caches frequently accessed skills
- Scales to hundreds of skills without performance issues

## File Created

**File**: `backend/agent/skills_loader.py` (370 lines)

## Key Concepts Explained

### 1. What is Progressive Disclosure?

**Progressive disclosure** is a design pattern where you reveal information gradually, only when needed.

**Without Progressive Disclosure** (load everything):
```python
# BAD: Load all 100 skills completely
skills = load_all_skills_with_all_details()
# Memory usage: HIGH
# Loading time: SLOW
# Most data: NEVER USED
```

**With Progressive Disclosure** (load incrementally):
```python
# GOOD: Load metadata first, details only when needed
metadata = loader.load_skill_metadata("change-agent/meeting-minutes")
# Memory usage: LOW
# Loading time: FAST

# Only load instructions when actually using the skill
instructions = loader.load_skill_instructions("change-agent/meeting-minutes", "capture.md")
# Memory usage: MEDIUM
# Loading time: ONLY WHEN NEEDED
```

### 2. The Four Layers of Progressive Disclosure

Our Skills Framework uses four layers:

**Layer 1: Metadata** (ALWAYS loaded - lightweight)
```yaml
---
name: meeting-minutes-capture
description: Capture meeting minutes from transcripts
domain: change-agent
category: meeting-management
parameters: [meeting_transcript, meeting_date, attendees]
---
```
- **Size**: ~200 bytes per skill
- **Use**: Browsing, filtering, selection
- **Loaded**: When listing skills or choosing which skill to use

**Layer 2: Instructions** (loaded ON-DEMAND)
```markdown
# instructions/capture.md
Step-by-step guide for capturing meeting minutes from various formats...
```
- **Size**: ~2-5 KB per instruction file
- **Use**: Executing the skill
- **Loaded**: When Claude needs to know HOW to execute

**Layer 3: Resources** (loaded ON-DEMAND)
```markdown
# resources/meeting-template.md
Standard template for meeting minutes output...
```
- **Size**: ~1-3 KB per resource
- **Use**: Templates, examples, reference data
- **Loaded**: When Claude needs examples or templates

**Layer 4: Code** (loaded ON-DEMAND - future)
```python
# code/parser.py
Specialized code for parsing meeting transcripts...
```
- **Size**: Varies
- **Use**: Computational tasks
- **Loaded**: When specialized computation needed

### 3. Why Use Dataclasses?

Python **dataclasses** are a clean way to define data structures:

**Traditional approach** (verbose):
```python
class SkillMetadata:
    def __init__(self, name, description, domain, category, taxonomy, parameters, output_format, estimated_duration, skill_path):
        self.name = name
        self.description = description
        self.domain = domain
        # ... 9 lines of boilerplate!
```

**Dataclass approach** (clean):
```python
from dataclasses import dataclass

@dataclass
class SkillMetadata:
    name: str
    description: str
    domain: str
    category: str
    taxonomy: str
    parameters: List[str]
    output_format: str
    estimated_duration: str
    skill_path: Path
```

**Benefits**:
- Automatic `__init__` method
- Automatic `__repr__` for debugging
- Type hints built-in
- Less code, clearer intent

### 4. YAML Parsing

**YAML** (YAML Ain't Markup Language) is a human-readable data format:

**Example YAML**:
```yaml
name: meeting-minutes-capture
description: Capture meeting minutes from transcripts
parameters:
  - meeting_transcript
  - meeting_date
  - attendees
```

**Python parsing**:
```python
import yaml

yaml_text = """
name: meeting-minutes-capture
parameters:
  - meeting_transcript
  - meeting_date
"""

data = yaml.safe_load(yaml_text)
# Result: {'name': 'meeting-minutes-capture', 'parameters': ['meeting_transcript', 'meeting_date']}
```

**Why YAML for skill metadata?**
- Human-readable and editable
- Supports lists and nested structures
- Industry standard for configuration
- Easy to parse in any language

### 5. Caching Pattern

**Caching** stores loaded data to avoid repeated file reads:

**Without caching** (slow):
```python
# Read file 5 times
metadata1 = load_skill("meeting-minutes")  # Reads from disk
metadata2 = load_skill("meeting-minutes")  # Reads from disk AGAIN
metadata3 = load_skill("meeting-minutes")  # Reads from disk AGAIN
metadata4 = load_skill("meeting-minutes")  # Reads from disk AGAIN
metadata5 = load_skill("meeting-minutes")  # Reads from disk AGAIN
```

**With caching** (fast):
```python
# Read file once, use 5 times
metadata1 = load_skill("meeting-minutes")  # Reads from disk
metadata2 = load_skill("meeting-minutes")  # Returns cached version (instant!)
metadata3 = load_skill("meeting-minutes")  # Returns cached version (instant!)
metadata4 = load_skill("meeting-minutes")  # Returns cached version (instant!)
metadata5 = load_skill("meeting-minutes")  # Returns cached version (instant!)
```

**Implementation**:
```python
class SkillsLoader:
    def __init__(self):
        self._skill_cache: Dict[str, SkillMetadata] = {}

    def load_skill_metadata(self, skill_path: str):
        # Check cache first
        if skill_path in self._skill_cache:
            return self._skill_cache[skill_path]

        # Not in cache - load from disk
        metadata = self._load_from_disk(skill_path)

        # Store in cache for next time
        self._skill_cache[skill_path] = metadata

        return metadata
```

### 6. File Path Construction

Building file paths safely across different operating systems:

**Wrong way** (breaks on Windows):
```python
path = "/Users/gavin/.claude/skills/change-agent/meeting-minutes/SKILL.md"
# Windows: C:\Users\gavin\.claude\skills\... (incompatible!)
```

**Right way** (works everywhere):
```python
from pathlib import Path

skills_dir = Path(".claude/skills")
domain = "change-agent"
skill = "meeting-minutes"

# Automatically uses correct separator (/ on Unix, \ on Windows)
skill_file = skills_dir / domain / skill / "SKILL.md"
```

**Why Path is better than strings**:
- Cross-platform compatibility
- Safer path construction with `/` operator
- Built-in methods (`.exists()`, `.is_dir()`, etc.)
- Clearer intent in code

## Code Walkthrough

Let's walk through the key parts of `SkillsLoader`:

### SkillMetadata Dataclass

```python
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class SkillMetadata:
    """
    Skill metadata extracted from YAML frontmatter

    This is Layer 1 of progressive disclosure - lightweight metadata
    that allows browsing and filtering without loading full skill details.
    """
    name: str                      # Skill identifier (e.g., "meeting-minutes-capture")
    description: str               # One-line description
    domain: str                    # Domain (e.g., "change-agent")
    category: str                  # Category (e.g., "meeting-management")
    taxonomy: str                  # Full taxonomy path
    parameters: List[str]          # Required input parameters
    output_format: str             # Expected output format
    estimated_duration: str        # How long skill takes to execute
    skill_path: Path              # Full path to skill directory
```

**What's happening**:
1. `@dataclass` decorator creates the class structure
2. Each field has a type hint (enforces correct usage)
3. Comments explain what each field means
4. This structure matches the YAML frontmatter in SKILL.md files

**Why this design**:
- Type safety prevents bugs
- Self-documenting code
- Easy to serialize/deserialize
- Matches YAML structure exactly

### Class Initialization

```python
class SkillsLoader:
    """
    Progressive Disclosure Skill Loader

    Loads skills in layers:
    1. Metadata (YAML frontmatter) - always loaded
    2. Instructions - loaded on-demand
    3. Resources - loaded on-demand
    4. Code - loaded on-demand (future)
    """

    def __init__(self, skills_dir: Path):
        """
        Initialize the Skills Loader

        Args:
            skills_dir: Path to .claude/skills directory
        """
        self.skills_dir = skills_dir
        self._skill_cache: Dict[str, SkillMetadata] = {}
```

**What's happening**:
1. Store the skills directory path
2. Initialize an empty cache dictionary
3. Cache will store skill_path → SkillMetadata mappings

**Why this design**:
- Path injection makes testing easier
- Cache improves performance for repeated loads
- Dict lookup is O(1) - instant retrieval

### Loading Skill Metadata (Layer 1)

```python
def load_skill_metadata(self, skill_path: str) -> SkillMetadata:
    """
    Load skill metadata from YAML frontmatter

    This is Progressive Disclosure Layer 1 - just the metadata.

    Args:
        skill_path: Path to skill (e.g., "change-agent/meeting-minutes-capture")

    Returns:
        SkillMetadata object with parsed YAML data

    Raises:
        FileNotFoundError: If skill doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    # Check cache first
    if skill_path in self._skill_cache:
        return self._skill_cache[skill_path]

    # Construct full path to SKILL.md
    full_path = self.skills_dir / skill_path / "SKILL.md"

    if not full_path.exists():
        raise FileNotFoundError(f"Skill not found: {skill_path}")

    # Read file
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract YAML frontmatter (between --- markers)
    parts = content.split('---', 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid SKILL.md format: {skill_path}")

    yaml_content = parts[1].strip()

    # Parse YAML
    metadata_dict = yaml.safe_load(yaml_content)

    # Create SkillMetadata object
    metadata = SkillMetadata(
        name=metadata_dict['name'],
        description=metadata_dict['description'],
        domain=metadata_dict['domain'],
        category=metadata_dict['category'],
        taxonomy=metadata_dict.get('taxonomy',
                                   f"{metadata_dict['domain']}/{metadata_dict['category']}"),
        parameters=metadata_dict.get('parameters', []),
        output_format=metadata_dict.get('output_format', 'markdown'),
        estimated_duration=metadata_dict.get('estimated_duration', 'varies'),
        skill_path=self.skills_dir / skill_path
    )

    # Cache for future use
    self._skill_cache[skill_path] = metadata

    return metadata
```

**What's happening**:
1. **Check cache**: If already loaded, return immediately (fast!)
2. **Construct path**: Build full path to SKILL.md file
3. **Validate**: Check file exists, raise error if not
4. **Read file**: Load entire file content
5. **Extract YAML**: Split on `---` markers to isolate frontmatter
6. **Parse YAML**: Convert YAML text to Python dictionary
7. **Create object**: Build SkillMetadata from parsed data
8. **Cache**: Store in cache for next time
9. **Return**: Give caller the metadata object

**Error handling**:
- `FileNotFoundError` if skill doesn't exist
- `ValueError` if SKILL.md format is wrong
- `yaml.YAMLError` if YAML parsing fails

**Example transformation**:
```yaml
# Input (SKILL.md):
---
name: meeting-minutes-capture
description: Capture meeting minutes
domain: change-agent
category: meeting-management
parameters:
  - meeting_transcript
  - meeting_date
---
```
↓
```python
# Output (SkillMetadata):
SkillMetadata(
    name="meeting-minutes-capture",
    description="Capture meeting minutes",
    domain="change-agent",
    category="meeting-management",
    taxonomy="change-agent/meeting-management",
    parameters=["meeting_transcript", "meeting_date"],
    output_format="markdown",
    estimated_duration="varies",
    skill_path=Path(".claude/skills/change-agent/meeting-minutes-capture")
)
```

### Loading Skill Instructions (Layer 2)

```python
def load_skill_instructions(self, skill_path: str, instruction_file: str) -> str:
    """
    Load specific instruction file for a skill

    This is Progressive Disclosure Layer 2 - detailed instructions.

    Args:
        skill_path: Path to skill (e.g., "change-agent/meeting-minutes-capture")
        instruction_file: Name of instruction file (e.g., "capture.md")

    Returns:
        Instruction content as markdown string

    Raises:
        FileNotFoundError: If instruction file doesn't exist
    """
    # Construct path to instruction file
    instruction_path = self.skills_dir / skill_path / "instructions" / instruction_file

    if not instruction_path.exists():
        raise FileNotFoundError(
            f"Instruction file not found: {skill_path}/instructions/{instruction_file}"
        )

    # Read and return
    with open(instruction_path, 'r', encoding='utf-8') as f:
        return f.read()
```

**What's happening**:
1. Construct path to specific instruction file
2. Validate file exists
3. Read entire file content
4. Return as string (markdown format)

**Why separate method?**
- Load instructions only when executing skill (not when browsing)
- Keeps metadata loading fast
- Skills can have multiple instruction files
- Clear separation of concerns

**Usage example**:
```python
# User asks: "Help me capture meeting minutes"

# Step 1: Load metadata to identify skill
metadata = loader.load_skill_metadata("change-agent/meeting-minutes-capture")
# (Fast - just YAML parsing)

# Step 2: Load specific instructions for capturing
capture_instructions = loader.load_skill_instructions(
    "change-agent/meeting-minutes-capture",
    "capture.md"
)
# (Loaded only when needed)

# Step 3: Use instructions to execute skill
# Claude reads capture_instructions and follows steps
```

### Loading Skill Resources (Layer 3)

```python
def load_skill_resources(self, skill_path: str, resource_file: str) -> str:
    """
    Load specific resource file for a skill

    This is Progressive Disclosure Layer 3 - templates, examples, data.

    Args:
        skill_path: Path to skill (e.g., "change-agent/meeting-minutes-capture")
        resource_file: Name of resource file (e.g., "meeting-template.md")

    Returns:
        Resource content as string

    Raises:
        FileNotFoundError: If resource file doesn't exist
    """
    # Construct path to resource file
    resource_path = self.skills_dir / skill_path / "resources" / resource_file

    if not resource_path.exists():
        raise FileNotFoundError(
            f"Resource file not found: {skill_path}/resources/{resource_file}"
        )

    # Read and return
    with open(resource_path, 'r', encoding='utf-8') as f:
        return f.read()
```

**What's happening**:
1. Construct path to specific resource file
2. Validate file exists
3. Read entire file content
4. Return as string

**Types of resources**:
- **Templates**: Standard formats for outputs
- **Examples**: Real-world usage demonstrations
- **Reference data**: Lookup tables, categories, etc.

**Usage example**:
```python
# Claude is executing meeting-minutes-capture skill

# Load template to format output correctly
template = loader.load_skill_resources(
    "change-agent/meeting-minutes-capture",
    "meeting-template.md"
)
# Returns: "# Meeting Minutes: [Title]\n**Date**: [Date]..."

# Load examples to understand formatting
examples = loader.load_skill_resources(
    "change-agent/meeting-minutes-capture",
    "examples.md"
)
# Returns: Three complete example transformations

# Use template and examples to format user's meeting minutes
```

### Listing All Skills

```python
def list_skills(
    self,
    domain: Optional[str] = None,
    category: Optional[str] = None
) -> List[SkillMetadata]:
    """
    List all available skills with optional filtering

    Loads only metadata (Layer 1) for each skill.

    Args:
        domain: Optional domain filter (e.g., "change-agent")
        category: Optional category filter (e.g., "meeting-management")

    Returns:
        List of SkillMetadata objects
    """
    skills = []

    # Scan domain directories
    for domain_dir in self.skills_dir.iterdir():
        # Skip hidden directories and files
        if not domain_dir.is_dir() or domain_dir.name.startswith('.'):
            continue

        # Skip if domain filter doesn't match
        if domain and domain_dir.name != domain:
            continue

        # Scan skill directories within domain
        for skill_dir in domain_dir.iterdir():
            # Skip hidden directories and files
            if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                continue

            # Check if SKILL.md exists (confirms it's a valid skill)
            if not (skill_dir / "SKILL.md").exists():
                continue

            try:
                # Load metadata
                skill_path = f"{domain_dir.name}/{skill_dir.name}"
                metadata = self.load_skill_metadata(skill_path)

                # Apply category filter if specified
                if category and metadata.category != category:
                    continue

                skills.append(metadata)

            except Exception as e:
                # Log warning but continue (don't fail entire listing)
                print(f"Warning: Could not load skill {skill_dir.name}: {e}")
                continue

    return skills
```

**What's happening**:
1. **Scan domains**: Loop through domain directories (change-agent, etc.)
2. **Skip invalid**: Ignore hidden dirs (starting with .)
3. **Apply domain filter**: Skip domains that don't match filter
4. **Scan skills**: Loop through skill directories within domain
5. **Validate skill**: Check SKILL.md exists
6. **Load metadata**: Use load_skill_metadata (benefits from cache)
7. **Apply category filter**: Skip skills that don't match
8. **Handle errors**: Log warnings but continue (robust)
9. **Return list**: All matching skills

**Example usage**:
```python
# List all skills (no filter)
all_skills = loader.list_skills()
# Returns: [skill1, skill2, skill3, ... skill100]

# List only change-agent skills
change_skills = loader.list_skills(domain="change-agent")
# Returns: [meeting-minutes, action-tracking, project-charter, ...]

# List only meeting-management skills
meeting_skills = loader.list_skills(category="meeting-management")
# Returns: [meeting-minutes, action-tracking, follow-up-generator]

# List change-agent + meeting-management skills
specific_skills = loader.list_skills(domain="change-agent", category="meeting-management")
# Returns: [meeting-minutes, action-tracking, follow-up-generator]
```

### Utility Methods

```python
def get_skill_categories(self, domain: Optional[str] = None) -> List[str]:
    """
    Get list of all skill categories

    Args:
        domain: Optional domain to filter categories

    Returns:
        List of unique category names
    """
    skills = self.list_skills(domain=domain)
    categories = set(skill.category for skill in skills)
    return sorted(categories)
```

**What's happening**:
1. Get all skills (with optional domain filter)
2. Extract category from each skill
3. Use `set()` to get unique categories
4. Sort alphabetically
5. Return list

**Example**:
```python
# Get all categories
categories = loader.get_skill_categories()
# Returns: ['meeting-management', 'project-artifacts', 'project-setup', ...]

# Get only change-agent categories
change_categories = loader.get_skill_categories(domain="change-agent")
# Returns: ['meeting-management', 'project-artifacts', 'project-setup', ...]
```

```python
def get_skill_domains(self) -> List[str]:
    """
    Get list of all skill domains

    Returns:
        List of domain names
    """
    domains = []

    for domain_dir in self.skills_dir.iterdir():
        if domain_dir.is_dir() and not domain_dir.name.startswith('.'):
            domains.append(domain_dir.name)

    return sorted(domains)
```

**What's happening**:
1. Scan skills directory
2. Collect directory names (each is a domain)
3. Skip hidden directories
4. Sort alphabetically
5. Return list

**Example**:
```python
domains = loader.get_skill_domains()
# Returns: ['change-agent', 'risk-analyst', 'data-engineer', ...]
```

```python
def search_skills(self, query: str) -> List[SkillMetadata]:
    """
    Search skills by name or description

    Args:
        query: Search query (case-insensitive)

    Returns:
        List of matching SkillMetadata objects
    """
    query_lower = query.lower()
    all_skills = self.list_skills()

    matching_skills = [
        skill for skill in all_skills
        if query_lower in skill.name.lower() or query_lower in skill.description.lower()
    ]

    return matching_skills
```

**What's happening**:
1. Convert query to lowercase (case-insensitive search)
2. Get all skills
3. Filter skills where query matches name OR description
4. Return matching skills

**Example**:
```python
# Search for "meeting" skills
results = loader.search_skills("meeting")
# Returns: [meeting-minutes-capture, follow-up-generator, ...]

# Search for "action" skills
results = loader.search_skills("action")
# Returns: [action-item-tracking, ...]

# Search for "project" skills
results = loader.search_skills("project")
# Returns: [project-charter, project-plan, project-artifacts, ...]
```

## How to Use the SkillsLoader

### Example 1: Load and Display Skill Metadata

```python
from pathlib import Path
from agent import SkillsLoader

# Create loader
loader = SkillsLoader(skills_dir=Path(".claude/skills"))

# Load specific skill metadata
metadata = loader.load_skill_metadata("change-agent/meeting-minutes-capture")

# Display information
print(f"Skill: {metadata.name}")
print(f"Description: {metadata.description}")
print(f"Category: {metadata.category}")
print(f"Parameters: {', '.join(metadata.parameters)}")
print(f"Estimated Duration: {metadata.estimated_duration}")
```

**Output**:
```
Skill: meeting-minutes-capture
Description: Capture meeting minutes from transcripts or notes and extract structured action items, decisions, and next steps
Category: meeting-management
Parameters: meeting_transcript, meeting_date, attendees
Estimated Duration: 2-3 minutes
```

### Example 2: List All Skills in a Domain

```python
# Create loader
loader = SkillsLoader(skills_dir=Path(".claude/skills"))

# List all change-agent skills
skills = loader.list_skills(domain="change-agent")

# Display
print(f"Found {len(skills)} change-agent skills:")
for skill in skills:
    print(f"  - {skill.name}: {skill.description}")
```

**Output**:
```
Found 15 change-agent skills:
  - meeting-minutes-capture: Capture meeting minutes from transcripts
  - action-item-tracking: Track action items and follow-ups
  - project-charter-generator: Generate project charter documents
  ...
```

### Example 3: Load Instructions When Executing Skill

```python
# Create loader
loader = SkillsLoader(skills_dir=Path(".claude/skills"))

# User wants to capture meeting minutes
skill_path = "change-agent/meeting-minutes-capture"

# Load metadata first
metadata = loader.load_skill_metadata(skill_path)
print(f"Executing skill: {metadata.name}")

# Load specific instructions
capture_instructions = loader.load_skill_instructions(skill_path, "capture.md")
extract_instructions = loader.load_skill_instructions(skill_path, "extract-actions.md")

# Load resources
template = loader.load_skill_resources(skill_path, "meeting-template.md")
examples = loader.load_skill_resources(skill_path, "examples.md")

# Now execute skill using loaded content
# (In real app, this would be passed to Claude)
print(f"Instructions loaded: {len(capture_instructions)} chars")
print(f"Template loaded: {len(template)} chars")
print(f"Examples loaded: {len(examples)} chars")
```

### Example 4: Search for Skills

```python
# Create loader
loader = SkillsLoader(skills_dir=Path(".claude/skills"))

# User searches for "status"
results = loader.search_skills("status")

print(f"Found {len(results)} skills matching 'status':")
for skill in results:
    print(f"  - {skill.name} ({skill.category})")
    print(f"    {skill.description}")
```

**Output**:
```
Found 3 skills matching 'status':
  - status-report-generator (status-tracking)
    Generate project status reports
  - milestone-tracker (status-tracking)
    Track project milestones and progress
  - issue-log-manager (status-tracking)
    Manage project issues and blockers
```

### Example 5: Browse by Category

```python
# Create loader
loader = SkillsLoader(skills_dir=Path(".claude/skills"))

# Get all categories
categories = loader.get_skill_categories()

print("Available skill categories:")
for category in categories:
    # Get skills in this category
    skills = loader.list_skills(category=category)
    print(f"\n{category} ({len(skills)} skills):")
    for skill in skills:
        print(f"  - {skill.name}")
```

**Output**:
```
Available skill categories:

meeting-management (3 skills):
  - meeting-minutes-capture
  - action-item-tracking
  - follow-up-generator

project-setup (3 skills):
  - project-charter-generator
  - stakeholder-analysis
  - project-plan-template

requirements-gathering (3 skills):
  - business-requirements-capture
  - requirement-validation
  - use-case-generator
...
```

### Example 6: Integration with RiskAgentClient

```python
from pathlib import Path
from agent import RiskAgentClient, SkillsLoader

# Create components
skills_dir = Path(".claude/skills")
loader = SkillsLoader(skills_dir=skills_dir)
client = RiskAgentClient(skills_dir=skills_dir)

# User asks: "Help me capture meeting minutes"

# 1. Search for relevant skill
skills = loader.search_skills("meeting minutes")
skill = skills[0]  # meeting-minutes-capture

# 2. Load instructions
instructions = loader.load_skill_instructions(
    "change-agent/meeting-minutes-capture",
    "capture.md"
)

# 3. Load template
template = loader.load_skill_resources(
    "change-agent/meeting-minutes-capture",
    "meeting-template.md"
)

# 4. Build context for Claude
context = {
    "skill_name": skill.name,
    "skill_instructions": instructions,
    "output_template": template
}

# 5. Query Claude with skill context
user_transcript = """
Meeting on Oct 22, 2025 with John, Sarah, Mike about Q4 planning...
"""

response = client.query(
    f"Using the {skill.name} skill, capture meeting minutes from this transcript:\n\n{user_transcript}",
    context=context
)

print(response)
```

This demonstrates how `SkillsLoader` and `RiskAgentClient` work together!

## Performance Benefits of Progressive Disclosure

Let's compare the performance impact:

### Without Progressive Disclosure (load everything):
```
Startup:
- Load 100 skills × 50 KB average = 5 MB
- Parse time: ~500ms
- Memory usage: 5 MB

Per query:
- Already loaded, but 5 MB in memory
- Claude processes unnecessary data
```

### With Progressive Disclosure (load incrementally):
```
Startup:
- Load 100 skills metadata only × 200 bytes = 20 KB
- Parse time: ~20ms (25x faster!)
- Memory usage: 20 KB (250x less!)

Per query:
- Load 1 skill instructions: ~5 KB
- Load 1-2 resources: ~3 KB
- Total: 8 KB per query (625x less than loading everything!)
- Claude processes only relevant data
```

**Real-world impact**:
- **Faster startup**: 20ms vs 500ms
- **Lower memory**: 20 KB vs 5 MB
- **Scalable**: Can support 1000+ skills without performance degradation
- **Efficient**: Only load what you use

## Design Decisions Explained

### Why use separate methods for instructions vs resources?

**Decision**: `load_skill_instructions()` and `load_skill_resources()` are separate methods

**Reasoning**:
1. **Different use cases**: Instructions = execution steps, Resources = reference data
2. **Selective loading**: Can load instructions without resources (or vice versa)
3. **Clear semantics**: Method name indicates what you're loading
4. **Future flexibility**: Can add caching strategies specific to each type

### Why cache metadata but not instructions/resources?

**Decision**: Metadata is cached, instructions/resources are loaded on-demand without caching

**Reasoning**:
1. **Metadata is reused**: Browsing, searching, filtering all use metadata
2. **Instructions are single-use**: Typically loaded once per skill execution
3. **Memory efficiency**: Caching everything would defeat progressive disclosure
4. **Simple implementation**: Less complexity = fewer bugs

**Future enhancement**: Could add LRU cache for frequently used instructions

### Why use Path instead of strings for file paths?

**Decision**: Use `pathlib.Path` throughout instead of string concatenation

**Reasoning**:
1. **Cross-platform**: Works on Windows, macOS, Linux
2. **Safety**: Automatic handling of path separators
3. **Clarity**: `/` operator clearly shows path construction
4. **Methods**: `.exists()`, `.is_dir()`, `.iterdir()` built-in

### Why use YAML for frontmatter instead of JSON?

**Decision**: YAML frontmatter in SKILL.md files

**Reasoning**:
1. **Human-readable**: No quotes, no commas, clean syntax
2. **Industry standard**: Used by Jekyll, Hugo, Obsidian, etc.
3. **List support**: Easy to write parameter lists
4. **Comments**: YAML supports comments (JSON doesn't)
5. **Convention**: Markdown + YAML frontmatter is established pattern

### Why scan directory structure instead of using an index file?

**Decision**: Discover skills by scanning `.claude/skills/` directory

**Reasoning**:
1. **No sync needed**: Adding a skill is just adding a directory
2. **Self-documenting**: Directory structure IS the organization
3. **Simplicity**: No index file to maintain
4. **Robust**: Can't get out of sync with filesystem
5. **Git-friendly**: Easy to see changes in version control

**Trade-off**: Slightly slower than index lookup, but negligible for 100-1000 skills

## Testing the SkillsLoader

We'll test this in Step 2.7, but here's what we'll verify:

- [ ] Load skill metadata successfully
- [ ] YAML parsing works correctly
- [ ] Caching prevents repeated file reads
- [ ] Load instructions from skills
- [ ] Load resources from skills
- [ ] List all skills
- [ ] Filter by domain
- [ ] Filter by category
- [ ] Search skills by query
- [ ] Error handling (missing files, invalid YAML)
- [ ] Performance (load 100+ skills in <100ms)

## Common Issues & Solutions

### Issue 1: "FileNotFoundError: Skill not found"

**Cause**: Skill path doesn't exist or is misspelled

**Solution**:
```python
# Check available skills first
all_skills = loader.list_skills()
print([s.name for s in all_skills])

# Use exact name from the list
metadata = loader.load_skill_metadata("change-agent/meeting-minutes-capture")
```

### Issue 2: "yaml.scanner.ScannerError: invalid YAML"

**Cause**: YAML frontmatter has syntax errors

**Solution**:
- Check YAML indentation (use spaces, not tabs)
- Ensure `---` markers are on their own lines
- Validate YAML at https://www.yamllint.com/

**Example fix**:
```yaml
# WRONG (tabs, incorrect indentation)
---
name: skill-name
parameters:
	- param1  # TAB character - bad!
---

# RIGHT (spaces, correct indentation)
---
name: skill-name
parameters:
  - param1  # Two spaces - good!
---
```

### Issue 3: Slow performance when listing many skills

**Cause**: Loading metadata for 100+ skills without caching

**Solution**: The caching is automatic! But you can optimize:
```python
# SLOW: List skills multiple times
for i in range(100):
    skills = loader.list_skills()  # Re-scans directory each time

# FAST: List once, reuse result
all_skills = loader.list_skills()  # Scan once
for i in range(100):
    # Use all_skills (cached in memory)
    meeting_skills = [s for s in all_skills if s.category == "meeting-management"]
```

### Issue 4: "TypeError: 'NoneType' object is not iterable"

**Cause**: Optional field in YAML is missing and not handled

**Solution**: Use `.get()` with default values:
```python
# WRONG: Assumes 'parameters' always exists
parameters = metadata_dict['parameters']  # KeyError if missing!

# RIGHT: Provide default if missing
parameters = metadata_dict.get('parameters', [])  # Returns [] if missing
```

## Key Takeaways

1. **Progressive disclosure makes the system scalable** - Load only what you need
2. **Four layers**: Metadata → Instructions → Resources → Code
3. **Caching improves performance** - Metadata cached, instructions loaded on-demand
4. **YAML frontmatter is clean and standard** - Human-readable skill metadata
5. **Dataclasses simplify code** - Less boilerplate, clearer intent
6. **Path is better than strings** - Cross-platform, safe, clear
7. **Directory scanning is robust** - No index file to maintain

---

**Files Created**: 1 (`backend/agent/skills_loader.py`)
**Lines of Code**: 370
**Time to Complete**: ~60 minutes
**Dependencies**: PyYAML (already installed)

**Next Step**: [Module 2, Step 2.3: Context Manager Implementation](module-2-step-2.3-context-manager.md)
