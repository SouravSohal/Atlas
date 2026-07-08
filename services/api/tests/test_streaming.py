import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient

from app.infrastructure.streaming import (
    WebSocketManager,
    BroadcastService,
    HeartbeatService,
)

@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    ws_manager = WebSocketManager()
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await ws_manager.handle_connection(websocket)
        
    app.state.ws_manager = ws_manager
    return app

def test_websocket_connection_and_subscription(test_app) -> None:
    client = TestClient(test_app)
    ws_manager = test_app.state.ws_manager

    with client.websocket_connect("/ws") as websocket:
        assert len(ws_manager.connection_manager.active_connections) == 1
        
        # 1. Send subscription payload
        websocket.send_text(json.dumps({
            "type": "subscribe",
            "topic": "incidents"
        }))
        
        # Verify response
        resp = json.loads(websocket.receive_text())
        assert resp["type"] == "subscribed"
        assert resp["topic"] == "incidents"
        
        # Check subscription status
        assert len(ws_manager.subscription_manager.get_subscribers("incidents")) == 1

        # 2. Send ping control message
        websocket.send_text(json.dumps({
            "type": "ping"
        }))
        
        # Verify response
        pong_resp = json.loads(websocket.receive_text())
        assert pong_resp["type"] == "pong"

        # 3. Send unsubscribe payload
        websocket.send_text(json.dumps({
            "type": "unsubscribe",
            "topic": "incidents"
        }))
        
        # Verify response
        unsub_resp = json.loads(websocket.receive_text())
        assert unsub_resp["type"] == "unsubscribed"
        assert unsub_resp["topic"] == "incidents"
        assert len(ws_manager.subscription_manager.get_subscribers("incidents")) == 0

@pytest.mark.asyncio
async def test_broadcast_service(test_app) -> None:
    client = TestClient(test_app)
    ws_manager = test_app.state.ws_manager
    broadcast_service = BroadcastService(ws_manager)

    with client.websocket_connect("/ws") as websocket:
        # Subscribe
        websocket.send_text(json.dumps({
            "type": "subscribe",
            "topic": "operational_state"
        }))
        _ = websocket.receive_text()

        # Broadcast to specific topic
        await broadcast_service.broadcast_to_topic("operational_state", {"density": 0.85})
        update_resp = json.loads(websocket.receive_text())
        assert update_resp["type"] == "update"
        assert update_resp["topic"] == "operational_state"
        assert update_resp["data"]["density"] == 0.85

        # General broadcast to all active connections
        await broadcast_service.broadcast_to_all({"message": "system warning"})
        broadcast_resp = json.loads(websocket.receive_text())
        assert broadcast_resp["type"] == "broadcast"
        assert broadcast_resp["data"]["message"] == "system warning"

@pytest.mark.asyncio
async def test_heartbeat_service() -> None:
    ws_manager = WebSocketManager()
    mock_ws = AsyncMock()
    ws_manager.connection_manager.active_connections.add(mock_ws)

    heartbeat_service = HeartbeatService(ws_manager, interval_seconds=0.005)
    
    # Run loop brief iteration
    await heartbeat_service.start()
    await asyncio.sleep(0.015)
    await heartbeat_service.stop()

    mock_ws.send_text.assert_called()
    assert "ping" in mock_ws.send_text.call_args[0][0]

@pytest.mark.asyncio
async def test_streaming_failures() -> None:
    ws_manager = WebSocketManager()
    mock_ws = AsyncMock()
    # Force exception when sending text
    mock_ws.send_text.side_effect = Exception("Connection terminated by peer")
    
    ws_manager.connection_manager.active_connections.add(mock_ws)
    ws_manager.subscription_manager.subscribe(mock_ws, "alerts")

    broadcast_service = BroadcastService(ws_manager)

    # 1. Test topic broadcast exception handling
    await broadcast_service.broadcast_to_topic("alerts", {"alert": "critical"})
    assert len(ws_manager.connection_manager.active_connections) == 0

    # Reset connection and subscriptions
    ws_manager.connection_manager.active_connections.add(mock_ws)
    ws_manager.subscription_manager.subscribe(mock_ws, "alerts")

    # 2. Test broadcast to all exception handling
    await broadcast_service.broadcast_to_all({"broadcast": "general"})
    assert len(ws_manager.connection_manager.active_connections) == 0

    # 3. Test heartbeat service exception handling
    ws_manager.connection_manager.active_connections.add(mock_ws)
    ws_manager.subscription_manager.subscribe(mock_ws, "alerts")
    heartbeat_service = HeartbeatService(ws_manager, interval_seconds=0.002)
    
    await heartbeat_service.start()
    await asyncio.sleep(0.008)
    await heartbeat_service.stop()
    assert len(ws_manager.connection_manager.active_connections) == 0

    # 4. Test invalid json message handling in manager
    await ws_manager.handle_message(mock_ws, "{invalid json}")
