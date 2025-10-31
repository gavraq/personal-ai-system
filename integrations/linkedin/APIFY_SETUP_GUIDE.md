# Apify LinkedIn Integration Setup Guide

This guide walks you through setting up Apify platform integration for LinkedIn profile and job scraping capabilities in your Personal Consultant system.

## Overview

The Apify integration provides enhanced LinkedIn job intelligence using free scrapers only:

- **Free LinkedIn Job Search**: Extract detailed job postings with requirements, descriptions, and company information  
- **Advanced Analytics**: Deep analysis of job market trends and skill requirements
- **Career Transition Intelligence**: AI-powered insights for your Risk Management to AI transition
- **Cost-Effective**: Uses only free Apify actors to keep costs minimal

**Note**: Profile scraping has been removed as it requires premium actors. Use the existing LinkedIn API for basic profile data instead.

## Step 1: Create Apify Account

1. **Sign Up**: Go to [https://apify.com](https://apify.com) and create a free account
2. **Verify Email**: Complete email verification process
3. **Free Tier**: Start with free tier which includes $5 monthly credit (sufficient for personal use)

### Free Tier Credits
- **Monthly Allowance**: $5 worth of credits
- **Job Scraping Cost**: ~$0.01 per search (typically finds 40-50 jobs)
- **Your Usage**: Approximately 500 job searches per month (more than enough!)

## Step 2: Get API Token

1. **Login** to Apify Console: [https://console.apify.com](https://console.apify.com)
2. **Navigate** to Account Settings → Integrations
3. **Generate** new API token:
   - Name: "LinkedIn Integration - Personal Consultant"
   - Permissions: Full access (for your personal account)
4. **Copy** the API token (starts with `apify_api_...`)

## Step 3: Configure Environment

### Set Environment Variable

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export APIFY_API_TOKEN="apify_api_xxxxxxxxxxxxxxxxxxxxxxxxx"

# Or set for current session
export APIFY_API_TOKEN="your_token_here"
```

### Verify Installation

```bash
# Navigate to LinkedIn integration directory
cd /Users/gavinslater/projects/Life/linkedin-integration

# Activate virtual environment
source venv/bin/activate

# Test the integration
python test_apify_integration.py
```

## Step 4: Understanding Costs

### Typical Usage Costs for Gavin's Use Case

| Operation | Frequency | Cost per Operation | Monthly Cost |
|-----------|-----------|-------------------|-------------|
| AI Job Search | 3x per week | $0.01 | $0.12 |
| Targeted Job Search | Daily | $0.01 | $0.31 |
| Market Analysis | Weekly | $0.05 | $0.22 |
| **Total Monthly** | | | **~$0.65** |

**Result**: Well within the $5 free monthly allowance! Profile data comes from existing LinkedIn API.

## Step 5: Test Integration

### Run Comprehensive Tests

```bash
# Make sure environment variable is set
echo $APIFY_API_TOKEN

# Run the test suite
python test_apify_integration.py
```

### Test Components
1. **Connection Test**: Verifies API token and credit balance
2. **Profile Scraping**: Tests scraping your LinkedIn profile (optional, uses credits)
3. **Job Scraping**: Tests job search functionality (optional, uses credits)
4. **Enhanced Search**: Multi-term AI job search (optional, uses more credits)
5. **Data Persistence**: Verifies file saving and management
6. **Integration**: Tests compatibility with existing tools

## Step 6: Usage Examples

### LinkedIn Job Intelligence
```python
from linkedin_apify_client import LinkedInApifyClient

# Initialize client (uses APIFY_API_TOKEN environment variable)
client = LinkedInApifyClient()

# Note: Profile scraping removed - use LinkedIn API for profile data
profile_result = client.scrape_gavin_profile()
print(profile_result["message"])  # Shows alternative approaches
```

### AI Job Search
```python
# Search for AI roles in London
job_results = client.scrape_jobs(
    keywords="AI Risk Management",
    location="London UK",
    max_results=20
)

# Comprehensive AI job search across multiple terms
ai_opportunities = client.get_ai_job_opportunities_enhanced()
```

### Integration with Job Search Agent
```python
# The Job Search Agent now automatically uses Apify when available
# Just use the agent normally - it will leverage enhanced capabilities
```

## Legal Considerations

### Important Notes
- **LinkedIn Terms**: Apify scraping violates LinkedIn's Terms of Service
- **Legal Gray Area**: Scraping publicly visible data may be legally permissible
- **Risk Assessment**: Low risk for personal, non-commercial use
- **Mitigation**: Use scraped data privately, don't redistribute or commercialize

### Best Practices
- **Rate Limiting**: Apify handles respectful scraping automatically
- **Data Usage**: Keep scraped data for personal career development only
- **Frequency**: Don't scrape excessively - weekly or bi-weekly is sufficient
- **Respect**: Use LinkedIn normally alongside scraping

## Troubleshooting

### Common Issues

#### "APIFY_API_TOKEN not set"
```bash
# Check if variable is set
echo $APIFY_API_TOKEN

# If empty, set it:
export APIFY_API_TOKEN="your_token_here"

# Make it permanent by adding to shell profile
echo 'export APIFY_API_TOKEN="your_token_here"' >> ~/.zshrc
```

#### "Insufficient Credits" Error
1. Check credit balance: [https://console.apify.com/account#/usage](https://console.apify.com/account#/usage)
2. Wait for monthly credit refresh
3. Consider upgrading if needed (unlikely for personal use)

#### "Actor Failed" Errors
1. LinkedIn may be temporarily blocking scraping
2. Try again in a few hours
3. Use smaller batch sizes (max_results=5 instead of 20)

#### Import Errors
```bash
# Ensure you're in virtual environment
source venv/bin/activate

# Verify Apify client is installed
pip list | grep apify
```

## Data Management

### File Locations
- **Scraped Data**: `linkedin-integration/apify_data/`
- **Profile Data**: `profile_gavinslater_TIMESTAMP.json`
- **Job Data**: `jobs_TIMESTAMP.json`

### Data Retention
- Files are automatically saved with timestamps
- Clean up old files periodically to save disk space
- Consider backing up valuable job search data

## Next Steps

Once Apify is configured:

1. **Update LinkedIn Profile**: Use scraped data to identify optimization opportunities
2. **Comprehensive Job Search**: Leverage enhanced job scraping for AI roles
3. **Market Analysis**: Use job data analytics for career strategy
4. **Application Tracking**: Integrate with existing application management
5. **Content Creation**: Use market insights for blog posts and LinkedIn content

## Cost Monitoring

### Track Usage
- **Monthly Check**: Review credit usage in Apify console
- **Optimization**: Adjust search frequency if approaching limit
- **Upgrade Path**: $49/month paid plan if usage grows significantly

### Expected Costs for Heavy Usage
- **Job Search 3x/week**: ~$4/month
- **Profile updates weekly**: ~$0.05/month  
- **Total**: Well within free tier for personal use

## Support

### Get Help
- **Apify Documentation**: [https://docs.apify.com](https://docs.apify.com)
- **LinkedIn Integration Issues**: Check `test_apify_integration.py` results
- **Claude Code Integration**: Use the updated Job Search Agent documentation

### Monitoring
- **Success Rate**: Monitor scraping success rates
- **Data Quality**: Review scraped data for completeness
- **Cost Tracking**: Watch monthly credit consumption

---

🎉 **You're Ready!** Once configured, your Personal Consultant system will have comprehensive LinkedIn intelligence capabilities to accelerate your AI career transition.