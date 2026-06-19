# System Architecture

## Pipeline

The application is organized as a five-stage pipeline:

```text
Video clip
  -> DetectionEngine
  -> SeverityClassifier
  -> ComplianceReportGenerator
  -> EscalationRouter
  -> Dashboard + audit storage
```

## Module 1: Detection Engine

`src/detection/detector.py` returns `DetectionRecord` objects with clip id, timestamp, behavior class, confidence, zone, bounding box, and policy reference.

The detector supports two paths:

- Dataset-label fallback for the Kaggle folder structure.
- Optional frame processing through OpenCV and YOLO when `DETECTION_USE_ML=True`.

This keeps the system runnable before custom model training while preserving a place for real CV inference.

## Module 2: Severity Categorization

`src/severity/classifier.py` loads `rules.json`, assigns default severity, then evaluates escalation conditions such as:

- `person_proximity_to_machinery < 1.0`
- `personnel_count > 1`
- `duration_open > 300`

The classifier returns both the severity and a rationale for auditability.

## Module 3: Escalation Pipeline

`src/escalation/router.py` applies the routing policy:

- LOW and MEDIUM: database log only.
- HIGH and CRITICAL: database log plus WebSocket alert.

`AlertManager` stores recent alerts and broadcasts to connected dashboard clients.

## Module 4: Report Generation

`src/reports/generator.py` creates immutable `ComplianceReport` records and writes them to:

- SQLite: `outputs/violations.db`
- JSON Lines: `outputs/compliance_reports.json`
- CSV: `outputs/compliance_reports.csv`

SQLite indexes support filtering by timestamp, severity, and behavior class.

## Module 5: Operations Dashboard

The React dashboard has three views:

- Live Feed Monitor: upload or process a path and see detection overlays.
- Alert Timeline: chronological stream of violations and live WebSocket alerts.
- Historical Log: filtered records with CSV and JSON export.

The UI is intentionally operational: compact, scan-friendly, and focused on repeated monitoring workflows.
