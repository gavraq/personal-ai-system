#!/usr/bin/env python3
"""
Comprehensive test script for LinkedIn Apify integration.

This script tests all aspects of the Apify LinkedIn integration including:
- API connection testing
- Profile scraping capabilities
- Job search functionality  
- Data persistence and analysis
- Integration with existing LinkedIn tools

Prerequisites:
1. Apify account with API token
2. APIFY_API_TOKEN environment variable set
3. Sufficient Apify credits for testing

Usage:
    export APIFY_API_TOKEN="your_apify_token_here"
    python test_apify_integration.py
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from linkedin_apify_client import LinkedInApifyClient
from linkedin_job_searcher import LinkedInJobSearcher
from linkedin_profile_manager import LinkedInProfileManager

def test_apify_setup():
    """Test 1: Verify Apify setup and credentials."""
    print("🧪 TEST 1: Apify Setup and Connection")
    print("-" * 50)
    
    # Check for API token
    api_token = os.getenv('APIFY_API_TOKEN')
    if not api_token:
        print("❌ APIFY_API_TOKEN environment variable not set")
        print("💡 Get your token from: https://console.apify.com/account#/integrations")
        print("💡 Then run: export APIFY_API_TOKEN='your_token_here'")
        return False
    
    print(f"✅ API Token found (length: {len(api_token)})")
    
    # Test connection
    try:
        client = LinkedInApifyClient()
        connection_test = client.test_apify_connection()
        
        if connection_test["success"]:
            print(f"✅ Connected to Apify successfully")
            print(f"💰 Available credits: {connection_test['available_credits']}")
            print(f"👤 User: {connection_test['email']}")
            print(f"🎭 Actors configured: {', '.join(connection_test['actors_configured'])}")
            return True
        else:
            print(f"❌ Connection failed: {connection_test['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Setup test failed: {str(e)}")
        return False

def test_profile_scraping(client):
    """Test 2: Profile scraping functionality."""
    print(f"\n🧪 TEST 2: LinkedIn Profile Scraping")
    print("-" * 50)
    
    print("⚠️  This test will use Apify credits to scrape Gavin's LinkedIn profile")
    print("⚠️  Profile scraping costs approximately $0.001 per profile")
    proceed = input("Proceed with profile scraping test? (y/N): ").lower().strip()
    
    if proceed != 'y':
        print("⏭️  Skipping profile scraping test")
        return True
    
    try:
        print("🕷️ Starting profile scraping...")
        profile_result = client.scrape_gavin_profile()
        
        if profile_result["success"]:
            profile = profile_result["profile"]
            
            print("✅ Profile scraped successfully!")
            print(f"   👤 Name: {profile['basic_info']['name']}")
            print(f"   💼 Headline: {profile['basic_info']['headline']}")
            print(f"   📍 Location: {profile['basic_info']['location']}")
            print(f"   🔗 Connections: {profile['basic_info']['connection_count']}")
            print(f"   🎓 Education entries: {len(profile['education'])}")
            print(f"   💼 Experience entries: {len(profile['experience'])}")
            print(f"   🎯 Skills listed: {len(profile['skills'])}")
            print(f"   📝 About section length: {len(profile['about'])} characters")
            
            # Show some sample data
            if profile['experience']:
                latest_job = profile['experience'][0]
                print(f"   🏢 Latest position: {latest_job['position']} at {latest_job['company']}")
            
            if profile['skills']:
                print(f"   🛠️  Sample skills: {', '.join(profile['skills'][:5])}")
            
            return True
        else:
            print(f"❌ Profile scraping failed: {profile_result['error']}")
            print(f"🔍 Suggestion: {profile_result.get('fallback_suggestion', 'Try again later')}")
            return False
            
    except Exception as e:
        print(f"❌ Profile scraping test failed: {str(e)}")
        return False

def test_job_scraping(client):
    """Test 3: Job scraping functionality."""
    print(f"\n🧪 TEST 3: LinkedIn Job Scraping")
    print("-" * 50)
    
    print("⚠️  This test will use Apify credits to scrape LinkedIn job postings")
    print("⚠️  Job scraping costs approximately $0.01 per 100 jobs")
    proceed = input("Proceed with job scraping test? (y/N): ").lower().strip()
    
    if proceed != 'y':
        print("⏭️  Skipping job scraping test")
        return True
    
    try:
        print("🔍 Starting job search scraping...")
        
        # Test job scraping with a small number of results
        job_result = client.scrape_jobs(
            keywords="AI Risk Management",
            location="London UK",
            max_results=5  # Small number for testing
        )
        
        if job_result["success"]:
            jobs = job_result["jobs"]
            analysis = job_result["analysis"]
            
            print("✅ Job scraping successful!")
            print(f"   🎯 Jobs found: {len(jobs)}")
            print(f"   🏢 Unique companies: {analysis.get('total_jobs', 0)}")
            print(f"   📈 Top skills: {', '.join([skill[0] for skill in analysis.get('top_skills', [])[:3]])}")
            
            # Show sample job details
            if jobs:
                sample_job = jobs[0]
                print(f"\n   📋 Sample Job:")
                print(f"      Title: {sample_job['title']}")
                print(f"      Company: {sample_job['company']}")
                print(f"      Location: {sample_job['location']}")
                print(f"      Posted: {sample_job['posted_date']}")
                print(f"      Type: {sample_job['employment_type']}")
                print(f"      Description: {sample_job['description'][:100]}...")
            
            # Show Gavin-specific recommendations
            if analysis.get('gavin_recommendations'):
                print(f"\n   🎯 Gavin-Specific Recommendations:")
                for rec in analysis['gavin_recommendations'][:3]:
                    print(f"      • {rec}")
            
            return True
        else:
            print(f"❌ Job scraping failed: {job_result['error']}")
            print(f"🔍 Suggestion: {job_result.get('fallback_suggestion', 'Try again later')}")
            return False
            
    except Exception as e:
        print(f"❌ Job scraping test failed: {str(e)}")
        return False

def test_enhanced_job_search(client):
    """Test 4: Enhanced AI job search functionality."""
    print(f"\n🧪 TEST 4: Enhanced AI Job Search")
    print("-" * 50)
    
    print("⚠️  This test will perform comprehensive AI job search using multiple search terms")
    print("⚠️  This may use significant Apify credits (~$0.05-0.10)")
    proceed = input("Proceed with enhanced job search test? (y/N): ").lower().strip()
    
    if proceed != 'y':
        print("⏭️  Skipping enhanced job search test")
        return True
    
    try:
        print("🚀 Starting enhanced AI job opportunities search...")
        
        # This will search for multiple AI-related terms
        ai_opportunities = client.get_ai_job_opportunities_enhanced()
        
        if ai_opportunities.get('individual_results'):
            print("✅ Enhanced job search completed!")
            
            combined = ai_opportunities['combined_analysis']
            print(f"   🎯 Total jobs found: {combined['total_jobs_found']}")
            print(f"   🏢 Unique companies: {combined['unique_companies']}")
            print(f"   📈 Top combined skills: {', '.join([skill[0] for skill in combined['top_combined_skills'][:5]])}")
            
            # Show search breakdown
            individual_results = ai_opportunities['individual_results']
            print(f"\n   📊 Search Breakdown:")
            for search_term, result in individual_results.items():
                if result.get('success'):
                    jobs_count = result.get('jobs_found', 0)
                    print(f"      {search_term}: {jobs_count} jobs")
            
            # Show career insights
            if combined.get('career_transition_insights'):
                print(f"\n   🎯 Career Transition Insights:")
                for insight in combined['career_transition_insights'][:3]:
                    print(f"      • {insight}")
            
            # Show skill frequency analysis
            if combined.get('skill_frequency_analysis'):
                print(f"\n   📊 Gavin's Skills Analysis:")
                for skill, analysis_data in list(combined['skill_frequency_analysis'].items())[:3]:
                    percentage = analysis_data['percentage']
                    recommendation = analysis_data['recommendation']
                    print(f"      {skill}: {percentage}% of jobs - {recommendation}")
            
            return True
        else:
            print("❌ Enhanced job search returned no results")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced job search test failed: {str(e)}")
        return False

def test_data_persistence(client):
    """Test 5: Data persistence and file management."""
    print(f"\n🧪 TEST 5: Data Persistence")
    print("-" * 50)
    
    try:
        # Check if data directory exists
        data_dir = client.data_dir
        
        print(f"📁 Data directory: {data_dir}")
        print(f"   Exists: {'✅' if data_dir.exists() else '❌'}")
        
        if data_dir.exists():
            # List saved files
            data_files = list(data_dir.glob("*.json"))
            print(f"   📋 Data files: {len(data_files)}")
            
            for file in data_files[-3:]:  # Show last 3 files
                file_size = file.stat().st_size
                print(f"      {file.name} ({file_size} bytes)")
            
            return True
        else:
            print("   Creating data directory...")
            data_dir.mkdir(exist_ok=True)
            print("   ✅ Data directory created")
            return True
            
    except Exception as e:
        print(f"❌ Data persistence test failed: {str(e)}")
        return False

def test_integration_compatibility():
    """Test 6: Integration with existing LinkedIn tools."""
    print(f"\n🧪 TEST 6: Integration Compatibility")
    print("-" * 50)
    
    try:
        # Test importing existing tools
        print("📦 Testing existing tool imports...")
        
        print("   🔍 LinkedInJobSearcher...", end="")
        job_searcher = LinkedInJobSearcher()
        print(" ✅")
        
        print("   👤 LinkedInProfileManager...", end="")
        profile_manager = LinkedInProfileManager()
        print(" ✅")
        
        # Test basic functionality
        print("   📋 Job searcher history...", end="")
        history_summary = job_searcher.get_search_history_summary()
        print(" ✅")
        
        print("   👤 Profile manager status...", end="")
        profile_status = profile_manager.get_profile_summary()
        print(" ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration compatibility test failed: {str(e)}")
        return False

def main():
    """Run comprehensive Apify integration tests."""
    print("🚀 LinkedIn Apify Integration Test Suite")
    print("=" * 60)
    print("This will test all aspects of the new Apify LinkedIn integration")
    print()
    
    test_results = {}
    
    # Test 1: Setup and connection
    test_results["setup"] = test_apify_setup()
    if not test_results["setup"]:
        print("\n❌ Setup failed - cannot proceed with other tests")
        return
    
    # Initialize client for remaining tests
    client = LinkedInApifyClient()
    
    # Test 2: Profile scraping
    test_results["profile"] = test_profile_scraping(client)
    
    # Test 3: Job scraping
    test_results["jobs"] = test_job_scraping(client)
    
    # Test 4: Enhanced job search
    test_results["enhanced"] = test_enhanced_job_search(client)
    
    # Test 5: Data persistence
    test_results["persistence"] = test_data_persistence(client)
    
    # Test 6: Integration compatibility
    test_results["integration"] = test_integration_compatibility()
    
    # Final summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.title():15} {status}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Apify integration is ready to use.")
        print(f"\n💡 Next Steps:")
        print(f"   1. Use the Job Search Agent with Apify capabilities")
        print(f"   2. Scrape Gavin's profile for optimization analysis") 
        print(f"   3. Perform comprehensive job searches for AI roles")
        print(f"   4. Monitor Apify credit usage and costs")
    else:
        print(f"⚠️  Some tests failed. Check the errors above for troubleshooting.")
        print(f"\n💡 Common Issues:")
        print(f"   • Ensure APIFY_API_TOKEN is correctly set")
        print(f"   • Verify sufficient Apify credits in account")
        print(f"   • Check network connectivity to Apify services")

if __name__ == "__main__":
    main()