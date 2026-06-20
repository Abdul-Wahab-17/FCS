# Factory Compliance System (FCS)

An advanced, hybrid compliance engine that combines computer vision, machine learning, and deterministic logic to create a fully auditable factory safety platform.

![Factory Compliance System](https://via.placeholder.com/1200x400.png?text=Factory+Compliance+System)

## Overview

The Factory Compliance System automatically detects safety violations in factory camera feeds by processing video streams against a dynamically parsed compliance policy.

Unlike traditional static detection systems, FCS features:
1. **Dynamic Policy Parsing**: It uses a Large Language Model (Groq + Llama-3.3-70b) to read the raw `compliance_policy.pdf` and extract a structured JSON schema of rules, severities, and mathematical escalation conditions.
2. **Zero-Shot Computer Vision**: It combines the speed of **YOLOv8** for localized object tracking (person, forklift) with the semantic reasoning of **OpenAI CLIP** to determine complex visual states (e.g., whether an electrical panel door is "open" or "closed").
3. **End-to-End Auditability**: A modern React **Command Center Dashboard** that traces every detected violation via WebSockets directly back to the exact sentence in the source policy document that triggered the alert.

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

- **Video Source**: Factory cameras provide continuous HD video streams stored in a `videos/` directory. The system processes each file sequentially or via live stream.
- **YOLO Detection**: `YOLOv8` detects objects (people, forklifts, safety gear) and provides bounding boxes with confidence scores.
- **CLIP Reasoning**: OpenAI CLIP evaluates the visual context to infer states (e.g., “safe walkway”, “hazardous zone”) beyond bounding boxes.
- **Groq Policy Parsing**: The Groq LLM parses the compliance policy PDF into structured JSON rules used by the Severity Classifier.
- **Severity Classification**: Combines detections with parsed rules to assign LOW‑MEDIUM‑HIGH‑CRITICAL levels.
- **Report Generation & Storage**: Generates a `ComplianceReport` stored in SQLite.
- **Escalation & Alert Routing**: High/Critical alerts are pushed via WebSockets to the dashboard.

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