"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Server Configuration
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "mysql+pymysql://irsal2025:RayDiva20!@35.221.1.172:3306/GenXvidsDB"
    
    # Remote MySQL Database Configuration
    REMOTE_DB_HOST: str = "35.221.1.172"
    REMOTE_DB_PORT: int = 3306
    REMOTE_DB_NAME: str = "GenXvidsDB"
    REMOTE_DB_USER: str = "irsal2025"
    REMOTE_DB_PASSWORD: str = "RayDiva20!"
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    # Authentication & Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production-make-it-very-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS: List[str] = ["*"]
    
    # File Upload Configuration
    UPLOAD_DIR: str = "./uploads"
    TEMP_DIR: str = "./temp"
    MAX_FILE_SIZE: int = 104857600  # 100MB in bytes
    ALLOWED_VIDEO_EXTENSIONS: List[str] = [".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"]
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]
    ALLOWED_AUDIO_EXTENSIONS: List[str] = [".mp3", ".wav", ".aac", ".ogg", ".m4a"]
    
    # FFmpeg Configuration
    FFMPEG_PATH: str = "/usr/local/bin/ffmpeg"
    FFPROBE_PATH: str = "/usr/local/bin/ffprobe"
    
    # Video Processing Configuration
    MAX_VIDEO_DURATION: int = 600  # 10 minutes in seconds
    MAX_VIDEO_RESOLUTION: str = "1920x1080"
    DEFAULT_VIDEO_QUALITY: str = "medium"
    VIDEO_BITRATE: str = "2000k"
    AUDIO_BITRATE: str = "128k"
    
    # Celery Configuration (Background Tasks)
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = None
    AZURE_OPENAI_API_VERSION: str = "2024-10-21"
    
    # OpenAI API Settings
    AZURE_OPENAI_MAX_TOKENS: int = 4000
    AZURE_OPENAI_TEMPERATURE: float = 0.7
    AZURE_OPENAI_TIMEOUT: int = 60
    AZURE_OPENAI_MAX_RETRIES: int = 3
    
    # OpenAI Rate Limiting
    AZURE_OPENAI_REQUESTS_PER_MINUTE: int = 60
    AZURE_OPENAI_TOKENS_PER_MINUTE: int = 150000
    
    # Image Generation Settings
    DALLE_IMAGE_SIZE: str = "1024x1024"
    DALLE_IMAGE_QUALITY: str = "hd"
    DALLE_IMAGE_STYLE: str = "vivid"
    
    # Text-to-Speech Settings
    TTS_RESPONSE_FORMAT: str = "mp3"
    TTS_SPEED: float = 1.0
    
    # Speech-to-Text Settings
    WHISPER_RESPONSE_FORMAT: str = "json"
    WHISPER_LANGUAGE: str = "en"
    
    # AI Content Generation Settings
    AI_SCRIPT_MAX_LENGTH: int = 2000
    AI_SCENE_DESCRIPTION_MAX_LENGTH: int = 500
    AI_ENABLE_CONTENT_FILTERING: bool = True
    
    # Legacy AI Configuration (keep for backward compatibility)
    HUGGINGFACE_TOKEN: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    STABILITY_AI_API_KEY: Optional[str] = None
    MODEL_CACHE_DIR: str = "./models"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "30 days"
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@genxvids.com"
    
    # Cloud Storage (optional)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = None
    
    # Monitoring & Analytics
    SENTRY_DSN: Optional[str] = None
    ANALYTICS_ENABLED: bool = False
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds
    
    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_MAX_CONNECTIONS: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(Path(settings.LOG_FILE).parent, exist_ok=True)
os.makedirs(settings.MODEL_CACHE_DIR, exist_ok=True)
