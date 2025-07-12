"""
Simple video generator that creates actual video files
"""

import os
import json
import tempfile
import subprocess
from typing import Dict, Any, List
from pathlib import Path
import logging
from PIL import Image, ImageDraw, ImageFont
import io
import base64

logger = logging.getLogger(__name__)


class SimpleVideoGenerator:
    """Simple video generator using PIL and FFmpeg"""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.gettempdir()) / "genxvids_temp"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def generate_video(
        self, 
        scenes: List[Dict[str, Any]], 
        config: Dict[str, Any],
        output_path: str
    ) -> Dict[str, Any]:
        """Generate video from scenes"""
        try:
            logger.info(f"Generating video with {len(scenes)} scenes")
            
            # Get video configuration
            aspect_ratio = config.get("aspect_ratio", "16:9")
            fps = config.get("fps", 30)
            quality = config.get("quality", "medium")
            
            # Get resolution
            resolution = self._get_resolution(aspect_ratio)
            width, height = resolution["width"], resolution["height"]
            
            # Create output directory
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate frames for all scenes
            all_frames = []
            total_duration = 0
            
            for scene_idx, scene in enumerate(scenes):
                scene_duration = scene.get("duration", 5)
                total_duration += scene_duration
                
                # Generate frames for this scene
                scene_frames = await self._generate_scene_frames(
                    scene, width, height, fps, scene_duration
                )
                all_frames.extend(scene_frames)
            
            if not all_frames:
                return {
                    "success": False,
                    "error": "No frames generated"
                }
            
            # Try to create video with FFmpeg
            try:
                video_path = await self._create_video_with_ffmpeg(
                    all_frames, output_path, fps, width, height
                )
                
                # Get file size
                file_size = os.path.getsize(video_path) if os.path.exists(video_path) else 0
                
                return {
                    "success": True,
                    "output_path": video_path,
                    "metadata": {
                        "duration": total_duration,
                        "resolution": f"{width}x{height}",
                        "fileSize": file_size,
                        "format": "mp4",
                        "fps": fps,
                        "quality": quality,
                        "aspectRatio": aspect_ratio,
                        "frameCount": len(all_frames)
                    }
                }
                
            except Exception as ffmpeg_error:
                logger.warning(f"FFmpeg failed: {ffmpeg_error}, creating HTML preview instead")
                
                # Fallback to HTML preview
                html_path = await self._create_html_preview(
                    scenes, config, output_path, all_frames
                )
                
                return {
                    "success": True,
                    "output_path": html_path,
                    "html_preview": html_path,
                    "metadata": {
                        "duration": total_duration,
                        "resolution": f"{width}x{height}",
                        "fileSize": os.path.getsize(html_path) if os.path.exists(html_path) else 0,
                        "format": "html",
                        "fps": fps,
                        "quality": quality,
                        "aspectRatio": aspect_ratio,
                        "frameCount": len(all_frames)
                    },
                    "message": "Video generated as HTML preview. Install FFmpeg for MP4 generation."
                }
                
        except Exception as e:
            logger.error(f"Video generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            # Clean up temporary files
            await self._cleanup_temp_files()
    
    async def _generate_scene_frames(
        self, 
        scene: Dict[str, Any], 
        width: int, 
        height: int, 
        fps: int, 
        duration: float
    ) -> List[str]:
        """Generate frames for a single scene"""
        frames = []
        frame_count = int(duration * fps)
        
        for frame_idx in range(frame_count):
            # Create frame image
            frame_image = Image.new('RGB', (width, height), color='black')
            draw = ImageDraw.Draw(frame_image)
            
            # Render elements
            for element in scene.get("elements", []):
                await self._render_element(draw, element, width, height, frame_image)
            
            # Save frame
            frame_path = self.temp_dir / f"frame_{len(frames):06d}.png"
            frame_image.save(frame_path, "PNG")
            frames.append(str(frame_path))
        
        return frames
    
    async def _render_element(
        self, 
        draw: ImageDraw.Draw, 
        element: Dict[str, Any], 
        canvas_width: int, 
        canvas_height: int,
        image: Image.Image
    ):
        """Render a single element on the frame"""
        element_type = element.get("type", "text")
        position = element.get("position", {"x": 50, "y": 50})
        size = element.get("size", {"width": 50, "height": 20})
        properties = element.get("properties", {})
        
        # Calculate actual position and size
        x = int((position["x"] / 100) * canvas_width)
        y = int((position["y"] / 100) * canvas_height)
        w = int((size["width"] / 100) * canvas_width)
        h = int((size["height"] / 100) * canvas_height)
        
        if element_type == "text":
            await self._render_text(draw, properties, x, y, w, h)
        elif element_type == "shape":
            await self._render_shape(draw, properties, x, y, w, h)
        elif element_type == "image":
            await self._render_image_element(image, properties, x, y, w, h)
    
    async def _render_text(
        self, 
        draw: ImageDraw.Draw, 
        properties: Dict[str, Any], 
        x: int, 
        y: int, 
        w: int, 
        h: int
    ):
        """Render text element"""
        text = properties.get("text", "Sample Text")
        font_size = properties.get("fontSize", 24)
        color = properties.get("color", "#ffffff")
        font_family = properties.get("fontFamily", "Arial")
        
        # Convert hex color to RGB
        if color.startswith("#"):
            color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        else:
            color = (255, 255, 255)  # Default white
        
        # Try to load font
        try:
            # Try to use a system font
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Simple text wrapping
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= w:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw lines
        line_height = font_size + 5
        for i, line in enumerate(lines):
            line_y = y + (i * line_height)
            if line_y + line_height <= y + h:  # Don't draw outside bounds
                draw.text((x, line_y), line, fill=color, font=font)
    
    async def _render_shape(
        self, 
        draw: ImageDraw.Draw, 
        properties: Dict[str, Any], 
        x: int, 
        y: int, 
        w: int, 
        h: int
    ):
        """Render shape element"""
        shape_type = properties.get("shapeType", "rectangle")
        fill_color = properties.get("fillColor", "#ffffff")
        
        # Convert hex color to RGB
        if fill_color.startswith("#"):
            fill_color = tuple(int(fill_color[i:i+2], 16) for i in (1, 3, 5))
        else:
            fill_color = (255, 255, 255)
        
        if shape_type == "rectangle":
            draw.rectangle([x, y, x + w, y + h], fill=fill_color)
        elif shape_type == "circle":
            draw.ellipse([x, y, x + w, y + h], fill=fill_color)
    
    async def _render_image_element(
        self, 
        canvas: Image.Image, 
        properties: Dict[str, Any], 
        x: int, 
        y: int, 
        w: int, 
        h: int
    ):
        """Render image element"""
        src = properties.get("src", "")
        if not src:
            return
        
        try:
            # For now, just draw a placeholder rectangle
            draw = ImageDraw.Draw(canvas)
            draw.rectangle([x, y, x + w, y + h], fill=(128, 128, 128))
            draw.text((x + 10, y + 10), "Image", fill=(255, 255, 255))
        except Exception as e:
            logger.warning(f"Failed to render image: {e}")
    
    async def _create_video_with_ffmpeg(
        self, 
        frame_paths: List[str], 
        output_path: str, 
        fps: int, 
        width: int, 
        height: int
    ) -> str:
        """Create video using FFmpeg"""
        
        # Create a text file listing all frames
        frame_list_path = self.temp_dir / "frame_list.txt"
        with open(frame_list_path, 'w') as f:
            for frame_path in frame_paths:
                f.write(f"file '{frame_path}'\n")
                f.write(f"duration {1/fps}\n")
        
        # Try different FFmpeg commands
        ffmpeg_commands = [
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(frame_list_path), 
             "-vf", f"fps={fps}", "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path],
            ["ffmpeg", "-y", "-r", str(fps), "-i", str(self.temp_dir / "frame_%06d.png"), 
             "-c:v", "libx264", "-pix_fmt", "yuv420p", output_path]
        ]
        
        for cmd in ffmpeg_commands:
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=60
                )
                
                if result.returncode == 0 and os.path.exists(output_path):
                    logger.info("Video created successfully with FFmpeg")
                    return output_path
                else:
                    logger.warning(f"FFmpeg command failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.warning("FFmpeg command timed out")
            except FileNotFoundError:
                logger.warning("FFmpeg not found")
            except Exception as e:
                logger.warning(f"FFmpeg error: {e}")
        
        raise Exception("All FFmpeg attempts failed")
    
    async def _create_html_preview(
        self, 
        scenes: List[Dict[str, Any]], 
        config: Dict[str, Any], 
        output_path: str,
        frame_paths: List[str]
    ) -> str:
        """Create HTML preview with frame images"""
        html_path = output_path.replace('.mp4', '.html')
        
        # Convert first few frames to base64 for preview
        frame_data = []
        max_frames = min(10, len(frame_paths))  # Limit to 10 frames for HTML size
        
        for i in range(0, len(frame_paths), max(1, len(frame_paths) // max_frames)):
            if len(frame_data) >= max_frames:
                break
                
            try:
                with open(frame_paths[i], 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
                    frame_data.append(f"data:image/png;base64,{img_data}")
            except Exception as e:
                logger.warning(f"Failed to encode frame {i}: {e}")
        
        aspect_ratio = config.get("aspect_ratio", "16:9")
        resolution = self._get_resolution(aspect_ratio)
        total_duration = sum(scene.get("duration", 0) for scene in scenes)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GenXvids - Video Preview</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #fff;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .video-container {{
            width: {min(resolution['width'], 800)}px;
            height: {min(resolution['height'], 450)}px;
            max-width: 100%;
            margin: 0 auto 30px;
            background: #000;
            position: relative;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        .frame {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            opacity: 0;
            transition: opacity 0.5s ease-in-out;
        }}
        .frame.active {{
            opacity: 1;
        }}
        .controls {{
            text-align: center;
            margin: 30px 0;
        }}
        .btn {{
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            border: none;
            padding: 12px 24px;
            margin: 0 10px;
            cursor: pointer;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }}
        .btn:active {{
            transform: translateY(0);
        }}
        .info {{
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            backdrop-filter: blur(10px);
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .info-item {{
            text-align: center;
        }}
        .info-label {{
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 5px;
        }}
        .info-value {{
            font-size: 1.2em;
            font-weight: bold;
        }}
        .progress-bar {{
            width: 100%;
            height: 6px;
            background: rgba(255,255,255,0.2);
            border-radius: 3px;
            margin: 20px 0;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b, #ee5a24);
            width: 0%;
            transition: width 0.3s ease;
        }}
        .scene-info {{
            text-align: center;
            margin: 15px 0;
            font-size: 1.1em;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            opacity: 0.7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 GenXvids</h1>
            <p>Video Preview - Generated Successfully!</p>
        </div>
        
        <div class="info">
            <h3>📊 Video Information</h3>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Duration</div>
                    <div class="info-value">{total_duration}s</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Resolution</div>
                    <div class="info-value">{resolution['width']}×{resolution['height']}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Scenes</div>
                    <div class="info-value">{len(scenes)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Frames</div>
                    <div class="info-value">{len(frame_paths)}</div>
                </div>
            </div>
        </div>
        
        <div class="video-container" id="videoContainer">
"""
        
        # Add frame images
        for i, frame_data_url in enumerate(frame_data):
            active_class = " active" if i == 0 else ""
            html_content += f'            <img class="frame{active_class}" src="{frame_data_url}" alt="Frame {i+1}">\n'
        
        html_content += f"""        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progressFill"></div>
        </div>
        
        <div class="scene-info" id="sceneInfo">Frame 1 of {len(frame_data)}</div>
        
        <div class="controls">
            <button class="btn" onclick="previousFrame()">⏮️ Previous</button>
            <button class="btn" onclick="playPause()" id="playBtn">▶️ Play</button>
            <button class="btn" onclick="nextFrame()">⏭️ Next</button>
        </div>
        
        <div class="info">
            <h3>💡 About This Preview</h3>
            <p>This is an interactive HTML preview of your generated video. The actual video processing creates individual frames that would normally be compiled into an MP4 file.</p>
            <p><strong>To generate actual MP4 videos:</strong> Install FFmpeg on your system for full video processing capabilities.</p>
        </div>
        
        <div class="footer">
            <p>Generated by GenXvids Platform | {len(frame_paths)} frames processed</p>
        </div>
    </div>

    <script>
        let currentFrame = 0;
        let isPlaying = false;
        let playInterval;
        const totalFrames = {len(frame_data)};
        const frameDuration = {total_duration / max(len(frame_data), 1) * 1000};  // ms per frame
        
        function showFrame(index) {{
            const frames = document.querySelectorAll('.frame');
            frames.forEach(frame => frame.classList.remove('active'));
            
            if (frames[index]) {{
                frames[index].classList.add('active');
            }}
            
            document.getElementById('sceneInfo').textContent = `Frame ${{index + 1}} of ${{totalFrames}}`;
            
            // Update progress bar
            const progress = ((index + 1) / totalFrames) * 100;
            document.getElementById('progressFill').style.width = progress + '%';
        }}
        
        function nextFrame() {{
            currentFrame = (currentFrame + 1) % totalFrames;
            showFrame(currentFrame);
        }}
        
        function previousFrame() {{
            currentFrame = (currentFrame - 1 + totalFrames) % totalFrames;
            showFrame(currentFrame);
        }}
        
        function playPause() {{
            const playBtn = document.getElementById('playBtn');
            
            if (isPlaying) {{
                clearInterval(playInterval);
                playBtn.textContent = '▶️ Play';
                isPlaying = false;
            }} else {{
                playInterval = setInterval(() => {{
                    nextFrame();
                }}, frameDuration);
                playBtn.textContent = '⏸️ Pause';
                isPlaying = true;
            }}
        }}
        
        // Auto-play on load
        setTimeout(() => {{
            playPause();
        }}, 1000);
    </script>
</body>
</html>"""
        
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        return html_path
    
    async def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                self.temp_dir.mkdir(exist_ok=True)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files: {e}")
    
    def _get_resolution(self, aspect_ratio: str) -> Dict[str, int]:
        """Get resolution based on aspect ratio"""
        resolutions = {
            "16:9": {"width": 1280, "height": 720},  # Reduced for faster processing
            "9:16": {"width": 720, "height": 1280},
            "1:1": {"width": 720, "height": 720},
            "21:9": {"width": 1280, "height": 540}
        }
        return resolutions.get(aspect_ratio, resolutions["16:9"])
