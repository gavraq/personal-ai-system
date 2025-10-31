#!/usr/bin/env python3
"""
LinkedIn Apify Client for Gavin's Personal Consultant System

This module uses Apify platform to scrape LinkedIn profile and job data
as an alternative to the limited LinkedIn API access.

WARNING: This code scrapes LinkedIn data which may violate LinkedIn's Terms of Service.
Use at your own risk and only for personal, non-commercial purposes.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from apify_client import ApifyClient

class LinkedInApifyClient:
    """
    LinkedIn data scraper using Apify platform.
    
    Provides functionality to scrape LinkedIn profiles and job postings
    using Apify actors as an alternative to limited LinkedIn API access.
    """
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize Apify client with API token."""
        
        # Use provided token or look for environment variable
        self.api_token = api_token or os.getenv('APIFY_API_TOKEN')
        
        if not self.api_token:
            raise ValueError(
                "Apify API token required. Set APIFY_API_TOKEN environment variable "
                "or pass token to constructor."
            )
        
        self.client = ApifyClient(self.api_token)
        self.data_dir = Path(__file__).parent / "apify_data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Free Apify LinkedIn actors only (no premium/paid required)
        self.actors = {
            "job_scraper": "valig/linkedin-jobs-scraper",  # Free LinkedIn Jobs Scraper - WORKING
        }
    
    def scrape_profile(self, profile_url: str, detailed: bool = True) -> Dict[str, Any]:
        """
        LinkedIn profile scraping - Not available with free actors.
        
        Args:
            profile_url: LinkedIn profile URL (e.g., https://www.linkedin.com/in/gavinslater/)
            detailed: Whether to get detailed profile information
            
        Returns:
            Dictionary indicating profile scraping not available
        """
        
        return {
            "success": False,
            "error": "LinkedIn profile scraping requires premium Apify actors",
            "profile_url": profile_url,
            "message": "Profile scraping removed to keep costs minimal",
            "alternatives": [
                "Use existing LinkedIn API for basic profile data",
                "Manual profile review and optimization",
                "Focus on job market intelligence (free and working)"
            ],
            "recommendation": "Use LinkedInAPIClient for basic profile access"
        }
    
    def scrape_gavin_profile(self) -> Dict[str, Any]:
        """Scrape Gavin's LinkedIn profile specifically."""
        return self.scrape_profile("https://www.linkedin.com/in/gavinslater/", detailed=True)
    
    def _format_scraped_profile(self, raw_data: Dict[str, Any], profile_url: str) -> Dict[str, Any]:
        """Format raw Apify profile data into standardized format."""
        
        formatted = {
            "profile_url": profile_url,
            "scraped_at": datetime.now().isoformat(),
            "basic_info": {
                "name": raw_data.get("fullName", "Unknown"),
                "headline": raw_data.get("headline", ""),
                "location": raw_data.get("location", ""),
                "connection_count": raw_data.get("connectionsCount", 0),
                "follower_count": raw_data.get("followersCount", 0)
            },
            "experience": [],
            "education": [],
            "skills": [],
            "accomplishments": {},
            "about": raw_data.get("summary", "")
        }
        
        # Process experience
        if raw_data.get("experience"):
            for exp in raw_data["experience"]:
                formatted_exp = {
                    "company": exp.get("companyName", ""),
                    "position": exp.get("title", ""),
                    "duration": f"{exp.get('startDate', '')} - {exp.get('endDate', 'Present')}",
                    "location": exp.get("location", ""),
                    "description": exp.get("description", "")
                }
                formatted["experience"].append(formatted_exp)
        
        # Process education
        if raw_data.get("education"):
            for edu in raw_data["education"]:
                formatted_edu = {
                    "institution": edu.get("schoolName", ""),
                    "degree": edu.get("degreeName", ""),
                    "field_of_study": edu.get("fieldOfStudy", ""),
                    "dates": f"{edu.get('startDate', '')} - {edu.get('endDate', '')}"
                }
                formatted["education"].append(formatted_edu)
        
        # Process skills
        if raw_data.get("skills"):
            formatted["skills"] = [skill.get("name", "") for skill in raw_data["skills"]]
        
        # Process accomplishments
        if raw_data.get("accomplishments"):
            formatted["accomplishments"] = raw_data["accomplishments"]
        
        return formatted
    
    def scrape_jobs(self, keywords: str, location: str = "London, UK", 
                   max_results: int = 20) -> Dict[str, Any]:
        """
        Scrape LinkedIn job postings using Apify.
        
        Args:
            keywords: Job search keywords
            location: Job location
            max_results: Maximum number of jobs to scrape
            
        Returns:
            Dictionary containing scraped job data
        """
        
        try:
            print(f"🔍 Scraping LinkedIn jobs: {keywords} in {location}")
            
            # Configure run input for job scraper
            run_input = {
                "queries": [f"{keywords} {location}"],
                "maxItems": max_results,
                "includeUnfilteredResults": False
            }
            
            print("🚀 Starting Apify job scraper...")
            run = self.client.actor(self.actors["job_scraper"]).call(run_input=run_input)
            
            # Get results
            jobs = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                jobs.append(item)
            
            if not jobs:
                return {
                    "success": False,
                    "error": "No job data returned from Apify",
                    "search_terms": f"{keywords} in {location}"
                }
            
            # Process and format job data
            formatted_jobs = [self._format_scraped_job(job) for job in jobs]
            
            # Analyze job patterns
            analysis = self._analyze_scraped_jobs(formatted_jobs, keywords)
            
            # Save scraped job data
            self._save_scraped_data("jobs", {
                "search_terms": f"{keywords} in {location}",
                "jobs": formatted_jobs,
                "analysis": analysis
            })
            
            return {
                "success": True,
                "search_terms": f"{keywords} in {location}",
                "jobs_found": len(formatted_jobs),
                "jobs": formatted_jobs,
                "analysis": analysis,
                "scraped_at": datetime.now().isoformat(),
                "source": "Apify"
            }
            
        except Exception as e:
            print(f"❌ Error scraping jobs: {str(e)}")
            return {
                "success": False,
                "error": f"Job scraping failed: {str(e)}",
                "search_terms": f"{keywords} in {location}",
                "fallback_suggestion": "Use LinkedIn job search manually or try web search approach"
            }
    
    def _format_scraped_job(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw Apify job data into standardized format."""
        
        return {
            "job_id": raw_job.get("jobId", ""),
            "title": raw_job.get("title", ""),
            "company": raw_job.get("companyName", ""),
            "location": raw_job.get("location", ""),
            "posted_date": raw_job.get("postedAt", ""),
            "description": raw_job.get("description", ""),
            "employment_type": raw_job.get("employmentType", ""),
            "seniority_level": raw_job.get("seniorityLevel", ""),
            "industry": raw_job.get("industries", []),
            "job_url": raw_job.get("jobUrl", ""),
            "company_url": raw_job.get("companyUrl", ""),
            "scraped_at": datetime.now().isoformat()
        }
    
    def _analyze_scraped_jobs(self, jobs: List[Dict[str, Any]], keywords: str) -> Dict[str, Any]:
        """Analyze scraped job data for patterns and insights."""
        
        if not jobs:
            return {"error": "No jobs to analyze"}
        
        # Extract common skills and requirements
        all_text = " ".join([
            job.get("description", "") + " " + job.get("title", "") 
            for job in jobs
        ]).lower()
        
        # AI/ML skills to look for
        ai_skills = {
            'python': all_text.count('python'),
            'machine learning': all_text.count('machine learning'),
            'tensorflow': all_text.count('tensorflow'),
            'pytorch': all_text.count('pytorch'),
            'ai': all_text.count(' ai '),
            'artificial intelligence': all_text.count('artificial intelligence'),
            'data science': all_text.count('data science'),
            'sql': all_text.count('sql'),
            'aws': all_text.count('aws'),
            'azure': all_text.count('azure')
        }
        
        # Sort skills by frequency
        top_skills = sorted(ai_skills.items(), key=lambda x: x[1], reverse=True)
        
        # Company analysis
        companies = {}
        for job in jobs:
            company = job.get("company", "Unknown")
            companies[company] = companies.get(company, 0) + 1
        
        top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)
        
        # Employment type analysis
        employment_types = {}
        for job in jobs:
            emp_type = job.get("employment_type", "Unknown")
            employment_types[emp_type] = employment_types.get(emp_type, 0) + 1
        
        return {
            "total_jobs": len(jobs),
            "top_skills": top_skills[:10],
            "top_companies": top_companies[:10],
            "employment_types": employment_types,
            "analysis_date": datetime.now().isoformat(),
            "gavin_recommendations": self._generate_gavin_specific_recommendations(top_skills, jobs)
        }
    
    def _generate_gavin_specific_recommendations(self, top_skills: List[tuple], 
                                               jobs: List[Dict]) -> List[str]:
        """Generate specific recommendations for Gavin based on job analysis."""
        
        recommendations = []
        
        # Skill-based recommendations
        skill_dict = dict(top_skills)
        
        if skill_dict.get('python', 0) > 5:
            recommendations.append("🐍 Python is in high demand - emphasize your Python experience")
        
        if skill_dict.get('machine learning', 0) > 3:
            recommendations.append("🤖 Machine learning skills are critical - continue your AI learning")
        
        if skill_dict.get('aws', 0) > 2 or skill_dict.get('azure', 0) > 2:
            recommendations.append("☁️ Cloud skills needed - consider AWS/Azure certification")
        
        # Risk + AI combination advantage
        risk_mentions = sum(1 for job in jobs if 'risk' in job.get('description', '').lower())
        if risk_mentions > 2:
            recommendations.append("🎯 Your risk management background is valuable in AI roles")
        
        # Financial services advantage
        finance_mentions = sum(1 for job in jobs 
                             if any(term in job.get('description', '').lower() 
                                   for term in ['financial', 'bank', 'finance']))
        if finance_mentions > 3:
            recommendations.append("🏦 Your financial services experience is a strong differentiator")
        
        return recommendations
    
    def _save_scraped_data(self, data_type: str, data: Dict[str, Any], 
                          identifier: str = None):
        """Save scraped data to local files."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if identifier:
            # Clean identifier for filename
            clean_id = "".join(c for c in identifier if c.isalnum() or c in ('-', '_'))
            filename = f"{data_type}_{clean_id}_{timestamp}.json"
        else:
            filename = f"{data_type}_{timestamp}.json"
        
        filepath = self.data_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved {data_type} data to {filepath}")
    
    def get_ai_job_opportunities_enhanced(self) -> Dict[str, Any]:
        """Get AI job opportunities using free Apify job scraper."""
        
        ai_search_terms = [
            "Artificial Intelligence London",
            "Machine Learning London", 
            "AI Risk Management",
            "Python Developer AI",
            "Data Science London"
        ]
        
        all_results = {}
        
        for search_term in ai_search_terms:
            print(f"🔍 Searching for: {search_term}")
            
            result = self.scrape_jobs(
                keywords=search_term,
                location="London UK",
                max_results=8  # Smaller batches for free tier
            )
            
            if result.get("success"):
                all_results[search_term] = result
                # Add delay to be respectful to Apify/LinkedIn
                time.sleep(3)  # Longer delay for free tier
        
        # Combine and analyze all results
        combined_analysis = self._combine_search_results(all_results)
        
        return {
            "search_date": datetime.now().isoformat(),
            "search_terms": ai_search_terms,
            "individual_results": all_results,
            "combined_analysis": combined_analysis,
            "cost_estimate": f"~${len(ai_search_terms) * 0.01:.2f} for comprehensive AI job search",
            "actor_used": "valig/linkedin-jobs-scraper (Free)",
            "next_steps": [
                "Review high-match jobs from scraping results",
                "Apply to positions that emphasize risk + AI combination",
                "Update LinkedIn profile using LinkedIn API integration",
                "Develop skills identified as high-frequency in job postings"
            ]
        }
    
    def _combine_search_results(self, all_results: Dict[str, Dict]) -> Dict[str, Any]:
        """Combine results from multiple job searches."""
        
        all_jobs = []
        all_skills = {}
        all_companies = {}
        
        for search_term, result in all_results.items():
            if result.get("success"):
                jobs = result.get("jobs", [])
                all_jobs.extend(jobs)
                
                # Aggregate skill data
                analysis = result.get("analysis", {})
                if "top_skills" in analysis:
                    for skill, count in analysis["top_skills"]:
                        all_skills[skill] = all_skills.get(skill, 0) + count
        
        # Re-sort combined skills
        top_combined_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_jobs_found": len(all_jobs),
            "unique_companies": len(set(job.get("company") for job in all_jobs)),
            "top_combined_skills": top_combined_skills[:15],
            "skill_frequency_analysis": self._analyze_skill_frequency(all_jobs),
            "career_transition_insights": self._generate_transition_insights(top_combined_skills)
        }
    
    def _analyze_skill_frequency(self, jobs: List[Dict]) -> Dict[str, Any]:
        """Analyze how frequently skills appear across all job postings."""
        
        total_jobs = len(jobs)
        if total_jobs == 0:
            return {}
        
        # Gavin's current skills
        gavin_skills = ['python', 'risk management', 'financial services', 
                       'project management', 'sql', 'data analysis']
        
        skill_analysis = {}
        
        for skill in gavin_skills:
            mentions = sum(1 for job in jobs 
                          if skill.lower() in job.get('description', '').lower())
            
            skill_analysis[skill] = {
                "job_mentions": mentions,
                "percentage": round((mentions / total_jobs) * 100, 1),
                "recommendation": self._get_skill_recommendation(skill, mentions, total_jobs)
            }
        
        return skill_analysis
    
    def _get_skill_recommendation(self, skill: str, mentions: int, total_jobs: int) -> str:
        """Get recommendation for a specific skill."""
        
        percentage = (mentions / total_jobs) * 100
        
        if percentage >= 60:
            return f"🔥 {skill.title()} is extremely valuable - highlight prominently"
        elif percentage >= 40:
            return f"✅ {skill.title()} is in high demand - emphasize in applications"
        elif percentage >= 20:
            return f"📈 {skill.title()} is moderately important - mention when relevant"
        else:
            return f"📝 {skill.title()} has limited mentions - consider supplementary skills"
    
    def _generate_transition_insights(self, top_skills: List[tuple]) -> List[str]:
        """Generate career transition insights based on skill analysis."""
        
        insights = []
        
        skill_dict = dict(top_skills)
        
        # Python emphasis
        if skill_dict.get('python', 0) > 10:
            insights.append("🐍 Python dominates AI job requirements - your Python skills are your biggest asset")
        
        # ML focus
        if skill_dict.get('machine learning', 0) > 5:
            insights.append("🤖 Machine Learning is core to most AI roles - prioritize ML learning")
        
        # Cloud importance
        cloud_total = skill_dict.get('aws', 0) + skill_dict.get('azure', 0) + skill_dict.get('gcp', 0)
        if cloud_total > 8:
            insights.append("☁️ Cloud platforms are essential - AWS or Azure certification recommended")
        
        # Risk + AI opportunity
        if skill_dict.get('risk', 0) > 3:
            insights.append("🎯 Risk + AI combination is valuable - leverage your unique background")
        
        # Financial services advantage
        finance_terms = skill_dict.get('financial', 0) + skill_dict.get('banking', 0)
        if finance_terms > 5:
            insights.append("🏦 Financial services AI roles are perfect fit for your background")
        
        return insights
    
    def test_apify_connection(self) -> Dict[str, Any]:
        """Test Apify API connection and available credits."""
        
        try:
            # Get user info to test connection
            user_info = self.client.user().get()
            
            return {
                "success": True,
                "user_id": user_info.get("id"),
                "email": user_info.get("email"),
                "available_credits": user_info.get("usageCredits", {}).get("current", 0),
                "connection_test": "✅ Apify API connection successful",
                "actors_configured": list(self.actors.keys()),
                "actor_details": {
                    "job_scraper": "valig/linkedin-jobs-scraper (Free LinkedIn Jobs Scraper - WORKING)"
                },
                "capabilities": [
                    "LinkedIn job search and analysis",
                    "Market intelligence for AI career transition", 
                    "Job-profile matching and recommendations"
                ],
                "removed_features": [
                    "LinkedIn profile scraping (requires premium actors)",
                    "Bulk operations (premium features)"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Apify connection failed: {str(e)}",
                "suggestion": "Check API token and network connectivity"
            }

def main():
    """Test the LinkedIn Apify client."""
    
    print("🕷️ Testing LinkedIn Apify Integration")
    print("=" * 50)
    
    # Note: Requires APIFY_API_TOKEN environment variable
    if not os.getenv('APIFY_API_TOKEN'):
        print("❌ APIFY_API_TOKEN environment variable not set")
        print("💡 Get your API token from: https://console.apify.com/account#/integrations")
        print("💡 Then run: export APIFY_API_TOKEN='your_token_here'")
        return
    
    try:
        client = LinkedInApifyClient()
        
        # Test connection
        print("1. Testing Apify connection...")
        connection_test = client.test_apify_connection()
        
        if connection_test["success"]:
            print(f"   ✅ Connected to Apify")
            print(f"   💰 Available credits: {connection_test['available_credits']}")
        else:
            print(f"   ❌ Connection failed: {connection_test['error']}")
            return
        
        # Test profile scraping (WARNING: This will use Apify credits)
        print(f"\n2. Testing profile scraping...")
        print("   ⚠️  This will use Apify credits - proceed? (y/N): ", end="")
        
        # In automated testing, skip interactive prompt
        proceed = input().lower().strip() == 'y'
        
        if proceed:
            profile_result = client.scrape_gavin_profile()
            
            if profile_result["success"]:
                profile = profile_result["profile"]
                print(f"   ✅ Profile scraped successfully")
                print(f"   👤 Name: {profile['basic_info']['name']}")
                print(f"   💼 Headline: {profile['basic_info']['headline']}")
                print(f"   📍 Location: {profile['basic_info']['location']}")
                print(f"   🎯 Experience entries: {len(profile['experience'])}")
            else:
                print(f"   ❌ Profile scraping failed: {profile_result['error']}")
        
        print(f"\n📋 Summary:")
        print(f"   • Apify client initialized successfully")
        print(f"   • {len(client.actors)} actors configured")
        print(f"   • Data directory: {client.data_dir}")
        print(f"   • Ready for LinkedIn scraping operations")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    main()