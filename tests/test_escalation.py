import asyncio

from src.escalation.router import EscalationRouter, RoutingRule


class FakeAlertManager:
    def __init__(self):
        self.sent = []

    async def trigger_alert(self, violation):
        self.sent.append(violation)
        return violation


def test_routing_rule_alert_tiers():
    assert RoutingRule.should_trigger_alert("HIGH")
    assert RoutingRule.should_trigger_alert("CRITICAL")
    assert not RoutingRule.should_trigger_alert("MEDIUM")


def test_router_sends_alert_for_critical():
    alert_manager = FakeAlertManager()
    router = EscalationRouter(alert_manager=alert_manager)
    violation = {
        "event_id": "evt-1",
        "timestamp": "2026-06-17T00:00:00Z",
        "severity": "CRITICAL",
        "behavior_class": "Carrying_Overload_with_Forklift",
        "event_description": "Overload",
        "zone": "Loading_Area",
    }

    result = asyncio.run(router.route_violation(violation))

    assert result["alert_sent"] is True
    assert alert_manager.sent == [violation]
