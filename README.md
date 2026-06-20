# Factory Compliance System (FCS)

An advanced, hybrid compliance engine that combines computer vision, machine learning, and deterministic logic to create a fully auditable factory safety platform.

![Factory Compliance System](https://via.placeholder.com/1200x400.png?text=Factory+Compliance+System)

## Overview

The Factory Compliance System watches video feeds from factory cameras, automatically spotting unsafe behaviors and equipment use. It matches what it sees against a set of safety rules derived from the compliance policy, then classifies each finding by severity and streams alerts to a live dashboard for immediate action.

---

## Architecture

The backend is built using **FastAPI** (Python) and follows a strict five‑stage pipeline:
1. **Policy Parser** – Uses `pdfplumber` and the **Groq API** to extract policy rules into `parsed_rules.json`.
2. **Detection Engine (YOLO + CLIP)** – Processes video frames using ML models and OpenCV spatial heuristics (like HSV color masking for walkways).
3. **Severity Classifier** – Evaluates the detection context against the dynamic rules to deterministically classify the severity (LOW, MEDIUM, HIGH, CRITICAL).
4. **Compliance Report Generator** – Packages the data into a formal, immutable `ComplianceReport` and saves it to a SQLite database.
5. **Escalation Router & Alert Manager** – Broadcasts High and Critical violations in real‑time to the dashboard via WebSockets.

The frontend is a React (Vite) application providing three main views: Live Feed Monitor, Alert Timeline, and Stats/History tabs. The Stats tab now consolidates per‑video detections, showing each behavior class only once with the highest confidence.

---

## Workflows

- **YOLO Detection**: `YOLOv8` identifies objects such as people, forklifts, and safety gear, returning confidence scores that are visualized on the dashboard.
- **CLIP Reasoning**: OpenAI CLIP analyzes the visual context to infer higher‑level states (e.g., “safe walkway”, “hazardous zone”) and augments the detection results.
- **Policy Parsing**: The system parses the compliance policy PDF into structured JSON rules used by the Severity Classifier.
- **Severity Classification**: Combines detections with parsed rules to assign LOW‑MEDIUM‑HIGH‑CRITICAL levels.
- **Report Generation & Storage**: Generates a `ComplianceReport` stored in SQLite.
- **Escalation & Alert Routing**: High/Critical alerts are pushed via WebSockets to the dashboard.

## Detailed Explanation

**Architecture Diagram**

```
Factory Video
      │
      ▼
Video Reader
(OpenCV)
      │
      ▼
Object Detection
(YOLO)
      │
      ▼
Violation Detection Engine
      │
      ▼
Severity Classification
      │
      ▼
Escalation Engine
      │
      ├────────► Alert Generation
      │
      ▼
Report Generator
(JSON)
      │
      ▼
SQLite Database
(compliance.db)
      │
      ▼
React Dashboard
```


**Video Ingestion**
- Factory cameras record HD video files stored under a `videos/` folder. The backend reads each file sequentially or can attach to a live stream.

**Policy Parsing**
- The compliance policy PDF is processed by a Groq‑hosted LLM which extracts rules, severity levels, and escalation formulas into a JSON file (`parsed_rules.json`). This file drives the rest of the pipeline.

**Detection Engine**
- `YOLOv8` scans each frame for objects such as people, forklifts, and safety equipment, outputting confidence scores.
- `CLIP` examines the surrounding visual context to infer higher‑level states (e.g., “safe walkway”).
- The engine combines these signals to produce a list of potential violations.

**Severity Classification**
- Each detection is matched against the parsed rules. The system computes a severity tier (LOW, MEDIUM, HIGH, CRITICAL) using deterministic logic.

**Compliance Report Generation**
- Findings are wrapped in a `ComplianceReport` model and persisted to a SQLite database (`violations.db`).

**Escalation & Real‑Time Alerts**
- High and Critical alerts are routed through a WebSocket server to the React dashboard.
- The dashboard flashes a red banner for Critical alerts and an amber banner for High alerts.

**Dashboard Views**
- **Live Feed Monitor** – Shows the video with detection overlays.
- **Alert Timeline** – Chronological list of incidents with deduplication (each behavior appears only once per video).
- **Stats/History** – Summarizes detection counts per severity and per video.

This pipeline runs end‑to‑end automatically once the backend service is started.

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- A **Groq API Key** (optional – the system falls back to a pre‑parsed `parsed_rules.json` if omitted)
- **Git**

---

## Setup & Run Guide

### Backend (FastAPI)
```bash
# Navigate to project root
cd FCS
# Create and activate virtual environment (Windows)
python -m venv venv
venv\\Scripts\\activate
# Install dependencies
pip install -r requirements.txt
# Configure environment (copy example and set your keys)
cp .env.example .env
# Start the server
python -m src.main
```
The API will be available at `http://localhost:8000`.

### Frontend (React / Vite)
```bash
# From the dashboard directory
cd src/dashboard
# Install node modules
npm install
# Run dev server
npm run dev
```
Open `http://localhost:5173` in a browser to see the Command Center.

### Standalone Scripts
- **`scripts/seed_demo.py`** – Generates synthetic video‑level reports for quick UI testing.
- **`scripts/run_policy_parser.py`** – Manually invoke the policy parsing step and output `parsed_rules.json`.
- **`scripts/export_reports.py`** – Exports all stored compliance reports to a single JSON or CSV file.

Run any script with:
```bash
python scripts/<script_name>.py
```
These utilities do not require the full server to be running.

---

## Known Limitations & Caveats
- **Walkway Assumptions** – `extract_walkway_mask()` relies on HSV masking of yellow floor tape. Different tape colors or lighting conditions may cause failures.
- **CLIP Sensitivity** – Zero‑shot classification can be impacted by glare or low‑light; confidence thresholds are tuned to mitigate false positives.
- **Single Camera Perspective** – Current heuristics assume a fixed top‑down angle. Extreme angles would need a calibrated 3D projection.
- **Model Dependencies** – YOLOv8 provides fast object detection but requires a GPU for optimal performance. CLIP runs on CPU if no GPU is available, which may increase latency.
- **Policy Parsing** – The Groq LLM is used for initial rule extraction; a secondary verification step cross‑checks each rule against the PDF to avoid hallucinations.

---

## Database Initialization

A convenient script is provided to reset the SQLite database:
```bash
# From the project root
python scripts/init_db.py
```
This will delete any existing `violations.db` file and create a fresh schema.

--- 