import json
import structlog
from typing import Any
from app.infrastructure.streaming.manager import WebSocketManager

logger = structlog.get_logger()

class BroadcastService:
    """Responsible for broadcasting structured updates to specific topics or all connected clients."""

    def __init__(self, websocket_manager: WebSocketManager) -> None:
        self.manager = websocket_manager

    async def broadcast_to_topic(self, topic: str, payload: Any) -> None:
        """Broadcasts a payload message to all clients subscribed to a specific topic."""
        subscribers = self.manager.subscription_manager.get_subscribers(topic)
        if not subscribers:
            return

        message = {
            "type": "update",
            "topic": topic,
            "data": payload
        }
        message_str = json.dumps(message, default=str)
        
        for ws in list(subscribers):
            try:
                await ws.send_text(message_str)
            except Exception as e:
                logger.warning("Failed to send message to subscriber, disconnecting", error=str(e))
                self.manager.subscription_manager.unsubscribe_all(ws)
                self.manager.connection_manager.disconnect(ws)

    async def broadcast_to_all(self, payload: Any) -> None:
        """Broadcasts a payload message to all currently connected WebSocket clients."""
        connections = self.manager.connection_manager.active_connections
        if not connections:
            return

        message = {
            "type": "broadcast",
            "data": payload
        }
        message_str = json.dumps(message, default=str)

        for ws in list(connections):
            try:
                await ws.send_text(message_str)
            except Exception as e:
                logger.warning("Failed to send broadcast, disconnecting", error=str(e))
                self.manager.subscription_manager.unsubscribe_all(ws)
                self.manager.connection_manager.disconnect(ws)
