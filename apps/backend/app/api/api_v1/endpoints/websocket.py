"""
WebSocket endpoints for real-time communication
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.utils.websocket_manager import connection_manager, notification_manager
from app.utils.auth import get_current_user_websocket
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/connect")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="Authentication token"),
    room_id: Optional[str] = Query(None, description="Optional room to join")
):
    """Main WebSocket endpoint for real-time communication"""
    user_id = None
    connection_id = None
    
    try:
        # Authenticate user
        user_id = await get_current_user_websocket(token)
        if not user_id:
            await websocket.close(code=4001, reason="Authentication failed")
            return
        
        # Establish connection
        connection_id = await connection_manager.connect(websocket, user_id)
        
        # Join room if specified
        if room_id:
            await connection_manager.join_room(connection_id, room_id)
        
        # Send welcome message
        await connection_manager.send_personal_message({
            "type": "welcome",
            "message": "Connected to GenXvids real-time service",
            "user_id": user_id,
            "connection_id": connection_id,
            "features": [
                "video_processing_updates",
                "template_notifications",
                "asset_notifications",
                "system_alerts",
                "collaboration"
            ]
        }, user_id)
        
        # Listen for messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Update connection activity
                connection_manager.stats["messages_received"] += 1
                
                # Handle different message types
                await handle_websocket_message(connection_id, user_id, message)
                
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, user_id)
            except Exception as e:
                logger.error(f"WebSocket message handling error: {e}")
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Message processing failed"
                }, user_id)
    
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        if websocket.client_state.name != "DISCONNECTED":
            await websocket.close(code=4000, reason="Connection error")
    
    finally:
        # Clean up connection
        if user_id and connection_id:
            connection_manager.disconnect(user_id, websocket)
            logger.info(f"WebSocket connection closed for user {user_id}")


async def handle_websocket_message(connection_id: str, user_id: int, message: Dict[str, Any]):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    
    if message_type == "ping":
        # Respond to ping with pong
        await connection_manager.send_personal_message({
            "type": "pong",
            "timestamp": message.get("timestamp")
        }, user_id)
    
    elif message_type == "join_room":
        # Join a collaboration room
        room_id = message.get("room_id")
        if room_id:
            await connection_manager.join_room(connection_id, room_id)
    
    elif message_type == "leave_room":
        # Leave a collaboration room
        room_id = message.get("room_id")
        if room_id:
            await connection_manager.leave_room(connection_id, room_id)
    
    elif message_type == "room_message":
        # Send message to room
        room_id = message.get("room_id")
        content = message.get("content")
        if room_id and content:
            await connection_manager.send_room_message({
                "type": "room_message",
                "room_id": room_id,
                "user_id": user_id,
                "content": content,
                "timestamp": message.get("timestamp")
            }, room_id)
    
    elif message_type == "subscribe":
        # Subscribe to specific notification types
        notification_types = message.get("notification_types", [])
        await connection_manager.send_personal_message({
            "type": "subscription_updated",
            "subscribed_to": notification_types,
            "message": f"Subscribed to {len(notification_types)} notification types"
        }, user_id)
    
    elif message_type == "get_status":
        # Get current connection status
        stats = connection_manager.get_connection_stats()
        await connection_manager.send_personal_message({
            "type": "status_response",
            "connection_stats": stats,
            "user_id": user_id,
            "connection_id": connection_id
        }, user_id)
    
    else:
        # Unknown message type
        await connection_manager.send_personal_message({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }, user_id)


@router.get("/connections/stats")
async def get_connection_stats():
    """Get WebSocket connection statistics"""
    try:
        stats = connection_manager.get_connection_stats()
        
        return {
            "success": True,
            "message": "Connection statistics retrieved successfully",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get connection stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get connection stats: {str(e)}"
        )


@router.get("/rooms/{room_id}/info")
async def get_room_info(room_id: str):
    """Get information about a specific room"""
    try:
        room_info = connection_manager.get_room_info(room_id)
        
        return {
            "success": True,
            "message": "Room information retrieved successfully",
            "data": room_info
        }
    except Exception as e:
        logger.error(f"Failed to get room info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get room info: {str(e)}"
        )


@router.post("/notifications/send")
async def send_notification(
    notification_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Send a notification to users (admin endpoint)"""
    try:
        notification_type = notification_data.get("type")
        target_users = notification_data.get("target_users")
        message = notification_data.get("message")
        
        if notification_type == "system":
            await notification_manager.send_system_notification(
                message=message,
                level=notification_data.get("level", "info"),
                target_users=target_users
            )
        elif notification_type == "video_processing":
            user_id = notification_data.get("user_id")
            video_id = notification_data.get("video_id")
            status = notification_data.get("status")
            progress = notification_data.get("progress")
            metadata = notification_data.get("metadata")
            
            await notification_manager.send_video_processing_notification(
                user_id=user_id,
                video_id=video_id,
                status=status,
                progress=progress,
                metadata=metadata
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown notification type: {notification_type}"
            )
        
        return {
            "success": True,
            "message": "Notification sent successfully",
            "data": {
                "type": notification_type,
                "target_users": target_users or "all",
                "message": message
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send notification: {str(e)}"
        )


@router.post("/rooms/{room_id}/broadcast")
async def broadcast_to_room(
    room_id: str,
    message_data: Dict[str, Any]
):
    """Broadcast a message to all users in a room"""
    try:
        room_info = connection_manager.get_room_info(room_id)
        
        if not room_info["exists"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Room {room_id} not found"
            )
        
        message = {
            "type": "room_broadcast",
            "room_id": room_id,
            "content": message_data.get("content"),
            "sender": message_data.get("sender", "system"),
            "timestamp": message_data.get("timestamp")
        }
        
        await connection_manager.send_room_message(message, room_id)
        
        return {
            "success": True,
            "message": f"Message broadcast to room {room_id}",
            "data": {
                "room_id": room_id,
                "recipients": room_info["connection_count"],
                "message": message
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to broadcast to room: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to broadcast to room: {str(e)}"
        )


@router.delete("/connections/{user_id}")
async def disconnect_user(user_id: int):
    """Disconnect all connections for a specific user (admin endpoint)"""
    try:
        if user_id in connection_manager.active_connections:
            connections = list(connection_manager.active_connections[user_id])
            
            for websocket in connections:
                try:
                    await websocket.close(code=4003, reason="Disconnected by admin")
                except:
                    pass
                connection_manager.disconnect(user_id, websocket)
            
            return {
                "success": True,
                "message": f"Disconnected {len(connections)} connections for user {user_id}",
                "data": {
                    "user_id": user_id,
                    "disconnected_connections": len(connections)
                }
            }
        else:
            return {
                "success": True,
                "message": f"User {user_id} has no active connections",
                "data": {
                    "user_id": user_id,
                    "disconnected_connections": 0
                }
            }
    except Exception as e:
        logger.error(f"Failed to disconnect user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect user: {str(e)}"
        )


@router.get("/health")
async def websocket_health_check():
    """Health check for WebSocket service"""
    try:
        stats = connection_manager.get_connection_stats()
        
        # Determine health status
        health_status = "healthy"
        if stats["active_connections"] > 1000:  # Threshold for high load
            health_status = "high_load"
        
        return {
            "success": True,
            "message": "WebSocket service is operational",
            "data": {
                "status": health_status,
                "active_connections": stats["active_connections"],
                "active_users": stats["active_users"],
                "active_rooms": stats["active_rooms"],
                "total_messages_sent": stats["messages_sent"],
                "total_messages_received": stats["messages_received"]
            }
        }
    except Exception as e:
        logger.error(f"WebSocket health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WebSocket health check failed: {str(e)}"
        )
