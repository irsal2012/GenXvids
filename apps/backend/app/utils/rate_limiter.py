"""
Rate limiting and API optimization middleware
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable
from collections import defaultdict, deque
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting implementation with sliding window"""
    
    def __init__(self):
        # Store request timestamps for each client
        self._requests: Dict[str, deque] = defaultdict(lambda: deque())
        
        # Rate limit configurations
        self.rate_limits = {
            "default": {"requests": 100, "window": 3600},  # 100 requests per hour
            "auth": {"requests": 10, "window": 300},       # 10 auth requests per 5 minutes
            "upload": {"requests": 20, "window": 3600},    # 20 uploads per hour
            "video_generation": {"requests": 5, "window": 3600},  # 5 video generations per hour
            "api_heavy": {"requests": 50, "window": 3600}, # 50 heavy API calls per hour
        }
        
        # Cleanup interval (seconds)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Try to get user ID from request state (if authenticated)
        if hasattr(request.state, 'user_id'):
            return f"user_{request.state.user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Check for forwarded IP headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            client_ip = real_ip
        
        return f"ip_{client_ip}"
    
    def _get_rate_limit_key(self, request: Request) -> str:
        """Determine rate limit category based on request"""
        path = request.url.path
        
        if "/auth/" in path:
            return "auth"
        elif "/upload" in path or request.method == "POST" and "/assets/" in path:
            return "upload"
        elif "/videos/generate" in path:
            return "video_generation"
        elif any(heavy_path in path for heavy_path in ["/videos/", "/templates/customize", "/templates/preview"]):
            return "api_heavy"
        else:
            return "default"
    
    def _cleanup_old_requests(self):
        """Clean up old request records"""
        current_time = time.time()
        
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        # Clean up requests older than the longest window
        max_window = max(config["window"] for config in self.rate_limits.values())
        cutoff_time = current_time - max_window
        
        for client_id, requests in self._requests.items():
            # Remove old requests
            while requests and requests[0] < cutoff_time:
                requests.popleft()
        
        # Remove empty client records
        empty_clients = [client_id for client_id, requests in self._requests.items() if not requests]
        for client_id in empty_clients:
            del self._requests[client_id]
        
        self.last_cleanup = current_time
        logger.info(f"Rate limiter cleanup completed. Active clients: {len(self._requests)}")
    
    async def check_rate_limit(self, request: Request) -> Optional[JSONResponse]:
        """Check if request should be rate limited"""
        try:
            # Cleanup old requests periodically
            self._cleanup_old_requests()
            
            client_id = self._get_client_id(request)
            rate_limit_key = self._get_rate_limit_key(request)
            rate_config = self.rate_limits[rate_limit_key]
            
            current_time = time.time()
            window_start = current_time - rate_config["window"]
            
            # Get client's request history
            client_requests = self._requests[client_id]
            
            # Remove requests outside the current window
            while client_requests and client_requests[0] < window_start:
                client_requests.popleft()
            
            # Check if rate limit exceeded
            if len(client_requests) >= rate_config["requests"]:
                # Calculate time until next request is allowed
                oldest_request = client_requests[0]
                retry_after = int(oldest_request + rate_config["window"] - current_time)
                
                logger.warning(f"Rate limit exceeded for {client_id} on {rate_limit_key}")
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "success": False,
                        "message": "Rate limit exceeded",
                        "error": f"Too many requests. Limit: {rate_config['requests']} per {rate_config['window']} seconds",
                        "retry_after": retry_after
                    },
                    headers={"Retry-After": str(retry_after)}
                )
            
            # Record this request
            client_requests.append(current_time)
            
            return None  # Request allowed
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return None  # Allow request on error
    
    def get_rate_limit_info(self, request: Request) -> Dict[str, Any]:
        """Get current rate limit status for client"""
        try:
            client_id = self._get_client_id(request)
            rate_limit_key = self._get_rate_limit_key(request)
            rate_config = self.rate_limits[rate_limit_key]
            
            current_time = time.time()
            window_start = current_time - rate_config["window"]
            
            client_requests = self._requests[client_id]
            
            # Count requests in current window
            recent_requests = sum(1 for req_time in client_requests if req_time >= window_start)
            
            return {
                "limit": rate_config["requests"],
                "remaining": max(0, rate_config["requests"] - recent_requests),
                "reset_time": int(current_time + rate_config["window"]),
                "window_seconds": rate_config["window"]
            }
            
        except Exception as e:
            logger.error(f"Error getting rate limit info: {e}")
            return {
                "limit": 0,
                "remaining": 0,
                "reset_time": 0,
                "window_seconds": 0
            }


class APIOptimizer:
    """API optimization utilities"""
    
    def __init__(self):
        self.response_compression_threshold = 1024  # Compress responses larger than 1KB
        self.pagination_defaults = {
            "default_limit": 20,
            "max_limit": 100,
            "default_skip": 0
        }
    
    def optimize_pagination(self, skip: int, limit: int) -> Dict[str, int]:
        """Optimize pagination parameters"""
        # Ensure skip is not negative
        skip = max(0, skip)
        
        # Ensure limit is within bounds
        limit = max(1, min(limit, self.pagination_defaults["max_limit"]))
        
        return {"skip": skip, "limit": limit}
    
    def should_compress_response(self, content_length: int) -> bool:
        """Determine if response should be compressed"""
        return content_length > self.response_compression_threshold
    
    def optimize_query_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize query parameters for better performance"""
        optimized = {}
        
        for key, value in params.items():
            if value is not None:
                # Convert string booleans
                if isinstance(value, str) and value.lower() in ["true", "false"]:
                    optimized[key] = value.lower() == "true"
                # Convert string numbers
                elif isinstance(value, str) and value.isdigit():
                    optimized[key] = int(value)
                else:
                    optimized[key] = value
        
        return optimized
    
    def add_performance_headers(self, response: Response, processing_time: float):
        """Add performance-related headers to response"""
        response.headers["X-Processing-Time"] = f"{processing_time:.3f}s"
        response.headers["X-Timestamp"] = str(int(time.time()))
        
        # Add cache control headers for static content
        if hasattr(response, 'media_type') and response.media_type in ['image/jpeg', 'image/png', 'video/mp4']:
            response.headers["Cache-Control"] = "public, max-age=3600"  # 1 hour cache


class PerformanceMonitor:
    """Monitor API performance and collect metrics"""
    
    def __init__(self):
        self.metrics = {
            "request_count": defaultdict(int),
            "response_times": defaultdict(list),
            "error_count": defaultdict(int),
            "cache_hits": defaultdict(int),
            "cache_misses": defaultdict(int)
        }
        self.start_time = time.time()
    
    def record_request(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Record request metrics"""
        key = f"{method}:{endpoint}"
        
        self.metrics["request_count"][key] += 1
        self.metrics["response_times"][key].append(response_time)
        
        if status_code >= 400:
            self.metrics["error_count"][key] += 1
        
        # Keep only last 1000 response times per endpoint
        if len(self.metrics["response_times"][key]) > 1000:
            self.metrics["response_times"][key] = self.metrics["response_times"][key][-1000:]
    
    def record_cache_hit(self, cache_type: str):
        """Record cache hit"""
        self.metrics["cache_hits"][cache_type] += 1
    
    def record_cache_miss(self, cache_type: str):
        """Record cache miss"""
        self.metrics["cache_misses"][cache_type] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {
            "uptime_seconds": time.time() - self.start_time,
            "total_requests": sum(self.metrics["request_count"].values()),
            "total_errors": sum(self.metrics["error_count"].values()),
            "endpoints": {}
        }
        
        # Calculate per-endpoint stats
        for endpoint, count in self.metrics["request_count"].items():
            response_times = self.metrics["response_times"][endpoint]
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
            else:
                avg_response_time = max_response_time = min_response_time = 0
            
            stats["endpoints"][endpoint] = {
                "request_count": count,
                "error_count": self.metrics["error_count"][endpoint],
                "avg_response_time": round(avg_response_time, 3),
                "max_response_time": round(max_response_time, 3),
                "min_response_time": round(min_response_time, 3),
                "error_rate": round(self.metrics["error_count"][endpoint] / count * 100, 2) if count > 0 else 0
            }
        
        # Cache statistics
        total_cache_requests = sum(self.metrics["cache_hits"].values()) + sum(self.metrics["cache_misses"].values())
        if total_cache_requests > 0:
            cache_hit_rate = sum(self.metrics["cache_hits"].values()) / total_cache_requests * 100
        else:
            cache_hit_rate = 0
        
        stats["cache_stats"] = {
            "total_cache_requests": total_cache_requests,
            "cache_hits": sum(self.metrics["cache_hits"].values()),
            "cache_misses": sum(self.metrics["cache_misses"].values()),
            "cache_hit_rate": round(cache_hit_rate, 2)
        }
        
        return stats


# Global instances
rate_limiter = RateLimiter()
api_optimizer = APIOptimizer()
performance_monitor = PerformanceMonitor()
