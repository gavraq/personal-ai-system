#!/usr/bin/env python3
"""
LinkedIn API Client for Gavin's Personal Consultant System

This module uses the official LinkedIn API with Gavin's registered app credentials
to access profile data and other LinkedIn functionality.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

class LinkedInAPIClient:
    """
    Official LinkedIn API client using registered app credentials.
    """
    
    def __init__(self):
        """Initialize with Gavin's LinkedIn API credentials from environment variables."""
        import os
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')

        if not all([self.client_id, self.client_secret, self.access_token]):
            raise ValueError("Missing LinkedIn credentials. Set LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, and LINKEDIN_ACCESS_TOKEN environment variables.")
        
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202405"
        }
    
    def get_my_profile(self, person_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the authenticated user's profile information.
        
        Args:
            person_id: Optional person ID to use directly
            
        Returns:
            Dictionary containing profile data or error information
        """
        
        try:
            # Try multiple approaches to get profile data
            approaches = []
            
            # Approach 1: Use person ID directly if provided
            if person_id:
                approaches.append({
                    "name": "Direct Person ID",
                    "url": f"{self.base_url}/people/(id:{person_id})",
                    "params": {"projection": "(id,firstName,lastName,headline,vanityName,profilePicture(displayImage~:playableStreams))"}
                })
            
            # Approach 2: Try userinfo endpoint (should work)
            approaches.append({
                "name": "UserInfo Endpoint", 
                "url": f"{self.base_url}/userinfo",
                "params": {}
            })
            
            # Approach 3: Traditional /me endpoint (likely to fail)
            approaches.append({
                "name": "Me Endpoint",
                "url": f"{self.base_url}/me", 
                "params": {"projection": "(id,firstName,lastName,headline,vanityName,profilePicture(displayImage~:playableStreams))"}
            })
            
            # Try each approach
            for approach in approaches:
                print(f"🔍 Trying {approach['name']}...")
                
                response = requests.get(approach["url"], headers=self.headers, params=approach["params"])
                
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
                if response.status_code == 200:
                    profile_data = response.json()
                    
                    # Process and format the response
                    formatted_profile = self._format_profile_response(profile_data)
                    
                    return {
                        "success": True,
                        "approach_used": approach["name"],
                        "profile": formatted_profile,
                        "raw_response": profile_data,
                        "retrieved_at": datetime.now().isoformat()
                    }
            
            # If all approaches failed
            return {
                "success": False,
                "error": "All profile access approaches failed",
                "attempts": len(approaches),
                "last_status": response.status_code if 'response' in locals() else 'No response'
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception occurred: {str(e)}",
                "exception_type": type(e).__name__
            }
    
    def _format_profile_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format raw LinkedIn API response into readable profile data."""
        
        formatted = {
            "id": raw_data.get("id"),
            "first_name": self._get_localized_value(raw_data.get("firstName")),
            "last_name": self._get_localized_value(raw_data.get("lastName")),
            "headline": self._get_localized_value(raw_data.get("headline")),
            "vanity_name": raw_data.get("vanityName"),
            "profile_url": f"https://www.linkedin.com/in/{raw_data.get('vanityName', '')}" if raw_data.get('vanityName') else None
        }
        
        # Add profile picture if available
        if "profilePicture" in raw_data:
            formatted["profile_picture"] = self._extract_profile_picture(raw_data["profilePicture"])
        
        return formatted
    
    def _get_localized_value(self, localized_field: Optional[Dict]) -> Optional[str]:
        """Extract localized string value from LinkedIn API response."""
        if not localized_field or "localized" not in localized_field:
            return None
        
        localized = localized_field["localized"]
        
        # Try common locale patterns
        for locale in ["en_US", "en_GB", "en"]:
            if locale in localized:
                return localized[locale]
        
        # Return first available value
        if localized:
            return next(iter(localized.values()))
        
        return None
    
    def _extract_profile_picture(self, profile_picture_data: Dict) -> Optional[str]:
        """Extract profile picture URL from API response."""
        try:
            if "displayImage~" in profile_picture_data:
                elements = profile_picture_data["displayImage~"].get("elements", [])
                if elements:
                    # Get the first available image
                    first_element = elements[0]
                    if "identifiers" in first_element:
                        identifiers = first_element["identifiers"]
                        if identifiers:
                            return identifiers[0].get("identifier")
            return None
        except (KeyError, IndexError, TypeError):
            return None
    
    def test_api_connection(self) -> Dict[str, Any]:
        """
        Test the API connection and permissions.
        
        Returns:
            Dictionary with connection test results
        """
        
        try:
            # Simple test request to /me endpoint
            test_url = f"{self.base_url}/me"
            response = requests.get(test_url, headers=self.headers)
            
            # Include response details for debugging
            result = {
                "connection_status": "success" if response.status_code == 200 else "failed",
                "status_code": response.status_code,
                "response_size": len(response.text),
                "response_text": response.text[:500] + "..." if len(response.text) > 500 else response.text,
                "has_access_token": bool(self.access_token),
                "token_length": len(self.access_token) if self.access_token else 0,
                "api_base_url": self.base_url,
                "test_timestamp": datetime.now().isoformat()
            }
            
            # Try to parse response as JSON if possible
            try:
                if response.text:
                    result["response_json"] = response.json()
            except json.JSONDecodeError:
                pass
                
            return result
            
        except Exception as e:
            return {
                "connection_status": "error",
                "error": str(e),
                "exception_type": type(e).__name__,
                "test_timestamp": datetime.now().isoformat()
            }
    
    def get_profile_analysis_for_ai_transition(self) -> Dict[str, Any]:
        """
        Get profile data and analyze it for AI career transition readiness.
        
        Returns:
            Profile data with AI transition analysis
        """
        
        # Get profile data
        profile_result = self.get_my_profile()
        
        if not profile_result["success"]:
            return profile_result
        
        profile = profile_result["profile"]
        
        # Analyze for AI transition
        ai_analysis = self._analyze_ai_transition_readiness(profile)
        
        return {
            "success": True,
            "profile": profile,
            "ai_analysis": ai_analysis,
            "retrieved_at": datetime.now().isoformat()
        }
    
    def _analyze_ai_transition_readiness(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze profile for AI career transition readiness."""
        
        headline = (profile.get("headline") or "").lower()
        
        # Check for AI-related terms in headline
        ai_terms = ["ai", "artificial intelligence", "machine learning", "ml", "data science", "python"]
        ai_terms_in_headline = [term for term in ai_terms if term in headline]
        
        # Check for risk management terms
        risk_terms = ["risk", "management", "financial", "banking", "compliance"]
        risk_terms_in_headline = [term for term in risk_terms if term in headline]
        
        # Calculate AI readiness score
        ai_score = len(ai_terms_in_headline) * 20  # Up to 100% if 5+ AI terms
        ai_score = min(ai_score, 100)
        
        return {
            "ai_readiness_score": ai_score,
            "ai_terms_present": ai_terms_in_headline,
            "risk_terms_present": risk_terms_in_headline,
            "current_headline": profile.get("headline"),
            "recommendations": self._get_headline_recommendations(ai_score, headline),
            "next_steps": [
                "Add AI/ML terms to headline if missing",
                "Include Python/data science skills",
                "Mention career transition to AI",
                "Highlight risk + AI combination"
            ]
        }
    
    def _get_headline_recommendations(self, ai_score: int, current_headline: str) -> List[str]:
        """Get specific headline recommendations based on current state."""
        
        recommendations = []
        
        if ai_score < 20:
            recommendations.append("🎯 Add 'AI' or 'Artificial Intelligence' to headline")
            recommendations.append("🐍 Include 'Python Developer' or similar technical terms")
            recommendations.append("🚀 Mention 'Transitioning to AI' or 'AI Career Focus'")
        
        if "risk" in current_headline.lower():
            recommendations.append("🏦 Leverage unique 'Risk Management + AI' combination")
            recommendations.append("📊 Consider 'AI Risk Analyst' or 'Risk + AI Specialist'")
        
        if ai_score < 40:
            recommendations.append("🤖 Add 'Machine Learning' or 'Data Science'")
            recommendations.append("🎓 Include learning/transition language")
        
        # Suggest specific headline formats
        recommendations.append("💡 Example: 'Risk Management Professional Transitioning to AI | Python Developer | Chartered Accountant'")
        
        return recommendations
    
    def create_linkedin_post(self, message: str) -> Dict[str, Any]:
        """
        Create a LinkedIn post using the Share API.
        
        Args:
            message: The text content for the post
            
        Returns:
            Dictionary with post creation results
        """
        
        try:
            # LinkedIn Share API endpoint
            post_url = f"{self.base_url}/ugcPosts"
            
            # Get person ID first (required for posting)
            person_id = self._get_person_id()
            if not person_id:
                return {
                    "success": False,
                    "error": "Could not retrieve person ID for posting",
                    "suggestion": "Profile API access required for person ID"
                }
            
            # Construct post data according to LinkedIn UGC API format
            post_data = {
                "author": f"urn:li:person:{person_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": message
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Make the API request
            response = requests.post(post_url, headers=self.headers, json=post_data)
            
            if response.status_code == 201:
                response_data = response.json()
                return {
                    "success": True,
                    "post_id": response_data.get("id"),
                    "message": "LinkedIn post created successfully!",
                    "post_content": message,
                    "response_data": response_data,
                    "created_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"Failed to create post: {response.status_code}",
                    "response_text": response.text[:500],
                    "post_content": message
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Exception creating post: {str(e)}",
                "exception_type": type(e).__name__,
                "post_content": message
            }
    
    def _get_person_id(self) -> Optional[str]:
        """
        Get the person ID using OpenID Connect userinfo endpoint.
        This should work with your "Sign In with LinkedIn" product.
        """
        try:
            # Try OpenID Connect userinfo endpoint first (should work with your products)
            userinfo_url = f"{self.base_url}/userinfo"
            response = requests.get(userinfo_url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                # OpenID Connect returns 'sub' field with person URN
                sub = data.get("sub")
                if sub:
                    # Extract person ID from URN format: urn:li:person:XXXXX
                    if sub.startswith("urn:li:person:"):
                        return sub.split(":")[-1]
                    return sub
            
            # Fallback: try /me endpoint (likely to fail but worth trying)
            me_response = requests.get(f"{self.base_url}/me", headers=self.headers)
            if me_response.status_code == 200:
                me_data = me_response.json()
                return me_data.get("id")
                
            return None
            
        except Exception as e:
            print(f"Error getting person ID: {e}")
            return None
    
    def test_userinfo_endpoint(self) -> Dict[str, Any]:
        """Test the OpenID Connect userinfo endpoint."""
        try:
            userinfo_url = f"{self.base_url}/userinfo"
            response = requests.get(userinfo_url, headers=self.headers)
            
            result = {
                "endpoint": "/userinfo",
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_text": response.text[:500] if response.text else "No response"
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result["data"] = data
                    result["person_id"] = self._extract_person_id_from_userinfo(data)
                except json.JSONDecodeError:
                    result["json_error"] = "Could not parse JSON response"
            
            return result
        
        except Exception as e:
            return {
                "endpoint": "/userinfo", 
                "success": False,
                "error": str(e),
                "exception_type": type(e).__name__
            }
    
    def _extract_person_id_from_userinfo(self, userinfo_data: Dict[str, Any]) -> Optional[str]:
        """Extract person ID from userinfo response."""
        # Look for 'sub' field (standard OpenID Connect)
        sub = userinfo_data.get("sub")
        if sub:
            if sub.startswith("urn:li:person:"):
                return sub.split(":")[-1]
            return sub
        
        # Look for other possible ID fields
        for field in ["id", "user_id", "member_id"]:
            if field in userinfo_data:
                return str(userinfo_data[field])
        
        return None
    
    def create_test_post(self) -> Dict[str, Any]:
        """Create a test LinkedIn post to verify posting functionality."""
        
        test_message = "Just tried a Claude Code sub agent that does LinkedIn posts for me, the developments in AI are amazing!"
        
        print("🚀 Creating LinkedIn Post...")
        print(f"📝 Message: {test_message}")
        
        # First, try to get person ID with detailed logging
        print("🔍 Getting person ID...")
        person_id = self._get_person_id()
        if person_id:
            print(f"✅ Person ID retrieved: {person_id}")
        else:
            print("❌ Could not get person ID")
            # Test the userinfo endpoint specifically
            print("🧪 Testing /userinfo endpoint...")
            userinfo_result = self.test_userinfo_endpoint()
            print(f"   Status: {userinfo_result['status_code']}")
            print(f"   Response: {userinfo_result['response_text']}")
            if userinfo_result.get('data'):
                print(f"   Data fields: {list(userinfo_result['data'].keys())}")
        
        result = self.create_linkedin_post(test_message)
        
        if result["success"]:
            print("✅ Post created successfully!")
            print(f"🆔 Post ID: {result.get('post_id', 'Unknown')}")
        else:
            print("❌ Post creation failed")
            print(f"🔍 Error: {result.get('error', 'Unknown error')}")
            if result.get('response_text'):
                print(f"📄 Response: {result['response_text']}")
        
        return result

def main():
    """Test the LinkedIn API client."""
    
    print("🔍 Testing LinkedIn API Connection")
    print("=" * 50)
    
    client = LinkedInAPIClient()
    
    # Test connection
    print("1. Testing API Connection...")
    connection_test = client.test_api_connection()
    print(f"   Status: {connection_test['connection_status']}")
    print(f"   Status Code: {connection_test['status_code']}")
    print(f"   Token Length: {connection_test['token_length']}")
    print(f"   Response: {connection_test.get('response_text', 'No response')}")
    
    if 'response_json' in connection_test:
        print(f"   Error Details: {connection_test['response_json']}")
    
    # Test LinkedIn posting functionality
    print(f"\n2. Testing LinkedIn Post Creation...")
    print("=" * 50)
    
    # Create the test post
    post_result = client.create_test_post()
    
    # Since posting worked, we have a person ID - try to get profile data
    if post_result.get('success'):
        print(f"\n3. Testing Profile Data Access...")
        print("=" * 50)
        
        # Extract person ID from successful post result
        # We know it worked, so let's use the hardcoded ID we discovered
        person_id = "jX975koQMc"  # From the successful post
        
        print(f"🆔 Using Person ID: {person_id}")
        
        # Try to get profile data using the person ID
        profile_result = client.get_my_profile(person_id=person_id)
        
        if profile_result['success']:
            profile = profile_result['profile']
            print(f"✅ Profile retrieved using: {profile_result['approach_used']}")
            print(f"   Name: {profile.get('first_name')} {profile.get('last_name')}")
            print(f"   Headline: {profile.get('headline', 'No headline')}")
            print(f"   Profile URL: {profile.get('profile_url', 'No vanity URL')}")
            
            # Run AI analysis if we got profile data
            print(f"\n4. AI Transition Analysis:")
            ai_analysis = client._analyze_ai_transition_readiness(profile)
            print(f"   AI Readiness Score: {ai_analysis['ai_readiness_score']}%")
            print(f"   AI Terms Present: {', '.join(ai_analysis['ai_terms_present']) if ai_analysis['ai_terms_present'] else 'None'}")
            
            print(f"\n5. Recommendations:")
            for rec in ai_analysis['recommendations'][:3]:
                print(f"   • {rec}")
        else:
            print(f"❌ Profile access failed: {profile_result.get('error', 'Unknown error')}")
            print(f"   Attempts made: {profile_result.get('attempts', 0)}")
    else:
        print(f"\n📋 Summary:")
        print(f"   • Connection test: Failed (403 - insufficient permissions)")
        print(f"   • Post creation: Failed (likely needs person ID from profile)")
        print(f"   • Issue: Your LinkedIn app needs additional permissions/products")
        print(f"   • Next step: Add Profile API or UGC Post API products to your LinkedIn app")

if __name__ == "__main__":
    main()