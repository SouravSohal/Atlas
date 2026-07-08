import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, WebSocket, Depends

from app.dependencies.container import ApplicationContainer
from app.infrastructure.streaming.manager import WebSocketManager

logger = structlog.get_logger()
router = APIRouter(tags=["Streaming"])

@router.websocket("/ws")
@inject
async def websocket_endpoint(
    websocket: WebSocket,
    ws_manager: WebSocketManager = Depends(Provide[ApplicationContainer.websocket_manager]),
) -> None:
    """FastAPI WebSocket endpoint for digital twin streaming subscriptions and heartbeats."""
    logger.info("Incoming WebSocket connection request")
    await ws_manager.handle_connection(websocket)
