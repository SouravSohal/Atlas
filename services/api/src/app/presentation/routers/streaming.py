import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, WebSocket, Depends, status

from app.dependencies.container import ApplicationContainer
from app.infrastructure.streaming.manager import WebSocketManager
from app.infrastructure.auth.firebase import FirebaseAuthProvider

logger = structlog.get_logger()
router = APIRouter(tags=["Streaming"])

@router.websocket("/ws")
@inject
async def websocket_endpoint(
    websocket: WebSocket,
    ws_manager: WebSocketManager = Depends(Provide[ApplicationContainer.websocket_manager]),
    auth_provider: FirebaseAuthProvider = Depends(Provide[ApplicationContainer.auth_provider]),
) -> None:
    """FastAPI WebSocket endpoint for digital twin streaming subscriptions and heartbeats."""
    token = websocket.query_params.get("token")
    if not token:
        auth_header = websocket.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        logger.warning("Unauthenticated WebSocket upgrade request: missing token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        auth_provider.verify_token(token)
    except Exception as e:
        logger.warning("Unauthenticated WebSocket upgrade request: invalid token", error=str(e))
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    logger.info("Authenticated WebSocket connection accepted")
    await ws_manager.handle_connection(websocket)
