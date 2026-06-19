"""FastAPI server for the Factory Compliance System."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Literal

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, File, HTTPException, Query, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from src.config import settings
from src.detection.detector import DetectionEngine
from src.escalation.alert_manager import AlertManager, WebSocketConnectionManager
from src.escalation.router import EscalationRouter, RoutingRule
from src.escalation.websocket_handler import alerts_websocket_endpoint
from src.reports.database import ViolationRepository
from src.reports.export import records_to_csv, records_to_json
from src.reports.generator import ComplianceReportGenerator
from src.severity.classifier import SeverityClassifier


class ProcessVideoRequest(BaseModel):
    video_path: str


settings.ensure_directories()
repository = ViolationRepository(settings.database_path)
generator = ComplianceReportGenerator(repository=repository)
detector = DetectionEngine()
classifier = SeverityClassifier()
ws_manager = WebSocketConnectionManager()
alert_manager = AlertManager(ws_manager)
router = EscalationRouter(alert_manager=alert_manager)

app = FastAPI(
    title="Factory Compliance & Alert Escalation System",
    version="1.0.0",
    description="Detect unsafe factory behaviors, classify severity, and route alerts.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def run_pipeline(video_path: str) -> list[dict]:
    detections = detector.process_video(video_path)
    reports = []
    for detection in detections:
        detection_data = detection.to_dict()
        decision = classifier.classify(detection_data)
        action = RoutingRule.action_for_severity(decision.severity.value)
        report = generator.generate(
            detection=detection_data,
            severity=decision.severity.value,
            escalation_action=action,
            rationale=decision.rationale,
        )
        await router.route_report(report)
        reports.append(report.model_dump())
    return reports


@app.get("/api/health")
async def health_check() -> dict:
    return {"status": "healthy", "service": "factory-compliance-system"}


@app.get("/api/stats")
async def get_stats() -> dict:
    return repository.stats()


@app.post("/api/process_video")
async def process_video(payload: ProcessVideoRequest) -> dict:
    try:
        reports = await run_pipeline(payload.video_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"status": "success", "count": len(reports), "reports": reports}


@app.post("/api/upload_video")
async def upload_video(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")
    upload_path = settings.output_dir / "uploads" / Path(file.filename).name
    with upload_path.open("wb") as output:
        shutil.copyfileobj(file.file, output)
    reports = await run_pipeline(str(upload_path))
    return {"status": "success", "count": len(reports), "reports": reports}


@app.post("/api/demo/seed")
async def seed_demo_records() -> dict:
    sample_paths = [
        "data/test/Safe_Walkway_Violation/demo_walkway.mp4",
        "data/test/Unauthorized_Intervention/demo_intervention.mp4",
        "data/test/Opened_Panel_Cover/demo_panel.mp4",
        "data/test/Carrying_Overload_with_Forklift/demo_overload.mp4",
    ]
    reports: list[dict] = []
    for sample in sample_paths:
        reports.extend(await run_pipeline(sample))
    return {"status": "success", "count": len(reports), "reports": reports}


@app.get("/api/violations")
async def get_violations(
    severity: str | None = None,
    behavior_class: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[dict]:
    return repository.list(
        severity=severity,
        behavior_class=behavior_class,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )


@app.get("/api/violations/{event_id}")
async def get_violation(event_id: str) -> dict:
    violation = repository.get(event_id)
    if violation is None:
        raise HTTPException(status_code=404, detail="Violation not found")
    return violation


@app.get("/api/export/violations")
async def export_violations(
    format: Literal["csv", "json"] = "csv",
    severity: str | None = None,
    behavior_class: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> Response:
    records = repository.list(
        severity=severity,
        behavior_class=behavior_class,
        start_date=start_date,
        end_date=end_date,
        limit=10000,
        offset=0,
    )
    if format == "json":
        return Response(
            records_to_json(records),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=violations.json"},
        )
    return Response(
        records_to_csv(records),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=violations.csv"},
    )


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket) -> None:
    await alerts_websocket_endpoint(websocket, ws_manager)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )
