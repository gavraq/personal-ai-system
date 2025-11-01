# Generate LinkedIn Access Token

Your LinkedIn API credentials are configured, but you need an access token to make API calls.

## Quick Method: LinkedIn Developer Portal

1. **Go to LinkedIn Developers**: https://www.linkedin.com/developers/apps
2. **Select your app**
3. **Navigate to "Auth" tab**
4. **Find "OAuth 2.0 Tools"** section
5. **Click "Generate token"** or "Request access token"
6. **Select required scopes**:
   - ✅ `openid` - For user identification
   - ✅ `profile` - For basic profile access
   - ✅ `w_member_social` - **Required for posting to LinkedIn**
7. **Click "Request access token"**
8. **Copy the generated token**
9. **Add to .env file**:
   ```bash
   LINKEDIN_ACCESS_TOKEN="your_generated_token_here"
   ```

## Alternative: OAuth 2.0 Flow (More Complex)

If the Developer Portal doesn't have a "Generate token" button, you'll need to use OAuth flow:

### Step 1: Get Authorization Code
Open this URL in your browser (replace CLIENT_ID and REDIRECT_URI with your values):
```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=openid%20profile%20w_member_social
```

### Step 2: Exchange Code for Access Token
After authorization, LinkedIn redirects you with a code. Use this curl command:
```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_AUTH_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=YOUR_REDIRECT_URI"
```

### Step 3: Extract Access Token
The response will contain an access token:
```json
{
  "access_token": "YOUR_ACCESS_TOKEN",
  "expires_in": 5184000
}
```

## After Getting Access Token

1. **Add to .env file**:
   ```bash
   # Edit /Users/gavinslater/projects/life/.env
   LINKEDIN_ACCESS_TOKEN="your_actual_token_here"
   ```

2. **Set environment variable** (for current session):
   ```bash
   export LINKEDIN_CLIENT_ID="your_client_id"
   export LINKEDIN_CLIENT_SECRET="your_client_secret"
   export LINKEDIN_ACCESS_TOKEN="your_actual_token_here"
   ```

3. **Test the integration**:
   ```bash
   cd /Users/gavinslater/projects/life/integrations/linkedin
   python3 post_to_linkedin.py
   ```

## Token Expiration

LinkedIn access tokens expire after 60 days (5,184,000 seconds). When expired:
1. Go back to LinkedIn Developer Portal
2. Generate a new token
3. Update the .env file
4. Restart any services using the token

## Troubleshooting

**"Invalid token" error**:
- Token might be expired (60-day lifetime)
- Regenerate token in Developer Portal
- Check you selected the right scopes (especially `w_member_social` for posting)

**"Insufficient permissions" error**:
- Your app needs "UGC Post" API product enabled
- Go to: LinkedIn Developers → Your App → Products tab
- Request "Share on LinkedIn" or "UGC Post" product access

**"Person ID not found" error**:
- This is automatic - the system retrieves it via OpenID Connect
- Ensure `openid` and `profile` scopes are included in your token

## App Configuration Requirements

Make sure your LinkedIn app has:
- ✅ **Products**: "Share on LinkedIn" or "Sign In with LinkedIn using OpenID Connect"
- ✅ **Authorized Redirect URLs**: Configured (if using OAuth flow)
- ✅ **OAuth 2.0 Scopes**: openid, profile, w_member_social
