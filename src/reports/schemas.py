"""Pydantic schemas for compliance records."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_event_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"evt-{stamp}-{uuid.uuid4().hex[:8]}"


class ComplianceReport(BaseModel):
    event_id: str = Field(default_factory=new_event_id)
    timestamp: str = Field(default_factory=utc_now_iso)
    clip_id: str
    zone: str
    behavior_class: str
    policy_rule_ref: str
    event_description: str
    severity: str
    escalation_action: str
    confidence: float = 0.0
    frame_number: int = 0
    bounding_box: tuple[int, int, int, int] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    rationale: str = ""
    created_at: str = Field(default_factory=utc_now_iso)


class ViolationFilters(BaseModel):
    severity: str | None = None
    behavior_class: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    limit: int = 100
    offset: int = 0
