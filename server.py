from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil
import os
import time
from pipeline import DictationPipeline

app = FastAPI(title="Intelligent Speech Dictation API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Pipeline
print("Initializing Pipeline...")
pipeline = DictationPipeline()
print("Pipeline Ready.")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    style: str = Form("Neutral")
):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        start_total = time.time()
        raw_text, final_text, latency_log, processing_latency = pipeline.process(file_path, style)
        total_time = (time.time() - start_total) * 1000
        
        # Cleanup
        os.remove(file_path)
        
        return {
            "status": "success",
            "raw_text": raw_text,
            "final_text": final_text,
            "latency_breakdown": latency_log,
            "processing_latency_ms": processing_latency,
            "total_request_latency_ms": total_time
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
def health_check():
    return {"status": "ok"}

import numpy as np
from fastapi import WebSocket, WebSocketDisconnect

def calculate_rms(audio_chunk):
    """Calculate Root Mean Square amplitude of a chunk."""
    # Assuming 16-bit PCM (2 bytes per sample)
    data = np.frombuffer(audio_chunk, dtype=np.int16)
    if len(data) == 0:
        return 0
    return np.sqrt(np.mean(data**2))

@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")
    
    audio_buffer = b""
    silence_counter = 0
    # Tuning for "Near Instant"
    # 2 chunks of silence = 0.5s.
    SILENCE_THRESHOLD_CHUNKS = 2 
    RMS_THRESHOLD = 300 # Tuned for Indian English / Mic Noise
    
    try:
        while True:
            # Receive audio chunk (bytes)
            data = await websocket.receive_bytes()
            
            rms = calculate_rms(data)
            
            if rms < RMS_THRESHOLD:
                silence_counter += 1
            else:
                silence_counter = 0
                
            audio_buffer += data
            
            # Force process if buffer > 5 seconds (16000 * 2 * 5 = 160000 bytes)
            force_process = len(audio_buffer) > 160000
            
            # If silence detected (> 0.5s) OR force process
            if (silence_counter >= SILENCE_THRESHOLD_CHUNKS and len(audio_buffer) > 16000) or force_process:
                print(f"Processing buffer... (Reason: {'Force' if force_process else 'Silence'}, RMS: {rms:.2f})")
                
                # Process the buffer with full pipeline
                final_text = pipeline.process_bytes(audio_buffer)
                
                if final_text:
                    await websocket.send_json({"text": final_text, "is_final": True})
                
                # Reset
                audio_buffer = b""
                silence_counter = 0
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
