// Export the simple video processor for now
export { SimpleVideoProcessor, ProcessingOptions, VideoProcessingResult } from './core/SimpleVideoProcessor';

// Export the full video processor (when dependencies are available)
export { VideoProcessor } from './core/VideoProcessor';

// Re-export shared types for convenience
export {
  VideoGenerationConfig,
  VideoQuality,
  AspectRatio,
  Scene,
  SceneElement,
  ElementType,
  VideoGenerationType,
  VideoStyle
} from '@genxvids/shared';
