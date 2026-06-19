"""Script to generate small, valid sample MP4 videos for testing the compliance dashboard."""

import os
from pathlib import Path

def generate_video(filename: str, label_text: str):
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("Error: 'opencv-python' and 'numpy' are required to generate sample videos.")
        print("Please run: pip install opencv-python numpy")
        return

    # Define video specs
    width, height = 640, 480
    fps = 24
    duration = 3  # seconds
    total_frames = fps * duration

    # Output directory
    output_dir = Path("samples")
    output_dir.mkdir(exist_ok=True)
    filepath = output_dir / filename

    print(f"Generating {filepath}...")

    # Define codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(filepath), fourcc, fps, (width, height))

    if not out.isOpened():
        print(f"Error: Could not open VideoWriter for {filename}")
        return

    # Draw frames
    for frame_idx in range(total_frames):
        # Create blank dark image
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Draw some background grid to simulate factory
        for y in range(0, height, 40):
            cv2.line(frame, (0, y), (width, y), (20, 20, 20), 1)
        for x in range(0, width, 40):
            cv2.line(frame, (x, 0), (x, height), (20, 20, 20), 1)

        # Draw a simulated "walkway" or camera zone line
        cv2.line(frame, (50, 400), (590, 400), (0, 150, 0), 3) # Green line
        cv2.putText(frame, "GREEN ZONE WALKWAY", (60, 390), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Draw visual elements indicating the behavior
        cv2.putText(frame, f"CAM-01: {label_text}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "TEST VIDEO", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)

        # Draw a moving square/circle simulating a person or machine
        px = 100 + int((frame_idx / total_frames) * 440)
        py = 250 + int(np.sin(frame_idx * 0.2) * 50)
        cv2.circle(frame, (px, py), 25, (0, 0, 255), -1) # Red moving indicator
        cv2.putText(frame, "TARGET", (px - 25, py - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

        # Write frame
        out.write(frame)

    out.release()
    print(f"Successfully created: {filepath} ({filepath.stat().st_size / 1024:.1f} KB)")

if __name__ == "__main__":
    videos = {
        "Safe_Walkway_Violation.mp4": "Safe Walkway Violation",
        "Unauthorized_Intervention.mp4": "Unauthorized Intervention",
        "Opened_Panel_Cover.mp4": "Opened Panel Cover",
        "Carrying_Overload_with_Forklift.mp4": "Carrying Overload with Forklift"
    }

    print("--- GENERATING SAMPLE VIDEOS FOR DASHBOARD ---")
    for filename, label in videos.items():
        generate_video(filename, label)
    print("\nAll done! You can find your sample videos in the './samples' directory.")
