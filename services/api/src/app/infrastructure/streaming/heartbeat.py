import asyncio
import json

import structlog

from app.infrastructure.streaming.manager import WebSocketManager

logger = structlog.get_logger()

class HeartbeatService:
    """Sends periodic heartbeats to verify client liveness."""

    def __init__(self, websocket_manager: WebSocketManager, interval_seconds: float = 30.0) -> None:
        self.manager = websocket_manager
        self.interval = interval_seconds
        self._task: asyncio.Task[None] | None = None
        self._running = False

    async def start(self) -> None:
        """Starts background loop sending periodic heartbeats."""
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("Heartbeat service started", interval=self.interval)

    async def stop(self) -> None:
        """Stops background loop and cleans up task resources."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Heartbeat service stopped")

    async def _loop(self) -> None:
        try:
            while self._running:
                await asyncio.sleep(self.interval)
                connections = self.manager.connection_manager.active_connections
                if not connections:
                    continue

                ping_message = json.dumps({"type": "ping"})
                for ws in list(connections):
                    try:
                        await ws.send_text(ping_message)
                    except Exception as e:
                        logger.warning("Heartbeat failed, disconnecting client", error=str(e))
                        self.manager.subscription_manager.unsubscribe_all(ws)
                        self.manager.connection_manager.disconnect(ws)
        except asyncio.CancelledError:
            pass
