"""
GenXvids Backend API
A comprehensive video generator platform built with FastAPI
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import os
from pathlib import Path

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.database import create_tables
from app.api.api_v1.api import api_router
from app.core.exceptions import setup_exception_handlers

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting GenXvids Backend API")
    
    # Create upload directories
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.TEMP_DIR, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Create database tables
    await create_tables()
    logger.info("✅ Database tables created/verified")
    
    logger.info(f"🌍 Server running on {settings.HOST}:{settings.PORT}")
    logger.info(f"📚 API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"🔧 Environment: {settings.ENVIRONMENT}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down GenXvids Backend API")

# Create FastAPI application
app = FastAPI(
    title="GenXvids API",
    description="Comprehensive video generator platform with AI-powered features",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Setup exception handlers
setup_exception_handlers(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Static file serving
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

if os.path.exists(settings.TEMP_DIR):
    app.mount("/temp", StaticFiles(directory=settings.TEMP_DIR), name="temp")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "GenXvids Backend API",
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "timestamp": time.time()
        }
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return JSONResponse(
        content={
            "message": "Welcome to GenXvids API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
            "api": "/api/v1"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
