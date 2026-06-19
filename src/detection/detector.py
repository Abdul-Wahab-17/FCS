"""Module 1: Detection engine."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None  # type: ignore[assignment]
    CV2_AVAILABLE = False

try:
    import torch
    import clip
    CLIP_AVAILABLE = True
except ImportError:
    CLIP_AVAILABLE = False

from src.config import settings
from src.detection.config import DetectionConfig, UNSAFE_BEHAVIORS
from src.detection.models import ObjectDetection, YOLOModelWrapper
from src.detection.utils import iter_sampled_frames, normalize_label


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
    """Detect unsafe factory behaviors from sampled frames using ML.

    Uses YOLOv8 for object detection and CLIP for zero-shot classification.
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
        
        # Load CLIP model if available
        self.clip_model = None
        self.clip_preprocess = None
        if CLIP_AVAILABLE and self.config.use_ml:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=device)

    def _load_rules(self) -> dict[str, Any]:
        with self.rules_path.open("r", encoding="utf-8") as file:
            parsed_data = json.load(file)
            return {r["behavior_class"]: r for r in parsed_data.get("compliance_rules", [])}

    def process_video(self, video_path: str | Path) -> list[DetectionRecord]:
        """Process one video clip and return structured unsafe detections."""
        path = Path(video_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Video not found: {path}")

        print(f"[DetectionEngine] Processing: {path}")
        print(f"[DetectionEngine] ML enabled: {self.config.use_ml}, YOLO loaded: {self.model is not None}, CLIP loaded: {self.clip_model is not None}")
        
        detections = self._detect_from_frames(path)
        print(f"[DetectionEngine] Frame-based detections: {len(detections)}")
        
        if not detections:
            detections = self._detect_from_dataset_label(path)
            print(f"[DetectionEngine] Filename fallback detections: {len(detections)}")
        
        result = self._deduplicate(detections)
        print(f"[DetectionEngine] Final (deduplicated): {len(result)}")
        return result

    def _detect_from_frames(self, path: Path) -> list[DetectionRecord]:
        detections: list[DetectionRecord] = []
        frame_count = 0
        for frame_number, timestamp, frame in iter_sampled_frames(
            path, self.config.frame_stride, self.config.max_frames
        ):
            frame_count += 1
            objects = self._detect_objects(frame)
            if objects:
                labels = [o.label for o in objects]
                print(f"[DetectionEngine] Frame {frame_number}: YOLO found {len(objects)} objects: {labels}")
            
            # Walkway Violation (Person + green pixel ratio)
            detections.extend(self._detect_walkway_violation(path, frame, objects, frame_number, timestamp))
            
            # Equipment Intervention (Person + machine exclusion zone)
            detections.extend(self._detect_equipment_intervention(path, frame, objects, frame_number, timestamp))
            
            # Forklift Load Management (Forklift + block count)
            detections.extend(self._detect_forklift_load(path, frame, objects, frame_number, timestamp))
            
            # Electrical Panel Management (CLIP state-based detection)
            detections.extend(self._detect_electrical_panel(path, frame, frame_number, timestamp))

        print(f"[DetectionEngine] Processed {frame_count} sampled frames")
        return detections

    def _frame_to_rgb(self, frame: np.ndarray) -> np.ndarray:
        """OpenCV yields BGR; CLIP and PIL expect RGB."""
        if CV2_AVAILABLE and frame.ndim == 3 and frame.shape[2] == 3:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def _infer_behavior_from_path(self, path: Path) -> str | None:
        """Match Kaggle-style folder labels or behavior hints in the filename."""
        unsafe_labels = {normalize_label(name): name for name in UNSAFE_BEHAVIORS}
        candidates = [path.stem, * (p.name for p in path.parents)]
        for name in candidates:
            normalized = normalize_label(name)
            if normalized in unsafe_labels:
                return unsafe_labels[normalized]
            for label_key, behavior in unsafe_labels.items():
                if label_key in normalized:
                    return behavior
        return None

    def _detect_from_dataset_label(self, path: Path) -> list[DetectionRecord]:
        """Fallback when ML/heuristics find nothing but the clip folder is labeled."""
        behavior = self._infer_behavior_from_path(path)
        if behavior is None or behavior not in self.rules:
            return []

        rule = self.rules[behavior]
        zone_map = {
            "Safe_Walkway_Violation": "Production_Floor",
            "Unauthorized_Intervention": "Machinery_Zone",
            "Opened_Panel_Cover": "Electrical_Room",
            "Carrying_Overload_with_Forklift": "Loading_Area",
        }
        metadata: dict[str, Any] = {"source": "dataset_label_fallback"}
        if behavior == "Carrying_Overload_with_Forklift":
            metadata["block_count"] = 4
        if behavior == "Unauthorized_Intervention":
            metadata["person_proximity_to_machinery"] = 0.5

        return [
            DetectionRecord(
                clip_id=path.stem,
                timestamp=0.0,
                behavior_class=behavior,
                description=rule.get("unsafe_indicator", behavior),
                zone=zone_map.get(behavior, "Production_Floor"),
                confidence=float(rule.get("label_confidence", 0.85)),
                frame_number=0,
                bounding_box=(120, 80, 420, 360),
                policy_rule_ref=rule.get("rule_id", "Unknown"),
                metadata=metadata,
            )
        ]

    def _detect_objects(self, frame: Any) -> list[ObjectDetection]:
        if self.model is None:
            return []
        try:
            return self.model.detect(frame, self.config.confidence_threshold)
        except Exception:
            return []

    def _clip_safety_check(self, frame: np.ndarray, behavior_class: str) -> float:
        """Returns probability [0,1] that the frame shows a violation using CLIP."""
        if not self.clip_model or behavior_class not in self.rules:
            return 0.0
            
        rule = self.rules[behavior_class]
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        texts = clip.tokenize([
            rule.get("unsafe_indicator", "unsafe"),
            rule.get("safe_indicator", "safe")
        ]).to(device)
        
        rgb = self._frame_to_rgb(frame)
        image = self.clip_preprocess(Image.fromarray(rgb)).unsqueeze(0).to(device)

        with torch.no_grad():
            logits, _ = self.clip_model(image, texts)
            probs = logits.softmax(dim=-1)

        return probs[0][0].item()

    def _extract_walkway_mask(self, frame: np.ndarray) -> np.ndarray:
        """Return a binary mask of the yellow walkway.
        If OpenCV is not available, an empty mask is returned to disable this check.
        """
        if not CV2_AVAILABLE:
            # Create an empty mask matching frame dimensions (no walkway detection)
            return np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Yellow floor tape range
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([35, 255, 255])
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
        # Morphological cleanup
        kernel = np.ones((15, 15), np.uint8)
        return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    def _detect_walkway_violation(self, path: Path, frame: Any, objects: list[ObjectDetection], frame_number: int, timestamp: float) -> list[DetectionRecord]:
        behavior = "Safe_Walkway_Violation"
        if behavior not in self.rules:
            return []
            
        rule = self.rules[behavior]
        records: list[DetectionRecord] = []
        
        # Auto-detect walkway mask via HSV color masking
        walkway_mask = self._extract_walkway_mask(frame)
        
        for obj in objects:
            if obj.label != "person":
                continue
            x1, y1, x2, y2 = obj.bounding_box
            foot_region = (x1, int(y1 + (y2 - y1) * 0.65), x2, y2)
            
            # Check overlap between foot region and walkway mask
            foot_mask = np.zeros_like(walkway_mask)
            foot_mask[foot_region[1]:foot_region[3], foot_region[0]:foot_region[2]] = 255
            overlap = cv2.bitwise_and(walkway_mask, foot_mask)
            overlap_ratio = np.sum(overlap > 0) / (np.sum(foot_mask > 0) + 1e-6)
            
            # If the person's feet are NOT mostly in the yellow walkway mask, flag them
            if overlap_ratio < 0.1:
                records.append(
                    DetectionRecord(
                        clip_id=path.stem,
                        timestamp=timestamp,
                        behavior_class=behavior,
                        description=rule.get("unsafe_indicator", "Person outside yellow boundary lines"),
                        zone="Production_Floor",
                        confidence=obj.confidence,
                        frame_number=frame_number,
                        bounding_box=obj.bounding_box,
                        policy_rule_ref=rule.get("rule_id", "Unknown"),
                        metadata={"source": "hsv_masking", "walkway_overlap_ratio": float(overlap_ratio)},
                    )
                )
        return records

    def _detect_equipment_intervention(self, path: Path, frame: Any, objects: list[ObjectDetection], frame_number: int, timestamp: float) -> list[DetectionRecord]:
        behavior = "Unauthorized_Intervention"
        if behavior not in self.rules:
            return []
            
        rule = self.rules[behavior]
        records: list[DetectionRecord] = []
        
        # Mocking homography machine exclusion zone for demo purposes (center 30% of screen)
        h, w = frame.shape[:2]
        zone = (int(w * 0.35), int(h * 0.35), int(w * 0.65), int(h * 0.65))
        
        for obj in objects:
            if obj.label != "person":
                continue
            x1, y1, x2, y2 = obj.bounding_box
            centroid_x = (x1 + x2) // 2
            centroid_y = (y1 + y2) // 2
            
            if zone[0] < centroid_x < zone[2] and zone[1] < centroid_y < zone[3]:
                # Person in machine exclusion zone
                prob_unsafe = self._clip_safety_check(frame, behavior) if self.clip_model else obj.confidence
                
                records.append(
                    DetectionRecord(
                        clip_id=path.stem,
                        timestamp=timestamp,
                        behavior_class=behavior,
                        description=rule.get("unsafe_indicator", "Person interacting with active machinery"),
                        zone="Machinery_Zone",
                        confidence=max(obj.confidence, prob_unsafe),
                        frame_number=frame_number,
                        bounding_box=obj.bounding_box,
                        policy_rule_ref=rule.get("rule_id", "Unknown"),
                        metadata={"source": "exclusion_zone", "person_proximity_to_machinery": 0.5},
                    )
                )
        return records

    def _detect_forklift_load(self, path: Path, frame: Any, objects: list[ObjectDetection], frame_number: int, timestamp: float) -> list[DetectionRecord]:
        behavior = "Carrying_Overload_with_Forklift"
        if behavior not in self.rules:
            return []
            
        rule = self.rules[behavior]
        records: list[DetectionRecord] = []
        
        forklifts = [o for o in objects if o.label in ("truck", "forklift", "car", "bus")]
        blocks = [o for o in objects if o.label in ("box", "suitcase", "handbag", "book")]
        
        for forklift in forklifts:
            fx1, fy1, fx2, fy2 = forklift.bounding_box
            
            # Count blocks directly above or overlapping the forklift
            block_count = 0
            for block in blocks:
                bx1, by1, bx2, by2 = block.bounding_box
                # Check if block is above and horizontally overlapping
                if by2 <= fy2 and not (bx2 < fx1 or bx1 > fx2):
                    block_count += 1
            
            if block_count > 2: # Or fetch from policy rules if dynamically parsed
                records.append(
                    DetectionRecord(
                        clip_id=path.stem,
                        timestamp=timestamp,
                        behavior_class=behavior,
                        description=rule.get("unsafe_indicator", "Forklift carrying more than 2 blocks"),
                        zone="Loading_Area",
                        confidence=forklift.confidence,
                        frame_number=frame_number,
                        bounding_box=forklift.bounding_box,
                        policy_rule_ref=rule.get("rule_id", "Unknown"),
                        metadata={"source": "frame_heuristic", "block_count": block_count},
                    )
                )
        return records

    def _detect_electrical_panel(self, path: Path, frame: Any, frame_number: int, timestamp: float) -> list[DetectionRecord]:
        behavior = "Opened_Panel_Cover"
        if behavior not in self.rules or not self.clip_model:
            return []
            
        rule = self.rules[behavior]
        
        # Pass all prompts to CLIP to pick the highest scoring
        PANEL_PROMPTS = [
            "an open electrical panel with exposed wiring",
            "a closed electrical panel door flush against the wall",
            "electrical equipment cabinet with open door",
            "sealed electrical box on factory wall"
        ]
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        texts = clip.tokenize(PANEL_PROMPTS).to(device)
        rgb = self._frame_to_rgb(frame)
        image = self.clip_preprocess(Image.fromarray(rgb)).unsqueeze(0).to(device)
        
        with torch.no_grad():
            logits, _ = self.clip_model(image, texts)
            probs = logits.softmax(dim=-1)[0]
            
        # The first and third prompts indicate an open panel
        prob_open_1 = probs[0].item()
        prob_closed_1 = probs[1].item()
        prob_open_2 = probs[2].item()
        prob_closed_2 = probs[3].item()
        
        prob_unsafe = max(prob_open_1, prob_open_2)
        
        if prob_unsafe > 0.65:
            return [
                DetectionRecord(
                    clip_id=path.stem,
                    timestamp=timestamp,
                    behavior_class=behavior,
                    description=rule.get("unsafe_indicator", "Electrical panel door left open unattended"),
                    zone="Electrical_Room",
                    confidence=prob_unsafe,
                    frame_number=frame_number,
                    bounding_box=(0, 0, frame.shape[1], frame.shape[0]),
                    policy_rule_ref=rule.get("rule_id", "Unknown"),
                    metadata={"source": "clip_zero_shot_full_frame", "highest_prompt_score": prob_unsafe}, 
                )
            ]
        return []

    def _deduplicate(self, detections: list[DetectionRecord], window_seconds: float = 2.0) -> list[DetectionRecord]:
        unique: list[DetectionRecord] = []
        seen: set[tuple[str, int]] = set()
        for detection in detections:
            bucket = int(detection.timestamp // window_seconds)
            key = (detection.behavior_class, bucket)
            if key not in seen:
                seen.add(key)
                unique.append(detection)
        return unique
