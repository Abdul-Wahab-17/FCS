"""WebSocket endpoint helper."""

from __future__ import annotations

from fastapi import WebSocket, WebSocketDisconnect

from src.escalation.alert_manager import WebSocketConnectionManager


async def alerts_websocket_endpoint(
    websocket: WebSocket, manager: WebSocketConnectionManager
) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
