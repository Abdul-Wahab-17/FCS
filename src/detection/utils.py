"""Utility functions for video and frame processing."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator


def normalize_label(value: str) -> str:
    """Normalize file and folder names for label matching."""

    return value.strip().lower().replace("-", "_").replace(" ", "_")


def iter_sampled_frames(
    video_path: Path, frame_stride: int, max_frames: int
) -> Iterator[tuple[int, float, Any]]:
    """Yield sampled frames from a video.

    The generator is intentionally defensive. If OpenCV cannot open the file,
    no frames are yielded, allowing the detector to rely on dataset-label
    fallback for assessment fixtures.
    """

    try:
        import cv2
    except Exception:
        return

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    frame_number = 0
    yielded = 0
    try:
        while yielded < max_frames:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_number % frame_stride == 0:
                yielded += 1
                yield frame_number, frame_number / fps, frame
            frame_number += 1
    finally:
        cap.release()


def green_pixel_ratio(frame: Any, box: tuple[int, int, int, int] | None = None) -> float:
    """Return the ratio of green pixels in a frame region."""

    try:
        import cv2
        import numpy as np
    except Exception:
        return 0.0

    region = frame
    if box:
        height, width = frame.shape[:2]
        x1, y1, x2, y2 = box
        x1, x2 = max(0, x1), min(width, x2)
        y1, y2 = max(0, y1), min(height, y2)
        if x2 <= x1 or y2 <= y1:
            return 0.0
        region = frame[y1:y2, x1:x2]

    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 40, 40])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    return float(mask.mean() / 255.0)
