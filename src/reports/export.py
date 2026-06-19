"""Export helpers for compliance records."""

from __future__ import annotations

import csv
import io
import json
from typing import Any


def records_to_csv(records: list[dict[str, Any]]) -> str:
    if not records:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(records[0].keys()))
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()


def records_to_json(records: list[dict[str, Any]]) -> str:
    return json.dumps(records, indent=2, sort_keys=True)
