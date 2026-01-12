#!/usr/bin/env python3
"""
Match Gavin's profile against parsed job requirements.
Produces a match analysis for cover letter tailoring.
"""

import json
import os
import sys
import argparse
from typing import Optional

PROFILE_CACHE = os.path.join(os.path.dirname(__file__), '..', 'data', 'profile_cache.json')
JOBS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'jobs')


def load_profile() -> dict:
    """Load Gavin's profile from cache."""
    if not os.path.exists(PROFILE_CACHE):
        print("Profile cache not found. Run fetch_profile.py first.", file=sys.stderr)
        sys.exit(1)

    with open(PROFILE_CACHE, 'r') as f:
        return json.load(f)


def load_job(job_file: str) -> dict:
    """Load a parsed job file."""
    # Check if it's an absolute path or relative to jobs dir
    if os.path.isabs(job_file):
        filepath = job_file
    else:
        filepath = os.path.join(JOBS_DIR, job_file)

    if not os.path.exists(filepath):
        print(f"Job file not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    with open(filepath, 'r') as f:
        return json.load(f)


def match_technical_skills(profile: dict, job_reqs: list) -> dict:
    """Match technical skills from job against profile."""
    # Gavin's technical skills (flattened from profile)
    gavin_skills = set()

    # Add from skills section
    for skill_list in profile.get('skills', {}).values():
        for skill in skill_list:
            gavin_skills.add(skill.lower())

    # Add from projects
    for project in profile.get('projects', []):
        for tech in project.get('tech', []):
            gavin_skills.add(tech.lower())

    # Skill mappings (job requirement -> Gavin's equivalent)
    skill_mappings = {
        'python': ['python', 'django', 'flask'],
        'ai': ['ai', 'artificial intelligence', 'claude ai', 'llm'],
        'ml': ['machine learning', 'ml'],
        'machine learning': ['machine learning', 'ml', 'ai'],
        'leadership': ['leadership', 'team lead', 'managing director', '300+ person'],
        'risk management': ['risk management', 'market risk', 'credit risk', 'operational risk'],
        'sql': ['sql', 'data'],
        'data': ['data architecture', 'data governance', 'data analysis'],
        'cloud': ['aws', 'azure', 'gcp'],
        'typescript': ['typescript', 'next.js'],
        'javascript': ['javascript', 'react', 'next.js'],
    }

    matches = {
        "strong_matches": [],
        "partial_matches": [],
        "gaps": [],
        "evidence": {}
    }

    for req in job_reqs:
        req_lower = req.lower()
        found = False

        # Check direct match
        for skill in gavin_skills:
            if req_lower in skill or skill in req_lower:
                matches["strong_matches"].append(req)
                matches["evidence"][req] = skill
                found = True
                break

        # Check mapped matches
        if not found and req_lower in skill_mappings:
            for mapped in skill_mappings[req_lower]:
                for skill in gavin_skills:
                    if mapped in skill:
                        matches["partial_matches"].append(req)
                        matches["evidence"][req] = f"{skill} (related to {req})"
                        found = True
                        break
                if found:
                    break

        if not found:
            matches["gaps"].append(req)

    return matches


def match_experience(profile: dict, job_reqs: list) -> dict:
    """Match experience requirements."""
    matches = {
        "strong_matches": [],
        "partial_matches": [],
        "gaps": [],
        "evidence": {}
    }

    # Gavin's experience level indicators
    experience_indicators = {
        "senior": "Managing Director at Barclays Capital, Head of Risk Infrastructure at ICBC",
        "lead": "Led 300+ person teams, Programme Manager at Nordea",
        "director": "Director at Deutsche Bank, Managing Director at Barclays",
        "head": "Head of Risk Infrastructure at ICBC Standard Bank",
        "vp": "VP/Programme Manager at Nordea",
        "principal": "Principal level roles across Barclays, Deutsche Bank",
        "10+ years": "30+ years financial services experience",
        "15+ years": "30+ years financial services experience",
        "proven track record": "Lehman integration, Nordea transformation, Barings/Daiwa investigations",
        "demonstrated experience": "Multiple successful large-scale transformations"
    }

    for req in job_reqs:
        req_lower = req.lower().strip()
        found = False

        for indicator, evidence in experience_indicators.items():
            if indicator in req_lower:
                matches["strong_matches"].append(req)
                matches["evidence"][req] = evidence
                found = True
                break

        if not found:
            # Check for years pattern
            import re
            years_match = re.search(r'(\d+)', req_lower)
            if years_match:
                years_needed = int(years_match.group(1))
                if years_needed <= 30:  # Gavin has 30+ years
                    matches["strong_matches"].append(req)
                    matches["evidence"][req] = f"30+ years experience (exceeds {years_needed} years required)"
                    found = True

        if not found:
            matches["partial_matches"].append(req)

    return matches


def match_domain(profile: dict, job_reqs: list) -> dict:
    """Match domain knowledge requirements."""
    matches = {
        "strong_matches": [],
        "partial_matches": [],
        "gaps": [],
        "evidence": {}
    }

    # Gavin's domain expertise with evidence
    domain_expertise = {
        "financial services": "30+ years across Barclays, Deutsche Bank, Nordea, ICBC, Arthur Andersen",
        "banking": "Tier-1 banks: Barclays Capital, Deutsche Bank, ICBC Standard Bank",
        "risk management": "Head of Risk Infrastructure, CRO team leadership, Basel implementations",
        "capital markets": "Managing Director at Barclays Capital, Deutsche Bank",
        "trading": "Front-to-back systems transformation at Nordea",
        "regulatory": "Basel II/III, FRTB, BCBS239, FSA/Fed/SEC primary contact",
        "compliance": "Basel implementations, regulatory reporting, internal model approvals",
        "audit": "Arthur Andersen audit practice, forensic investigations",
        "consulting": "Stream Financial co-founder, Arthur Andersen consulting",
        "enterprise": "Enterprise-wide transformations at Barclays, Nordea, ICBC",
        "fintech": "Stream Financial co-founder, Risk Agents platform development"
    }

    for req in job_reqs:
        req_lower = req.lower()
        found = False

        for domain, evidence in domain_expertise.items():
            if domain in req_lower or req_lower in domain:
                matches["strong_matches"].append(req)
                matches["evidence"][req] = evidence
                found = True
                break

        if not found:
            matches["gaps"].append(req)

    return matches


def generate_match_analysis(profile: dict, job: dict) -> dict:
    """Generate comprehensive match analysis."""
    reqs = job.get("requirements", {})

    # Run all matchers
    tech_match = match_technical_skills(profile, reqs.get("technical_skills", []))
    exp_match = match_experience(profile, reqs.get("experience_level", []))
    domain_match = match_domain(profile, reqs.get("domain_knowledge", []))

    # Calculate overall score
    total_reqs = (len(reqs.get("technical_skills", [])) +
                  len(reqs.get("experience_level", [])) +
                  len(reqs.get("domain_knowledge", [])))

    strong_matches = (len(tech_match["strong_matches"]) +
                      len(exp_match["strong_matches"]) +
                      len(domain_match["strong_matches"]))

    partial_matches = (len(tech_match["partial_matches"]) +
                       len(exp_match["partial_matches"]) +
                       len(domain_match["partial_matches"]))

    if total_reqs > 0:
        match_score = int((strong_matches + partial_matches * 0.5) / total_reqs * 100)
    else:
        match_score = 75  # Default if we couldn't extract requirements

    # Identify key selling points for this role
    selling_points = []

    if any('ai' in r.lower() or 'ml' in r.lower() for r in reqs.get("technical_skills", [])):
        selling_points.append({
            "point": "Hands-on AI Implementation Experience",
            "evidence": "Personal AI Infrastructure with 15 agents, Risk Agents platform, Credit Risk Workflow app"
        })

    if any('risk' in r.lower() for r in reqs.get("domain_knowledge", [])):
        selling_points.append({
            "point": "Deep Risk Management Expertise",
            "evidence": "30+ years risk management, Head of Risk Infrastructure, Basel implementations"
        })

    if any('leader' in r.lower() or 'senior' in r.lower() for r in reqs.get("experience_level", [])):
        selling_points.append({
            "point": "Proven Leadership at Scale",
            "evidence": "Led 300+ person teams, Managing Director at Barclays Capital"
        })

    if any('transform' in r.lower() or 'change' in r.lower() for r in reqs.get("soft_skills", [])):
        selling_points.append({
            "point": "Digital Transformation Track Record",
            "evidence": "Nordea EUR125M transformation, Lehman integration in 3 months"
        })

    # Always include the unique differentiator
    selling_points.append({
        "point": "Unique Risk + AI + Leadership Combination",
        "evidence": "Rare combination of senior risk management leadership with hands-on AI implementation"
    })

    analysis = {
        "job_info": {
            "company": job.get("company"),
            "role": job.get("role"),
            "location": job.get("location")
        },
        "overall_match_score": match_score,
        "match_level": "Excellent" if match_score >= 80 else "Strong" if match_score >= 60 else "Moderate" if match_score >= 40 else "Low",
        "technical_skills": tech_match,
        "experience": exp_match,
        "domain_knowledge": domain_match,
        "key_selling_points": selling_points,
        "gaps_to_address": {
            "technical": tech_match["gaps"],
            "experience": exp_match["gaps"],
            "domain": domain_match["gaps"]
        },
        "cover_letter_focus": [],
        "recommended_projects_to_highlight": []
    }

    # Determine cover letter focus areas
    if match_score >= 60:
        analysis["cover_letter_focus"] = [
            "Lead with strongest matches to job requirements",
            "Emphasize unique differentiators early",
            "Provide concrete metrics and achievements",
            "Address any gaps by highlighting transferable skills"
        ]
    else:
        analysis["cover_letter_focus"] = [
            "Focus on transferable skills and learning agility",
            "Emphasize passion and genuine interest in the role",
            "Highlight relevant adjacent experience",
            "Show commitment to filling any skill gaps"
        ]

    # Recommend projects based on job type
    if any('ai' in r.lower() for r in reqs.get("technical_skills", [])):
        analysis["recommended_projects_to_highlight"] = [
            "Risk Agents - AI-powered risk intelligence platform",
            "Personal AI Infrastructure - 15 specialized agents",
            "Credit Risk Workflow - 60% efficiency improvement"
        ]
    else:
        analysis["recommended_projects_to_highlight"] = [
            "Lehman Brothers Integration - Crisis leadership",
            "Nordea Transformation - EUR125M programme",
            "ICBC Data Platform - Enterprise architecture"
        ]

    return analysis


def main():
    parser = argparse.ArgumentParser(description='Match profile against job requirements')
    parser.add_argument('--job-file', type=str, help='Path to parsed job JSON file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    # Load profile
    profile = load_profile()

    # Load job
    if args.job_file:
        job = load_job(args.job_file)
    else:
        # Try to use most recent job file
        if os.path.exists(JOBS_DIR):
            files = sorted(os.listdir(JOBS_DIR), reverse=True)
            if files:
                job = load_job(files[0])
                print(f"Using most recent job file: {files[0]}", file=sys.stderr)
            else:
                print("No job files found. Run parse_job.py first.", file=sys.stderr)
                sys.exit(1)
        else:
            print("No jobs directory found. Run parse_job.py first.", file=sys.stderr)
            sys.exit(1)

    # Generate analysis
    analysis = generate_match_analysis(profile, job)

    # Output
    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print(f"\n{'='*60}")
        print("PROFILE-JOB MATCH ANALYSIS")
        print(f"{'='*60}\n")

        info = analysis["job_info"]
        if info["company"]:
            print(f"Company: {info['company']}")
        if info["role"]:
            print(f"Role: {info['role']}")
        if info["location"]:
            print(f"Location: {info['location']}")

        print(f"\n{'='*40}")
        print(f"OVERALL MATCH: {analysis['overall_match_score']}% ({analysis['match_level']})")
        print(f"{'='*40}")

        print("\nSTRONG MATCHES:")
        for skill in analysis["technical_skills"]["strong_matches"]:
            evidence = analysis["technical_skills"]["evidence"].get(skill, "")
            print(f"  ✓ {skill}: {evidence}")
        for exp in analysis["experience"]["strong_matches"]:
            evidence = analysis["experience"]["evidence"].get(exp, "")
            print(f"  ✓ {exp}: {evidence}")
        for domain in analysis["domain_knowledge"]["strong_matches"]:
            evidence = analysis["domain_knowledge"]["evidence"].get(domain, "")
            print(f"  ✓ {domain}: {evidence}")

        if analysis["gaps_to_address"]["technical"] or analysis["gaps_to_address"]["domain"]:
            print("\nGAPS TO ADDRESS:")
            for gap in analysis["gaps_to_address"]["technical"]:
                print(f"  △ {gap}")
            for gap in analysis["gaps_to_address"]["domain"]:
                print(f"  △ {gap}")

        print("\nKEY SELLING POINTS FOR COVER LETTER:")
        for i, point in enumerate(analysis["key_selling_points"], 1):
            print(f"  {i}. {point['point']}")
            print(f"     Evidence: {point['evidence']}")

        print("\nPROJECTS TO HIGHLIGHT:")
        for project in analysis["recommended_projects_to_highlight"]:
            print(f"  • {project}")

        print("\nCOVER LETTER FOCUS:")
        for focus in analysis["cover_letter_focus"]:
            print(f"  → {focus}")


if __name__ == '__main__':
    main()
