"""
WebSocket manager for real-time communication
"""

import json
import asyncio
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and real-time communication"""
    
    def __init__(self):
        # Store active connections by user ID
        self.active_connections: Dict[int, List[WebSocket]] = defaultdict(list)
        
        # Store connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Store room-based connections (for collaborative features)
        self.rooms: Dict[str, Set[str]] = defaultdict(set)
        
        # Message queue for offline users
        self.offline_messages: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
        
        # Connection statistics
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "messages_sent": 0,
            "messages_received": 0
        }
    
    async def connect(self, websocket: WebSocket, user_id: int, connection_id: str = None) -> str:
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if connection_id is None:
            connection_id = str(uuid.uuid4())
        
        # Add to active connections
        self.active_connections[user_id].append(websocket)
        
        # Store connection metadata
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "websocket": websocket,
            "connected_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        }
        
        # Update statistics
        self.stats["total_connections"] += 1
        self.stats["active_connections"] = len(self.connection_metadata)
        
        logger.info(f"User {user_id} connected with connection ID: {connection_id}")
        
        # Send any queued offline messages
        await self._send_offline_messages(user_id)
        
        # Send connection confirmation
        await self.send_personal_message({
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat(),
            "message": "WebSocket connection established successfully"
        }, user_id)
        
        return connection_id
    
    def disconnect(self, user_id: int, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                
                # Remove empty user entries
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
        
        # Remove from connection metadata
        connection_id = None
        for conn_id, metadata in self.connection_metadata.items():
            if metadata["websocket"] == websocket:
                connection_id = conn_id
                break
        
        if connection_id:
            del self.connection_metadata[connection_id]
        
        # Update statistics
        self.stats["active_connections"] = len(self.connection_metadata)
        
        logger.info(f"User {user_id} disconnected")
    
    async def send_personal_message(self, message: Dict[str, Any], user_id: int):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            # Send to all user's active connections
            disconnected_connections = []
            
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                    self.stats["messages_sent"] += 1
                except Exception as e:
                    logger.warning(f"Failed to send message to user {user_id}: {e}")
                    disconnected_connections.append(websocket)
            
            # Clean up disconnected connections
            for websocket in disconnected_connections:
                self.disconnect(user_id, websocket)
        else:
            # User is offline, queue the message
            self.offline_messages[user_id].append({
                **message,
                "queued_at": datetime.now().isoformat()
            })
            logger.info(f"Message queued for offline user {user_id}")
    
    async def send_room_message(self, message: Dict[str, Any], room_id: str):
        """Send a message to all users in a room"""
        if room_id in self.rooms:
            for connection_id in self.rooms[room_id]:
                if connection_id in self.connection_metadata:
                    metadata = self.connection_metadata[connection_id]
                    user_id = metadata["user_id"]
                    await self.send_personal_message(message, user_id)
    
    async def broadcast_message(self, message: Dict[str, Any], exclude_user: Optional[int] = None):
        """Broadcast a message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            if exclude_user is None or user_id != exclude_user:
                await self.send_personal_message(message, user_id)
    
    async def join_room(self, connection_id: str, room_id: str):
        """Add a connection to a room"""
        self.rooms[room_id].add(connection_id)
        
        if connection_id in self.connection_metadata:
            metadata = self.connection_metadata[connection_id]
            user_id = metadata["user_id"]
            
            await self.send_personal_message({
                "type": "room_joined",
                "room_id": room_id,
                "timestamp": datetime.now().isoformat(),
                "message": f"Joined room: {room_id}"
            }, user_id)
            
            logger.info(f"Connection {connection_id} joined room {room_id}")
    
    async def leave_room(self, connection_id: str, room_id: str):
        """Remove a connection from a room"""
        if room_id in self.rooms:
            self.rooms[room_id].discard(connection_id)
            
            # Remove empty rooms
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            
            if connection_id in self.connection_metadata:
                metadata = self.connection_metadata[connection_id]
                user_id = metadata["user_id"]
                
                await self.send_personal_message({
                    "type": "room_left",
                    "room_id": room_id,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Left room: {room_id}"
                }, user_id)
                
                logger.info(f"Connection {connection_id} left room {room_id}")
    
    async def _send_offline_messages(self, user_id: int):
        """Send queued messages to a newly connected user"""
        if user_id in self.offline_messages:
            messages = self.offline_messages[user_id]
            
            for message in messages:
                await self.send_personal_message({
                    **message,
                    "type": "offline_message",
                    "delivered_at": datetime.now().isoformat()
                }, user_id)
            
            # Clear the queue
            del self.offline_messages[user_id]
            logger.info(f"Delivered {len(messages)} offline messages to user {user_id}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            **self.stats,
            "active_users": len(self.active_connections),
            "active_rooms": len(self.rooms),
            "queued_messages": sum(len(messages) for messages in self.offline_messages.values()),
            "connections_by_user": {
                user_id: len(connections) 
                for user_id, connections in self.active_connections.items()
            }
        }
    
    def get_room_info(self, room_id: str) -> Dict[str, Any]:
        """Get information about a specific room"""
        if room_id not in self.rooms:
            return {"exists": False}
        
        connections = list(self.rooms[room_id])
        users = []
        
        for connection_id in connections:
            if connection_id in self.connection_metadata:
                metadata = self.connection_metadata[connection_id]
                users.append({
                    "user_id": metadata["user_id"],
                    "connected_at": metadata["connected_at"],
                    "last_activity": metadata["last_activity"]
                })
        
        return {
            "exists": True,
            "room_id": room_id,
            "connection_count": len(connections),
            "users": users
        }


class NotificationManager:
    """Manages real-time notifications"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.notification_types = {
            "video_processing_started",
            "video_processing_completed",
            "video_processing_failed",
            "template_updated",
            "asset_uploaded",
            "system_maintenance",
            "user_activity",
            "collaboration_invite"
        }
    
    async def send_video_processing_notification(
        self, 
        user_id: int, 
        video_id: int, 
        status: str, 
        progress: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Send video processing status notification"""
        notification = {
            "type": f"video_processing_{status}",
            "video_id": video_id,
            "status": status,
            "progress": progress,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        
        await self.connection_manager.send_personal_message(notification, user_id)
    
    async def send_template_notification(
        self, 
        user_id: int, 
        template_id: int, 
        action: str,
        template_data: Optional[Dict[str, Any]] = None
    ):
        """Send template-related notification"""
        notification = {
            "type": "template_updated",
            "template_id": template_id,
            "action": action,
            "template_data": template_data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        await self.connection_manager.send_personal_message(notification, user_id)
    
    async def send_asset_notification(
        self, 
        user_id: int, 
        asset_id: int, 
        action: str,
        asset_data: Optional[Dict[str, Any]] = None
    ):
        """Send asset-related notification"""
        notification = {
            "type": "asset_uploaded",
            "asset_id": asset_id,
            "action": action,
            "asset_data": asset_data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        await self.connection_manager.send_personal_message(notification, user_id)
    
    async def send_system_notification(
        self, 
        message: str, 
        level: str = "info",
        target_users: Optional[List[int]] = None
    ):
        """Send system-wide notification"""
        notification = {
            "type": "system_maintenance",
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat()
        }
        
        if target_users:
            for user_id in target_users:
                await self.connection_manager.send_personal_message(notification, user_id)
        else:
            await self.connection_manager.broadcast_message(notification)
    
    async def send_collaboration_notification(
        self, 
        user_id: int, 
        project_id: int, 
        action: str,
        collaborator_data: Optional[Dict[str, Any]] = None
    ):
        """Send collaboration-related notification"""
        notification = {
            "type": "collaboration_invite",
            "project_id": project_id,
            "action": action,
            "collaborator_data": collaborator_data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        await self.connection_manager.send_personal_message(notification, user_id)


# Global instances
connection_manager = ConnectionManager()
notification_manager = NotificationManager(connection_manager)
