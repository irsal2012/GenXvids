"""
Cache manager for video processing and API response caching
"""

import json
import hashlib
import asyncio
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching for video processing and API responses"""
    
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent.parent / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Cache directories
        self.video_cache_dir = self.cache_dir / "videos"
        self.template_cache_dir = self.cache_dir / "templates"
        self.api_cache_dir = self.cache_dir / "api"
        
        # Create cache directories
        self.video_cache_dir.mkdir(exist_ok=True)
        self.template_cache_dir.mkdir(exist_ok=True)
        self.api_cache_dir.mkdir(exist_ok=True)
        
        # In-memory cache for frequently accessed data
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        # Cache TTL settings (in seconds)
        self.cache_ttl = {
            "video_processing": 3600,  # 1 hour
            "template_data": 1800,     # 30 minutes
            "api_response": 300,       # 5 minutes
            "asset_metadata": 7200,    # 2 hours
            "user_data": 900          # 15 minutes
        }
    
    def _generate_cache_key(self, data: Union[str, Dict[str, Any]]) -> str:
        """Generate a unique cache key from data"""
        if isinstance(data, str):
            content = data
        else:
            content = json.dumps(data, sort_keys=True)
        
        return hashlib.md5(content.encode()).hexdigest()
    
    async def get_video_cache(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached video processing result"""
        try:
            cache_key = self._generate_cache_key(config)
            cache_file = self.video_cache_dir / f"{cache_key}.json"
            
            if not cache_file.exists():
                return None
            
            # Check if cache is still valid
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age > timedelta(seconds=self.cache_ttl["video_processing"]):
                # Cache expired, remove it
                cache_file.unlink()
                return None
            
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            logger.info(f"Video cache hit for key: {cache_key}")
            return cached_data
            
        except Exception as e:
            logger.warning(f"Failed to get video cache: {e}")
            return None
    
    async def set_video_cache(self, config: Dict[str, Any], result: Dict[str, Any]) -> bool:
        """Cache video processing result"""
        try:
            cache_key = self._generate_cache_key(config)
            cache_file = self.video_cache_dir / f"{cache_key}.json"
            
            cache_data = {
                "config": config,
                "result": result,
                "cached_at": datetime.now().isoformat(),
                "ttl": self.cache_ttl["video_processing"]
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Video result cached with key: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache video result: {e}")
            return False
    
    async def get_template_cache(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Get cached template data"""
        try:
            cache_key = f"template_{template_id}"
            
            # Check memory cache first
            if cache_key in self._memory_cache:
                cached_item = self._memory_cache[cache_key]
                cache_age = datetime.now() - datetime.fromisoformat(cached_item["cached_at"])
                
                if cache_age < timedelta(seconds=self.cache_ttl["template_data"]):
                    logger.info(f"Template memory cache hit for ID: {template_id}")
                    return cached_item["data"]
                else:
                    # Remove expired cache
                    del self._memory_cache[cache_key]
            
            # Check file cache
            cache_file = self.template_cache_dir / f"{cache_key}.json"
            
            if not cache_file.exists():
                return None
            
            cache_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if cache_age > timedelta(seconds=self.cache_ttl["template_data"]):
                cache_file.unlink()
                return None
            
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Store in memory cache for faster access
            self._memory_cache[cache_key] = {
                "data": cached_data,
                "cached_at": datetime.now().isoformat()
            }
            
            logger.info(f"Template file cache hit for ID: {template_id}")
            return cached_data
            
        except Exception as e:
            logger.warning(f"Failed to get template cache: {e}")
            return None
    
    async def set_template_cache(self, template_id: int, data: Dict[str, Any]) -> bool:
        """Cache template data"""
        try:
            cache_key = f"template_{template_id}"
            
            # Store in memory cache
            self._memory_cache[cache_key] = {
                "data": data,
                "cached_at": datetime.now().isoformat()
            }
            
            # Store in file cache
            cache_file = self.template_cache_dir / f"{cache_key}.json"
            cache_data = {
                "template_id": template_id,
                "data": data,
                "cached_at": datetime.now().isoformat(),
                "ttl": self.cache_ttl["template_data"]
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            logger.info(f"Template cached with ID: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache template: {e}")
            return False
    
    async def get_api_cache(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get cached API response"""
        try:
            cache_key = self._generate_cache_key(f"{endpoint}_{params}")
            
            # Check memory cache first
            if cache_key in self._memory_cache:
                cached_item = self._memory_cache[cache_key]
                cache_age = datetime.now() - datetime.fromisoformat(cached_item["cached_at"])
                
                if cache_age < timedelta(seconds=self.cache_ttl["api_response"]):
                    logger.info(f"API memory cache hit for: {endpoint}")
                    return cached_item["data"]
                else:
                    del self._memory_cache[cache_key]
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to get API cache: {e}")
            return None
    
    async def set_api_cache(self, endpoint: str, params: Dict[str, Any], response: Dict[str, Any]) -> bool:
        """Cache API response"""
        try:
            cache_key = self._generate_cache_key(f"{endpoint}_{params}")
            
            # Store in memory cache only for API responses (they're typically small and frequently accessed)
            self._memory_cache[cache_key] = {
                "data": response,
                "cached_at": datetime.now().isoformat()
            }
            
            logger.info(f"API response cached for: {endpoint}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache API response: {e}")
            return False
    
    async def invalidate_template_cache(self, template_id: int) -> bool:
        """Invalidate template cache when template is updated"""
        try:
            cache_key = f"template_{template_id}"
            
            # Remove from memory cache
            if cache_key in self._memory_cache:
                del self._memory_cache[cache_key]
            
            # Remove from file cache
            cache_file = self.template_cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                cache_file.unlink()
            
            logger.info(f"Template cache invalidated for ID: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to invalidate template cache: {e}")
            return False
    
    async def cleanup_expired_cache(self) -> Dict[str, int]:
        """Clean up expired cache files"""
        cleanup_stats = {
            "video_cache_cleaned": 0,
            "template_cache_cleaned": 0,
            "api_cache_cleaned": 0,
            "memory_cache_cleaned": 0
        }
        
        try:
            current_time = datetime.now()
            
            # Clean up video cache
            for cache_file in self.video_cache_dir.glob("*.json"):
                cache_age = current_time - datetime.fromtimestamp(cache_file.stat().st_mtime)
                if cache_age > timedelta(seconds=self.cache_ttl["video_processing"]):
                    cache_file.unlink()
                    cleanup_stats["video_cache_cleaned"] += 1
            
            # Clean up template cache
            for cache_file in self.template_cache_dir.glob("*.json"):
                cache_age = current_time - datetime.fromtimestamp(cache_file.stat().st_mtime)
                if cache_age > timedelta(seconds=self.cache_ttl["template_data"]):
                    cache_file.unlink()
                    cleanup_stats["template_cache_cleaned"] += 1
            
            # Clean up memory cache
            expired_keys = []
            for cache_key, cached_item in self._memory_cache.items():
                cache_age = current_time - datetime.fromisoformat(cached_item["cached_at"])
                # Use the shortest TTL for memory cache cleanup
                if cache_age > timedelta(seconds=min(self.cache_ttl.values())):
                    expired_keys.append(cache_key)
            
            for key in expired_keys:
                del self._memory_cache[key]
                cleanup_stats["memory_cache_cleaned"] += 1
            
            logger.info(f"Cache cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
            return cleanup_stats
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            stats = {
                "memory_cache_size": len(self._memory_cache),
                "video_cache_files": len(list(self.video_cache_dir.glob("*.json"))),
                "template_cache_files": len(list(self.template_cache_dir.glob("*.json"))),
                "api_cache_files": len(list(self.api_cache_dir.glob("*.json"))),
                "cache_directories": {
                    "video_cache": str(self.video_cache_dir),
                    "template_cache": str(self.template_cache_dir),
                    "api_cache": str(self.api_cache_dir)
                },
                "cache_ttl_settings": self.cache_ttl
            }
            
            # Calculate total cache size
            total_size = 0
            for cache_dir in [self.video_cache_dir, self.template_cache_dir, self.api_cache_dir]:
                for cache_file in cache_dir.glob("*.json"):
                    total_size += cache_file.stat().st_size
            
            stats["total_cache_size_bytes"] = total_size
            stats["total_cache_size_mb"] = round(total_size / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}


# Global cache manager instance
cache_manager = CacheManager()
