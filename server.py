from fastapi import FastAPI, UploadFile, File, Form, WebSocket
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
