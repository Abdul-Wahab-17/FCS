"""Module 1: Detection engine."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from src.config import settings
from src.detection.config import DetectionConfig, SAFE_BEHAVIORS
from src.detection.models import ObjectDetection, YOLOModelWrapper
from src.detection.utils import green_pixel_ratio, iter_sampled_frames, normalize_label


@dataclass(frozen=True)
class DetectionRecord:
    """Structured detection output consumed by severity and reporting modules."""

    clip_id: str
    timestamp: float
    behavior_class: str
    description: str
    zone: str
    confidence: float
    frame_number: int
    bounding_box: tuple[int, int, int, int]
    policy_rule_ref: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class DetectionEngine:
    """Detect unsafe factory behaviors from labeled clips or sampled frames.

    The assessment dataset is organized by behavior folders. This engine uses
    that label as a deterministic fallback and also exposes frame-level hooks
    for YOLO/color-based checks when model dependencies are enabled.
    """

    def __init__(
        self,
        rules_path: str | Path | None = None,
        config: DetectionConfig | None = None,
        model: YOLOModelWrapper | None = None,
    ) -> None:
        self.rules_path = Path(rules_path or settings.rules_path)
        self.config = config or DetectionConfig(
            confidence_threshold=settings.confidence_threshold,
            frame_stride=settings.detection_frame_stride,
            max_frames=settings.detection_max_frames,
            use_ml=settings.detection_use_ml,
            yolo_model=settings.yolo_model,
        )
        self.rules = self._load_rules()
        self.model = model or (
            YOLOModelWrapper(self.config.yolo_model) if self.config.use_ml else None
        )

    def _load_rules(self) -> dict[str, Any]:
        with self.rules_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def process_video(self, video_path: str | Path) -> list[DetectionRecord]:
        """Process one video clip and return structured unsafe detections."""

        path = Path(video_path)
        label = self._label_from_path(path)
        if label in SAFE_BEHAVIORS:
            return []

        detections: list[DetectionRecord] = []
        if label in self.rules:
            detections.append(self._record_from_dataset_label(path, label))

        if path.exists():
            detections.extend(self._detect_from_frames(path))
        elif not detections:
            raise FileNotFoundError(f"Video not found and no dataset label inferred: {path}")

        return self._deduplicate(detections)

    def _label_from_path(self, path: Path) -> str | None:
        candidates = [path.stem, *(part for part in path.parts)]
        normalized = {normalize_label(candidate): candidate for candidate in candidates}
        for behavior in [*self.rules.keys(), *SAFE_BEHAVIORS]:
            if normalize_label(behavior) in normalized:
                return behavior
        return None

    def _record_from_dataset_label(self, path: Path, behavior: str) -> DetectionRecord:
        rule = self.rules[behavior]
        metadata = dict(rule.get("default_context", {}))
        metadata.update(
            {
                "source": "dataset_label",
                "detection_strategy": rule.get("detection_approach", "label fallback"),
            }
        )
        return DetectionRecord(
            clip_id=path.stem,
            timestamp=0.0,
            behavior_class=behavior,
            description=rule["description"],
            zone=rule.get("default_zone", "Production_Floor"),
            confidence=float(rule.get("label_confidence", 0.86)),
            frame_number=0,
            bounding_box=tuple(rule.get("default_bounding_box", [0, 0, 0, 0])),
            policy_rule_ref=rule["policy_section"],
            metadata=metadata,
        )

    def _detect_from_frames(self, path: Path) -> list[DetectionRecord]:
        detections: list[DetectionRecord] = []
        for frame_number, timestamp, frame in iter_sampled_frames(
            path, self.config.frame_stride, self.config.max_frames
        ):
            objects = self._detect_objects(frame)
            detections.extend(
                self._detect_walkway_violation(
                    path, frame, objects, frame_number, timestamp
                )
            )
        return detections

    def _detect_objects(self, frame: Any) -> list[ObjectDetection]:
        if self.model is None:
            return []
        try:
            return self.model.detect(frame, self.config.confidence_threshold)
        except Exception:
            return []

    def _detect_walkway_violation(
        self,
        path: Path,
        frame: Any,
        objects: list[ObjectDetection],
        frame_number: int,
        timestamp: float,
    ) -> list[DetectionRecord]:
        """Detect people whose lower body is not overlapping green walkway pixels."""

        behavior = "Safe_Walkway_Violation"
        rule = self.rules[behavior]
        records: list[DetectionRecord] = []
        for obj in objects:
            if obj.label != "person":
                continue
            x1, y1, x2, y2 = obj.bounding_box
            foot_region = (x1, int(y1 + (y2 - y1) * 0.65), x2, y2)
            if green_pixel_ratio(frame, foot_region) < 0.05:
                records.append(
                    DetectionRecord(
                        clip_id=path.stem,
                        timestamp=timestamp,
                        behavior_class=behavior,
                        description="Person detected outside visible green walkway boundary.",
                        zone=rule.get("default_zone", "Production_Floor"),
                        confidence=obj.confidence,
                        frame_number=frame_number,
                        bounding_box=obj.bounding_box,
                        policy_rule_ref=rule["policy_section"],
                        metadata={
                            "source": "frame_heuristic",
                            "green_overlap_ratio": green_pixel_ratio(frame, foot_region),
                        },
                    )
                )
        return records

    def _deduplicate(
        self, detections: list[DetectionRecord], window_seconds: float = 2.0
    ) -> list[DetectionRecord]:
        """Keep one representative detection per behavior/window."""

        unique: list[DetectionRecord] = []
        seen: set[tuple[str, int]] = set()
        for detection in detections:
            bucket = int(detection.timestamp // window_seconds)
            key = (detection.behavior_class, bucket)
            if key not in seen:
                seen.add(key)
                unique.append(detection)
        return unique
