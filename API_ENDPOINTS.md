# API Endpoints

Base URL: `http://localhost:8000`

## Health

`GET /api/health`

Returns service status.

```json
{
  "status": "healthy",
  "service": "factory-compliance-system"
}
```

## Process Video Path

`POST /api/process_video`

Request:

```json
{
  "video_path": "data/test/Carrying_Overload_with_Forklift/demo_overload.mp4"
}
```

Response:

```json
{
  "status": "success",
  "count": 1,
  "reports": []
}
```

## Upload Video

`POST /api/upload_video`

Multipart form field: `file`.

The uploaded file is saved under `outputs/uploads/` and processed through the same pipeline.

## Seed Demo Records

`POST /api/demo/seed`

Creates one sample record for each unsafe behavior using dataset-label fallback paths.

## List Violations

`GET /api/violations`

Optional query parameters:

- `severity`
- `behavior_class`
- `start_date`
- `end_date`
- `limit`
- `offset`

Example:

```text
/api/violations?severity=CRITICAL&behavior_class=Carrying_Overload_with_Forklift
```

## Get Single Violation

`GET /api/violations/{event_id}`

Returns one compliance record or `404`.

## Export Violations

`GET /api/export/violations?format=csv`

Formats:

- `csv`
- `json`

Filters match `GET /api/violations`.

## WebSocket Alerts

`WebSocket /ws/alerts`

Receives HIGH and CRITICAL alert payloads:

```json
{
  "type": "COMPLIANCE_ALERT",
  "event_id": "evt-...",
  "timestamp": "2026-06-17T...",
  "severity": "CRITICAL",
  "behavior_class": "Carrying_Overload_with_Forklift",
  "description": "Forklift is carrying three or more blocks...",
  "zone": "Loading_Area"
}
```
