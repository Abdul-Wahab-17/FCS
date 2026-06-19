"""Real-time alert management for HIGH and CRITICAL violations."""

from __future__ import annotations

from typing import Any

from fastapi import WebSocket


class WebSocketConnectionManager:
    """Tracks dashboard WebSocket clients and broadcasts alert payloads."""

    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_json(payload)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


class AlertManager:
    """Creates and sends real-time alert payloads."""

    def __init__(self, websocket_manager: WebSocketConnectionManager | None = None) -> None:
        self.websocket_manager = websocket_manager or WebSocketConnectionManager()
        self.recent_alerts: list[dict[str, Any]] = []

    async def trigger_alert(self, violation: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "type": "COMPLIANCE_ALERT",
            "event_id": violation["event_id"],
            "timestamp": violation["timestamp"],
            "severity": violation["severity"],
            "behavior_class": violation["behavior_class"],
            "description": violation["event_description"],
            "zone": violation["zone"],
        }
        self.recent_alerts.insert(0, payload)
        self.recent_alerts = self.recent_alerts[:50]
        await self.websocket_manager.broadcast(payload)
        return payload
