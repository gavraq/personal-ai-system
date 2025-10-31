#!/usr/bin/env python3
"""
LinkedIn Profile Manager for Personal Consultant System

This module manages LinkedIn profile data and job search integration.
Since LinkedIn API requires expensive partnerships, this uses manual profile 
management and web search techniques that respect LinkedIn's terms of service.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re

class LinkedInProfileManager:
    """
    Manages LinkedIn profile data and job search capabilities.
    
    Uses manual profile management and legitimate web search methods
    to provide LinkedIn integration while respecting terms of service.
    """
    
    def __init__(self):
        self.profile_file = Path(__file__).parent / "gavin_linkedin_profile.json"
        self.job_searches_file = Path(__file__).parent / "linkedin_job_searches.json"
        self.profile_url = "https://www.linkedin.com/in/gavinslater/"
        
        # Initialize profile data
        self.profile_data = self._load_profile_data()
        self.job_search_history = self._load_job_search_history()
    
    def _load_profile_data(self) -> Dict[str, Any]:
        """Load existing profile data or create template."""
        if self.profile_file.exists():
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        else:
            # Create initial profile template based on known information
            template = self._create_profile_template()
            self._save_profile_data(template)
            return template
    
    def _create_profile_template(self) -> Dict[str, Any]:
        """Create initial LinkedIn profile template from known information."""
        return {
            "profile_url": self.profile_url,
            "last_updated": datetime.now().isoformat(),
            "basic_info": {
                "name": "Gavin Slater",
                "headline": "Risk Management Professional | AI Enthusiast | Chartered Accountant",
                "location": "Esher, Surrey, United Kingdom",
                "current_position": "Risk Management Specialist at ICBC Standard Bank",
                "industry": "Financial Services"
            },
            "experience": [
                {
                    "company": "ICBC Standard Bank",
                    "position": "Risk Management Specialist",
                    "duration": "February 2021 - Present",
                    "location": "London, UK",
                    "description": "Leading Risk Reporting team and Risk Change initiatives, implementing large system and process changes",
                    "key_responsibilities": [
                        "Risk reporting and analytics",
                        "System implementation and change management",
                        "Regulatory compliance and reporting",
                        "Team leadership and stakeholder management"
                    ]
                },
                {
                    "company": "Arthur Andersen", 
                    "position": "Auditor",
                    "duration": "1994 - [End Date]",
                    "location": "London, UK",
                    "description": "Started career as auditor, extensive international travel"
                }
            ],
            "education": [
                {
                    "institution": "University of Pietermaritzburg",
                    "degree": "Accounting",
                    "field_of_study": "Accounting",
                    "qualification": "Chartered Accountant"
                }
            ],
            "skills": [
                "Risk Management",
                "Financial Services", 
                "Python Programming",
                "Data Analysis",
                "Regulatory Compliance",
                "Project Management",
                "Team Leadership",
                "Artificial Intelligence (Learning)",
                "Data Architecture",
                "System Implementation"
            ],
            "interests": [
                "Artificial Intelligence",
                "Machine Learning",
                "Data Science",
                "Python Development",
                "Risk Analytics",
                "Financial Technology"
            ],
            "career_goals": {
                "current_focus": "Risk Management Excellence",
                "transition_goal": "AI and Machine Learning Career",
                "timeline": "Long-term transition",
                "target_roles": [
                    "AI Risk Management Specialist",
                    "ML Engineer - Financial Services",
                    "Data Science - Risk Analytics",
                    "AI Solutions Architect",
                    "Risk + AI Consultant"
                ]
            },
            "profile_optimization_status": {
                "needs_update": True,
                "ai_transition_ready": False,
                "portfolio_linked": False,
                "recommendations": [
                    "Update headline to include AI/ML interests",
                    "Add Python projects to experience",
                    "Include AI learning and certifications",
                    "Link to risk-agents.com website",
                    "Add GitHub profile link",
                    "Request recommendations from ICBC colleagues"
                ]
            }
        }
    
    def _save_profile_data(self, data: Dict[str, Any]):
        """Save profile data to file."""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.profile_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_job_search_history(self) -> Dict[str, Any]:
        """Load job search history."""
        if self.job_searches_file.exists():
            with open(self.job_searches_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "searches": [],
                "saved_jobs": [],
                "applications": [],
                "last_search": None
            }
    
    def _save_job_search_history(self):
        """Save job search history."""
        with open(self.job_searches_file, 'w') as f:
            json.dump(self.job_search_history, f, indent=2)
    
    def get_profile_summary(self) -> str:
        """Get formatted profile summary."""
        profile = self.profile_data
        
        summary = f"""# LinkedIn Profile Summary - Gavin Slater

## Current Status
- **Profile URL**: {profile['profile_url']}
- **Last Updated**: {profile.get('last_updated', 'Never')}
- **Current Position**: {profile['basic_info']['current_position']}
- **Location**: {profile['basic_info']['location']}

## Professional Experience
"""
        
        for exp in profile['experience']:
            summary += f"""
### {exp['company']} - {exp['position']}
- **Duration**: {exp['duration']}
- **Location**: {exp.get('location', 'N/A')}
- **Description**: {exp.get('description', 'N/A')}
"""
        
        summary += f"""
## Skills ({len(profile['skills'])})
{', '.join(profile['skills'])}

## Career Transition Goals
- **Current Focus**: {profile['career_goals']['current_focus']}
- **Target**: {profile['career_goals']['transition_goal']}
- **Timeline**: {profile['career_goals']['timeline']}

## Target Roles
{chr(10).join([f"• {role}" for role in profile['career_goals']['target_roles']])}

## Profile Optimization Status
- **Needs Update**: {profile['profile_optimization_status']['needs_update']}
- **AI Transition Ready**: {profile['profile_optimization_status']['ai_transition_ready']}

## Recommended Improvements
{chr(10).join([f"• {rec}" for rec in profile['profile_optimization_status']['recommendations']])}
"""
        
        return summary
    
    def update_profile_section(self, section: str, data: Dict[str, Any]) -> str:
        """Update a specific section of the profile."""
        if section not in self.profile_data:
            return f"❌ Error: Section '{section}' not found in profile"
        
        self.profile_data[section].update(data)
        self._save_profile_data(self.profile_data)
        
        return f"✅ Updated LinkedIn profile section: {section}"
    
    def add_skill(self, skill: str) -> str:
        """Add a skill to the profile."""
        if skill not in self.profile_data['skills']:
            self.profile_data['skills'].append(skill)
            self._save_profile_data(self.profile_data)
            return f"✅ Added skill: {skill}"
        else:
            return f"⚠️ Skill already exists: {skill}"
    
    def generate_linkedin_job_search_urls(self, keywords: List[str], location: str = "London, UK") -> List[Dict[str, str]]:
        """
        Generate LinkedIn job search URLs for manual searching.
        
        These URLs can be used for manual job searching on LinkedIn
        while respecting their terms of service.
        """
        base_url = "https://www.linkedin.com/jobs/search/"
        search_urls = []
        
        for keyword in keywords:
            # Create URL-encoded search parameters
            encoded_keyword = keyword.replace(" ", "%20")
            encoded_location = location.replace(" ", "%20").replace(",", "%2C")
            
            # Construct search URL
            url = f"{base_url}?keywords={encoded_keyword}&location={encoded_location}&f_TPR=r604800&f_JT=F"
            
            search_urls.append({
                "keyword": keyword,
                "url": url,
                "description": f"LinkedIn jobs for '{keyword}' in {location} (past week, full-time)"
            })
        
        return search_urls
    
    def get_ai_career_search_urls(self) -> List[Dict[str, str]]:
        """Get LinkedIn search URLs specifically for AI career transition."""
        ai_keywords = [
            "AI Risk Management",
            "Machine Learning Financial Services", 
            "AI Solutions Architect",
            "Data Science Risk",
            "ML Engineer Finance",
            "Artificial Intelligence Consultant",
            "AI Product Manager",
            "Risk Analytics AI",
            "Python Developer AI",
            "AI Implementation Manager"
        ]
        
        return self.generate_linkedin_job_search_urls(ai_keywords)
    
    def analyze_job_match(self, job_description: str) -> Dict[str, Any]:
        """
        Analyze how well a job matches Gavin's profile.
        
        Takes job description text and returns match analysis.
        """
        profile_skills = set([skill.lower() for skill in self.profile_data['skills']])
        profile_keywords = set(['risk', 'management', 'python', 'ai', 'artificial intelligence', 
                               'machine learning', 'data', 'financial', 'banking'])
        
        # Simple keyword matching analysis
        job_text_lower = job_description.lower()
        
        skill_matches = []
        keyword_matches = []
        
        for skill in profile_skills:
            if skill in job_text_lower:
                skill_matches.append(skill)
        
        for keyword in profile_keywords:
            if keyword in job_text_lower:
                keyword_matches.append(keyword)
        
        # Calculate match score
        total_possible = len(profile_skills) + len(profile_keywords)
        actual_matches = len(skill_matches) + len(keyword_matches)
        match_score = (actual_matches / total_possible) * 100 if total_possible > 0 else 0
        
        return {
            "match_score": round(match_score, 1),
            "skill_matches": skill_matches,
            "keyword_matches": keyword_matches,
            "recommendation": self._get_match_recommendation(match_score),
            "missing_skills": list(profile_skills - set(skill_matches)),
            "analysis_date": datetime.now().isoformat()
        }
    
    def _get_match_recommendation(self, score: float) -> str:
        """Get recommendation based on match score."""
        if score >= 40:
            return "🎯 Excellent match! Strong alignment with your profile. Apply now."
        elif score >= 25:
            return "✅ Good match! Worth applying with tailored cover letter."
        elif score >= 15:
            return "⚠️ Moderate match. Consider if role offers learning opportunities."
        else:
            return "❌ Low match. Focus on roles better aligned with your skills."
    
    def save_job_opportunity(self, job_data: Dict[str, Any]) -> str:
        """Save a job opportunity for tracking."""
        job_entry = {
            "id": f"job_{len(self.job_search_history['saved_jobs']) + 1}",
            "saved_date": datetime.now().isoformat(),
            **job_data
        }
        
        self.job_search_history['saved_jobs'].append(job_entry)
        self._save_job_search_history()
        
        return f"✅ Saved job opportunity: {job_data.get('title', 'Unknown Title')}"
    
    def get_profile_optimization_suggestions(self) -> List[str]:
        """Get specific suggestions for optimizing LinkedIn profile for AI transition."""
        suggestions = [
            "📝 Update headline to: 'Risk Management Professional Transitioning to AI | Python Developer | Chartered Accountant'",
            "🎯 Add AI/ML skills: TensorFlow, PyTorch, Scikit-learn, Machine Learning, Deep Learning",
            "📊 Create 'Featured' section showcasing Python risk management projects",
            "🔗 Link to GitHub profile with AI/Python projects",
            "🌐 Add risk-agents.com website to contact info",
            "📚 List AI courses/certifications (add current learning progress)", 
            "💼 Update current role description to include AI applications in risk management",
            "📝 Write LinkedIn articles about 'AI in Risk Management' to demonstrate expertise",
            "🤝 Request recommendations from ICBC colleagues highlighting technical skills",
            "🔍 Use AI-related keywords in all sections for better discoverability"
        ]
        
        return suggestions
    
    def track_application(self, job_info: Dict[str, Any], application_data: Dict[str, Any]) -> str:
        """Track a job application."""
        application = {
            "id": f"app_{len(self.job_search_history['applications']) + 1}",
            "application_date": datetime.now().isoformat(),
            "job_info": job_info,
            "application_data": application_data,
            "status": "applied"
        }
        
        self.job_search_history['applications'].append(application)
        self._save_job_search_history()
        
        return f"✅ Tracked application for: {job_info.get('title', 'Unknown Position')}"
    
    def get_application_status(self) -> str:
        """Get summary of job applications."""
        apps = self.job_search_history['applications']
        
        if not apps:
            return "📝 No job applications tracked yet."
        
        total = len(apps)
        recent = len([app for app in apps if 
                     datetime.fromisoformat(app['application_date']) > datetime.now() - timedelta(days=30)])
        
        return f"""# Job Application Status

## Summary
- **Total Applications**: {total}
- **Recent (30 days)**: {recent}

## Recent Applications
"""
        + "\n".join([f"• {app['job_info'].get('title', 'Unknown')} - {app['application_date'][:10]}" 
                    for app in apps[-5:]])  # Show last 5 applications