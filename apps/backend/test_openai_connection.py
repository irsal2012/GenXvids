#!/usr/bin/env python3
"""
Test script to verify OpenAI connection and configuration
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import settings
from app.services.openai_service import openai_service


async def test_openai_connection():
    """Test the OpenAI connection and basic functionality"""
    
    print("🔍 Testing OpenAI Configuration...")
    print(f"Endpoint: {settings.AZURE_OPENAI_ENDPOINT}")
    print(f"Deployment: {settings.AZURE_OPENAI_DEPLOYMENT}")
    print(f"API Version: {settings.AZURE_OPENAI_API_VERSION}")
    print(f"API Key: {'✅ Set' if settings.AZURE_OPENAI_API_KEY else '❌ Not Set'}")
    print("-" * 50)
    
    # Test health check
    print("🏥 Running health check...")
    health_result = await openai_service.health_check()
    print(f"Health Status: {health_result}")
    print("-" * 50)
    
    if health_result.get("status") == "healthy":
        print("✅ OpenAI service is healthy!")
        
        # Test basic text generation
        print("\n🤖 Testing text generation...")
        test_prompt = "Write a brief hello message for testing purposes."
        
        result = await openai_service.generate_text(
            prompt=test_prompt,
            max_tokens=50
        )
        
        if result:
            print(f"✅ Text generation successful!")
            print(f"Prompt: {test_prompt}")
            print(f"Response: {result}")
        else:
            print("❌ Text generation failed")
        
        print("-" * 50)
        
        # Test video script generation
        print("\n📹 Testing video script generation...")
        script_result = await openai_service.generate_video_script(
            topic="Introduction to AI",
            duration=30,
            style="engaging"
        )
        
        if script_result:
            print(f"✅ Video script generation successful!")
            print(f"Script preview: {script_result[:200]}...")
        else:
            print("❌ Video script generation failed")
            
    else:
        print("❌ OpenAI service is not healthy")
        print("Please check your configuration in .env file")
        
        # Print configuration help
        print("\n📋 Configuration Requirements:")
        print("1. AZURE_OPENAI_API_KEY - Your Azure OpenAI API key")
        print("2. AZURE_OPENAI_ENDPOINT - Your Azure OpenAI endpoint URL")
        print("3. AZURE_OPENAI_DEPLOYMENT - Your model deployment name")
        print("4. AZURE_OPENAI_API_VERSION - API version (currently: 2024-10-21)")


if __name__ == "__main__":
    print("🚀 Starting OpenAI Connection Test")
    print("=" * 50)
    
    try:
        asyncio.run(test_openai_connection())
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed")
