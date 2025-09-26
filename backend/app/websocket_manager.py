"""WebSocket connection manager for real-time updates"""

from typing import List, Dict, Any
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.update_interval = 5  # seconds
        self.is_broadcasting = False

    async def connect(self, websocket: WebSocket):
        """Accept and store new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        await websocket.send_text(message)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connections"""
        if not self.active_connections:
            return

        message_json = json.dumps(message)
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error sending to WebSocket: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

    async def start_broadcasting(self, get_data_callback):
        """Start periodic broadcasting of data updates"""
        if self.is_broadcasting:
            return

        self.is_broadcasting = True
        logger.info("Started WebSocket broadcasting")

        while self.is_broadcasting:
            if self.active_connections:
                try:
                    # Get latest data
                    data = await get_data_callback()

                    # Add timestamp
                    data['ws_timestamp'] = datetime.now().isoformat()
                    data['connection_count'] = len(self.active_connections)

                    # Broadcast to all connections
                    await self.broadcast(data)

                except Exception as e:
                    logger.error(f"Error in broadcast loop: {e}")

            await asyncio.sleep(self.update_interval)

    def stop_broadcasting(self):
        """Stop broadcasting"""
        self.is_broadcasting = False
        logger.info("Stopped WebSocket broadcasting")

# Global instance
manager = ConnectionManager()