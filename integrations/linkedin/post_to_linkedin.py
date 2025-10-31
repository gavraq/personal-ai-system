#!/usr/bin/env python3
"""
Post content to LinkedIn using the LinkedIn API integration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from linkedin_api_client import LinkedInAPIClient

def main():
    """Post the specified content to LinkedIn."""
    
    # Your LinkedIn post content
    post_content = """Building my Personal Consultant Agent system on Claude Code and stumbled across this post from the Manus Team back in July 2025: https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus

I recall the wow moment people were seeing from what Manus was able to achieve and the comments that they were able to do this by leveraging existing LLM model capabilities but I never understood exactly how....now I get it...they were the first to really understand the importance of context engineering which is now becoming mainstream!

A couple of nuggets worth pointing out:

📁 **File System as Ultimate Context** - Treating the file system as unlimited, persistent, directly accessible context. This is the part I am using as the basis for "priming" my agent with the right context at the right time! In my case, I am using markdown files with selected context that can be pulled in on an 'as-needed' basis to prevent polluting the main context window.

❌ **"Keep the Wrong Stuff In"** - Probably the most counterintuitive point: preserve failed actions in context so models learn from mistakes.

⚙️ **"Mask, Don't Remove" Philosophy** - Instead of removing tools from agents, they used context-aware state machines. Only give the agent the tools they need at the right time - with the right context you can select the right tools at the beginning!

🎯 **Dynamic Attention Management** - Interesting insight "recite objectives into end of context" - this seems to keep the agent on-track during long-running tasks to prevent lost-in-the-middle issues.

**The market has caught up to what Manus understood a long time ago**: Context isn't just input - it's the foundation of agent intelligence. Their systematic approach to context engineering has established principles we're only now seeing adopted in the wider market. In my mind, the best insights come from teams building in production, not always in research labs."""

    print("🚀 Posting content to LinkedIn...")
    print("=" * 60)
    print(f"Content preview (first 200 chars):")
    print(f"{post_content[:200]}...")
    print("=" * 60)
    
    # Initialize LinkedIn client
    client = LinkedInAPIClient()
    
    # Test API connection first
    print("🔍 Testing LinkedIn API connection...")
    connection_test = client.test_api_connection()
    print(f"   Connection status: {connection_test['connection_status']}")
    print(f"   Status code: {connection_test['status_code']}")
    
    # Create the LinkedIn post
    print("\n📝 Creating LinkedIn post...")
    result = client.create_linkedin_post(post_content)
    
    if result["success"]:
        print("✅ SUCCESS! LinkedIn post created successfully!")
        print(f"🆔 Post ID: {result.get('post_id', 'Unknown')}")
        print(f"📅 Created at: {result.get('created_at', 'Unknown')}")
        print(f"🔗 Check your LinkedIn profile to see the post")
    else:
        print("❌ FAILED to create LinkedIn post")
        print(f"🔍 Error: {result.get('error', 'Unknown error')}")
        print(f"📄 Status code: {result.get('status_code', 'Unknown')}")
        if result.get('response_text'):
            print(f"📄 Response: {result['response_text'][:300]}...")
            
        # Provide troubleshooting suggestions
        print("\n🛠️ Troubleshooting suggestions:")
        print("   • Check if LinkedIn API access token is valid")
        print("   • Verify LinkedIn app has UGC Post API permissions")
        print("   • Ensure person ID can be retrieved from profile")
    
    print("\n" + "=" * 60)
    return result

if __name__ == "__main__":
    main()