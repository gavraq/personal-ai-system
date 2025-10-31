#!/usr/bin/env python3
"""
LinkedIn Job Searcher for Personal Consultant System

This module provides LinkedIn job search capabilities using web search techniques
that respect LinkedIn's terms of service while providing valuable job intelligence.
"""

import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

class LinkedInJobSearcher:
    """
    Searches for LinkedIn jobs using legitimate web search methods.
    
    Uses web search APIs to find LinkedIn job postings and provides
    analysis and filtering capabilities.
    """
    
    def __init__(self, web_search_tool=None, web_fetch_tool=None):
        """Initialize with web search tools from Claude Code environment."""
        self.web_search = web_search_tool
        self.web_fetch = web_fetch_tool
        self.search_history_file = Path(__file__).parent / "linkedin_job_search_history.json"
        self.search_history = self._load_search_history()
    
    def _load_search_history(self) -> Dict[str, Any]:
        """Load search history from file."""
        if self.search_history_file.exists():
            with open(self.search_history_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "searches": [],
                "jobs_found": [],
                "last_search_date": None
            }
    
    def _save_search_history(self):
        """Save search history to file."""
        with open(self.search_history_file, 'w') as f:
            json.dump(self.search_history, f, indent=2)
    
    def search_linkedin_jobs(self, keywords: str, location: str = "London UK", 
                           experience_level: str = "senior", max_results: int = 10) -> Dict[str, Any]:
        """
        Search for LinkedIn job postings using web search.
        
        Args:
            keywords: Job search keywords (e.g., "AI Risk Management")
            location: Job location
            experience_level: Experience level filter
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with search results and analysis
        """
        
        if not self.web_search:
            return {
                "error": "Web search tool not available. Must run in Claude Code environment.",
                "manual_search_url": f"https://www.linkedin.com/jobs/search/?keywords={keywords.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
            }
        
        # Construct search query for LinkedIn jobs
        search_query = f'site:linkedin.com/jobs "{keywords}" "{location}" {experience_level}'
        
        try:
            # Perform web search for LinkedIn job postings
            search_results = self.web_search(
                query=search_query,
                allowed_domains=["linkedin.com"]
            )
            
            # Process and analyze results
            jobs_analysis = self._analyze_search_results(search_results, keywords)
            
            # Save search to history
            self._save_search_to_history(keywords, location, jobs_analysis)
            
            return jobs_analysis
            
        except Exception as e:
            return {
                "error": f"Search failed: {str(e)}",
                "fallback_approach": "Manual search recommended",
                "manual_search_urls": self._generate_manual_search_urls(keywords, location)
            }
    
    def _analyze_search_results(self, search_results: Any, keywords: str) -> Dict[str, Any]:
        """Analyze web search results for job information."""
        
        jobs_found = []
        analysis_summary = {
            "search_date": datetime.now().isoformat(),
            "keywords": keywords,
            "total_results_found": 0,
            "jobs_analyzed": [],
            "common_requirements": [],
            "salary_ranges": [],
            "top_companies": [],
            "recommendations": []
        }
        
        # Extract job information from search results (simplified)
        # In practice, this would parse the actual search results structure
        if hasattr(search_results, 'results') and search_results.results:
            for result in search_results.results[:10]:  # Limit to top 10
                job_info = self._extract_job_info_from_result(result)
                if job_info:
                    jobs_found.append(job_info)
        
        analysis_summary["total_results_found"] = len(jobs_found)
        analysis_summary["jobs_analyzed"] = jobs_found
        
        # Analyze common patterns
        if jobs_found:
            analysis_summary.update(self._analyze_job_patterns(jobs_found))
        
        return analysis_summary
    
    def _extract_job_info_from_result(self, result: Any) -> Optional[Dict[str, str]]:
        """Extract job information from a search result."""
        
        try:
            # Extract basic information from search result
            title = getattr(result, 'title', 'Unknown Title')
            url = getattr(result, 'url', '')
            snippet = getattr(result, 'snippet', '')
            
            # Parse company name from LinkedIn URL or title
            company = self._extract_company_from_linkedin_url(url) or "Unknown Company"
            
            # Extract location if available in snippet
            location = self._extract_location_from_snippet(snippet)
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "url": url,
                "snippet": snippet,
                "source": "LinkedIn",
                "found_date": datetime.now().isoformat()
            }
            
        except Exception:
            return None
    
    def _extract_company_from_linkedin_url(self, url: str) -> Optional[str]:
        """Extract company name from LinkedIn job URL."""
        # LinkedIn job URLs often contain company info
        # This is a simplified extraction
        if 'linkedin.com' in url:
            # Look for patterns in URL that might indicate company
            match = re.search(r'/company/([^/]+)', url)
            if match:
                return match.group(1).replace('-', ' ').title()
        return None
    
    def _extract_location_from_snippet(self, snippet: str) -> str:
        """Extract location information from search snippet."""
        # Look for location patterns in snippet
        location_patterns = [
            r'London[^,]*(?:UK|United Kingdom)?',
            r'Remote.*UK',
            r'Manchester[^,]*UK',
            r'Birmingham[^,]*UK',
            r'Edinburgh[^,]*UK'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, snippet, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Location not specified"
    
    def _analyze_job_patterns(self, jobs: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """Analyze patterns in job postings."""
        
        # Extract common requirements and skills
        all_text = " ".join([job.get('snippet', '') + " " + job.get('title', '') for job in jobs])
        
        # Common AI/ML skills to look for
        ai_skills = ['python', 'machine learning', 'tensorflow', 'pytorch', 'scikit-learn', 
                    'deep learning', 'neural networks', 'ai', 'artificial intelligence',
                    'data science', 'pandas', 'numpy', 'sql', 'aws', 'azure', 'gcp']
        
        # Find mentioned skills
        found_skills = []
        for skill in ai_skills:
            if skill.lower() in all_text.lower():
                found_skills.append(skill)
        
        # Extract companies
        companies = list(set([job.get('company', '') for job in jobs if job.get('company')]))
        
        return {
            "common_requirements": found_skills,
            "top_companies": companies,
            "recommendations": self._generate_search_recommendations(found_skills)
        }
    
    def _generate_search_recommendations(self, found_skills: List[str]) -> List[str]:
        """Generate recommendations based on search analysis."""
        recommendations = []
        
        if 'python' in found_skills:
            recommendations.append("🐍 Python skills are highly valued - highlight your Python experience")
        
        if 'machine learning' in found_skills or 'tensorflow' in found_skills:
            recommendations.append("🤖 Machine learning skills in demand - consider ML certification")
        
        if 'aws' in found_skills or 'azure' in found_skills:
            recommendations.append("☁️ Cloud platform experience needed - consider cloud certification")
        
        if len(found_skills) < 3:
            recommendations.append("📚 Limited skill matches found - broaden search keywords")
        
        recommendations.append("🎯 Tailor applications to emphasize risk management + AI combination")
        
        return recommendations
    
    def _generate_manual_search_urls(self, keywords: str, location: str) -> List[Dict[str, str]]:
        """Generate manual search URLs for different scenarios."""
        
        base_linkedin_url = "https://www.linkedin.com/jobs/search/"
        encoded_keywords = keywords.replace(" ", "%20")
        encoded_location = location.replace(" ", "%20")
        
        search_variations = [
            {
                "name": "Primary Search",
                "url": f"{base_linkedin_url}?keywords={encoded_keywords}&location={encoded_location}&f_TPR=r604800",
                "description": f"LinkedIn jobs for '{keywords}' in {location} (past week)"
            },
            {
                "name": "Senior Level",
                "url": f"{base_linkedin_url}?keywords={encoded_keywords}&location={encoded_location}&f_E=4&f_TPR=r604800",
                "description": f"Senior level positions for '{keywords}'"
            },
            {
                "name": "Remote Options", 
                "url": f"{base_linkedin_url}?keywords={encoded_keywords}%20remote&location={encoded_location}&f_TPR=r604800",
                "description": f"Remote '{keywords}' opportunities"
            }
        ]
        
        return search_variations
    
    def _save_search_to_history(self, keywords: str, location: str, results: Dict[str, Any]):
        """Save search results to history."""
        
        search_entry = {
            "search_id": f"search_{len(self.search_history['searches']) + 1}",
            "date": datetime.now().isoformat(),
            "keywords": keywords,
            "location": location,
            "results_count": results.get("total_results_found", 0),
            "summary": results
        }
        
        self.search_history["searches"].append(search_entry)
        self.search_history["last_search_date"] = datetime.now().isoformat()
        
        # Keep only last 50 searches
        self.search_history["searches"] = self.search_history["searches"][-50:]
        
        self._save_search_history()
    
    def get_ai_job_opportunities(self) -> Dict[str, Any]:
        """Get AI job opportunities specifically aligned with Gavin's background."""
        
        ai_search_terms = [
            "AI Risk Management",
            "Machine Learning Financial Services",
            "Python Developer AI", 
            "Risk Analytics AI",
            "AI Solutions Architect Finance"
        ]
        
        all_results = []
        
        for search_term in ai_search_terms:
            result = self.search_linkedin_jobs(
                keywords=search_term,
                location="London UK",
                experience_level="senior",
                max_results=5
            )
            
            if not result.get("error"):
                all_results.append({
                    "search_term": search_term,
                    "results": result
                })
        
        return {
            "search_date": datetime.now().isoformat(),
            "total_searches": len(ai_search_terms),
            "successful_searches": len(all_results),
            "combined_results": all_results,
            "next_steps": [
                "Review job matches and requirements",
                "Apply to high-match positions", 
                "Update LinkedIn profile based on common requirements",
                "Develop missing skills identified in job postings"
            ]
        }
    
    def analyze_job_description(self, job_description: str, job_title: str = "") -> Dict[str, Any]:
        """
        Analyze a job description for match with Gavin's profile.
        
        Args:
            job_description: Full job description text
            job_title: Job title (optional)
            
        Returns:
            Analysis of job fit and recommendations
        """
        
        # Gavin's key skills and experience
        gavin_skills = {
            'technical': ['python', 'risk management', 'data analysis', 'sql', 'financial services'],
            'business': ['project management', 'team leadership', 'regulatory compliance', 'stakeholder management'],
            'domain': ['banking', 'financial services', 'risk assessment', 'audit', 'chartered accountant'],
            'learning': ['ai', 'artificial intelligence', 'machine learning', 'data science']
        }
        
        # Analyze job description
        job_text = (job_title + " " + job_description).lower()
        
        skill_matches = {}
        total_matches = 0
        
        for category, skills in gavin_skills.items():
            matches = [skill for skill in skills if skill in job_text]
            skill_matches[category] = matches
            total_matches += len(matches)
        
        # Calculate match score
        total_possible = sum(len(skills) for skills in gavin_skills.values())
        match_percentage = (total_matches / total_possible) * 100
        
        # Identify missing skills
        required_skills = self._extract_required_skills(job_description)
        missing_skills = [skill for skill in required_skills 
                         if not any(skill in matches for matches in skill_matches.values())]
        
        return {
            "job_title": job_title,
            "match_percentage": round(match_percentage, 1),
            "skill_matches": skill_matches,
            "total_matching_skills": total_matches,
            "required_skills": required_skills,
            "missing_skills": missing_skills,
            "recommendation": self._get_application_recommendation(match_percentage, skill_matches),
            "cover_letter_focus": self._suggest_cover_letter_focus(skill_matches),
            "analysis_date": datetime.now().isoformat()
        }
    
    def _extract_required_skills(self, job_description: str) -> List[str]:
        """Extract required skills from job description."""
        
        # Common skill patterns in job descriptions
        skill_patterns = [
            r'\b(?:python|java|sql|r\b|scala|javascript)\b',
            r'\b(?:machine learning|deep learning|ai|artificial intelligence)\b', 
            r'\b(?:tensorflow|pytorch|scikit-learn|pandas|numpy)\b',
            r'\b(?:aws|azure|gcp|cloud)\b',
            r'\b(?:docker|kubernetes|git)\b',
            r'\b(?:agile|scrum|project management)\b'
        ]
        
        found_skills = []
        job_text = job_description.lower()
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            found_skills.extend(matches)
        
        return list(set(found_skills))  # Remove duplicates
    
    def _get_application_recommendation(self, match_percentage: float, skill_matches: Dict[str, List[str]]) -> str:
        """Get recommendation on whether to apply."""
        
        if match_percentage >= 60:
            return "🎯 Excellent fit! Apply immediately with confidence."
        elif match_percentage >= 40:
            return "✅ Strong candidate! Apply with tailored cover letter highlighting matching skills."
        elif match_percentage >= 25:
            return "⚠️ Moderate fit. Apply if role offers growth opportunities in missing areas."
        elif any(len(matches) > 0 for matches in skill_matches.values()):
            return "📝 Some relevant skills. Consider applying if passionate about the role."
        else:
            return "❌ Limited match. Focus on roles better aligned with your background."
    
    def _suggest_cover_letter_focus(self, skill_matches: Dict[str, List[str]]) -> List[str]:
        """Suggest what to emphasize in cover letter."""
        
        focus_areas = []
        
        if skill_matches.get('technical'):
            focus_areas.append(f"🔧 Emphasize technical skills: {', '.join(skill_matches['technical'])}")
        
        if skill_matches.get('business'):
            focus_areas.append(f"💼 Highlight leadership experience: {', '.join(skill_matches['business'])}")
        
        if skill_matches.get('domain'):
            focus_areas.append(f"🏦 Leverage financial services expertise: {', '.join(skill_matches['domain'])}")
        
        if skill_matches.get('learning'):
            focus_areas.append(f"🚀 Showcase AI learning journey: {', '.join(skill_matches['learning'])}")
        
        # Always include transition story
        focus_areas.append("📖 Tell your career transition story from Risk Management to AI")
        
        return focus_areas
    
    def get_search_history_summary(self) -> str:
        """Get summary of recent job searches."""
        
        searches = self.search_history.get("searches", [])
        
        if not searches:
            return "📝 No job searches performed yet."
        
        recent_searches = searches[-5:]  # Last 5 searches
        
        summary = f"""# LinkedIn Job Search History

## Recent Searches ({len(recent_searches)})
"""
        
        for search in recent_searches:
            summary += f"""
### {search.get('keywords', 'Unknown')}
- **Date**: {search.get('date', 'Unknown')[:10]}
- **Location**: {search.get('location', 'Not specified')}
- **Results Found**: {search.get('results_count', 0)}
"""
        
        summary += f"""
## Search Statistics
- **Total Searches**: {len(searches)}
- **Last Search**: {self.search_history.get('last_search_date', 'Never')[:10] if self.search_history.get('last_search_date') else 'Never'}
"""
        
        return summary