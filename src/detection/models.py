"""Optional computer-vision model wrappers.

The project can run without downloading YOLO weights. When DETECTION_USE_ML=True,
this wrapper lazily imports ultralytics and performs COCO detections.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ObjectDetection:
    label: str
    confidence: float
    bounding_box: tuple[int, int, int, int]


class ModelUnavailable(RuntimeError):
    """Raised when an optional ML dependency cannot be loaded."""


class YOLOModelWrapper:
    """Small adapter around ultralytics.YOLO."""

    COCO_LABELS = {
        0: "person",
        2: "car",
        5: "bus",
        7: "truck",
        9: "traffic light",
        26: "handbag",
        28: "suitcase",
        39: "bottle",
        56: "chair",
        63: "laptop",
        73: "book",
    }

    def __init__(self, model_name: str = "yolov8n.pt") -> None:
        self.model_name = model_name
        self._model: Any | None = None

    def _load(self) -> Any:
        if self._model is not None:
            return self._model
        try:
            from ultralytics import YOLO
        except Exception as exc:  # pragma: no cover - depends on local install
            raise ModelUnavailable(
                "ultralytics is not available. Install requirements or set "
                "DETECTION_USE_ML=False."
            ) from exc
        self._model = YOLO(self.model_name)
        return self._model

    def detect(self, frame: Any, confidence_threshold: float) -> list[ObjectDetection]:
        """Run object detection and normalize results."""

        model = self._load()
        results = model(frame, conf=confidence_threshold, verbose=False)
        if not results:
            return []

        detections: list[ObjectDetection] = []
        boxes = getattr(results[0], "boxes", [])
        for box in boxes:
            cls_id = int(box.cls[0])
            label = self.COCO_LABELS.get(cls_id, str(cls_id))
            conf = float(box.conf[0])
            x1, y1, x2, y2 = (int(v) for v in box.xyxy[0])
            detections.append(
                ObjectDetection(
                    label=label,
                    confidence=conf,
                    bounding_box=(x1, y1, x2, y2),
                )
            )
        return detections
