"""Application configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _bool_from_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Runtime settings read from environment variables."""

    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = _bool_from_env("DEBUG", True)
    output_dir: Path = PROJECT_ROOT / os.getenv("OUTPUT_DIR", "outputs")
    video_input_dir: Path = PROJECT_ROOT / os.getenv("VIDEO_INPUT_DIR", "data")
    database_path: Path = PROJECT_ROOT / "outputs" / "violations.db"
    json_log_path: Path = PROJECT_ROOT / "outputs" / "compliance_reports.json"
    csv_log_path: Path = PROJECT_ROOT / "outputs" / "compliance_reports.csv"
    rules_path: Path = PROJECT_ROOT / "src" / "severity" / "parsed_rules.json"
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
    detection_frame_stride: int = int(os.getenv("DETECTION_FRAME_STRIDE", "12"))
    detection_max_frames: int = int(os.getenv("DETECTION_MAX_FRAMES", "180"))
    detection_use_ml: bool = _bool_from_env("DETECTION_USE_ML", True)
    yolo_model: str = os.getenv("YOLO_MODEL", "yolov8n.pt")
    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
        ).split(",")
        if origin.strip()
    )

    @classmethod
    def load(cls) -> "Settings":
        """Create settings and normalize DATABASE_URL if provided."""

        database_url = os.getenv("DATABASE_URL")
        settings = cls()
        if database_url and database_url.startswith("sqlite:///"):
            object.__setattr__(
                settings,
                "database_path",
                PROJECT_ROOT / database_url.replace("sqlite:///", "", 1),
            )
        return settings

    def ensure_directories(self) -> None:
        """Create directories required by the application."""

        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "exports").mkdir(parents=True, exist_ok=True)
        (self.output_dir / "uploads").mkdir(parents=True, exist_ok=True)
        self.video_input_dir.mkdir(parents=True, exist_ok=True)


settings = Settings.load()
