"""Context enrichment for severity classification."""

from __future__ import annotations

from typing import Any

from src.severity.utils import flatten_context


class ContextAnalyzer:
    """Extract context values used by policy-derived escalation rules."""

    def analyze(
        self, detection: dict[str, Any], frame_context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        context = flatten_context(detection)
        if frame_context:
            context.update(frame_context)
        return context
