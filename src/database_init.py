"""Initialize the SQLite database."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import settings
from src.reports.database import ViolationRepository


def main() -> None:
    settings.ensure_directories()
    repository = ViolationRepository(settings.database_path)
    repository.ensure_schema()
    print(f"Database initialized at {settings.database_path}")


if __name__ == "__main__":
    main()
