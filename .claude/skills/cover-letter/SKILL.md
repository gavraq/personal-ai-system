---
name: cover-letter
description: Generate tailored cover letters for job applications by analyzing job requirements and matching them with Gavin's skills and experience from gavinslater.com. Use when user asks to write, create, or draft a cover letter for a job application, or when applying for a position.
---

# Cover Letter Generation Skill

## Purpose
Generate compelling, personalized cover letters that match Gavin's skills and experience to specific job requirements. Uses profile data from gavinslater.com and example cover letters to maintain consistent professional voice.

## When to Use
- User shares a job posting and asks for a cover letter
- User mentions "apply for" or "application" for a job
- User asks to draft a cover letter for a specific role
- Job search agent identifies a high-match opportunity

## Workflow

### Step 1: Parse Job Posting
Extract key requirements from the job posting:
- Company name and role title
- Required skills and qualifications
- Desired experience and background
- Key responsibilities
- Company values or culture indicators
- Specific keywords and terminology

Run the job parser script:
```bash
python3 /Users/gavinslater/projects/life/.claude/skills/cover-letter/scripts/parse_job.py --url "JOB_URL"
# Or with clipboard content
python3 /Users/gavinslater/projects/life/.claude/skills/cover-letter/scripts/parse_job.py --text "PASTED_JOB_TEXT"
```

### Step 2: Fetch Profile Data
Retrieve Gavin's professional profile from gavinslater.com:
```bash
python3 /Users/gavinslater/projects/life/.claude/skills/cover-letter/scripts/fetch_profile.py
```

This fetches and caches:
- Professional summary
- Career history and achievements
- Key projects (Risk Agents, PAI, Credit Risk Workflow, etc.)
- Skills and competencies
- Education and certifications

### Step 3: Match Skills to Requirements
Analyze alignment between job requirements and Gavin's profile:
```bash
python3 /Users/gavinslater/projects/life/.claude/skills/cover-letter/scripts/match_skills.py --job-file "parsed_job.json"
```

Output includes:
- Strong matches (directly relevant experience)
- Partial matches (transferable skills)
- Gaps to address (areas to acknowledge or reframe)
- Unique differentiators to highlight

### Step 4: Generate Cover Letter
Using the analysis, generate a tailored cover letter following Gavin's established style:

**Structure (from example letters):**
1. Opening hook - specific reference to company/role that shows genuine interest
2. "Why am I a good fit" section with 3-4 key areas
3. Detailed evidence sections with concrete examples
4. Practical AI/technical hands-on experience section
5. Change management/leadership track record
6. Understanding of buyer/industry perspective
7. Strong closing with next steps

**Writing Style Guidelines:**
- Professional but personable tone
- Concrete achievements with metrics where possible
- Bridge between business and technical domains
- Emphasize unique combination: Risk Management + AI + Leadership
- Include practical hands-on AI experience (Personal Consultant, Risk Agents)
- Reference specific transformations (Nordea, Barclays/Lehman, ICBC)
- Use bullet points for readability
- Keep to 1-2 pages

### Step 5: Output Options
Save the generated cover letter:
```bash
# Save to Obsidian vault
python3 /Users/gavinslater/projects/life/.claude/skills/cover-letter/scripts/save_letter.py --company "COMPANY" --role "ROLE"
```

Default location: `/Users/gavinslater/Library/Mobile Documents/iCloud~md~obsidian/Documents/GavinsiCloudVault/Job & Career/Cover Letters/`

Filename format: `Cover Letter - {Company} - {Role} - {Date}.md`

## Gavin's Key Selling Points

### Unique Value Proposition
"Bridge between business professionals and AI/technology infrastructure - combining 30+ years of risk management leadership with hands-on AI implementation experience"

### Core Differentiators
1. **Scale Leadership**: Led 300+ person teams at Barclays Capital
2. **Crisis Experience**: Lehman integration during 2008 financial crisis
3. **Digital Transformation**: Nordea's EUR125M investment bank transformation
4. **Regulatory Authority**: Primary contact with FSA, Fed, SEC; Basel implementations
5. **Hands-on AI**: Personal AI Infrastructure with 15 agents, Risk Agents platform
6. **Technical Credibility**: Python development, Credit Risk Workflow app (60% efficiency gain)

### Career Highlights for Cover Letters
- **Barings Investigation**: Bank of England specialist team, £827M collapse
- **Daiwa Investigation**: NY Federal Reserve, $1.1B fraud
- **Barclays/Lehman**: 10,000 employees, 2 data centers, 3-month integration
- **Nordea Transformation**: EUR125M programme, cultural transformation
- **ICBC Standard Bank**: Greenfield data platform, Target Operating Model

### Technical Projects to Reference
- Risk Agents (Next.js, TypeScript, Claude AI)
- Personal AI Infrastructure (15 agents, Python, MCP)
- Credit Risk Workflow App (Python, Django, 60% time reduction)
- 8-bit Computer Build (first principles learning)

### Education & Credentials
- MBA, University of Warwick
- CA(SA) - Chartered Accountant
- 30+ years financial services

## Template Sections

### Opening Variations
- Reference keynote/event (if applicable)
- Reference company's AI strategy or transformation
- Reference specific product or service
- Reference mutual connection

### Evidence Sections
- "Practical hands-on experience" - current AI work
- "Deep financial services knowledge" - career history
- "Proven track record of change management" - specific programmes
- "Understanding the [buyer/industry] perspective" - relevant insights

### Closing Variations
- Specific request for interview
- Reference to enclosed CV
- Offer to discuss specific areas in detail
- Next steps suggestion

## File Locations
- `SKILL.md` - This skill definition
- `scripts/parse_job.py` - Job posting parser
- `scripts/fetch_profile.py` - Profile data fetcher
- `scripts/match_skills.py` - Skills matching engine
- `scripts/save_letter.py` - Letter saving utility
- `templates/cover_letter_template.md` - Base template
- `data/profile_cache.json` - Cached profile data
- `data/example_letters/` - Reference cover letters

## Example Invocations

**From Job URL:**
"Write a cover letter for this Anthropic role: [URL]"

**From Pasted Job Description:**
"Create a cover letter for this position at M&G: [pasted text]"

**Quick Application:**
"Apply for the AI Risk Manager role at Barclays - here's the job description..."

## Notes
- Always fetch fresh profile data for important applications
- Tailor technical depth based on role type (technical vs. business)
- Highlight Risk + AI combination for financial services roles
- For AI-native companies, emphasize hands-on Claude experience
- For traditional banks, emphasize regulatory and transformation experience
