# Detection Model Rationale

YOLOv8 is a reasonable default for real-time factory monitoring because it has strong person detection, a mature Python API, and good CPU/GPU deployment options.

For this assessment, the repository does not include trained weights for custom classes such as panel covers, vests, blocks, or forklifts. The code keeps YOLO optional through `DETECTION_USE_ML=True` and uses dataset-label fallback by default.

## With More Time

- Fine-tune YOLO on the Kaggle behavior clips.
- Add custom labels for panels, forklifts, blocks, vest colors, and walkways.
- Measure precision, recall, and latency per behavior class.
- Store model version in every compliance record.
