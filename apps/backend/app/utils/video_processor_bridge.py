"""
Bridge between Python backend and video generation engines
"""

import asyncio
import json
import os
from typing import Dict, Any, List
from pathlib import Path
import logging
from .simple_video_generator import SimpleVideoGenerator

logger = logging.getLogger(__name__)


class VideoProcessorBridge:
    """Bridge to communicate with video generation engines"""
    
    def __init__(self):
        self.uploads_dir = Path(__file__).parent.parent.parent / "uploads"
        self.uploads_dir.mkdir(exist_ok=True)
        
        # Create required subdirectories
        (self.uploads_dir / "videos").mkdir(exist_ok=True)
        (self.uploads_dir / "thumbnails").mkdir(exist_ok=True)
        (self.uploads_dir / "temp").mkdir(exist_ok=True)
        
        # Initialize the simple video generator
        self.simple_generator = SimpleVideoGenerator()
    
    async def process_video(
        self, 
        scenes: List[Dict[str, Any]], 
        config: Dict[str, Any],
        output_path: str
    ) -> Dict[str, Any]:
        """Process video using available video engines"""
        try:
            logger.info(f"Starting video processing with {len(scenes)} scenes")
            logger.info(f"Output path: {output_path}")
            logger.info(f"Config: {config}")
            
            # Create output directory
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Use the simple video generator
            result = await self.simple_generator.generate_video(scenes, config, output_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "output_path": None
            }
    
    async def _process_with_typescript_engine(
        self, 
        scenes: List[Dict[str, Any]], 
        config: Dict[str, Any],
        output_path: str
    ) -> Dict[str, Any]:
        """Process video using the TypeScript video engine"""
        
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            video_config = {
                "scenes": scenes,
                "config": {
                    "outputPath": output_path,
                    "tempDir": str(self.uploads_dir / "temp"),
                    "quality": config.get("quality", "medium"),
                    "aspectRatio": config.get("aspect_ratio", "16:9"),
                    "fps": config.get("fps", 30)
                }
            }
            json.dump(video_config, f, indent=2)
            config_path = f.name
        
        try:
            # Check if video engine exists and has dependencies
            if not self.video_engine_path.exists():
                raise Exception("Video engine not found")
            
            # Try to run the TypeScript video processor
            cmd = [
                "node",
                "-e",
                f"""
                const {{ SimpleVideoProcessor }} = require('{self.video_engine_path}/dist/index.js');
                const fs = require('fs');
                const config = JSON.parse(fs.readFileSync('{config_path}', 'utf8'));
                
                async function processVideo() {{
                    try {{
                        const processor = new SimpleVideoProcessor();
                        const result = await processor.processVideo(config.scenes, config.config);
                        console.log(JSON.stringify(result));
                    }} catch (error) {{
                        console.error(JSON.stringify({{ success: false, error: error.message }}));
                        process.exit(1);
                    }}
                }}
                
                processVideo();
                """
            ]
            
            # Run the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.video_engine_path)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                result = json.loads(stdout.decode())
                return result
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise Exception(f"Video engine failed: {error_msg}")
                
        finally:
            # Clean up temp file
            try:
                os.unlink(config_path)
            except:
                pass
    
    async def _process_with_simple_implementation(
        self, 
        scenes: List[Dict[str, Any]], 
        config: Dict[str, Any],
        output_path: str
    ) -> Dict[str, Any]:
        """Simple fallback video generation using HTML5 Canvas simulation"""
        try:
            logger.info("Using simple video implementation")
            
            # Calculate total duration
            total_duration = sum(scene.get("duration", 0) for scene in scenes)
            
            # Create a simple HTML file that represents the video content
            html_content = self._generate_html_video(scenes, config)
            
            # Save as HTML file (for demonstration)
            html_path = output_path.replace('.mp4', '.html')
            with open(html_path, 'w') as f:
                f.write(html_content)
            
            # Create a simple text-based "video" file for now
            video_content = {
                "type": "simple_video",
                "scenes": scenes,
                "config": config,
                "duration": total_duration,
                "html_preview": html_path
            }
            
            with open(output_path, 'w') as f:
                json.dump(video_content, f, indent=2)
            
            return {
                "success": True,
                "output_path": output_path,
                "html_preview": html_path,
                "message": "Video generated using simple implementation. Install FFmpeg and video dependencies for full video generation."
            }
            
        except Exception as e:
            logger.error(f"Simple video implementation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_html_video(self, scenes: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
        """Generate an HTML representation of the video"""
        aspect_ratio = config.get("aspect_ratio", "16:9")
        resolution = self._get_resolution(aspect_ratio)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Preview</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #000;
            color: #fff;
        }}
        .video-container {{
            width: {resolution['width']}px;
            height: {resolution['height']}px;
            max-width: 100%;
            max-height: 80vh;
            margin: 0 auto;
            background: #000;
            position: relative;
            border: 2px solid #333;
        }}
        .scene {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: none;
        }}
        .scene.active {{
            display: block;
        }}
        .element {{
            position: absolute;
        }}
        .text-element {{
            color: #fff;
            font-family: Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .controls {{
            text-align: center;
            margin-top: 20px;
        }}
        button {{
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 5px;
            cursor: pointer;
            border-radius: 5px;
        }}
        button:hover {{
            background: #0056b3;
        }}
        .info {{
            text-align: center;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="info">
        <h2>Video Preview</h2>
        <p>Duration: {sum(scene.get('duration', 0) for scene in scenes)} seconds | Resolution: {resolution['width']}x{resolution['height']}</p>
        <p><em>This is a preview. Install video processing dependencies for actual MP4 generation.</em></p>
    </div>
    
    <div class="video-container" id="videoContainer">
"""
        
        # Generate scenes
        for i, scene in enumerate(scenes):
            html += f'        <div class="scene{"" if i > 0 else " active"}" id="scene{i}">\n'
            
            # Generate elements for this scene
            for element in scene.get('elements', []):
                element_html = self._generate_element_html(element, resolution)
                html += f"            {element_html}\n"
            
            html += "        </div>\n"
        
        html += """    </div>
    
    <div class="controls">
        <button onclick="previousScene()">Previous</button>
        <button onclick="playPause()" id="playBtn">Play</button>
        <button onclick="nextScene()">Next</button>
        <span id="sceneInfo">Scene 1 of """ + str(len(scenes)) + """</span>
    </div>

    <script>
        let currentScene = 0;
        let isPlaying = false;
        let playInterval;
        const scenes = """ + json.dumps(scenes) + """;
        
        function showScene(index) {
            document.querySelectorAll('.scene').forEach(scene => scene.classList.remove('active'));
            document.getElementById(`scene${index}`).classList.add('active');
            document.getElementById('sceneInfo').textContent = `Scene ${index + 1} of ${scenes.length}`;
        }
        
        function nextScene() {
            currentScene = (currentScene + 1) % scenes.length;
            showScene(currentScene);
        }
        
        function previousScene() {
            currentScene = (currentScene - 1 + scenes.length) % scenes.length;
            showScene(currentScene);
        }
        
        function playPause() {
            if (isPlaying) {
                clearInterval(playInterval);
                document.getElementById('playBtn').textContent = 'Play';
                isPlaying = false;
            } else {
                playInterval = setInterval(() => {
                    nextScene();
                }, scenes[currentScene]?.duration * 1000 || 3000);
                document.getElementById('playBtn').textContent = 'Pause';
                isPlaying = true;
            }
        }
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_element_html(self, element: Dict[str, Any], resolution: Dict[str, int]) -> str:
        """Generate HTML for a scene element"""
        position = element.get('position', {'x': 0, 'y': 0})
        size = element.get('size', {'width': 100, 'height': 100})
        properties = element.get('properties', {})
        
        # Calculate actual position and size
        x = (position['x'] / 100) * resolution['width']
        y = (position['y'] / 100) * resolution['height']
        width = (size['width'] / 100) * resolution['width']
        height = (size['height'] / 100) * resolution['height']
        
        if element.get('type') == 'text':
            text = properties.get('text', 'Sample Text')
            font_size = properties.get('fontSize', 24)
            color = properties.get('color', '#ffffff')
            font_family = properties.get('fontFamily', 'Arial')
            
            return f'''<div class="element text-element" style="left: {x}px; top: {y}px; width: {width}px; height: {height}px; font-size: {font_size}px; color: {color}; font-family: {font_family};">{text}</div>'''
        
        elif element.get('type') == 'image':
            src = properties.get('src', '')
            return f'''<div class="element" style="left: {x}px; top: {y}px; width: {width}px; height: {height}px; background: url('{src}') center/cover; border: 1px solid #666;"></div>'''
        
        else:
            return f'''<div class="element" style="left: {x}px; top: {y}px; width: {width}px; height: {height}px; background: #333; border: 1px solid #666;"></div>'''
    
    async def generate_thumbnail(self, video_path: str, thumbnail_path: str) -> Dict[str, Any]:
        """Generate thumbnail from video"""
        try:
            # Create thumbnail directory
            thumbnail_dir = Path(thumbnail_path).parent
            thumbnail_dir.mkdir(parents=True, exist_ok=True)
            
            # Create mock thumbnail
            with open(thumbnail_path, 'w') as f:
                json.dump({
                    "type": "mock_thumbnail",
                    "source_video": video_path,
                    "resolution": "320x240"
                }, f, indent=2)
            
            return {
                "success": True,
                "thumbnail_path": thumbnail_path
            }
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_resolution(self, aspect_ratio: str) -> Dict[str, int]:
        """Get resolution based on aspect ratio"""
        resolutions = {
            "16:9": {"width": 1920, "height": 1080},
            "9:16": {"width": 1080, "height": 1920},
            "1:1": {"width": 1080, "height": 1080},
            "21:9": {"width": 2560, "height": 1080}
        }
        return resolutions.get(aspect_ratio, resolutions["16:9"])
