import time
import os
import traceback
from pipeline import DictationPipeline
import wave

def create_dummy_wav(filename="debug_audio.wav"):
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        # Write 1 second of silence
        wav_file.writeframes(b'\x00\x00' * 16000)

if __name__ == "__main__":
    create_dummy_wav()
    
    try:
        print("Initializing Pipeline...")
        pipeline = DictationPipeline()
        
        print("Testing process_stream...")
        # Consume the generator
        for segment in pipeline.process_stream("debug_audio.wav"):
            print(f"Segment: {segment}")
            
        print("Success!")
        
    except Exception:
        traceback.print_exc()
    finally:
        if os.path.exists("debug_audio.wav"):
            os.remove("debug_audio.wav")
