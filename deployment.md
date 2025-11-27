# Deployment Guide - Intelligent Speech Dictation Engine

## Prerequisites
- **OS**: Windows (preferred), Linux, or macOS.
- **Python**: Version 3.8 or higher.
- **Node.js**: Version 16 or higher.
- **Hardware**: CPU supported, GPU recommended.

## Tech Stack
- **Backend**: Python (FastAPI, Faster-Whisper, HappyTransformer)
- **Frontend**: React + **Vite**

## Installation & Startup

### Option 1: Automated Script (Windows)
Run the provided PowerShell script to install dependencies and start both servers (Vite + FastAPI).
```powershell
.\start_app.ps1
```

### Option 2: Manual Startup

#### 1. Backend (FastAPI)
```bash
cd c:/dev/python/speech_dictation_engine
pip install -r requirements.txt
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```
*Wait for "Application startup complete" before using the app.*

#### 2. Frontend (Vite)
```bash
cd frontend
npm install
npm run dev
```
*Access the app at the URL shown (usually http://localhost:5173).*

## Production Build (Vite)
To build the frontend for production:
```bash
cd frontend
npm run build
npm run preview
```

## Troubleshooting
- **"It ain't online"**:
    -   Ensure both terminal windows are open and running.
    -   Check for errors in the Backend terminal (e.g., model loading failures).
    -   Ensure port 8000 (Backend) and 5173 (Frontend) are not in use.
-   **Model Loading**: The first run will download models (`tiny.en`, `t5-base`). This may take a few minutes.
