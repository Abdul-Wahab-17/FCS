# Known Limitations & Trade-offs

## Detection Accuracy

This repository is an end-to-end functional MVP, not a finished production CV model.

### Safe Walkway Violation

- Works best when green floor markings are visible and the person detector succeeds.
- Struggles with worn markings, occlusions, and unusual camera angles.
- Future work: segment walkway regions and fine-tune person detection on factory footage.

### Unauthorized Intervention

- Current implementation relies on dataset-label fallback unless a custom vest/equipment model is added.
- Production detection needs vest color classification and hand-equipment proximity estimation.
- Future work: train a vest classifier and add pose tracking.

### Opened Panel Cover

- Current implementation does not include a trained open/closed panel classifier.
- Production detection needs panel localization and state classification.
- Future work: label panel states and train a small classifier or YOLO head.

### Forklift Overload

- Current implementation can route and classify overload clips by folder label.
- Production detection needs forklift localization and block counting.
- Future work: train a custom detector on forklift and block annotations.

## System Constraints

- SQLite is appropriate for a local assessment and small facilities, not high-volume multi-camera deployments.
- WebSocket alerts are in-memory. Restarting the backend clears connected clients and recent alert cache.
- The dashboard has no authentication or user roles.
- There is no background job queue; processing runs in the API request lifecycle.

## Honest Scope

The project demonstrates module integration, policy-to-code translation, persistence, API behavior, real-time alert routing, and dashboard UX. It does not claim production-grade computer-vision accuracy without model training.
