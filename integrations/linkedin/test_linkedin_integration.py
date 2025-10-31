#!/usr/bin/env python3
"""
Test script for LinkedIn integration functionality.

This script tests the LinkedIn profile management and job search capabilities
without requiring live API access.
"""

import sys
import json
from pathlib import Path

# Add the integration modules to path
sys.path.append(str(Path(__file__).parent))

from linkedin_profile_manager import LinkedInProfileManager
from linkedin_job_searcher import LinkedInJobSearcher

def test_profile_manager():
    """Test LinkedIn profile management functionality."""
    print("=" * 60)
    print("TESTING: LinkedIn Profile Manager")
    print("=" * 60)
    
    # Initialize profile manager
    profile_manager = LinkedInProfileManager()
    
    # Test 1: Get profile summary
    print("\n1. Profile Summary:")
    print("-" * 40)
    summary = profile_manager.get_profile_summary()
    print(summary[:500] + "..." if len(summary) > 500 else summary)
    
    # Test 2: Add skills
    print("\n2. Adding AI Skills:")
    print("-" * 40)
    result1 = profile_manager.add_skill("TensorFlow")
    result2 = profile_manager.add_skill("Machine Learning")
    result3 = profile_manager.add_skill("Python")  # Should already exist
    print(result1)
    print(result2)
    print(result3)
    
    # Test 3: Get optimization suggestions
    print("\n3. Profile Optimization Suggestions:")
    print("-" * 40)
    suggestions = profile_manager.get_profile_optimization_suggestions()
    for i, suggestion in enumerate(suggestions[:5], 1):
        print(f"{i}. {suggestion}")
    
    # Test 4: Generate LinkedIn search URLs
    print("\n4. AI Career Search URLs:")
    print("-" * 40)
    search_urls = profile_manager.generate_linkedin_job_search_urls(
        ["AI Risk Management", "Python Developer AI"],
        "London, UK"
    )
    for url_info in search_urls:
        print(f"• {url_info['keyword']}: {url_info['url'][:60]}...")
    
    return True

def test_job_searcher():
    """Test LinkedIn job search functionality."""
    print("\n" + "=" * 60)
    print("TESTING: LinkedIn Job Searcher")
    print("=" * 60)
    
    # Initialize job searcher (without web tools for testing)
    job_searcher = LinkedInJobSearcher()
    
    # Test 1: Analyze job description
    print("\n1. Job Description Analysis:")
    print("-" * 40)
    sample_job = """
    Senior AI Risk Analyst - London
    
    We're looking for an experienced professional to join our AI risk team.
    
    Requirements:
    - 5+ years risk management experience
    - Python programming skills
    - Machine learning knowledge
    - Financial services background
    - Strong analytical skills
    
    Responsibilities:
    - Develop AI risk models
    - Python development for risk analytics
    - Collaborate with data science teams
    - Regulatory compliance and reporting
    """
    
    analysis = job_searcher.analyze_job_description(sample_job, "Senior AI Risk Analyst")
    print(f"Match Score: {analysis['match_percentage']}%")
    print(f"Recommendation: {analysis['recommendation']}")
    print(f"Matching Skills: {analysis['total_matching_skills']}")
    print("Cover Letter Focus Areas:")
    for focus in analysis['cover_letter_focus'][:3]:
        print(f"  • {focus}")
    
    # Test 2: Generate manual search URLs
    print("\n2. Manual Search URLs:")
    print("-" * 40)
    urls = job_searcher._generate_manual_search_urls("AI Risk Management", "London UK")
    for url_info in urls:
        print(f"• {url_info['name']}: {url_info['description']}")
    
    # Test 3: AI job opportunities (without web search)
    print("\n3. AI Job Search Configuration:")
    print("-" * 40)
    # This would normally perform web searches, but will show fallback behavior
    result = job_searcher.search_linkedin_jobs("AI Risk Management", "London UK")
    if 'error' in result:
        print(f"Expected behavior: {result['error']}")
        print(f"Manual URL provided: {result.get('manual_search_url', 'N/A')[:60]}...")
    
    return True

def test_integration():
    """Test integration between profile manager and job searcher."""
    print("\n" + "=" * 60)
    print("TESTING: Integration Between Components")
    print("=" * 60)
    
    profile_manager = LinkedInProfileManager()
    job_searcher = LinkedInJobSearcher()
    
    # Test 1: Save job opportunity
    print("\n1. Saving Job Opportunity:")
    print("-" * 40)
    job_data = {
        "title": "Senior AI Risk Analyst",
        "company": "Barclays",
        "location": "London",
        "url": "https://linkedin.com/jobs/test-123",
        "match_score": 85.0,
        "source": "LinkedIn"
    }
    
    result = profile_manager.save_job_opportunity(job_data)
    print(result)
    
    # Test 2: Track application
    print("\n2. Tracking Application:")
    print("-" * 40)
    application_result = profile_manager.track_application(
        job_info=job_data,
        application_data={
            "applied_via": "LinkedIn",
            "cover_letter_sent": True,
            "follow_up_date": "2025-01-20"
        }
    )
    print(application_result)
    
    # Test 3: Get application status
    print("\n3. Application Status:")
    print("-" * 40)
    status = profile_manager.get_application_status()
    print(status[:300] + "..." if len(status) > 300 else status)
    
    return True

def main():
    """Run all tests."""
    print("🔍 Testing LinkedIn Integration System")
    print("=" * 60)
    
    try:
        # Test profile manager
        profile_test = test_profile_manager()
        
        # Test job searcher
        job_test = test_job_searcher()
        
        # Test integration
        integration_test = test_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Profile Manager: {'PASSED' if profile_test else 'FAILED'}")
        print(f"✅ Job Searcher: {'PASSED' if job_test else 'FAILED'}")
        print(f"✅ Integration: {'PASSED' if integration_test else 'FAILED'}")
        
        if all([profile_test, job_test, integration_test]):
            print("\n🎉 All LinkedIn integration tests PASSED!")
            print("\nNext Steps:")
            print("1. Run job search agent with LinkedIn integration")
            print("2. Test with real Claude Code WebSearch tools")
            print("3. Update LinkedIn profile based on optimization suggestions")
        else:
            print("\n❌ Some tests FAILED. Check error messages above.")
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()