#!/usr/bin/env python3
"""
Parse job postings from URLs or pasted text to extract structured requirements.
Outputs JSON with categorized requirements for cover letter matching.
"""

import json
import os
import re
import sys
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
import argparse

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'jobs')


class HTMLTextExtractor(HTMLParser):
    """Extract text from HTML, preserving some structure."""
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip_tags = {'script', 'style', 'nav', 'footer', 'meta', 'link'}
        self.current_tag = None
        self.in_skip = False

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag in self.skip_tags:
            self.in_skip = True
        if tag in ['p', 'br', 'div', 'h1', 'h2', 'h3', 'h4', 'li']:
            self.text.append('\n')

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.in_skip = False
        self.current_tag = None

    def handle_data(self, data):
        if not self.in_skip:
            text = data.strip()
            if text:
                self.text.append(text)

    def get_text(self):
        return ' '.join(self.text)


def fetch_url(url: str) -> str:
    """Fetch content from a URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8')
    except (URLError, HTTPError) as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return ""


def extract_text_from_html(html: str) -> str:
    """Convert HTML to plain text."""
    parser = HTMLTextExtractor()
    parser.feed(html)
    text = parser.get_text()
    # Clean up whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()


def extract_requirements(text: str) -> dict:
    """Extract structured requirements from job description text."""
    text_lower = text.lower()

    # Patterns for different requirement categories
    skill_patterns = [
        r'\b(python|java|javascript|typescript|sql|c\+\+|go|rust|scala)\b',
        r'\b(aws|azure|gcp|kubernetes|docker|terraform)\b',
        r'\b(machine learning|ml|ai|artificial intelligence|deep learning|nlp)\b',
        r'\b(tensorflow|pytorch|scikit-learn|keras|hugging face)\b',
        r'\b(react|angular|vue|node\.?js|django|flask|fastapi)\b',
        r'\b(pandas|numpy|spark|hadoop|databricks)\b',
        r'\b(git|ci/cd|jenkins|github actions)\b',
        r'\b(agile|scrum|kanban)\b',
        r'\b(risk management|compliance|regulatory|basel|frtb)\b',
        r'\b(leadership|management|team lead|people management)\b',
    ]

    # Experience patterns
    experience_patterns = [
        r'(\d+)\+?\s*years?\s*(of)?\s*(experience|exp)',
        r'(senior|lead|principal|director|head|vp|managing director)',
        r'(proven track record|demonstrated experience)',
    ]

    # Education patterns
    education_patterns = [
        r"\b(bachelor'?s?|master'?s?|mba|phd|doctorate)\b",
        r'\b(degree|qualification|certified|certification)\b',
        r'\b(computer science|engineering|mathematics|finance|business)\b',
    ]

    requirements = {
        "technical_skills": [],
        "experience_level": [],
        "education": [],
        "soft_skills": [],
        "domain_knowledge": [],
        "responsibilities": [],
        "keywords": []
    }

    # Extract technical skills
    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower)
        requirements["technical_skills"].extend([m if isinstance(m, str) else m[0] for m in matches])

    # Extract experience requirements
    for pattern in experience_patterns:
        matches = re.findall(pattern, text_lower)
        requirements["experience_level"].extend([' '.join(m) if isinstance(m, tuple) else m for m in matches])

    # Extract education requirements
    for pattern in education_patterns:
        matches = re.findall(pattern, text_lower)
        requirements["education"].extend(matches)

    # Common soft skills
    soft_skills = [
        'communication', 'leadership', 'collaboration', 'problem-solving',
        'analytical', 'strategic', 'stakeholder', 'presentation',
        'interpersonal', 'mentoring', 'influencing', 'negotiation'
    ]
    for skill in soft_skills:
        if skill in text_lower:
            requirements["soft_skills"].append(skill)

    # Domain knowledge
    domains = [
        'financial services', 'banking', 'fintech', 'risk management',
        'capital markets', 'trading', 'investment', 'regulatory',
        'compliance', 'audit', 'consulting', 'enterprise'
    ]
    for domain in domains:
        if domain in text_lower:
            requirements["domain_knowledge"].append(domain)

    # Clean up - deduplicate and sort
    for key in requirements:
        requirements[key] = sorted(list(set(requirements[key])))

    return requirements


def extract_company_role(text: str, url: str = None) -> dict:
    """Try to extract company name and role title."""
    info = {
        "company": None,
        "role": None,
        "location": None,
        "job_type": None
    }

    # Common patterns for titles
    title_patterns = [
        r'(?:job title|position|role)[:\s]*([^\n]+)',
        r'^#?\s*([A-Z][^.!?\n]{10,60})\s*$',  # Lines that look like titles
    ]

    # Common patterns for company
    company_patterns = [
        r'(?:company|employer|at)[:\s]*([^\n]+)',
        r'(?:join|work for|about)\s+([A-Z][a-zA-Z\s&]+?)(?:\s+is|\s+are|\.)',
    ]

    # Location patterns
    location_patterns = [
        r'(?:location|based in|office)[:\s]*([^\n]+)',
        r'\b(london|new york|san francisco|remote|hybrid)\b',
    ]

    text_lower = text.lower()

    for pattern in title_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            info["role"] = match.group(1).strip()
            break

    for pattern in company_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info["company"] = match.group(1).strip()
            break

    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info["location"] = match.group(1).strip()
            break

    # Job type
    if 'remote' in text_lower:
        info["job_type"] = "Remote"
    elif 'hybrid' in text_lower:
        info["job_type"] = "Hybrid"
    elif 'on-site' in text_lower or 'onsite' in text_lower:
        info["job_type"] = "On-site"

    return info


def parse_job(text: str, url: str = None) -> dict:
    """Parse a job posting into structured data."""
    requirements = extract_requirements(text)
    company_info = extract_company_role(text, url)

    parsed = {
        "source_url": url,
        "parsed_at": datetime.now().isoformat(),
        "company": company_info["company"],
        "role": company_info["role"],
        "location": company_info["location"],
        "job_type": company_info["job_type"],
        "requirements": requirements,
        "raw_text": text[:5000],  # Keep first 5000 chars for reference
        "word_count": len(text.split())
    }

    return parsed


def save_parsed_job(parsed: dict, company: str = None, role: str = None) -> str:
    """Save parsed job to file and return path."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate filename
    company_slug = (company or parsed.get("company") or "unknown").lower()
    company_slug = re.sub(r'[^a-z0-9]+', '-', company_slug)[:30]

    role_slug = (role or parsed.get("role") or "role").lower()
    role_slug = re.sub(r'[^a-z0-9]+', '-', role_slug)[:30]

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{company_slug}_{role_slug}_{date_str}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, 'w') as f:
        json.dump(parsed, f, indent=2)

    return filepath


def main():
    parser = argparse.ArgumentParser(description='Parse job posting for cover letter generation')
    parser.add_argument('--url', type=str, help='URL of job posting to fetch and parse')
    parser.add_argument('--text', type=str, help='Raw job description text')
    parser.add_argument('--file', type=str, help='File containing job description')
    parser.add_argument('--company', type=str, help='Override company name')
    parser.add_argument('--role', type=str, help='Override role title')
    parser.add_argument('--save', action='store_true', help='Save parsed job to file')
    parser.add_argument('--json', action='store_true', help='Output as JSON only')
    args = parser.parse_args()

    # Get job text
    text = None
    url = None

    if args.url:
        url = args.url
        print(f"Fetching job posting from: {url}", file=sys.stderr)
        html = fetch_url(url)
        if html:
            text = extract_text_from_html(html)
        else:
            print("Failed to fetch URL", file=sys.stderr)
            sys.exit(1)

    elif args.text:
        text = args.text

    elif args.file:
        with open(args.file, 'r') as f:
            text = f.read()

    else:
        # Read from stdin
        print("Reading job description from stdin (paste and press Ctrl+D when done):", file=sys.stderr)
        text = sys.stdin.read()

    if not text or len(text.strip()) < 50:
        print("Error: Job description too short or empty", file=sys.stderr)
        sys.exit(1)

    # Parse
    parsed = parse_job(text, url)

    # Apply overrides
    if args.company:
        parsed["company"] = args.company
    if args.role:
        parsed["role"] = args.role

    # Save if requested
    if args.save:
        filepath = save_parsed_job(parsed, args.company, args.role)
        print(f"Saved to: {filepath}", file=sys.stderr)

    # Output
    if args.json:
        print(json.dumps(parsed, indent=2))
    else:
        print(f"\n{'='*60}")
        print("PARSED JOB POSTING")
        print(f"{'='*60}\n")

        if parsed["company"]:
            print(f"Company: {parsed['company']}")
        if parsed["role"]:
            print(f"Role: {parsed['role']}")
        if parsed["location"]:
            print(f"Location: {parsed['location']}")
        if parsed["job_type"]:
            print(f"Type: {parsed['job_type']}")

        print(f"\nWord count: {parsed['word_count']}")

        reqs = parsed["requirements"]
        if reqs["technical_skills"]:
            print(f"\nTechnical Skills Required:")
            for skill in reqs["technical_skills"]:
                print(f"  • {skill}")

        if reqs["experience_level"]:
            print(f"\nExperience Level:")
            for exp in reqs["experience_level"]:
                print(f"  • {exp}")

        if reqs["education"]:
            print(f"\nEducation:")
            for edu in reqs["education"]:
                print(f"  • {edu}")

        if reqs["domain_knowledge"]:
            print(f"\nDomain Knowledge:")
            for domain in reqs["domain_knowledge"]:
                print(f"  • {domain}")

        if reqs["soft_skills"]:
            print(f"\nSoft Skills:")
            for skill in reqs["soft_skills"]:
                print(f"  • {skill}")

        print(f"\n{'='*60}")
        print("Use --json for machine-readable output")
        print("Use --save to save parsed job for later matching")


if __name__ == '__main__':
    main()
