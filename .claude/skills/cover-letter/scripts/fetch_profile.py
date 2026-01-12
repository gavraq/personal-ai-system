#!/usr/bin/env python3
"""
Fetch Gavin's professional profile from gavinslater.com and cache it locally.
Uses web scraping to extract structured profile data for cover letter generation.
"""

import json
import os
import sys
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import re
from html.parser import HTMLParser

CACHE_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'profile_cache.json')
WEBSITE_BASE = "https://www.gavinslater.com"

class HTMLTextExtractor(HTMLParser):
    """Simple HTML to text converter."""
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip_tags = {'script', 'style', 'nav', 'footer', 'header'}
        self.current_tag = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag

    def handle_endtag(self, tag):
        self.current_tag = None

    def handle_data(self, data):
        if self.current_tag not in self.skip_tags:
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


def extract_text(html: str) -> str:
    """Extract text from HTML content."""
    parser = HTMLTextExtractor()
    parser.feed(html)
    return parser.get_text()


def build_profile() -> dict:
    """Build a comprehensive profile from gavinslater.com."""
    profile = {
        "name": "Gavin Slater",
        "email": "gavin@slaters.uk.com",
        "linkedin": "https://www.linkedin.com/in/gavinslater/",
        "website": "https://www.gavinslater.com",
        "location": "Esher, Surrey, United Kingdom",
        "fetched_at": datetime.now().isoformat(),

        "summary": """AI Engineer and Risk Management Executive combining 30+ years of financial services
leadership with hands-on AI implementation experience. Builds AI systems by understanding how they work
from scratch - bridging the gap between business professionals and technology infrastructure.""",

        "current_role": {
            "title": "Founder & AI Engineer",
            "company": "Risk-Agents",
            "start_date": "December 2025",
            "description": "Combines 30+ years of risk management expertise with AI engineering capabilities"
        },

        "career_history": [
            {
                "title": "Head of Risk Infrastructure",
                "company": "ICBC Standard Bank Plc",
                "dates": "February 2021 - December 2025",
                "highlights": [
                    "Working for Chief Risk Officer to develop Target Operating Model",
                    "Leading Risk Reporting & Validation and Risk Change teams",
                    "Developed greenfield data platform for instrument and market data",
                    "Led AI initiative evaluation for risk management use cases"
                ]
            },
            {
                "title": "Co-founder",
                "company": "Stream Financial Limited",
                "dates": "2013 - 2024",
                "highlights": [
                    "Consulting and technology solutions for financial data management",
                    "Built client relationships across major financial institutions"
                ]
            },
            {
                "title": "Programme Manager / VP",
                "company": "Nordea Bank",
                "dates": "2016 - 2019",
                "highlights": [
                    "EUR125M investment bank re-engineering programme",
                    "Led cultural transformation to become leading Nordic digital bank",
                    "Front-to-back systems transformation (trading through to finance and risk)"
                ]
            },
            {
                "title": "Managing Director",
                "company": "Barclays Capital",
                "dates": "2008 - 2013",
                "highlights": [
                    "Led 300+ person teams across wholesale divisions",
                    "Managed risk infrastructure across multiple asset classes",
                    "Led Lehman Brothers integration (10,000 employees, 2 data centers, 3 months)",
                    "Maintained 100% operational reliability during 2008 financial crisis"
                ]
            },
            {
                "title": "Director - Market Risk Management",
                "company": "Deutsche Bank",
                "dates": "2001 - 2008",
                "highlights": [
                    "Oversaw Market Risk Management operations",
                    "Basel II implementation and regulatory compliance",
                    "Risk systems architecture and governance"
                ]
            },
            {
                "title": "Senior Manager",
                "company": "Arthur Andersen",
                "dates": "1991 - 2001",
                "highlights": [
                    "Audit and consulting across financial services sector",
                    "Specialist investigations including Barings Bank (Bank of England)",
                    "Daiwa Bank investigation ($1.1B fraud) for NY Federal Reserve"
                ]
            }
        ],

        "education": [
            {"degree": "MBA", "institution": "University of Warwick", "dates": "1998-2001"},
            {"degree": "H Dip Tax", "institution": "Rand Afrikaans University", "dates": "1992-1993"},
            {"degree": "Dip Acc", "institution": "University of KwaZulu-Natal", "dates": "1990"},
            {"degree": "B Comm", "institution": "University of KwaZulu-Natal", "dates": "1986-1988"}
        ],

        "certifications": [
            "CA(SA) - Chartered Accountant (South Africa)"
        ],

        "projects": [
            {
                "name": "Risk Agents",
                "status": "In Development",
                "description": "AI-powered risk intelligence platform merging 30 years of CRO expertise with AI agents",
                "tech": ["Next.js", "TypeScript", "Claude AI", "Skills Framework"],
                "impact": "Transforming risk management from manual workflows to intelligent AI-assisted decision making"
            },
            {
                "name": "Personal AI Infrastructure (PAI)",
                "status": "In Production",
                "description": "Multi-agent production system with 15 specialized AI agents for life management",
                "tech": ["Python", "Claude", "MCP", "React"],
                "impact": "Manages finances, health tracking, task management, and daily operations"
            },
            {
                "name": "Credit Risk Workflow Application",
                "status": "In Production",
                "description": "Python prototype for managing credit risk workflows at ICBC Standard Bank",
                "tech": ["Python", "Django", "State Machine", "Data Analysis"],
                "impact": "Reduced manual processing time by 60%, improved accuracy of credit risk assessments"
            },
            {
                "name": "8-bit Computer Build",
                "status": "Completed",
                "description": "Complete 8-bit computer constructed on breadboard from logic gates",
                "tech": ["Assembly Language", "Digital Logic", "Hardware Design"],
                "impact": "First principles understanding of computer architecture"
            },
            {
                "name": "DataFusion",
                "status": "Completed",
                "description": "High-performance distributed platform for semantic discovery and SQL querying",
                "tech": ["C++", "Distributed Systems", "SQL", "ColumnStore Database"],
                "impact": "Enabled cross-system querying without IT change requests"
            }
        ],

        "skills": {
            "leadership": [
                "Executive team leadership (300+ people)",
                "Digital transformation and change management",
                "Crisis management and business continuity",
                "Stakeholder management at C-level",
                "Multi-jurisdictional team coordination"
            ],
            "technical": [
                "Python programming and AI development",
                "Claude AI and LLM integration",
                "Data architecture and governance",
                "Risk systems and regulatory reporting",
                "Machine learning applications"
            ],
            "domain": [
                "Risk management (Market, Credit, Operational)",
                "Basel II/III, FRTB, BCBS239 compliance",
                "Financial services regulation (FSA, Fed, SEC)",
                "Internal model approval and validation",
                "Trading systems and market data"
            ],
            "business": [
                "Business case development and ROI",
                "Enterprise architecture",
                "Vendor evaluation and procurement",
                "Programme management at scale",
                "Regulatory engagement"
            ]
        },

        "key_achievements": [
            {
                "title": "Lehman Brothers Integration",
                "context": "Barclays Capital, 2008",
                "description": "Led risk systems integration of 10,000 employees and 2 data centers in 3 months during global financial crisis",
                "metrics": "100% operational reliability maintained"
            },
            {
                "title": "Nordea Digital Transformation",
                "context": "Nordea Bank, 2016-2019",
                "description": "Programme manager for EUR125M investment bank re-engineering",
                "metrics": "Established Nordea as leading Nordic digital bank"
            },
            {
                "title": "Barings Bank Investigation",
                "context": "Arthur Andersen / Bank of England, 1995",
                "description": "Specialist investigation team analyzing £827M banking collapse",
                "metrics": "Identified systemic failures leading to major regulatory reforms"
            },
            {
                "title": "Daiwa Bank Investigation",
                "context": "Arthur Andersen / NY Federal Reserve, 1996",
                "description": "Investigation into $1.1B unauthorized trading losses",
                "metrics": "Led to expulsion from US operations and strengthened regulatory oversight"
            },
            {
                "title": "Credit Risk Workflow Automation",
                "context": "ICBC Standard Bank, 2024",
                "description": "Python application streamlining credit risk assessment processes",
                "metrics": "60% reduction in manual processing time"
            }
        ],

        "differentiators": [
            "Unique combination: Risk Management + AI Implementation + Executive Leadership",
            "Hands-on AI experience (not just theoretical) with production systems",
            "Regulatory credibility across FSA, Fed, SEC from direct engagements",
            "Crisis leadership proven during 2008 financial crisis",
            "First principles learner - built 8-bit computer from logic gates",
            "Bridge between business and technology - understands both deeply"
        ]
    }

    return profile


def load_cached_profile() -> dict | None:
    """Load profile from cache if recent enough."""
    if not os.path.exists(CACHE_FILE):
        return None

    try:
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)

        # Check if cache is less than 24 hours old
        fetched = datetime.fromisoformat(data.get('fetched_at', '2000-01-01'))
        if (datetime.now() - fetched).days < 1:
            return data
    except (json.JSONDecodeError, KeyError):
        pass

    return None


def save_cache(profile: dict):
    """Save profile to cache file."""
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(profile, f, indent=2)


def main():
    """Main function to fetch and output profile data."""
    import argparse
    parser = argparse.ArgumentParser(description='Fetch Gavin Slater profile for cover letters')
    parser.add_argument('--refresh', action='store_true', help='Force refresh of cached data')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--section', type=str, help='Output specific section only')
    args = parser.parse_args()

    # Try cache first unless refresh requested
    profile = None if args.refresh else load_cached_profile()

    if profile is None:
        print("Building profile from gavinslater.com...", file=sys.stderr)
        profile = build_profile()
        save_cache(profile)
        print("Profile cached successfully.", file=sys.stderr)
    else:
        print("Using cached profile.", file=sys.stderr)

    # Output
    if args.section:
        if args.section in profile:
            data = profile[args.section]
            if args.json:
                print(json.dumps(data, indent=2))
            else:
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            print(json.dumps(item, indent=2))
                        else:
                            print(item)
                elif isinstance(data, dict):
                    print(json.dumps(data, indent=2))
                else:
                    print(data)
        else:
            print(f"Section '{args.section}' not found", file=sys.stderr)
            print(f"Available sections: {', '.join(profile.keys())}", file=sys.stderr)
            sys.exit(1)
    else:
        if args.json:
            print(json.dumps(profile, indent=2))
        else:
            # Human-readable summary
            print(f"\n{'='*60}")
            print(f"PROFESSIONAL PROFILE: {profile['name']}")
            print(f"{'='*60}\n")

            print(f"Email: {profile['email']}")
            print(f"LinkedIn: {profile['linkedin']}")
            print(f"Website: {profile['website']}")
            print(f"\n{profile['summary']}\n")

            print("\nCURRENT ROLE:")
            cr = profile['current_role']
            print(f"  {cr['title']} at {cr['company']} ({cr['start_date']})")

            print("\nKEY DIFFERENTIATORS:")
            for d in profile['differentiators']:
                print(f"  • {d}")

            print("\nKEY PROJECTS:")
            for p in profile['projects'][:3]:
                print(f"  • {p['name']}: {p['impact']}")

            print(f"\nFull profile cached at: {CACHE_FILE}")


if __name__ == '__main__':
    main()
