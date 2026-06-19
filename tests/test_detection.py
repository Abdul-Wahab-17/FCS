from src.detection.detector import DetectionEngine


def test_detector_uses_dataset_label_fallback(labeled_video, rules_path):
    detector = DetectionEngine(rules_path=rules_path)

    detections = detector.process_video(labeled_video)

    assert len(detections) == 1
    assert detections[0].behavior_class == "Carrying_Overload_with_Forklift"
    assert detections[0].policy_rule_ref == "Section 6.3.2"
    assert detections[0].metadata["source"] == "dataset_label"


def test_detector_returns_no_violations_for_safe_folder(tmp_path, rules_path):
    path = tmp_path / "data" / "test" / "Safe_Walkway"
    path.mkdir(parents=True)
    video = path / "safe_clip.mp4"
    detector = DetectionEngine(rules_path=rules_path)

    assert detector.process_video(video) == []
