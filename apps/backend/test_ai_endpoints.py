#!/usr/bin/env python3
"""
Test script to demonstrate AI endpoints usage
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_ai_health():
    """Test AI service health"""
    print("🏥 Testing AI Health...")
    response = requests.get(f"{BASE_URL}/ai/health")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ AI Service Status: {data['status']}")
        print(f"   Endpoint: {data['endpoint']}")
        print(f"   Model: {data['deployment']}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code}")
        return False

def test_ai_capabilities():
    """Test AI capabilities endpoint"""
    print("\n🔧 Testing AI Capabilities...")
    response = requests.get(f"{BASE_URL}/ai/capabilities")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Service: {data['service']}")
        print(f"   Model: {data['models']['chat']}")
        print(f"   Max Tokens: {data['models']['max_tokens']}")
        print("\n   Available Capabilities:")
        for cap in data['capabilities']:
            print(f"   - {cap['name']}: {cap['description']}")
        return True
    else:
        print(f"❌ Capabilities check failed: {response.status_code}")
        return False

def test_video_script_generation():
    """Test video script generation (requires authentication)"""
    print("\n📹 Testing Video Script Generation...")
    
    # Note: This endpoint requires authentication
    # For testing purposes, we'll show what the request would look like
    payload = {
        "topic": "Introduction to Artificial Intelligence",
        "duration": 60,
        "style": "engaging"
    }
    
    print("Request payload:")
    print(json.dumps(payload, indent=2))
    print("\nNote: This endpoint requires authentication (Bearer token)")
    print("To test with authentication, you would need to:")
    print("1. Register/login to get an access token")
    print("2. Include the token in the Authorization header")
    print("3. Make the POST request to /api/v1/ai/generate-video-script")
    
    return True

def test_text_generation():
    """Test basic text generation (requires authentication)"""
    print("\n🤖 Testing Text Generation...")
    
    payload = {
        "prompt": "Write a brief introduction about video generation technology",
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    print("Request payload:")
    print(json.dumps(payload, indent=2))
    print("\nNote: This endpoint also requires authentication")
    print("Example curl command (with token):")
    print('curl -X POST "http://localhost:8000/api/v1/ai/generate-text" \\')
    print('  -H "Authorization: Bearer YOUR_TOKEN_HERE" \\')
    print('  -H "Content-Type: application/json" \\')
    print(f'  -d \'{json.dumps(payload)}\'')
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing AI Endpoints")
    print("=" * 50)
    
    # Test public endpoints (no auth required)
    health_ok = test_ai_health()
    capabilities_ok = test_ai_capabilities()
    
    if health_ok and capabilities_ok:
        print("\n✅ Public AI endpoints are working!")
        
        # Show examples of authenticated endpoints
        test_video_script_generation()
        test_text_generation()
        
        print("\n" + "=" * 50)
        print("🎉 AI Integration Setup Complete!")
        print("\nNext Steps:")
        print("1. Use the authentication endpoints to get a token")
        print("2. Test the AI generation endpoints with the token")
        print("3. Integrate AI features into your frontend application")
        
    else:
        print("\n❌ Some tests failed. Check your configuration.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server. Make sure it's running on localhost:8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)
