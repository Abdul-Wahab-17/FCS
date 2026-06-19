from src.detection.detector import DetectionEngine
from pathlib import Path
import pytest
import numpy as np

def test_detector_initialization(rules_path):
    detector = DetectionEngine(rules_path=rules_path)
    assert detector.rules is not None
    assert len(detector.rules) > 0

def test_process_missing_video(rules_path):
    detector = DetectionEngine(rules_path=rules_path)
    with pytest.raises(FileNotFoundError):
        detector.process_video(Path("non_existent_video.mp4"))

def test_clip_safety_check_fallback(rules_path):
    detector = DetectionEngine(rules_path=rules_path)
    # If CLIP isn't available or behavior class is unknown, should return 0.0
    dummy_frame = np.zeros((100, 100, 3), dtype=np.uint8)
    prob = detector._clip_safety_check(dummy_frame, "Unknown_Alien_Activity")
    assert prob == 0.0
