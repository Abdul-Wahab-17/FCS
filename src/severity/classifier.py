"""Module 2: Severity categorization matrix."""

from __future__ import annotations

import json
import operator
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from src.config import settings
from src.severity.context_analyzer import ContextAnalyzer
from src.severity.utils import higher_severity


class SeverityTier(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class SeverityDecision:
    severity: SeverityTier
    rationale: str
    policy_signal: str
    applied_rules: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity.value,
            "rationale": self.rationale,
            "policy_signal": self.policy_signal,
            "applied_rules": self.applied_rules,
        }


class SeverityClassifier:
    """Assign LOW/MEDIUM/HIGH/CRITICAL tiers from policy-derived parsed rules."""

    OPERATORS = {
        "<": operator.lt,
        "<=": operator.le,
        ">": operator.gt,
        ">=": operator.ge,
        "==": operator.eq,
        "!=": operator.ne,
    }

    def __init__(
        self,
        rules_path: str | Path | None = None,
        context_analyzer: ContextAnalyzer | None = None,
    ) -> None:
        self.rules_path = Path(rules_path or settings.rules_path)
        with self.rules_path.open("r", encoding="utf-8") as file:
            parsed_data = json.load(file)
            # Map by behavior_class
            self.rules = {r["behavior_class"]: r for r in parsed_data.get("compliance_rules", [])}
        self.context_analyzer = context_analyzer or ContextAnalyzer()

    def classify(
        self, detection: dict[str, Any], frame_context: dict[str, Any] | None = None
    ) -> SeverityDecision:
        """Classify one detection using policy-grounded rules."""

        behavior = detection.get("behavior_class")
        rule = self.rules.get(str(behavior))
        if not rule:
            return SeverityDecision(
                severity=SeverityTier.MEDIUM,
                rationale="Unknown behavior class; defaulted to MEDIUM pending review.",
                policy_signal="No policy rule matched.",
                applied_rules=[],
            )

        base_severity = rule.get("severity_tier", "MEDIUM")
        policy_callout = rule.get("policy_callout", "NOTICE")
        rationale = f"Per {rule.get('rule_id', 'Unknown')}: baseline {base_severity} per policy callout {policy_callout}."
        
        applied_rules: list[str] = []
        context = self.context_analyzer.analyze(detection, frame_context)

        current_severity = base_severity

        # Apply contextual multipliers only using thresholds mentioned in the policy text
        for escalation in rule.get("escalation_conditions", []):
            condition = escalation["condition"]
            if self._evaluate_condition(condition, context):
                next_severity = escalation["new_severity"]
                current_severity = higher_severity(current_severity, next_severity)
                rationale = f"Per {rule.get('rule_id', 'Unknown')}: {escalation.get('rationale', rule.get('hazard_description', 'Escalated'))}"
                applied_rules.append(condition)

        # Ensure CRITICAL SAFETY NOTICE implies at least HIGH
        if policy_callout == "CRITICAL SAFETY NOTICE" and current_severity in ("LOW", "MEDIUM"):
            current_severity = "HIGH"
            rationale = f"Per {rule.get('rule_id')}: {rule.get('hazard_description')}"

        return SeverityDecision(
            severity=SeverityTier(current_severity),
            rationale=rationale,
            policy_signal=policy_callout,
            applied_rules=applied_rules,
        )

    def _evaluate_condition(self, condition: str, context: dict[str, Any]) -> bool:
        """Evaluate a simple policy condition such as ``duration_open > 300``."""

        for op_text, op_func in sorted(self.OPERATORS.items(), key=lambda item: -len(item[0])):
            if op_text not in condition:
                continue
            left, right = (part.strip() for part in condition.split(op_text, 1))
            if left not in context:
                return False
            return op_func(context[left], self._coerce_value(right))
        return False

    def _coerce_value(self, raw: str) -> Any:
        value = raw.strip().strip('"').strip("'")
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value
