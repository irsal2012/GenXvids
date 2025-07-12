#!/usr/bin/env python3
"""
Debug script to test image upload functionality
"""

import requests
import io
from PIL import Image
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def create_test_image():
    """Create a test image in memory"""
    # Create a simple test image
    img = Image.new('RGB', (200, 150), color='blue')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

def test_upload_endpoint():
    """Test the upload endpoint with detailed debugging"""
    
    print("🧪 Testing Image Upload Endpoint")
    print("=" * 50)
    
    # Test 1: Check if endpoint exists
    print("\n1. Testing endpoint availability")
    try:
        response = requests.options(f"{API_BASE}/assets/upload")
        print(f"   OPTIONS Status: {response.status_code}")
        print(f"   Allowed methods: {response.headers.get('Allow', 'Not specified')}")
    except Exception as e:
        print(f"   ❌ Error checking endpoint: {e}")
    
    # Test 2: Test actual upload
    print("\n2. Testing image upload")
    try:
        # Create test image
        test_image = create_test_image()
        
        # Prepare files and data
        files = {
            'file': ('test_image.png', test_image, 'image/png')
        }
        
        data = {
            'name': 'Test Image',
            'category': 'media'
        }
        
        print(f"   📤 Uploading test image...")
        print(f"   📋 Data: {data}")
        
        response = requests.post(f"{API_BASE}/assets/upload", files=files, data=data)
        
        print(f"   📊 Status: {response.status_code}")
        print(f"   📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"   ✅ Success: {result}")
            except:
                print(f"   ✅ Success (non-JSON): {response.text}")
        else:
            print(f"   ❌ Failed: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"   📋 Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   📋 Raw error: {response.text}")
                
    except Exception as e:
        print(f"   ❌ Exception during upload: {e}")
    
    # Test 3: Test with different content types
    print("\n3. Testing with different approaches")
    try:
        test_image = create_test_image()
        
        # Try with explicit content-type
        files = {
            'file': ('test_image2.png', test_image, 'image/png')
        }
        
        # Don't set Content-Type header, let requests handle it
        response = requests.post(
            f"{API_BASE}/assets/upload", 
            files=files,
            data={'name': 'Test Image 2', 'category': 'media'}
        )
        
        print(f"   📊 Alternative approach status: {response.status_code}")
        if response.status_code != 200:
            print(f"   📋 Alternative error: {response.text}")
        else:
            print(f"   ✅ Alternative success!")
            
    except Exception as e:
        print(f"   ❌ Alternative approach error: {e}")

if __name__ == "__main__":
    test_upload_endpoint()
