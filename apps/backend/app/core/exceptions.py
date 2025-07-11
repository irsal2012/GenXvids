"""
Exception handlers and custom exceptions
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger
import traceback


class GenXvidsException(Exception):
    """Base exception for GenXvids application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(GenXvidsException):
    """Validation error exception"""
    def __init__(self, message: str):
        super().__init__(message, 400)


class AuthenticationException(GenXvidsException):
    """Authentication error exception"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)


class AuthorizationException(GenXvidsException):
    """Authorization error exception"""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, 403)


class NotFoundException(GenXvidsException):
    """Resource not found exception"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class VideoProcessingException(GenXvidsException):
    """Video processing error exception"""
    def __init__(self, message: str = "Video processing failed"):
        super().__init__(message, 422)


def setup_exception_handlers(app: FastAPI):
    """Setup exception handlers for the FastAPI app"""
    
    @app.exception_handler(GenXvidsException)
    async def genxvids_exception_handler(request: Request, exc: GenXvidsException):
        logger.error(f"GenXvids Exception: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "message": exc.message,
                    "type": exc.__class__.__name__,
                    "status_code": exc.status_code
                }
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTP Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "message": exc.detail,
                    "type": "HTTPException",
                    "status_code": exc.status_code
                }
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error(f"Starlette HTTP Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "message": exc.detail,
                    "type": "HTTPException",
                    "status_code": exc.status_code
                }
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation Error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "message": "Validation error",
                    "type": "ValidationError",
                    "status_code": 422,
                    "details": exc.errors()
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "message": "Internal server error",
                    "type": "InternalServerError",
                    "status_code": 500
                }
            }
        )
