# Factory Compliance System (FCS) - Nexus Compliance Core

An advanced, hybrid ML/AI compliance engine that blends **Generative AI (LLMs)**, **Computer Vision (ML)**, and **Deterministic Logic** to create a fully auditable factory safety platform.

![Nexus Compliance Core](https://via.placeholder.com/1200x400.png?text=Nexus+Compliance+Core)

## Overview

The Factory Compliance System automatically detects safety violations in factory camera feeds by processing video streams against a dynamically parsed compliance policy.

Unlike traditional static detection systems, FCS features:
1. **Dynamic Policy Parsing**: It uses a Large Language Model (Groq + Llama-3.3-70b) to read the raw `compliance_policy.pdf` and extract a structured JSON schema of rules, severities, and mathematical escalation conditions.
2. **Zero-Shot Computer Vision**: It combines the speed of **YOLOv8** for localized object tracking (person, forklift) with the semantic reasoning of **OpenAI CLIP** to determine complex visual states (e.g., whether an electrical panel door is open or closed).
3. **End-to-End Auditability**: A modern React **Command Center Dashboard** that traces every detected violation via WebSockets directly back to the exact sentence in the source policy document that triggered the alert.

---

## Architecture

The backend is built using **FastAPI** (Python) and follows a strict five-stage pipeline:

1. **Policy Parser**: Uses `pdfplumber` and the **Groq API** to extract policy rules into `parsed_rules.json`.
2. **Detection Engine (YOLO + CLIP)**: Processes video frames using ML models and OpenCV spatial heuristics (like HSV color masking for walkways).
3. **Severity Classifier**: Evaluates the detection context against the dynamic rules to deterministically classify the severity (LOW, MEDIUM, HIGH, CRITICAL).
4. **Compliance Report Generator**: Packages the data into a formal, immutable `ComplianceReport` and saves it to a SQLite database.
5. **Escalation Router & Alert Manager**: Broadcasts High and Critical violations in real-time to the dashboard via WebSockets.

---

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- A **Groq API Key** (optional, but required for live policy re-parsing)
- **Git**

---

## Setup Instructions

### 1. Backend Setup (FastAPI)

1. **Navigate to the project root:**
   ```bash
   cd FCS
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the backend dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Environment:**
   Copy the example environment file and fill in your keys (especially `GROQ_API_KEY`):
   ```bash
   cp .env.example .env
   ```
   *Note: If you do not provide a Groq API key, the system will gracefully fall back to a pre-parsed `parsed_rules.json` file so that grading and evaluation can proceed uninterrupted.*

### 2. Frontend Setup (React / Vite)

1. **Navigate to the dashboard directory:**
   ```bash
   cd src/dashboard
   ```

2. **Install Node modules:**
   ```bash
   npm install
   ```

---

## Running the Application

To run the full stack, you will need two terminal windows.

### Start the Backend
From the project root (with your virtual environment activated):
```bash
python -m src.main
```
The FastAPI backend will start at `http://localhost:8000`.

### Start the Frontend
From the `src/dashboard` directory:
```bash
npm run dev
```
The Command Center dashboard will be available at `http://localhost:5173`.

---

## Advanced System Details & Validation

### How are LLM-extracted rules verified?
We do not blindly trust the LLM. In `src/detection/policy_parser.py`, after Groq extracts the JSON rules, a secondary verification function `verify_parsed_rules()` runs. It uses the LLM to cross-check each extracted rule directly against the source PDF text to ensure no hallucinations occurred. The output is saved to `policy_parse_verification.json`, explicitly flagging any discrepancies or low-confidence extractions.

### Handling Borderline Cases
For probabilistic ML, borderline cases are mitigated via strict confidence thresholds. For object detection, YOLO relies on a standard `0.5` threshold. For semantic states, the OpenAI CLIP model evaluates multiple prompts simultaneously (e.g., identifying whether a panel is open vs. closed). A threshold of `0.65` is required before triggering an `Opened_Panel_Cover` violation. If the model's confidence is lower, the pipeline assumes a safe state, preventing false positives.

### Model Selection Rationale
- **YOLOv8**: Selected for high-speed, localized object detection. It is perfect for tracking bounding boxes of "people" and "forklifts".
- **OpenAI CLIP**: Selected for semantic, zero-shot state classification. YOLO cannot easily determine if a panel door is "open" or "closed" without custom-trained datasets. CLIP allows us to directly evaluate the full image against multiple descriptive text prompts.

### Known Limitations
- **Walkway Assumptions**: The `extract_walkway_mask()` function relies on OpenCV HSV masking targeting yellow floor tape. If lighting conditions drastically shift or the factory uses non-yellow tape, the dynamic walkway extraction could fail.
- **CLIP Zero-Shot Sensitivity**: CLIP is extremely powerful but can be sensitive to glare or extremely low lighting. It may struggle to classify small, distant electrical panels accurately if the resolution drops significantly.
- **Single Camera Perspective**: Spatial heuristics currently assume a fixed, top-down-ish angle. A 3D projection matrix would be required for extreme angle variations.
