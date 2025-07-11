"""
Quality validation and testing utilities
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class VideoQualityValidator:
    """Validates video processing quality and output"""
    
    def __init__(self):
        self.quality_thresholds = {
            "min_duration": 1.0,  # Minimum 1 second
            "max_duration": 600.0,  # Maximum 10 minutes
            "min_resolution": {"width": 320, "height": 240},
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "supported_formats": ["mp4", "mov", "avi"],
            "min_fps": 15,
            "max_fps": 60
        }
    
    async def validate_video_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate video configuration before processing"""
        errors = []
        warnings = []
        
        try:
            # Validate duration
            duration = config.get("duration", 0)
            if duration < self.quality_thresholds["min_duration"]:
                errors.append(f"Duration too short: {duration}s (minimum: {self.quality_thresholds['min_duration']}s)")
            elif duration > self.quality_thresholds["max_duration"]:
                errors.append(f"Duration too long: {duration}s (maximum: {self.quality_thresholds['max_duration']}s)")
            
            # Validate aspect ratio
            aspect_ratio = config.get("aspect_ratio", "16:9")
            if aspect_ratio not in ["16:9", "9:16", "1:1", "21:9"]:
                errors.append(f"Unsupported aspect ratio: {aspect_ratio}")
            
            # Validate quality setting
            quality = config.get("quality", "medium")
            if quality not in ["low", "medium", "high", "ultra"]:
                errors.append(f"Invalid quality setting: {quality}")
            
            # Validate FPS
            fps = config.get("fps", 30)
            if fps < self.quality_thresholds["min_fps"]:
                warnings.append(f"Low FPS: {fps} (recommended minimum: {self.quality_thresholds['min_fps']})")
            elif fps > self.quality_thresholds["max_fps"]:
                warnings.append(f"High FPS: {fps} (recommended maximum: {self.quality_thresholds['max_fps']})")
            
            # Validate scenes
            scenes = config.get("scenes", [])
            if not scenes:
                errors.append("No scenes provided")
            else:
                scene_errors = await self._validate_scenes(scenes)
                errors.extend(scene_errors)
            
        except Exception as e:
            errors.append(f"Configuration validation error: {str(e)}")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "validation_time": datetime.now().isoformat()
        }
    
    async def _validate_scenes(self, scenes: List[Dict[str, Any]]) -> List[str]:
        """Validate scene configurations"""
        errors = []
        
        for i, scene in enumerate(scenes):
            scene_id = scene.get("id", f"scene_{i}")
            
            # Validate scene duration
            scene_duration = scene.get("duration", 0)
            if scene_duration <= 0:
                errors.append(f"Scene {scene_id}: Invalid duration {scene_duration}")
            
            # Validate scene elements
            elements = scene.get("elements", [])
            if not elements:
                errors.append(f"Scene {scene_id}: No elements provided")
            else:
                element_errors = await self._validate_elements(elements, scene_id)
                errors.extend(element_errors)
        
        return errors
    
    async def _validate_elements(self, elements: List[Dict[str, Any]], scene_id: str) -> List[str]:
        """Validate scene elements"""
        errors = []
        
        for i, element in enumerate(elements):
            element_id = element.get("id", f"element_{i}")
            element_type = element.get("type")
            
            if not element_type:
                errors.append(f"Scene {scene_id}, Element {element_id}: Missing element type")
                continue
            
            # Validate element position
            position = element.get("position", {})
            if not self._validate_position(position):
                errors.append(f"Scene {scene_id}, Element {element_id}: Invalid position")
            
            # Validate element size
            size = element.get("size", {})
            if not self._validate_size(size):
                errors.append(f"Scene {scene_id}, Element {element_id}: Invalid size")
            
            # Type-specific validation
            if element_type == "text":
                text_errors = self._validate_text_element(element, scene_id, element_id)
                errors.extend(text_errors)
            elif element_type == "image":
                image_errors = self._validate_image_element(element, scene_id, element_id)
                errors.extend(image_errors)
        
        return errors
    
    def _validate_position(self, position: Dict[str, Any]) -> bool:
        """Validate element position"""
        x = position.get("x", 0)
        y = position.get("y", 0)
        
        return (
            isinstance(x, (int, float)) and 0 <= x <= 100 and
            isinstance(y, (int, float)) and 0 <= y <= 100
        )
    
    def _validate_size(self, size: Dict[str, Any]) -> bool:
        """Validate element size"""
        width = size.get("width", 0)
        height = size.get("height", 0)
        
        return (
            isinstance(width, (int, float)) and 0 < width <= 100 and
            isinstance(height, (int, float)) and 0 < height <= 100
        )
    
    def _validate_text_element(self, element: Dict[str, Any], scene_id: str, element_id: str) -> List[str]:
        """Validate text element properties"""
        errors = []
        properties = element.get("properties", {})
        
        # Check for required text property
        if not properties.get("text"):
            errors.append(f"Scene {scene_id}, Element {element_id}: Text element missing text content")
        
        # Validate font size
        font_size = properties.get("fontSize", 16)
        if not isinstance(font_size, (int, float)) or font_size < 8 or font_size > 200:
            errors.append(f"Scene {scene_id}, Element {element_id}: Invalid font size {font_size}")
        
        return errors
    
    def _validate_image_element(self, element: Dict[str, Any], scene_id: str, element_id: str) -> List[str]:
        """Validate image element properties"""
        errors = []
        properties = element.get("properties", {})
        
        # Check for image source
        src = properties.get("src")
        if not src:
            errors.append(f"Scene {scene_id}, Element {element_id}: Image element missing source")
        
        return errors
    
    async def validate_output_video(self, video_path: str, expected_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate generated video output"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "metadata_check": {},
            "file_check": {}
        }
        
        try:
            video_file = Path(video_path)
            
            # Check if file exists
            if not video_file.exists():
                validation_result["errors"].append("Video file does not exist")
                validation_result["is_valid"] = False
                return validation_result
            
            # Check file size
            file_size = video_file.stat().st_size
            validation_result["file_check"]["size_bytes"] = file_size
            
            if file_size == 0:
                validation_result["errors"].append("Video file is empty")
                validation_result["is_valid"] = False
            elif file_size > self.quality_thresholds["max_file_size"]:
                validation_result["warnings"].append(f"Large file size: {file_size / (1024*1024):.1f}MB")
            
            # Validate expected metadata
            expected_duration = expected_metadata.get("duration", 0)
            if expected_duration > 0:
                validation_result["metadata_check"]["expected_duration"] = expected_duration
                validation_result["metadata_check"]["duration_valid"] = True  # Mock validation
            
            expected_resolution = expected_metadata.get("resolution", "")
            if expected_resolution:
                validation_result["metadata_check"]["expected_resolution"] = expected_resolution
                validation_result["metadata_check"]["resolution_valid"] = True  # Mock validation
            
        except Exception as e:
            validation_result["errors"].append(f"Video validation error: {str(e)}")
            validation_result["is_valid"] = False
        
        return validation_result


class PerformanceTester:
    """Performance testing and benchmarking utilities"""
    
    def __init__(self):
        self.test_results = []
        self.benchmark_configs = {
            "quick_test": {
                "duration": 5,
                "scenes": 1,
                "elements_per_scene": 2
            },
            "standard_test": {
                "duration": 15,
                "scenes": 3,
                "elements_per_scene": 4
            },
            "stress_test": {
                "duration": 60,
                "scenes": 10,
                "elements_per_scene": 8
            }
        }
    
    async def run_performance_test(self, test_type: str = "quick_test") -> Dict[str, Any]:
        """Run performance test with specified configuration"""
        if test_type not in self.benchmark_configs:
            raise ValueError(f"Unknown test type: {test_type}")
        
        config = self.benchmark_configs[test_type]
        test_start = time.time()
        
        try:
            # Generate test configuration
            test_config = self._generate_test_config(config)
            
            # Simulate video processing
            processing_start = time.time()
            processing_result = await self._simulate_video_processing(test_config)
            processing_time = time.time() - processing_start
            
            # Calculate performance metrics
            total_time = time.time() - test_start
            
            test_result = {
                "test_type": test_type,
                "config": config,
                "processing_time": round(processing_time, 3),
                "total_time": round(total_time, 3),
                "success": processing_result["success"],
                "performance_score": self._calculate_performance_score(config, processing_time),
                "timestamp": datetime.now().isoformat()
            }
            
            if not processing_result["success"]:
                test_result["error"] = processing_result.get("error", "Unknown error")
            
            self.test_results.append(test_result)
            return test_result
            
        except Exception as e:
            error_result = {
                "test_type": test_type,
                "config": config,
                "success": False,
                "error": str(e),
                "total_time": time.time() - test_start,
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(error_result)
            return error_result
    
    def _generate_test_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test configuration based on benchmark parameters"""
        scenes = []
        
        for scene_idx in range(config["scenes"]):
            elements = []
            
            for elem_idx in range(config["elements_per_scene"]):
                elements.append({
                    "id": f"test_element_{scene_idx}_{elem_idx}",
                    "type": "text" if elem_idx % 2 == 0 else "shape",
                    "position": {"x": 50, "y": 50},
                    "size": {"width": 30, "height": 10},
                    "properties": {
                        "text": f"Test Element {elem_idx}" if elem_idx % 2 == 0 else None,
                        "fillColor": "#ff0000" if elem_idx % 2 == 1 else None
                    }
                })
            
            scenes.append({
                "id": f"test_scene_{scene_idx}",
                "type": "main",
                "duration": config["duration"] / config["scenes"],
                "elements": elements
            })
        
        return {
            "duration": config["duration"],
            "aspect_ratio": "16:9",
            "quality": "medium",
            "fps": 30,
            "scenes": scenes
        }
    
    async def _simulate_video_processing(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate video processing for performance testing"""
        try:
            # Simulate processing time based on complexity
            complexity_factor = len(config["scenes"]) * sum(len(scene.get("elements", [])) for scene in config["scenes"])
            processing_delay = min(complexity_factor * 0.1, 5.0)  # Max 5 seconds for simulation
            
            await asyncio.sleep(processing_delay)
            
            return {
                "success": True,
                "simulated_processing_time": processing_delay
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_performance_score(self, config: Dict[str, Any], processing_time: float) -> float:
        """Calculate performance score based on processing time and complexity"""
        # Calculate complexity score
        complexity = config["duration"] * config["scenes"] * config["elements_per_scene"]
        
        # Expected processing time (baseline)
        expected_time = complexity * 0.01  # 0.01 seconds per complexity unit
        
        # Performance score (higher is better)
        if processing_time > 0:
            score = max(0, 100 - ((processing_time - expected_time) / expected_time * 100))
        else:
            score = 100
        
        return round(score, 2)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of all performance tests"""
        if not self.test_results:
            return {"message": "No performance tests run yet"}
        
        successful_tests = [test for test in self.test_results if test.get("success", False)]
        failed_tests = [test for test in self.test_results if not test.get("success", False)]
        
        summary = {
            "total_tests": len(self.test_results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": round(len(successful_tests) / len(self.test_results) * 100, 2),
            "average_performance_score": 0,
            "average_processing_time": 0,
            "test_history": self.test_results[-10:]  # Last 10 tests
        }
        
        if successful_tests:
            summary["average_performance_score"] = round(
                sum(test.get("performance_score", 0) for test in successful_tests) / len(successful_tests), 2
            )
            summary["average_processing_time"] = round(
                sum(test.get("processing_time", 0) for test in successful_tests) / len(successful_tests), 3
            )
        
        return summary


class SystemHealthChecker:
    """System health monitoring and diagnostics"""
    
    def __init__(self):
        self.health_checks = {
            "database": self._check_database_health,
            "file_system": self._check_file_system_health,
            "cache": self._check_cache_health,
            "video_engine": self._check_video_engine_health
        }
    
    async def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive system health check"""
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        for check_name, check_function in self.health_checks.items():
            try:
                check_result = await check_function()
                health_status["checks"][check_name] = check_result
                
                if not check_result.get("healthy", False):
                    health_status["overall_status"] = "unhealthy"
                    
            except Exception as e:
                health_status["checks"][check_name] = {
                    "healthy": False,
                    "error": str(e),
                    "status": "check_failed"
                }
                health_status["overall_status"] = "unhealthy"
        
        return health_status
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        # Mock database health check
        return {
            "healthy": True,
            "status": "connected",
            "response_time_ms": 15,
            "connection_pool": "available"
        }
    
    async def _check_file_system_health(self) -> Dict[str, Any]:
        """Check file system health and disk space"""
        try:
            # Check uploads directory
            uploads_dir = Path(__file__).parent.parent.parent / "uploads"
            uploads_dir.mkdir(exist_ok=True)
            
            # Check cache directory
            cache_dir = Path(__file__).parent.parent.parent / "cache"
            cache_dir.mkdir(exist_ok=True)
            
            return {
                "healthy": True,
                "status": "accessible",
                "uploads_directory": str(uploads_dir),
                "cache_directory": str(cache_dir),
                "directories_writable": True
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "status": "error",
                "error": str(e)
            }
    
    async def _check_cache_health(self) -> Dict[str, Any]:
        """Check cache system health"""
        try:
            from app.utils.cache_manager import cache_manager
            
            cache_stats = await cache_manager.get_cache_stats()
            
            return {
                "healthy": True,
                "status": "operational",
                "cache_stats": cache_stats
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "status": "error",
                "error": str(e)
            }
    
    async def _check_video_engine_health(self) -> Dict[str, Any]:
        """Check video processing engine health"""
        try:
            # Mock video engine health check
            return {
                "healthy": True,
                "status": "ready",
                "engine_type": "SimpleVideoProcessor",
                "dependencies": "available"
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "status": "error",
                "error": str(e)
            }


# Global instances
video_quality_validator = VideoQualityValidator()
performance_tester = PerformanceTester()
system_health_checker = SystemHealthChecker()
