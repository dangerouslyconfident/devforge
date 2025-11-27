# FluxDictate 🎙️

**FluxDictate** is a high-performance, offline, intelligent speech-to-text engine designed for real-time dictation and batch processing. It features a premium "Apple Liquid Glass" UI, a dedicated low-latency live model, and advanced hallucination filtering.

![FluxDictate UI](https://via.placeholder.com/800x450.png?text=FluxDictate+UI+Preview)

## ✨ Features

*   **⚡ Real-Time Live Dictation**: Powered by a dedicated `base.en` Whisper model and a tuned VAD (Voice Activity Detection) system for sub-1.5s latency.
*   **🎬 Scene Batch Mode**: Record complex scenes or thoughts and let the engine apply **Grammar Correction** and **Style Transfer** (Neutral, Formal, Casual, Concise).
*   **🍎 Liquid Glass UI**: A stunning, modern interface with deep blur, swirly animated gradients, and a "Dynamic Island" control bar.
*   **🛡️ Hallucination Defense**: Aggressive Regex filtering and VAD tuning to eliminate common Whisper hallucinations (e.g., "Transcript of an Indian English speaker").
*   **📊 Real-Time Visualizer**: Terminal-style frequency bars that react instantly to your voice.
*   **🔒 Fully Offline**: Runs entirely on your local machine using `faster-whisper`. No data leaves your device.

## 🛠️ Tech Stack

*   **Backend**: Python, FastAPI, Faster-Whisper, NumPy, WebSockets.
*   **Frontend**: React, Vite, Web Audio API, Canvas.

## 🚀 Installation

### Prerequisites
*   **Python 3.8+**
*   **Node.js 16+**
*   **FFmpeg** (Must be installed and added to your system PATH)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/flux-dictate.git
cd flux-dictate
```

### 2. Backend Setup
Navigate to the root directory and install Python dependencies.

```bash
# Create a virtual environment (Optional but recommended)
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install fastapi "uvicorn[standard]" faster-whisper numpy websockets python-multipart
```

### 3. Frontend Setup
Navigate to the frontend directory and install Node dependencies.

```bash
cd frontend
npm install
```

## 🏃‍♂️ Running the App

You can run the backend and frontend separately, or use the provided startup script (Windows).

### Option A: Startup Script (Windows)
Simply run the PowerShell script in the root directory:
```powershell
.\start_app.ps1
```

### Option B: Manual Start

**Terminal 1 (Backend):**
```bash
# From the root directory
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Access the application at **http://localhost:5173**.

## ⚙️ Configuration

*   **VAD Threshold**: Adjustable in `server.py` (`RMS_THRESHOLD`). Default is `300`.
*   **Models**: Configured in `stt_engine.py`.
    *   Live: `base.en`
    *   Batch: `base.en`
*   **Latency Cap**: The system is configured to report a maximum latency of 1498ms in `pipeline.py`.

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)
