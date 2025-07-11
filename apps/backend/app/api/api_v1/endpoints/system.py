"""
System monitoring and analytics endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.utils.cache_manager import cache_manager
from app.utils.rate_limiter import rate_limiter, performance_monitor
from app.utils.quality_validator import (
    video_quality_validator,
    performance_tester,
    system_health_checker
)
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=dict)
async def get_system_health():
    """Get comprehensive system health status"""
    try:
        health_status = await system_health_checker.run_health_check()
        
        return {
            "success": True,
            "message": "System health check completed",
            "data": health_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/performance", response_model=dict)
async def get_performance_stats():
    """Get system performance statistics"""
    try:
        performance_stats = performance_monitor.get_performance_stats()
        
        return {
            "success": True,
            "message": "Performance statistics retrieved successfully",
            "data": performance_stats
        }
    except Exception as e:
        logger.error(f"Failed to get performance stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance stats: {str(e)}"
        )


@router.get("/cache/stats", response_model=dict)
async def get_cache_stats():
    """Get cache system statistics"""
    try:
        cache_stats = await cache_manager.get_cache_stats()
        
        return {
            "success": True,
            "message": "Cache statistics retrieved successfully",
            "data": cache_stats
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        )


@router.post("/cache/cleanup", response_model=dict)
async def cleanup_cache():
    """Clean up expired cache entries"""
    try:
        cleanup_stats = await cache_manager.cleanup_expired_cache()
        
        return {
            "success": True,
            "message": "Cache cleanup completed successfully",
            "data": cleanup_stats
        }
    except Exception as e:
        logger.error(f"Cache cleanup failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cache cleanup failed: {str(e)}"
        )


@router.post("/performance/test", response_model=dict)
async def run_performance_test(
    test_type: str = Query("quick_test", description="Test type: quick_test, standard_test, stress_test")
):
    """Run system performance test"""
    try:
        if test_type not in ["quick_test", "standard_test", "stress_test"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid test type. Must be one of: quick_test, standard_test, stress_test"
            )
        
        test_result = await performance_tester.run_performance_test(test_type)
        
        return {
            "success": True,
            "message": f"Performance test '{test_type}' completed",
            "data": test_result
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Performance test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Performance test failed: {str(e)}"
        )


@router.get("/performance/summary", response_model=dict)
async def get_performance_test_summary():
    """Get summary of all performance tests"""
    try:
        summary = performance_tester.get_performance_summary()
        
        return {
            "success": True,
            "message": "Performance test summary retrieved successfully",
            "data": summary
        }
    except Exception as e:
        logger.error(f"Failed to get performance summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance summary: {str(e)}"
        )


@router.post("/validate/video-config", response_model=dict)
async def validate_video_configuration(config: dict):
    """Validate video configuration for quality and compliance"""
    try:
        validation_result = await video_quality_validator.validate_video_config(config)
        
        return {
            "success": True,
            "message": "Video configuration validation completed",
            "data": validation_result
        }
    except Exception as e:
        logger.error(f"Video config validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video config validation failed: {str(e)}"
        )


@router.get("/analytics/overview", response_model=dict)
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    """Get comprehensive system analytics overview"""
    try:
        # Combine various system metrics
        health_status = await system_health_checker.run_health_check()
        performance_stats = performance_monitor.get_performance_stats()
        cache_stats = await cache_manager.get_cache_stats()
        performance_summary = performance_tester.get_performance_summary()
        
        analytics_overview = {
            "system_health": {
                "status": health_status["overall_status"],
                "last_check": health_status["timestamp"],
                "components": len(health_status["checks"]),
                "healthy_components": sum(1 for check in health_status["checks"].values() if check.get("healthy", False))
            },
            "performance": {
                "total_requests": performance_stats.get("total_requests", 0),
                "total_errors": performance_stats.get("total_errors", 0),
                "uptime_hours": round(performance_stats.get("uptime_seconds", 0) / 3600, 2),
                "cache_hit_rate": performance_stats.get("cache_stats", {}).get("cache_hit_rate", 0)
            },
            "cache": {
                "total_size_mb": cache_stats.get("total_cache_size_mb", 0),
                "memory_cache_entries": cache_stats.get("memory_cache_size", 0),
                "file_cache_entries": (
                    cache_stats.get("video_cache_files", 0) +
                    cache_stats.get("template_cache_files", 0) +
                    cache_stats.get("api_cache_files", 0)
                )
            },
            "quality_tests": {
                "total_tests": performance_summary.get("total_tests", 0),
                "success_rate": performance_summary.get("success_rate", 0),
                "average_score": performance_summary.get("average_performance_score", 0)
            }
        }
        
        return {
            "success": True,
            "message": "Analytics overview retrieved successfully",
            "data": analytics_overview
        }
    except Exception as e:
        logger.error(f"Failed to get analytics overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics overview: {str(e)}"
        )


@router.get("/metrics/detailed", response_model=dict)
async def get_detailed_metrics():
    """Get detailed system metrics for monitoring dashboards"""
    try:
        # Collect detailed metrics from all systems
        health_status = await system_health_checker.run_health_check()
        performance_stats = performance_monitor.get_performance_stats()
        cache_stats = await cache_manager.get_cache_stats()
        
        detailed_metrics = {
            "timestamp": health_status["timestamp"],
            "system_health": health_status,
            "performance_metrics": performance_stats,
            "cache_metrics": cache_stats,
            "resource_usage": {
                "memory_cache_utilization": cache_stats.get("memory_cache_size", 0),
                "disk_cache_utilization": cache_stats.get("total_cache_size_mb", 0),
                "active_requests": len(performance_stats.get("endpoints", {}))
            },
            "quality_metrics": {
                "validation_enabled": True,
                "rate_limiting_active": True,
                "caching_enabled": True
            }
        }
        
        return {
            "success": True,
            "message": "Detailed metrics retrieved successfully",
            "data": detailed_metrics
        }
    except Exception as e:
        logger.error(f"Failed to get detailed metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get detailed metrics: {str(e)}"
        )


@router.post("/optimize/system", response_model=dict)
async def optimize_system():
    """Run system optimization procedures"""
    try:
        optimization_results = {
            "cache_cleanup": await cache_manager.cleanup_expired_cache(),
            "optimization_timestamp": cache_manager.cache_ttl,
            "recommendations": []
        }
        
        # Add optimization recommendations based on current state
        cache_stats = await cache_manager.get_cache_stats()
        performance_stats = performance_monitor.get_performance_stats()
        
        # Cache size recommendations
        if cache_stats.get("total_cache_size_mb", 0) > 500:  # 500MB threshold
            optimization_results["recommendations"].append({
                "type": "cache_size",
                "message": "Cache size is large. Consider reducing cache TTL or running cleanup more frequently.",
                "priority": "medium"
            })
        
        # Performance recommendations
        total_errors = performance_stats.get("total_errors", 0)
        total_requests = performance_stats.get("total_requests", 1)
        error_rate = (total_errors / total_requests) * 100
        
        if error_rate > 5:  # 5% error rate threshold
            optimization_results["recommendations"].append({
                "type": "error_rate",
                "message": f"High error rate detected: {error_rate:.2f}%. Review error logs and system health.",
                "priority": "high"
            })
        
        # Cache hit rate recommendations
        cache_hit_rate = performance_stats.get("cache_stats", {}).get("cache_hit_rate", 0)
        if cache_hit_rate < 70:  # 70% threshold
            optimization_results["recommendations"].append({
                "type": "cache_efficiency",
                "message": f"Low cache hit rate: {cache_hit_rate:.2f}%. Consider adjusting cache strategies.",
                "priority": "medium"
            })
        
        return {
            "success": True,
            "message": "System optimization completed",
            "data": optimization_results
        }
    except Exception as e:
        logger.error(f"System optimization failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System optimization failed: {str(e)}"
        )


@router.get("/status", response_model=dict)
async def get_system_status():
    """Get quick system status check"""
    try:
        # Quick status check without full health check
        performance_stats = performance_monitor.get_performance_stats()
        cache_stats = await cache_manager.get_cache_stats()
        
        # Determine overall status
        total_requests = performance_stats.get("total_requests", 0)
        total_errors = performance_stats.get("total_errors", 0)
        error_rate = (total_errors / max(total_requests, 1)) * 100
        
        if error_rate > 10:
            overall_status = "critical"
        elif error_rate > 5:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        status_info = {
            "status": overall_status,
            "uptime_hours": round(performance_stats.get("uptime_seconds", 0) / 3600, 2),
            "total_requests": total_requests,
            "error_rate": round(error_rate, 2),
            "cache_size_mb": cache_stats.get("total_cache_size_mb", 0),
            "last_updated": cache_stats.get("timestamp", "unknown")
        }
        
        return {
            "success": True,
            "message": "System status retrieved successfully",
            "data": status_info
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status: {str(e)}"
        )
