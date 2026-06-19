"""Generate sample MP4 clips under data/test/<behavior_class>/ for local pipeline testing."""

from pathlib import Path


def generate_video(filepath: Path, label_text: str) -> None:
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("Error: opencv-python and numpy are required.")
        print("Run: pip install opencv-python numpy")
        return

    width, height = 640, 480
    fps = 24
    duration = 3
    total_frames = fps * duration

    filepath.parent.mkdir(parents=True, exist_ok=True)
    print(f"Generating {filepath}...")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(filepath), fourcc, fps, (width, height))

    if not out.isOpened():
        print(f"Error: Could not open VideoWriter for {filepath}")
        return

    for frame_idx in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        for y in range(0, height, 40):
            cv2.line(frame, (0, y), (width, y), (20, 20, 20), 1)
        for x in range(0, width, 40):
            cv2.line(frame, (x, 0), (x, height), (20, 20, 20), 1)

        # Yellow walkway tape (matches detector HSV masking)
        cv2.rectangle(frame, (40, 350), (600, 430), (0, 220, 255), -1)
        cv2.putText(
            frame,
            "YELLOW WALKWAY",
            (50, 390),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 0, 0),
            1,
        )

        cv2.putText(
            frame,
            f"CAM-01: {label_text}",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        px = 100 + int((frame_idx / total_frames) * 440)
        py = 250 + int(np.sin(frame_idx * 0.2) * 50)
        cv2.rectangle(frame, (px - 20, py - 50), (px + 20, py + 10), (255, 180, 0), -1)
        cv2.putText(frame, "PERSON", (px - 30, py - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        out.write(frame)

    out.release()
    print(f"Created: {filepath} ({filepath.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    samples = {
        "data/test/Safe_Walkway_Violation/demo_walkway.mp4": "Safe Walkway Violation",
        "data/test/Unauthorized_Intervention/demo_intervention.mp4": "Unauthorized Intervention",
        "data/test/Opened_Panel_Cover/demo_panel.mp4": "Opened Panel Cover",
        "data/test/Carrying_Overload_with_Forklift/demo_overload.mp4": "Carrying Overload with Forklift",
    }

    print("--- GENERATING SAMPLE VIDEOS ---")
    for rel_path, label in samples.items():
        generate_video(Path(rel_path), label)
    print("\nDone. Default scan path: data/test/Carrying_Overload_with_Forklift/demo_overload.mp4")
