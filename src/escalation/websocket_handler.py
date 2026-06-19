"""WebSocket endpoint helper."""

from __future__ import annotations

import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from src.escalation.alert_manager import WebSocketConnectionManager


async def alerts_websocket_endpoint(
    websocket: WebSocket, manager: WebSocketConnectionManager
) -> None:
    """Handle WebSocket connections for real‑time alerts.

    The client only receives messages; it does not send any.
    We acknowledge the connection, register it with ``WebSocketConnectionManager``,
    send an initial ``connected`` payload, then emit a heartbeat every 15 seconds.
    Any unexpected error results in a graceful disconnect.
    """
    # Register connection (accepts the socket)
    await websocket.accept()
    await manager.connect(websocket)
    try:
        # Initial acknowledgment so the client knows the stream is live
        await websocket.send_json({"type": "connected"})
        while True:
            # Send heartbeat periodically to keep connection alive
            await websocket.send_json({"type": "heartbeat"})
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as exc:
        print(f"WebSocket error: {exc}")
        manager.disconnect(websocket)
