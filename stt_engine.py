from faster_whisper import WhisperModel
import os
import time

class STTEngine:
    def __init__(self, model_size="base.en", device="cpu", compute_type="int8"):
        print(f"Loading STT Model: {model_size} on {device} with {compute_type}...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print("STT Model Loaded.")

    def transcribe(self, audio_path):
        """
        Transcribes the audio file and returns the text.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        start_time = time.time()
        segments, info = self.model.transcribe(audio_path, beam_size=5)
        
        text = ""
        for segment in segments:
            text += segment.text + " "
        
        end_time = time.time()
        latency = (end_time - start_time) * 1000 # ms
        
        return text.strip(), latency

if __name__ == "__main__":
    # Simple test
    # Create a dummy file or use an existing one if testing manually
    pass
