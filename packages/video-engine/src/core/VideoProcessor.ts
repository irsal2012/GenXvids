import path from 'path';
import fs from 'fs/promises';
import { 
  VideoGenerationConfig, 
  VideoQuality, 
  AspectRatio, 
  Scene, 
  SceneElement, 
  ElementType 
} from '@genxvids/shared';

// Dynamic imports for optional dependencies
let ffmpeg: any;
let ffmpegStatic: any;
let createCanvas: any;
let loadImage: any;
let sharp: any;

// Initialize optional dependencies
try {
  ffmpeg = require('fluent-ffmpeg');
  ffmpegStatic = require('ffmpeg-static');
  const canvas = require('canvas');
  createCanvas = canvas.createCanvas;
  loadImage = canvas.loadImage;
  sharp = require('sharp');
  
  // Set FFmpeg path
  if (ffmpegStatic) {
    ffmpeg.setFfmpegPath(ffmpegStatic);
  }
} catch (error) {
  console.warn('Optional video processing dependencies not installed:', error);
}

// Set FFmpeg path
if (ffmpegStatic) {
  ffmpeg.setFfmpegPath(ffmpegStatic);
}

export interface ProcessingOptions {
  outputPath: string;
  tempDir: string;
  quality: VideoQuality;
  aspectRatio: AspectRatio;
  fps: number;
}

export class VideoProcessor {
  private tempDir: string;
  private outputPath: string;
  private quality: VideoQuality;
  private aspectRatio: AspectRatio;
  private fps: number;

  constructor(options: ProcessingOptions) {
    this.tempDir = options.tempDir;
    this.outputPath = options.outputPath;
    this.quality = options.quality;
    this.aspectRatio = options.aspectRatio;
    this.fps = options.fps;
  }

  /**
   * Process scenes into a complete video
   */
  async processScenes(scenes: Scene[]): Promise<string> {
    try {
      // Create temp directory if it doesn't exist
      await fs.mkdir(this.tempDir, { recursive: true });

      // Process each scene
      const sceneVideos: string[] = [];
      for (let i = 0; i < scenes.length; i++) {
        const sceneVideo = await this.processScene(scenes[i], i);
        sceneVideos.push(sceneVideo);
      }

      // Concatenate all scene videos
      const finalVideo = await this.concatenateVideos(sceneVideos);
      
      // Clean up temporary files
      await this.cleanup(sceneVideos);

      return finalVideo;
    } catch (error) {
      console.error('Error processing scenes:', error);
      throw new Error(`Video processing failed: ${error}`);
    }
  }

  /**
   * Process a single scene
   */
  private async processScene(scene: Scene, index: number): Promise<string> {
    const { width, height } = this.getResolution();
    const canvas = createCanvas(width, height);
    const ctx = canvas.getContext('2d');

    // Set background
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, width, height);

    // Process each element in the scene
    for (const element of scene.elements) {
      await this.renderElement(ctx, element, width, height);
    }

    // Generate frames for the scene duration
    const frameCount = Math.ceil(scene.duration * this.fps);
    const frameDir = path.join(this.tempDir, `scene_${index}_frames`);
    await fs.mkdir(frameDir, { recursive: true });

    // For now, we'll create static frames
    // In a more advanced implementation, we'd handle animations
    for (let frame = 0; frame < frameCount; frame++) {
      const frameBuffer = canvas.toBuffer('image/png');
      const framePath = path.join(frameDir, `frame_${frame.toString().padStart(6, '0')}.png`);
      await fs.writeFile(framePath, frameBuffer);
    }

    // Convert frames to video
    const sceneVideoPath = path.join(this.tempDir, `scene_${index}.mp4`);
    await this.framesToVideo(frameDir, sceneVideoPath, this.fps);

    return sceneVideoPath;
  }

  /**
   * Render a scene element on the canvas
   */
  private async renderElement(
    ctx: CanvasRenderingContext2D, 
    element: SceneElement, 
    canvasWidth: number, 
    canvasHeight: number
  ): Promise<void> {
    const { position, size, properties } = element;
    
    // Calculate actual position and size based on canvas dimensions
    const x = (position.x / 100) * canvasWidth;
    const y = (position.y / 100) * canvasHeight;
    const width = (size.width / 100) * canvasWidth;
    const height = (size.height / 100) * canvasHeight;

    switch (element.type) {
      case ElementType.TEXT:
        await this.renderText(ctx, element, x, y, width, height);
        break;
      case ElementType.IMAGE:
        await this.renderImage(ctx, element, x, y, width, height);
        break;
      case ElementType.SHAPE:
        await this.renderShape(ctx, element, x, y, width, height);
        break;
      default:
        console.warn(`Unsupported element type: ${element.type}`);
    }
  }

  /**
   * Render text element
   */
  private async renderText(
    ctx: CanvasRenderingContext2D,
    element: SceneElement,
    x: number,
    y: number,
    width: number,
    height: number
  ): Promise<void> {
    const { properties } = element;
    const text = properties.text || '';
    const fontSize = properties.fontSize || 24;
    const fontFamily = properties.fontFamily || 'Arial';
    const color = properties.color || '#ffffff';
    const textAlign = properties.textAlign || 'left';

    ctx.font = `${fontSize}px ${fontFamily}`;
    ctx.fillStyle = color;
    ctx.textAlign = textAlign as CanvasTextAlign;
    ctx.textBaseline = 'top';

    // Simple text wrapping
    const words = text.split(' ');
    const lines: string[] = [];
    let currentLine = '';

    for (const word of words) {
      const testLine = currentLine + (currentLine ? ' ' : '') + word;
      const metrics = ctx.measureText(testLine);
      
      if (metrics.width > width && currentLine) {
        lines.push(currentLine);
        currentLine = word;
      } else {
        currentLine = testLine;
      }
    }
    
    if (currentLine) {
      lines.push(currentLine);
    }

    // Render lines
    const lineHeight = fontSize * 1.2;
    lines.forEach((line, index) => {
      ctx.fillText(line, x, y + (index * lineHeight));
    });
  }

  /**
   * Render image element
   */
  private async renderImage(
    ctx: CanvasRenderingContext2D,
    element: SceneElement,
    x: number,
    y: number,
    width: number,
    height: number
  ): Promise<void> {
    const { properties } = element;
    const imagePath = properties.src;

    if (!imagePath) return;

    try {
      const image = await loadImage(imagePath);
      ctx.drawImage(image, x, y, width, height);
    } catch (error) {
      console.error('Error loading image:', error);
      // Draw placeholder rectangle
      ctx.fillStyle = '#cccccc';
      ctx.fillRect(x, y, width, height);
      ctx.fillStyle = '#666666';
      ctx.font = '16px Arial';
      ctx.fillText('Image not found', x + 10, y + 20);
    }
  }

  /**
   * Render shape element
   */
  private async renderShape(
    ctx: CanvasRenderingContext2D,
    element: SceneElement,
    x: number,
    y: number,
    width: number,
    height: number
  ): Promise<void> {
    const { properties } = element;
    const shapeType = properties.shapeType || 'rectangle';
    const fillColor = properties.fillColor || '#ffffff';
    const strokeColor = properties.strokeColor;
    const strokeWidth = properties.strokeWidth || 0;

    ctx.fillStyle = fillColor;
    if (strokeColor && strokeWidth > 0) {
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = strokeWidth;
    }

    switch (shapeType) {
      case 'rectangle':
        ctx.fillRect(x, y, width, height);
        if (strokeColor && strokeWidth > 0) {
          ctx.strokeRect(x, y, width, height);
        }
        break;
      case 'circle':
        const centerX = x + width / 2;
        const centerY = y + height / 2;
        const radius = Math.min(width, height) / 2;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.fill();
        if (strokeColor && strokeWidth > 0) {
          ctx.stroke();
        }
        break;
    }
  }

  /**
   * Convert frames to video using FFmpeg
   */
  private async framesToVideo(frameDir: string, outputPath: string, fps: number): Promise<void> {
    return new Promise((resolve, reject) => {
      const inputPattern = path.join(frameDir, 'frame_%06d.png');
      
      ffmpeg()
        .input(inputPattern)
        .inputFPS(fps)
        .videoCodec('libx264')
        .outputOptions([
          '-pix_fmt yuv420p',
          '-preset medium',
          '-crf 23'
        ])
        .output(outputPath)
        .on('end', () => resolve())
        .on('error', (err) => reject(err))
        .run();
    });
  }

  /**
   * Concatenate multiple videos
   */
  private async concatenateVideos(videoPaths: string[]): Promise<string> {
    return new Promise((resolve, reject) => {
      const command = ffmpeg();
      
      // Add all input videos
      videoPaths.forEach(videoPath => {
        command.input(videoPath);
      });

      command
        .on('end', () => resolve(this.outputPath))
        .on('error', (err) => reject(err))
        .mergeToFile(this.outputPath, this.tempDir);
    });
  }

  /**
   * Get resolution based on aspect ratio
   */
  private getResolution(): { width: number; height: number } {
    const resolutions = {
      [AspectRatio.LANDSCAPE]: { width: 1920, height: 1080 },
      [AspectRatio.PORTRAIT]: { width: 1080, height: 1920 },
      [AspectRatio.SQUARE]: { width: 1080, height: 1080 },
      [AspectRatio.WIDESCREEN]: { width: 2560, height: 1080 }
    };

    return resolutions[this.aspectRatio] || resolutions[AspectRatio.LANDSCAPE];
  }

  /**
   * Clean up temporary files
   */
  private async cleanup(filePaths: string[]): Promise<void> {
    try {
      for (const filePath of filePaths) {
        await fs.unlink(filePath);
      }
    } catch (error) {
      console.warn('Error cleaning up temporary files:', error);
    }
  }

  /**
   * Generate thumbnail from video
   */
  async generateThumbnail(videoPath: string, thumbnailPath: string, timeOffset: number = 1): Promise<string> {
    return new Promise((resolve, reject) => {
      ffmpeg(videoPath)
        .screenshots({
          timestamps: [timeOffset],
          filename: path.basename(thumbnailPath),
          folder: path.dirname(thumbnailPath),
          size: '320x240'
        })
        .on('end', () => resolve(thumbnailPath))
        .on('error', (err) => reject(err));
    });
  }

  /**
   * Get video metadata
   */
  async getVideoMetadata(videoPath: string): Promise<any> {
    return new Promise((resolve, reject) => {
      ffmpeg.ffprobe(videoPath, (err, metadata) => {
        if (err) {
          reject(err);
        } else {
          resolve(metadata);
        }
      });
    });
  }
}
