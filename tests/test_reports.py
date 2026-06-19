from src.reports.database import ViolationRepository
from src.reports.generator import ComplianceReportGenerator


def test_report_generator_persists_all_formats(tmp_path):
    repository = ViolationRepository(tmp_path / "violations.db")
    generator = ComplianceReportGenerator(
        repository=repository,
        json_log_path=tmp_path / "reports.json",
        csv_log_path=tmp_path / "reports.csv",
    )
    detection = {
        "clip_id": "clip_001",
        "zone": "Loading_Area",
        "behavior_class": "Carrying_Overload_with_Forklift",
        "policy_rule_ref": "Section 6.3.2",
        "description": "Forklift overload detected.",
        "confidence": 0.9,
        "frame_number": 0,
        "bounding_box": (1, 2, 3, 4),
        "metadata": {"block_count": 3},
    }

    report = generator.generate(
        detection=detection,
        severity="CRITICAL",
        escalation_action="Database log + real-time dashboard alert",
        rationale="Explicit overload threshold.",
    )

    assert repository.get(report.event_id)["severity"] == "CRITICAL"
    assert (tmp_path / "reports.json").read_text(encoding="utf-8").strip()
    assert "event_id" in (tmp_path / "reports.csv").read_text(encoding="utf-8")
