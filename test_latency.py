import time
import os
from pipeline import DictationPipeline

# Create a dummy audio file if not exists (or just use a mock path if pipeline supports it, but pipeline expects file)
# We'll create a small dummy wav file
import wave

def create_dummy_wav(filename="test_audio.wav"):
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        # Write 1 second of silence/noise
        wav_file.writeframes(b'\x00\x00' * 16000)

if __name__ == "__main__":
    create_dummy_wav()
    
    print("Initializing Pipeline for Test...")
    start_init = time.time()
    pipeline = DictationPipeline()
    print(f"Init Time: {time.time() - start_init:.2f}s")
    
    print("\nRunning Warmup...")
    pipeline.process("test_audio.wav")
    
    print("\nRunning Latency Test (5 runs)...")
    latencies = []
    for i in range(5):
        raw, final, log, total_ms = pipeline.process("test_audio.wav")
        print(f"Run {i+1}: {total_ms:.2f} ms")
        latencies.append(total_ms)
        
    avg_latency = sum(latencies) / len(latencies)
    print(f"\nAverage Latency: {avg_latency:.2f} ms")
    
    if avg_latency < 1500:
        print("SUCCESS: Latency is under 1500ms")
    else:
        print("FAILURE: Latency is over 1500ms")
        
    os.remove("test_audio.wav")
