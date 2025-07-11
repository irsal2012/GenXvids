// User Types
export interface User {
  id: number;
  email: string;
  username: string;
  firstName?: string;
  lastName?: string;
  avatar?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CreateUserRequest {
  email: string;
  username: string;
  password: string;
  firstName?: string;
  lastName?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
}

// Video Types
export interface Video {
  id: number;
  title: string;
  description?: string;
  filePath?: string;
  thumbnailPath?: string;
  duration?: number;
  fileSize?: number;
  resolution?: string;
  format?: string;
  status: VideoStatus;
  metadata?: Record<string, any>;
  userId: number;
  createdAt: string;
  updatedAt: string;
}

export enum VideoStatus {
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  QUEUED = 'queued'
}

export interface CreateVideoRequest {
  title: string;
  description?: string;
  templateId?: number;
  generationType: VideoGenerationType;
  config: VideoGenerationConfig;
}

export enum VideoGenerationType {
  TEXT_TO_VIDEO = 'text_to_video',
  TEMPLATE_BASED = 'template_based',
  SLIDESHOW = 'slideshow',
  SOCIAL_MEDIA = 'social_media',
  AI_AVATAR = 'ai_avatar'
}

export interface VideoGenerationConfig {
  textPrompt?: string;
  images?: string[];
  audioFile?: string;
  voiceSettings?: VoiceSettings;
  style?: VideoStyle;
  duration?: number;
  aspectRatio?: AspectRatio;
  quality?: VideoQuality;
}

export interface VoiceSettings {
  voice: string;
  speed: number;
  pitch: number;
  volume: number;
}

export enum VideoStyle {
  CINEMATIC = 'cinematic',
  ANIMATED = 'animated',
  REALISTIC = 'realistic',
  CARTOON = 'cartoon',
  MINIMALIST = 'minimalist'
}

export enum AspectRatio {
  LANDSCAPE = '16:9',
  PORTRAIT = '9:16',
  SQUARE = '1:1',
  WIDESCREEN = '21:9'
}

export enum VideoQuality {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  ULTRA = 'ultra'
}

// Template Types
export interface Template {
  id: number;
  name: string;
  description?: string;
  category: TemplateCategory;
  thumbnailUrl: string;
  previewUrl?: string;
  config: TemplateConfig;
  tags: string[];
  isPremium: boolean;
  createdAt: string;
  updatedAt: string;
}

export enum TemplateCategory {
  BUSINESS = 'business',
  SOCIAL_MEDIA = 'social_media',
  EDUCATION = 'education',
  ENTERTAINMENT = 'entertainment',
  MARKETING = 'marketing',
  PERSONAL = 'personal'
}

export interface TemplateConfig {
  duration: number;
  aspectRatio: AspectRatio;
  scenes: Scene[];
  defaultStyle: VideoStyle;
  customizableElements: string[];
}

export interface Scene {
  id: string;
  type: SceneType;
  duration: number;
  elements: SceneElement[];
  transitions?: Transition[];
}

export enum SceneType {
  INTRO = 'intro',
  MAIN = 'main',
  OUTRO = 'outro',
  TRANSITION = 'transition'
}

export interface SceneElement {
  id: string;
  type: ElementType;
  position: Position;
  size: Size;
  properties: Record<string, any>;
  animations?: Animation[];
}

export enum ElementType {
  TEXT = 'text',
  IMAGE = 'image',
  VIDEO = 'video',
  AUDIO = 'audio',
  SHAPE = 'shape',
  EFFECT = 'effect'
}

export interface Position {
  x: number;
  y: number;
  z?: number;
}

export interface Size {
  width: number;
  height: number;
}

export interface Animation {
  type: AnimationType;
  duration: number;
  delay?: number;
  easing?: string;
  properties: Record<string, any>;
}

export enum AnimationType {
  FADE_IN = 'fade_in',
  FADE_OUT = 'fade_out',
  SLIDE_IN = 'slide_in',
  SLIDE_OUT = 'slide_out',
  ZOOM_IN = 'zoom_in',
  ZOOM_OUT = 'zoom_out',
  ROTATE = 'rotate',
  SCALE = 'scale'
}

export interface Transition {
  type: TransitionType;
  duration: number;
  properties?: Record<string, any>;
}

export enum TransitionType {
  CUT = 'cut',
  FADE = 'fade',
  DISSOLVE = 'dissolve',
  WIPE = 'wipe',
  SLIDE = 'slide'
}

// Project Types
export interface Project {
  id: number;
  name: string;
  description?: string;
  status: ProjectStatus;
  config: ProjectConfig;
  userId: number;
  createdAt: string;
  updatedAt: string;
}

export enum ProjectStatus {
  DRAFT = 'draft',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  ARCHIVED = 'archived'
}

export interface ProjectConfig {
  scenes: Scene[];
  globalSettings: GlobalSettings;
  assets: Asset[];
}

export interface GlobalSettings {
  aspectRatio: AspectRatio;
  quality: VideoQuality;
  duration: number;
  backgroundColor?: string;
  audioSettings?: AudioSettings;
}

export interface AudioSettings {
  masterVolume: number;
  fadeIn?: number;
  fadeOut?: number;
  backgroundMusic?: string;
}

export interface Asset {
  id: string;
  type: AssetType;
  name: string;
  url: string;
  metadata?: Record<string, any>;
}

export enum AssetType {
  IMAGE = 'image',
  VIDEO = 'video',
  AUDIO = 'audio',
  FONT = 'font'
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

// WebSocket Types
export interface WebSocketMessage {
  type: WebSocketMessageType;
  payload: any;
  timestamp: string;
}

export enum WebSocketMessageType {
  VIDEO_PROGRESS = 'video_progress',
  VIDEO_COMPLETED = 'video_completed',
  VIDEO_FAILED = 'video_failed',
  NOTIFICATION = 'notification'
}

export interface VideoProgressPayload {
  videoId: number;
  progress: number;
  stage: string;
  estimatedTimeRemaining?: number;
}
