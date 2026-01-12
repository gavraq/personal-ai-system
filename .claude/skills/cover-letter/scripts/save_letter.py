#!/usr/bin/env python3
"""
Save generated cover letters to Obsidian vault with proper formatting.
"""

import os
import sys
import re
import argparse
from datetime import datetime

OBSIDIAN_VAULT = "/Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault"
DEFAULT_DIR = os.path.join(OBSIDIAN_VAULT, "Job & Career", "Cover Letters")


def sanitize_filename(name: str) -> str:
    """Clean a string for use as filename."""
    # Remove or replace invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:100]  # Limit length


def create_frontmatter(company: str, role: str, tags: list = None) -> str:
    """Create YAML frontmatter for the cover letter."""
    default_tags = ["cover-letter", "job-application"]
    if tags:
        default_tags.extend(tags)

    # Make tags lowercase with hyphens
    clean_tags = [re.sub(r'\s+', '-', t.lower()) for t in default_tags]

    frontmatter = f"""---
tags:
  - {chr(10) + '  - '.join(clean_tags)}
company: "{company}"
role: "{role}"
date: {datetime.now().strftime('%Y-%m-%d')}
status: draft
---
"""
    return frontmatter


def save_cover_letter(content: str, company: str, role: str,
                      output_dir: str = None, tags: list = None) -> str:
    """Save cover letter to file and return path."""

    # Use default directory if not specified
    if output_dir is None:
        output_dir = DEFAULT_DIR

    # Create directory if needed
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    company_clean = sanitize_filename(company) if company else "Unknown"
    role_clean = sanitize_filename(role) if role else "Role"
    date_str = datetime.now().strftime("%Y-%m-%d")

    filename = f"Cover Letter - {company_clean} - {role_clean} - {date_str}.md"
    filepath = os.path.join(output_dir, filename)

    # Check if file exists and add suffix if needed
    counter = 1
    while os.path.exists(filepath):
        filename = f"Cover Letter - {company_clean} - {role_clean} - {date_str} ({counter}).md"
        filepath = os.path.join(output_dir, filename)
        counter += 1

    # Create full document with frontmatter
    frontmatter = create_frontmatter(company, role, tags)

    full_content = f"""{frontmatter}
# Cover Letter: {role} at {company}

## Application Details
- **Company**: {company}
- **Role**: {role}
- **Date**: {date_str}
- **Status**: Draft

---

{content}

---

## Notes
- Created with cover-letter skill
- Review and personalize before sending
- Update status to "sent" after submission

## Related
- [[Job Search Tracking]]
- [[Career Transition Notes]]
"""

    # Write file
    with open(filepath, 'w') as f:
        f.write(full_content)

    return filepath


def main():
    parser = argparse.ArgumentParser(description='Save cover letter to Obsidian vault')
    parser.add_argument('--company', type=str, required=True, help='Company name')
    parser.add_argument('--role', type=str, required=True, help='Role title')
    parser.add_argument('--file', type=str, help='File containing cover letter content')
    parser.add_argument('--output-dir', type=str, help='Output directory (default: Obsidian vault)')
    parser.add_argument('--tags', type=str, nargs='+', help='Additional tags')
    args = parser.parse_args()

    # Get content
    if args.file:
        with open(args.file, 'r') as f:
            content = f.read()
    else:
        print("Reading cover letter content from stdin (paste and press Ctrl+D):", file=sys.stderr)
        content = sys.stdin.read()

    if not content.strip():
        print("Error: No content provided", file=sys.stderr)
        sys.exit(1)

    # Save
    filepath = save_cover_letter(
        content=content,
        company=args.company,
        role=args.role,
        output_dir=args.output_dir,
        tags=args.tags
    )

    print(f"Cover letter saved to: {filepath}")


if __name__ == '__main__':
    main()
