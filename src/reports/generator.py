"""Module 4: Automated compliance report generation."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.config import settings
from src.reports.database import ViolationRepository
from src.reports.schemas import ComplianceReport


class ComplianceReportGenerator:
    """Generate and persist immutable compliance records."""

    CSV_FIELDS = [
        "event_id",
        "timestamp",
        "clip_id",
        "zone",
        "behavior_class",
        "policy_rule_ref",
        "event_description",
        "severity",
        "escalation_action",
        "confidence",
        "frame_number",
        "rationale",
    ]

    def __init__(
        self,
        repository: ViolationRepository | None = None,
        json_log_path: str | Path | None = None,
        csv_log_path: str | Path | None = None,
    ) -> None:
        self.repository = repository or ViolationRepository()
        self.json_log_path = Path(json_log_path or settings.json_log_path)
        self.csv_log_path = Path(csv_log_path or settings.csv_log_path)
        self.json_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.csv_log_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_csv_header()

    def generate(
        self,
        detection: dict[str, Any],
        severity: str,
        escalation_action: str,
        rationale: str = "",
    ) -> ComplianceReport:
        """Create a report from a detection and persist it to DB, JSONL, and CSV."""

        report = ComplianceReport(
            clip_id=str(detection.get("clip_id", "unknown_clip")),
            zone=str(detection.get("zone", "Unknown")),
            behavior_class=str(detection.get("behavior_class", "Unknown")),
            policy_rule_ref=str(detection.get("policy_rule_ref", "Unmapped")),
            event_description=str(
                detection.get("description") or detection.get("event_description") or ""
            ),
            severity=severity,
            escalation_action=escalation_action,
            confidence=float(detection.get("confidence", 0.0) or 0.0),
            frame_number=int(detection.get("frame_number", 0) or 0),
            bounding_box=detection.get("bounding_box"),
            metadata=detection.get("metadata") or {},
            rationale=rationale,
        )
        self.repository.insert(report)
        self._append_json(report)
        self._append_csv(report)
        return report

    def _append_json(self, report: ComplianceReport) -> None:
        with self.json_log_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(report.model_dump(), sort_keys=True) + "\n")

    def _append_csv(self, report: ComplianceReport) -> None:
        with self.csv_log_path.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.CSV_FIELDS)
            row = report.model_dump()
            writer.writerow({field: row.get(field, "") for field in self.CSV_FIELDS})

    def _ensure_csv_header(self) -> None:
        if self.csv_log_path.exists() and self.csv_log_path.stat().st_size > 0:
            return
        with self.csv_log_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.CSV_FIELDS)
            writer.writeheader()
