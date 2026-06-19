"""Module 3: Escalation routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.escalation.alert_manager import AlertManager


class RoutingRule:
    """Policy routing rules for compliance events."""

    ALERT_TIERS = {"HIGH", "CRITICAL"}

    @classmethod
    def should_trigger_alert(cls, severity: str) -> bool:
        return severity in cls.ALERT_TIERS

    @classmethod
    def action_for_severity(cls, severity: str) -> str:
        if cls.should_trigger_alert(severity):
            return "Database log + real-time dashboard alert"
        return "Database log only"


@dataclass
class EscalationRouter:
    """Route compliance reports to database and alert channels."""

    alert_manager: AlertManager
    db_logger: Any | None = None

    async def route_violation(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Log every violation and alert only HIGH/CRITICAL records."""

        if self.db_logger is not None:
            self.db_logger.insert(violation)

        alert_payload = None
        if RoutingRule.should_trigger_alert(violation["severity"]):
            alert_payload = await self.alert_manager.trigger_alert(violation)

        return {
            "event_id": violation["event_id"],
            "severity": violation["severity"],
            "escalation_action": RoutingRule.action_for_severity(violation["severity"]),
            "alert_sent": alert_payload is not None,
        }

    async def route_report(self, report: Any) -> dict[str, Any]:
        data = report.model_dump() if hasattr(report, "model_dump") else dict(report)
        return await self.route_violation(data)
