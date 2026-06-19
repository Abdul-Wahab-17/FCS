"""SQLite persistence for immutable compliance records."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from src.config import settings
from src.reports.schemas import ComplianceReport


class ViolationRepository:
    """Thin SQLite repository for violation records."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path = Path(db_path or settings.database_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_schema()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def ensure_schema(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS violations (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    clip_id TEXT NOT NULL,
                    zone TEXT NOT NULL,
                    behavior_class TEXT NOT NULL,
                    policy_rule_ref TEXT NOT NULL,
                    event_description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    escalation_action TEXT NOT NULL,
                    confidence REAL NOT NULL DEFAULT 0,
                    frame_number INTEGER NOT NULL DEFAULT 0,
                    bounding_box TEXT,
                    metadata TEXT,
                    rationale TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON violations(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_violations_severity ON violations(severity)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_violations_behavior ON violations(behavior_class)"
            )

    def insert(self, report: ComplianceReport | dict[str, Any]) -> str:
        data = report.model_dump() if isinstance(report, ComplianceReport) else dict(report)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO violations (
                    event_id, timestamp, clip_id, zone, behavior_class,
                    policy_rule_ref, event_description, severity,
                    escalation_action, confidence, frame_number, bounding_box,
                    metadata, rationale, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["event_id"],
                    data["timestamp"],
                    data["clip_id"],
                    data["zone"],
                    data["behavior_class"],
                    data["policy_rule_ref"],
                    data["event_description"],
                    data["severity"],
                    data["escalation_action"],
                    float(data.get("confidence") or 0.0),
                    int(data.get("frame_number") or 0),
                    json.dumps(data.get("bounding_box")),
                    json.dumps(data.get("metadata") or {}),
                    data.get("rationale", ""),
                    data["created_at"],
                ),
            )
        return data["event_id"]

    def list(
        self,
        severity: str | None = None,
        behavior_class: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if severity:
            clauses.append("severity = ?")
            params.append(severity)
        if behavior_class:
            clauses.append("behavior_class = ?")
            params.append(behavior_class)
        if start_date:
            clauses.append("timestamp >= ?")
            params.append(start_date)
        if end_date:
            clauses.append("timestamp <= ?")
            params.append(end_date)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.extend([limit, offset])
        with self.connect() as conn:
            rows = conn.execute(
                f"""
                SELECT * FROM violations
                {where}
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
                """,
                params,
            ).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get(self, event_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM violations WHERE event_id = ?", (event_id,)
            ).fetchone()
        return self._row_to_dict(row) if row else None

    def stats(self) -> dict[str, Any]:
        with self.connect() as conn:
            total = conn.execute("SELECT COUNT(*) AS count FROM violations").fetchone()[
                "count"
            ]
            by_severity = conn.execute(
                "SELECT severity, COUNT(*) AS count FROM violations GROUP BY severity"
            ).fetchall()
            by_behavior = conn.execute(
                "SELECT behavior_class, COUNT(*) AS count FROM violations GROUP BY behavior_class"
            ).fetchall()
        return {
            "total": total,
            "by_severity": {row["severity"]: row["count"] for row in by_severity},
            "by_behavior": {row["behavior_class"]: row["count"] for row in by_behavior},
        }

    def clear(self) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM violations")

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        data = dict(row)
        data["bounding_box"] = json.loads(data["bounding_box"] or "null")
        data["metadata"] = json.loads(data["metadata"] or "{}")
        return data
