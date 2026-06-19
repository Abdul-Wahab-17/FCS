"""Database logging adapter used by the escalation router."""

from __future__ import annotations

from typing import Any

from src.reports.database import ViolationRepository


class DatabaseLogger:
    def __init__(self, repository: ViolationRepository | None = None) -> None:
        self.repository = repository or ViolationRepository()

    def insert(self, violation: dict[str, Any]) -> str:
        return self.repository.insert(violation)
