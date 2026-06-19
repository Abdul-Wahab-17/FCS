"""Severity utility functions."""

from __future__ import annotations


SEVERITY_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


def higher_severity(current: str, candidate: str) -> str:
    """Return the more severe tier."""

    return (
        candidate
        if SEVERITY_ORDER.get(candidate, 0) > SEVERITY_ORDER.get(current, 0)
        else current
    )


def flatten_context(detection: dict) -> dict:
    """Merge detection metadata into top-level context for rule evaluation."""

    context = dict(detection)
    metadata = detection.get("metadata") or {}
    if isinstance(metadata, dict):
        context.update(metadata)
    return context
