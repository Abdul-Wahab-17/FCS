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
    """Assign LOW/MEDIUM/HIGH/CRITICAL tiers from policy-derived rules."""

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
            self.rules = json.load(file)
        self.context_analyzer = context_analyzer or ContextAnalyzer()

    def classify(
        self, detection: dict[str, Any], frame_context: dict[str, Any] | None = None
    ) -> SeverityDecision:
        """Classify one detection and explain the decision."""

        behavior = detection.get("behavior_class")
        rule = self.rules.get(str(behavior))
        if not rule:
            return SeverityDecision(
                severity=SeverityTier.MEDIUM,
                rationale="Unknown behavior class; defaulted to MEDIUM pending review.",
                policy_signal="No policy rule matched.",
                applied_rules=[],
            )

        severity = rule["default_severity"]
        rationale = rule.get("tier_justification", rule.get("policy_signal", "Default"))
        applied_rules: list[str] = []
        context = self.context_analyzer.analyze(detection, frame_context)

        for escalation in rule.get("escalation_rules", []):
            condition = escalation["condition"]
            if self._evaluate_condition(condition, context):
                next_severity = escalation["new_severity"]
                severity = higher_severity(severity, next_severity)
                rationale = escalation["rationale"]
                applied_rules.append(condition)

        return SeverityDecision(
            severity=SeverityTier(severity),
            rationale=rationale,
            policy_signal=rule.get("policy_signal", ""),
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
