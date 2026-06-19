"""Detection module constants and configuration."""

from __future__ import annotations

from dataclasses import dataclass


UNSAFE_BEHAVIORS = (
    "Safe_Walkway_Violation",
    "Unauthorized_Intervention",
    "Opened_Panel_Cover",
    "Carrying_Overload_with_Forklift",
)

SAFE_BEHAVIORS = (
    "Safe_Walkway",
    "Authorized_Intervention",
    "Closed_Panel_Cover",
    "Safe_Carrying",
)


@dataclass(frozen=True)
class DetectionConfig:
    confidence_threshold: float = 0.5
    frame_stride: int = 12
    max_frames: int = 180
    use_ml: bool = False
    yolo_model: str = "yolov8n.pt"
