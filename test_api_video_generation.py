#!/usr/bin/env python3
"""
Test script to directly test the video generation API endpoint
"""

import requests
import json

def test_video_api():
    """Test the video generation API endpoint"""
    print("🧪 Testing Video Generation API Endpoint")
    print("=" * 50)
    
    # API endpoint
    url = "http://localhost:8000/api/v1/videos/test-generate"
    
    # Test data matching what the frontend sends
    test_data = {
        "title": "Test Video from API",
        "description": "Testing video generation through API",
        "generation_type": "template_based",
        "config": {
            "elements": [
                {
                    "id": "1",
                    "type": "text",
                    "content": "Hello from API Test!",
                    "position": {"x": 50, "y": 50},
                    "size": {"width": 300, "height": 60},
                    "style": {
                        "fontSize": 24,
                        "fontFamily": "Arial",
                        "color": "#ffffff",
                        "backgroundColor": "transparent"
                    },
                    "timing": {"start": 0, "duration": 5}
                }
            ],
            "duration": 10,
            "resolution": "1920x1080",
            "fps": 30,
            "format": "mp4",
            "aspect_ratio": "16:9"
        },
        "template_id": None
    }
    
    print(f"📡 Making request to: {url}")
    print(f"📦 Request data:")
    print(json.dumps(test_data, indent=2))
    print()
    
    try:
        # Make the request without authentication first
        print("🔓 Testing without authentication...")
        response = requests.post(url, json=test_data)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📋 Response Body:")
            print(json.dumps(response_data, indent=2))
        except:
            print(f"📋 Response Body (raw): {response.text}")
        
        if response.status_code == 401:
            print("\n🔐 Authentication required. This is expected.")
            print("💡 The endpoint exists and is responding correctly.")
            print("🎯 The issue might be with authentication in the frontend.")
        elif response.status_code == 422:
            print("\n❌ Validation error. Data format issue.")
        elif response.status_code == 500:
            print("\n💥 Server error. Backend processing issue.")
        else:
            print(f"\n✅ Unexpected response code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Is the backend server running on localhost:8000?")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🧪 API test completed!")


if __name__ == "__main__":
    test_video_api()
