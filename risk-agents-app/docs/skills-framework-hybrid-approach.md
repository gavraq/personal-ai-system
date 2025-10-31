# Skills Framework: Hybrid Approach

**Last Updated**: October 23, 2025

## Overview

Our Skills Framework implements a **hybrid approach** that supports both:
1. **Standard Claude structure** (flat, simple)
2. **Enhanced structure** (nested, organized)

This provides backward compatibility with Claude's official skills framework while enabling better organization for large skill collections (100+ skills).

## Why Hybrid?

### The Challenge
Claude's official skills framework uses a flat structure:
```
.claude/skills/
├── meeting-minutes/
│   ├── SKILL.md
│   ├── reference.md
│   └── examples.md
├── status-report/
│   ├── SKILL.md
│   └── reference.md
└── project-charter/
    ├── SKILL.md
    └── reference.md
```

**Problem**: With 100+ skills, this becomes difficult to manage and browse.

### Our Solution
We support BOTH structures:

**Standard Claude** (for compatibility):
```
.claude/skills/
└── meeting-minutes/
    ├── SKILL.md (name + description required)
    ├── reference.md (instructions)
    └── examples.md (examples)
```

**Enhanced** (for organization):
```
.claude/skills/
└── change-agent/
    └── meeting-minutes-capture/
        ├── SKILL.md (name + description + domain + category + ...)
        ├── instructions/
        │   ├── capture.md
        │   └── extract-actions.md
        └── resources/
            ├── meeting-template.md
            └── examples.md
```

## Structure Comparison

### Standard Claude Structure

**Directory Layout**:
```
.claude/skills/skill-name/
├── SKILL.md          # Required
├── reference.md      # Optional (instructions)
├── examples.md       # Optional (examples)
├── templates/        # Optional (templates directory)
└── scripts/          # Optional (executable scripts)
```

**SKILL.md YAML Frontmatter** (minimal):
```yaml
---
name: meeting-minutes-capture
description: Capture meeting minutes from transcripts or notes and extract structured action items, decisions, and next steps
---
```

**Pros**:
- ✅ Standard Claude compatibility
- ✅ Simple structure
- ✅ Works with Claude Code directly

**Cons**:
- ❌ Doesn't scale well (100+ skills in one directory)
- ❌ No organizational hierarchy
- ❌ Limited metadata for filtering

### Enhanced Structure

**Directory Layout**:
```
.claude/skills/domain/skill-name/
├── SKILL.md          # Required (enhanced YAML)
├── instructions/     # Multiple instruction files
│   ├── capture.md
│   ├── extract-actions.md
│   └── format-output.md
└── resources/        # Multiple resource files
    ├── meeting-template.md
    ├── examples.md
    └── reference-data.json
```

**SKILL.md YAML Frontmatter** (enhanced):
```yaml
---
name: meeting-minutes-capture
description: Capture meeting minutes from transcripts or notes and extract structured action items, decisions, and next steps
domain: change-agent
category: meeting-management
taxonomy: change-agent/meeting-management
parameters:
  - meeting_transcript
  - meeting_date
  - attendees
output_format: structured_markdown
estimated_duration: 2-3 minutes
---
```

**Pros**:
- ✅ Organized by domain/category
- ✅ Scales to 100+ skills easily
- ✅ Rich metadata for filtering
- ✅ Multiple instruction files per skill
- ✅ Better separation of concerns

**Cons**:
- ⚠️ Not directly portable to Claude Code (requires conversion)
- ⚠️ Extra metadata fields (though backward compatible)

## How SkillsLoader Handles Both

### Smart Path Detection

```python
# Flat structure (standard Claude)
metadata = loader.load_skill_metadata("meeting-minutes")
# Looks in: .claude/skills/meeting-minutes/SKILL.md

# Nested structure (enhanced)
metadata = loader.load_skill_metadata("change-agent/meeting-minutes-capture")
# Looks in: .claude/skills/change-agent/meeting-minutes-capture/SKILL.md
```

**Detection logic**:
- If `skill_path` contains `/` → nested structure
- If `skill_path` has no `/` → flat structure

### Multi-Location File Loading

#### Instructions

```python
# Try enhanced structure first
instructions = loader.load_skill_instructions("change-agent/meeting-minutes", "capture.md")
# Searches:
# 1. .claude/skills/change-agent/meeting-minutes/instructions/capture.md ✅ Found!

# Try standard structure
instructions = loader.load_skill_instructions("meeting-minutes", "reference.md")
# Searches:
# 1. .claude/skills/meeting-minutes/instructions/reference.md (not found)
# 2. .claude/skills/meeting-minutes/reference.md ✅ Found!
```

#### Resources

```python
# Enhanced structure
template = loader.load_skill_resources("change-agent/meeting-minutes", "meeting-template.md")
# Searches:
# 1. .claude/skills/change-agent/meeting-minutes/resources/meeting-template.md ✅ Found!

# Standard structure
examples = loader.load_skill_resources("meeting-minutes", "examples.md")
# Searches:
# 1. .claude/skills/meeting-minutes/resources/examples.md (not found)
# 2. .claude/skills/meeting-minutes/examples.md ✅ Found!
# 3. .claude/skills/meeting-minutes/templates/examples.md (fallback)
```

### Automatic Structure Discovery

```python
# Lists ALL skills regardless of structure
all_skills = loader.list_skills()
# Returns: [
#   <Skill: meeting-minutes>,           # Flat structure
#   <Skill: change-agent/meeting-minutes-capture>,  # Nested structure
#   <Skill: status-report>,             # Flat structure
#   <Skill: risk-analyst/threat-assessment>,  # Nested structure
# ]

# Filter by domain (works for both!)
change_skills = loader.list_skills(domain="change-agent")
# Returns all skills with domain="change-agent" regardless of structure
```

## YAML Frontmatter Compatibility

### Required Fields (Both Structures)

```yaml
---
name: skill-name               # Required: 64 chars max, lowercase
description: What and when     # Required: 1024 chars max
---
```

### Optional Enhanced Fields

```yaml
---
name: skill-name
description: What and when
domain: change-agent           # Enhanced: organizational domain
category: meeting-management   # Enhanced: skill category
taxonomy: change-agent/meeting-management  # Enhanced: full path
parameters:                    # Enhanced: expected inputs
  - input1
  - input2
output_format: markdown        # Enhanced: expected output
estimated_duration: 2-3 min    # Enhanced: execution time
---
```

**Backward Compatibility**:
- Standard Claude ignores unknown fields (safe to add extra metadata)
- Our loader provides defaults for missing enhanced fields
- Works with both Claude API and Claude Code

## Migration Paths

### From Standard → Enhanced

```bash
# Before (flat)
.claude/skills/meeting-minutes/
├── SKILL.md
├── reference.md
└── examples.md

# After (nested)
.claude/skills/change-agent/meeting-minutes-capture/
├── SKILL.md (add domain, category to YAML)
├── instructions/
│   └── reference.md (moved from root)
└── resources/
    └── examples.md (moved from root)
```

**Code changes**: None! Loader automatically detects new structure.

### From Enhanced → Standard

```bash
# Before (nested)
.claude/skills/change-agent/meeting-minutes/
├── SKILL.md (domain, category, etc.)
├── instructions/
│   └── capture.md
└── resources/
    └── examples.md

# After (flat)
.claude/skills/meeting-minutes/
├── SKILL.md (remove domain, category from YAML)
├── reference.md (renamed from capture.md, moved to root)
└── examples.md (moved to root)
```

**Use case**: Porting to pure Claude Code environment.

## Best Practices

### When to Use Standard Structure

✅ **Use standard Claude structure when**:
- Building skills for Claude Code
- Creating portable skills for sharing
- Working with small skill collections (< 20 skills)
- Need maximum compatibility

**Example**:
```
.claude/skills/
├── meeting-notes/
├── status-report/
└── code-review/
```

### When to Use Enhanced Structure

✅ **Use enhanced structure when**:
- Building large skill collections (50+ skills)
- Need organizational hierarchy
- Want rich filtering capabilities
- Building custom agent platforms (like Risk Agents)

**Example**:
```
.claude/skills/
├── change-agent/
│   ├── meeting-minutes-capture/
│   ├── action-item-tracking/
│   └── project-charter-generator/
├── risk-analyst/
│   ├── threat-assessment/
│   ├── control-evaluation/
│   └── risk-register-manager/
└── data-engineer/
    ├── data-quality-checker/
    ├── pipeline-validator/
    └── schema-generator/
```

### Mixing Both Structures

✅ **You can mix structures!**

```
.claude/skills/
├── quick-note/              # Flat (simple utility)
│   ├── SKILL.md
│   └── reference.md
├── change-agent/            # Nested (organized domain)
│   ├── meeting-minutes/
│   └── action-tracking/
└── status-report/           # Flat (standalone skill)
    ├── SKILL.md
    └── examples.md
```

The loader handles this seamlessly!

## Code Examples

### Example 1: Loading from Either Structure

```python
from pathlib import Path
from agent import SkillsLoader

loader = SkillsLoader(skills_dir=Path(".claude/skills"))

# Works with flat structure
metadata = loader.load_skill_metadata("meeting-notes")
print(f"Loaded: {metadata.name}")
# Output: Loaded: meeting-notes

# Works with nested structure
metadata = loader.load_skill_metadata("change-agent/meeting-minutes")
print(f"Loaded: {metadata.domain}/{metadata.name}")
# Output: Loaded: change-agent/meeting-minutes
```

### Example 2: Loading Instructions (Both Structures)

```python
# Enhanced structure (instructions/ directory)
instructions = loader.load_skill_instructions(
    "change-agent/meeting-minutes",
    "capture.md"
)

# Standard structure (reference.md at root)
instructions = loader.load_skill_instructions(
    "meeting-notes",
    "reference.md"  # Default parameter
)

# Both return the same type: string content
```

### Example 3: Listing All Skills

```python
# Get all skills (both structures)
all_skills = loader.list_skills()

for skill in all_skills:
    if skill.is_flat_structure:
        print(f"Flat: {skill.name}")
    else:
        print(f"Nested: {skill.domain}/{skill.name}")

# Output:
# Flat: meeting-notes
# Flat: status-report
# Nested: change-agent/meeting-minutes
# Nested: risk-analyst/threat-assessment
```

### Example 4: Filtering Works Across Structures

```python
# Filter by domain (works for both!)
change_skills = loader.list_skills(domain="change-agent")
# Returns all change-agent skills from:
# 1. Nested: change-agent/ directory
# 2. Flat: skills with domain="change-agent" in YAML

# Filter by category
meeting_skills = loader.list_skills(category="meeting-management")
# Returns all meeting-management skills regardless of structure
```

## Testing Both Structures

### Create Test Skills

**Standard structure**:
```bash
mkdir -p .claude/skills/test-flat
cat > .claude/skills/test-flat/SKILL.md <<EOF
---
name: test-flat
description: Test skill using flat structure
---

# Test Flat Skill
This is a test skill using standard Claude structure.
EOF

echo "Standard instructions" > .claude/skills/test-flat/reference.md
echo "Standard examples" > .claude/skills/test-flat/examples.md
```

**Enhanced structure**:
```bash
mkdir -p .claude/skills/test-domain/test-nested/instructions
mkdir -p .claude/skills/test-domain/test-nested/resources
cat > .claude/skills/test-domain/test-nested/SKILL.md <<EOF
---
name: test-nested
description: Test skill using nested structure
domain: test-domain
category: testing
---

# Test Nested Skill
This is a test skill using enhanced structure.
EOF

echo "Enhanced instructions" > .claude/skills/test-domain/test-nested/instructions/main.md
echo "Enhanced examples" > .claude/skills/test-domain/test-nested/resources/examples.md
```

### Test Loading

```python
from pathlib import Path
from agent import SkillsLoader

loader = SkillsLoader(skills_dir=Path(".claude/skills"))

# Test flat structure
flat_metadata = loader.load_skill_metadata("test-flat")
print(f"Flat skill: {flat_metadata.name}, Structure: {flat_metadata.is_flat_structure}")
# Output: Flat skill: test-flat, Structure: True

flat_instructions = loader.load_skill_instructions("test-flat", "reference.md")
print(f"Instructions: {flat_instructions[:30]}...")
# Output: Instructions: Standard instructions...

# Test nested structure
nested_metadata = loader.load_skill_metadata("test-domain/test-nested")
print(f"Nested skill: {nested_metadata.name}, Structure: {nested_metadata.is_flat_structure}")
# Output: Nested skill: test-nested, Structure: False

nested_instructions = loader.load_skill_instructions("test-domain/test-nested", "main.md")
print(f"Instructions: {nested_instructions[:30]}...")
# Output: Instructions: Enhanced instructions...

# Test listing both
all_skills = loader.list_skills()
print(f"Total skills: {len(all_skills)}")
# Output: Total skills: 2 (includes both flat and nested)
```

## Performance Considerations

### Both Structures Use Progressive Disclosure

**Flat structure**:
```
Load order:
1. SKILL.md metadata (200 bytes) - instant
2. reference.md (5 KB) - on-demand
3. examples.md (3 KB) - on-demand
```

**Nested structure**:
```
Load order:
1. SKILL.md metadata (200 bytes) - instant
2. instructions/capture.md (5 KB) - on-demand
3. resources/examples.md (3 KB) - on-demand
```

**Same performance characteristics!** The only difference is organization.

### Caching Works for Both

```python
# First load: reads from disk
metadata1 = loader.load_skill_metadata("meeting-notes")  # 5ms

# Second load: cached
metadata2 = loader.load_skill_metadata("meeting-notes")  # 0.1ms (50x faster!)

# Same for nested
metadata3 = loader.load_skill_metadata("change-agent/meeting-minutes")  # 5ms
metadata4 = loader.load_skill_metadata("change-agent/meeting-minutes")  # 0.1ms
```

## Troubleshooting

### Issue: "Skill file not found"

**Cause**: Wrong path format for structure type

**Solution**:
```python
# WRONG: Using flat path for nested skill
loader.load_skill_metadata("meeting-minutes")
# Error: Skill file not found

# RIGHT: Use full path
loader.load_skill_metadata("change-agent/meeting-minutes")

# WRONG: Using nested path for flat skill
loader.load_skill_metadata("general/meeting-notes")
# Error: Skill file not found

# RIGHT: Use flat path
loader.load_skill_metadata("meeting-notes")
```

### Issue: Instructions not found

**Cause**: Using wrong filename for structure type

**Solution**:
```python
# Standard structure: use "reference.md"
instructions = loader.load_skill_instructions("meeting-notes", "reference.md")

# Enhanced structure: use actual filename
instructions = loader.load_skill_instructions("change-agent/meeting-minutes", "capture.md")
```

### Issue: Skills not appearing in list

**Check**:
1. SKILL.md exists: `ls .claude/skills/*/SKILL.md`
2. YAML frontmatter valid: Check for `---` markers
3. name and description present in YAML

## Summary

| Feature | Standard Claude | Enhanced | Hybrid (Our Implementation) |
|---------|----------------|----------|----------------------------|
| **Structure** | Flat | Nested | Both supported ✅ |
| **File Organization** | Root level | Directories | Both supported ✅ |
| **YAML Fields** | name, description | + domain, category, etc. | All fields supported ✅ |
| **Claude Code Compatible** | Yes ✅ | Needs conversion ⚠️ | Standard mode: Yes ✅ |
| **Scales to 100+ skills** | Poor ❌ | Excellent ✅ | Excellent ✅ |
| **Progressive Disclosure** | Yes ✅ | Yes ✅ | Yes ✅ |
| **Filtering/Browsing** | Limited | Rich | Rich ✅ |

**Recommendation**: Use **enhanced structure** for Risk Agents (100+ skills planned), with the knowledge that you can always convert to standard structure if needed for Claude Code compatibility.

---

**Files Modified**:
- `backend/agent/skills_loader.py` (enhanced with hybrid support)

**Benefits**:
- ✅ Backward compatible with Claude's standard
- ✅ Forward compatible with our organizational needs
- ✅ No breaking changes to existing code
- ✅ Flexible for future requirements
