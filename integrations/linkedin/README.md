# LinkedIn Integration for Personal Consultant System

This directory contains the LinkedIn integration components for Gavin's Personal Consultant system, providing LinkedIn profile management, job search capabilities, and automated posting functionality.

## Overview

The LinkedIn integration enables:
- **Profile Management**: Track and optimize LinkedIn profile for AI career transition
- **Job Search**: Find and analyze LinkedIn job opportunities using web search
- **Profile-Job Matching**: Score job opportunities against current profile
- **Application Tracking**: Monitor applications and follow-up activities
- **LinkedIn Posting**: Automated content publishing via LinkedIn API
- **Optimization Guidance**: Receive specific recommendations for profile improvement

## Architecture

### Core Components

#### `linkedin_api_client.py`
Official LinkedIn API integration:
- **Authentication**: OAuth 2.0 via LinkedIn Developer App
- **Posting**: Create LinkedIn posts programmatically
- **Profile Access**: Basic profile data via OpenID Connect
- **Person ID**: jX975koQMc (for posting operations)

#### `linkedin_profile_manager.py`
Manages LinkedIn profile data and optimization:
- **Profile Template**: Auto-generated from Gavin's background
- **Skills Management**: Add/update technical and business skills
- **Optimization Engine**: Provides AI transition recommendations
- **Application Tracking**: Monitor job applications and status

#### `linkedin_job_searcher.py`
Handles LinkedIn job search and analysis:
- **Web Search Integration**: Uses Claude Code's WebSearch for LinkedIn jobs
- **Job Analysis**: Match job requirements against profile
- **Search History**: Track searches and results over time
- **Manual Fallback**: Provides LinkedIn URLs when web search unavailable

#### `post_to_linkedin.py`
Command-line script for posting to LinkedIn:
- **Simple Interface**: Edit content directly in the script
- **API Integration**: Uses LinkedInAPIClient for posting
- **Error Handling**: Clear feedback on success/failure

#### `test_linkedin_integration.py`
Comprehensive test suite validating all functionality:
- **Profile Management Tests**: Skills, optimization, data persistence
- **Job Search Tests**: Analysis, matching, URL generation
- **Integration Tests**: Component interaction and data flow

## Setup

### LinkedIn API Credentials

You'll need credentials from your LinkedIn Developer App:

1. Go to: https://www.linkedin.com/developers/apps
2. Select your app (or create one if needed)
3. Get your credentials from the "Auth" tab

Set environment variables:
```bash
export LINKEDIN_CLIENT_ID="your_client_id"
export LINKEDIN_CLIENT_SECRET="your_client_secret"
export LINKEDIN_ACCESS_TOKEN="your_access_token"
```

**Note**: Access tokens expire. You'll need to regenerate them periodically via the LinkedIn Developer Portal.

### Python Environment

The integration uses Python 3.13+ with standard library only (no external dependencies for core functionality).

## Usage

### LinkedIn Profile Analysis
```python
from linkedin_profile_manager import LinkedInProfileManager

profile_manager = LinkedInProfileManager()

# Get current profile status
summary = profile_manager.get_profile_summary()

# Get optimization suggestions
suggestions = profile_manager.get_profile_optimization_suggestions()

# Add AI-related skills
profile_manager.add_skill("TensorFlow")
profile_manager.add_skill("Machine Learning")
```

### LinkedIn Job Search
```python
from linkedin_job_searcher import LinkedInJobSearcher

job_searcher = LinkedInJobSearcher(WebSearch, WebFetch)

# Search for AI jobs on LinkedIn
results = job_searcher.search_linkedin_jobs(
    keywords="AI Risk Management",
    location="London UK",
    experience_level="senior"
)

# Analyze specific job posting
analysis = job_searcher.analyze_job_description(job_text, job_title)
print(f"Match Score: {analysis['match_percentage']}%")
print(f"Recommendation: {analysis['recommendation']}")
```

### LinkedIn Posting
```python
from linkedin_api_client import LinkedInAPIClient

client = LinkedInAPIClient()

# Create a LinkedIn post
result = client.create_linkedin_post("Your post content here...")

if result["success"]:
    print(f"Post created! ID: {result['post_id']}")
else:
    print(f"Error: {result['error']}")
```

Or use the command-line script:
```bash
cd /Users/gavinslater/projects/life/integrations/linkedin
python3 post_to_linkedin.py
```

### Application Tracking
```python
# Save job opportunity
profile_manager.save_job_opportunity({
    "title": "Senior AI Risk Analyst",
    "company": "Barclays",
    "match_score": 85.0,
    "url": "linkedin.com/jobs/123"
})

# Track application
profile_manager.track_application(job_info, application_data)

# Get application status
status = profile_manager.get_application_status()
```

## Data Storage

### Profile Data (`gavin_linkedin_profile.json`)
Stores comprehensive profile information:
- **Basic Info**: Name, headline, location, current position
- **Experience**: Work history with ICBC, Barclays, etc.
- **Skills**: Technical and business skills with AI learning focus
- **Career Goals**: Current role and AI transition objectives
- **Optimization Status**: Profile readiness and improvement recommendations

### Search History (`linkedin_job_searches.json`)
Tracks job search activities:
- **Searches**: Keywords, locations, results counts
- **Saved Jobs**: Interesting opportunities with match scores
- **Applications**: Applied positions with tracking data
- **Analytics**: Search patterns and success rates

## Terms of Service Compliance

### Respectful Integration
- **Official API**: Uses LinkedIn's official API for posting and profile access
- **Web Search Only**: Job discovery via legitimate web search APIs
- **No Scraping**: Does not scrape or bypass LinkedIn's access controls
- **Manual Fallback**: Provides LinkedIn URLs for manual browsing when needed
- **Rate Limiting**: Respects API limits and best practices

### Legitimate Use Cases
- **Profile Optimization**: Helps improve public LinkedIn profile
- **Job Discovery**: Finds publicly posted job opportunities
- **Application Support**: Assists with application materials and strategy
- **Career Planning**: Provides market intelligence for career decisions
- **Content Publishing**: Automated posting via official API

## Integration with Job Search Agent

The LinkedIn integration is primarily accessed through the Job Search Agent sub-agent:

```markdown
# Job Search Agent Commands
- "How's my LinkedIn profile for AI roles?" → Profile analysis
- "Find me LinkedIn AI jobs" → Job search with matching
- "Analyze this LinkedIn job for me" → Job-profile fit analysis
- "Track this application" → Application monitoring
- "Post this to LinkedIn" → Automated content publishing
- "What LinkedIn optimizations should I make?" → Profile improvements
```

## Testing

Run the test suite to validate functionality:

```bash
cd /Users/gavinslater/projects/life/integrations/linkedin
python3 test_linkedin_integration.py
```

Tests cover:
- Profile management and optimization
- Job search and analysis capabilities
- Application tracking functionality
- Component integration and data persistence

## Troubleshooting

### LinkedIn API Issues

**Token Expired**:
- Access tokens expire regularly
- Regenerate via LinkedIn Developer Portal
- Update `LINKEDIN_ACCESS_TOKEN` environment variable

**Permission Errors**:
- Verify your LinkedIn app has "UGC Post" permissions
- Check "Sign In with LinkedIn using OpenID Connect" is enabled
- Ensure you've accepted the latest API terms

**Person ID Not Found**:
- The person ID (jX975koQMc) is documented for reference
- System automatically retrieves it via OpenID Connect
- If issues persist, check OAuth scope includes `openid` and `profile`

### Job Search Issues

**No Results**:
- Try broader keywords
- Check location formatting ("London UK" vs "London, United Kingdom")
- Use WebSearch tool if available in your environment

**Low Match Scores**:
- Update LinkedIn profile with relevant skills
- Add AI/ML skills to profile template
- Review job requirements for missing competencies

## Security and Privacy

### Data Protection
- **Local Storage**: All profile and search data stored locally
- **No External Sharing**: Profile information never transmitted except via official LinkedIn API
- **Secure File Handling**: JSON files with appropriate permissions
- **Privacy First**: Respects user control over personal data

### Access Control
- **File Permissions**: Appropriate read/write permissions on data files
- **No Stored Credentials**: Does not store LinkedIn login credentials
- **Environment Variables**: API credentials via env vars only (never in code)
- **User Control**: All data management under user control

## Future Enhancements

### Planned Features
- **LinkedIn Content Strategy**: Article topic suggestions for thought leadership
- **Skills Gap Tracking**: Monitor progress on missing skills from job analysis
- **Interview Preparation**: Company research and question preparation
- **Salary Intelligence**: Market data analysis for negotiation support

### Integration Opportunities
- **Daily Brief Agent**: LinkedIn news and industry updates
- **Content Creation Agent**: LinkedIn article planning and publishing
- **Learning Agent**: Skill development aligned with job requirements
- **Calendar Integration**: Interview scheduling and follow-up reminders

This LinkedIn integration provides comprehensive career transition support while maintaining security, privacy, and respect for LinkedIn's platform policies.
