#!/usr/bin/env python3
"""
Test script for video generation functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend app to the path
sys.path.append(str(Path(__file__).parent / "apps" / "backend"))

from app.utils.simple_video_generator import SimpleVideoGenerator


async def test_video_generation():
    """Test the video generation system"""
    print("🎬 Testing GenXvids Video Generation System")
    print("=" * 50)
    
    # Create test scenes using the example text from our guide
    test_scenes = [
        {
            "id": "intro_scene",
            "type": "intro",
            "duration": 5.0,
            "elements": [
                {
                    "id": "title_text",
                    "type": "text",
                    "position": {"x": 50, "y": 40},
                    "size": {"width": 80, "height": 20},
                    "properties": {
                        "text": "Welcome to GenXvids!",
                        "fontSize": 48,
                        "fontFamily": "Arial",
                        "color": "#ffffff",
                        "textAlign": "center"
                    }
                },
                {
                    "id": "subtitle_text",
                    "type": "text",
                    "position": {"x": 50, "y": 60},
                    "size": {"width": 80, "height": 15},
                    "properties": {
                        "text": "Where innovation meets excellence",
                        "fontSize": 24,
                        "fontFamily": "Arial",
                        "color": "#cccccc",
                        "textAlign": "center"
                    }
                }
            ]
        },
        {
            "id": "content_scene",
            "type": "main",
            "duration": 8.0,
            "elements": [
                {
                    "id": "main_text",
                    "type": "text",
                    "position": {"x": 50, "y": 30},
                    "size": {"width": 80, "height": 40},
                    "properties": {
                        "text": "Transform your ideas into stunning videos with our AI-powered platform. Create professional content in minutes, not hours.",
                        "fontSize": 32,
                        "fontFamily": "Arial",
                        "color": "#ffffff",
                        "textAlign": "center"
                    }
                },
                {
                    "id": "highlight_box",
                    "type": "shape",
                    "position": {"x": 20, "y": 75},
                    "size": {"width": 60, "height": 15},
                    "properties": {
                        "shapeType": "rectangle",
                        "fillColor": "#ff6b6b"
                    }
                },
                {
                    "id": "cta_text",
                    "type": "text",
                    "position": {"x": 50, "y": 80},
                    "size": {"width": 50, "height": 10},
                    "properties": {
                        "text": "Get Started Today!",
                        "fontSize": 28,
                        "fontFamily": "Arial",
                        "color": "#ffffff",
                        "textAlign": "center"
                    }
                }
            ]
        }
    ]
    
    # Test configuration
    test_config = {
        "aspect_ratio": "16:9",
        "fps": 30,
        "quality": "medium",
        "generation_type": "template_based"
    }
    
    # Output path
    output_path = Path(__file__).parent / "test_video_output.mp4"
    
    print(f"📝 Test Configuration:")
    print(f"   - Scenes: {len(test_scenes)}")
    print(f"   - Total Duration: {sum(scene['duration'] for scene in test_scenes)} seconds")
    print(f"   - Aspect Ratio: {test_config['aspect_ratio']}")
    print(f"   - Output: {output_path}")
    print()
    
    # Initialize video generator
    generator = SimpleVideoGenerator()
    
    print("🚀 Starting video generation...")
    try:
        result = await generator.generate_video(
            scenes=test_scenes,
            config=test_config,
            output_path=str(output_path)
        )
        
        print("\n✅ Video Generation Results:")
        print(f"   - Success: {result['success']}")
        
        if result['success']:
            print(f"   - Output Path: {result['output_path']}")
            
            if 'metadata' in result:
                metadata = result['metadata']
                print(f"   - Duration: {metadata.get('duration', 'N/A')} seconds")
                print(f"   - Resolution: {metadata.get('resolution', 'N/A')}")
                print(f"   - Format: {metadata.get('format', 'N/A')}")
                print(f"   - Frame Count: {metadata.get('frameCount', 'N/A')}")
                print(f"   - File Size: {metadata.get('fileSize', 0)} bytes")
            
            if 'html_preview' in result:
                print(f"   - HTML Preview: {result['html_preview']}")
                print(f"   - Message: {result.get('message', '')}")
            
            # Check if output file exists
            if os.path.exists(result['output_path']):
                print(f"   - File Created: ✅ {result['output_path']}")
                
                # If it's an HTML file, we can open it
                if result['output_path'].endswith('.html'):
                    print(f"\n🌐 You can view the video preview by opening:")
                    print(f"   {result['output_path']}")
                    print(f"   Or run: open {result['output_path']}")
            else:
                print(f"   - File Created: ❌ File not found")
        else:
            print(f"   - Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Video generation failed with exception:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎬 Test completed!")


if __name__ == "__main__":
    asyncio.run(test_video_generation())
