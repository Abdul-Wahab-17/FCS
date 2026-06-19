# Run Guide: Factory Compliance & Alert Escalation System

This guide outlines step-by-step instructions on how to set up the system, generate sample videos, start the backend/frontend services, and upload a clip to verify compliance and alert routing.

---

## 📋 Prerequisites
Ensure you have the following installed on your system:
- **Python (v3.10 or newer)**
- **Node.js (v18 or newer)**
- **NPM** (comes with Node.js)

---

## 🛠 Step 1: Initialize the Environment & Database

Open a **Command Prompt** (cmd) or **PowerShell** window, navigate to the project directory, and initialize the database.

```cmd
:: 1. Navigate to the project root
cd d:\internshiptask\factory-compliance-system

:: 2. Create a Python virtual environment
python -m venv venv

:: 3. Activate the virtual environment
venv\Scripts\activate

:: 4. Install backend dependencies
pip install -r requirements.txt

:: 5. Initialize the SQLite database
python src/database_init.py
```

---

## 🎥 Step 2: Generate Sample Videos

Because the ML model works with specific safety violation types, we have included a helper script to generate small, valid, lightweight `.mp4` video files for testing.

In the same activated command prompt, run:
```cmd
python generate_samples.py
```

This will create a `samples/` folder containing 4 video clips:
1. `Safe_Walkway_Violation.mp4`
2. `Unauthorized_Intervention.mp4`
3. `Opened_Panel_Cover.mp4`
4. `Carrying_Overload_with_Forklift.mp4`

---

## 🚀 Step 3: Run the Backend API Server

In your first command prompt window, start the backend server:

```cmd
:: Ensure you are in the project root with the venv activated
python src/main.py
```

- **Backend API URL**: `http://localhost:8000`
- **Interactive API Documentation (Swagger)**: `http://localhost:8000/docs`

Keep this window running.

---

## 💻 Step 4: Run the Operations Dashboard

Open a **new, second Command Prompt** window to run the React dashboard:

```cmd
:: 1. Navigate to the dashboard directory
cd d:\internshiptask\factory-compliance-system\src\dashboard

:: 2. Install frontend dependencies
npm install

:: 3. Start the dashboard development server
npm run dev
```

- **Dashboard URL**: `http://localhost:5173`

---

## 📤 Step 5: Upload & Test a Sample Video

1. Open your browser and navigate to the dashboard at **`http://localhost:5173`**.
2. Under the **"Process Clip"** panel on the right side of the **Live Feed Monitor**:
   - Click the **"Choose or drop a video file"** button.
   - Navigate to the **`samples/`** folder inside the project root (`d:\internshiptask\factory-compliance-system\samples`).
   - Select one of the generated videos (e.g., `Safe_Walkway_Violation.mp4` or `Carrying_Overload_with_Forklift.mp4`).
3. Click the **"▶ Run Detection"** button.
4. **Observe the changes**:
   - The file will be uploaded, processed through the pipeline, and categorized based on severity.
   - Real-time alerts will slide down at the top of the page.
   - The interactive stats counter, active timeline logs, and historical archives will refresh dynamically.
