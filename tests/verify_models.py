import time
import os
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stt_engine import STTEngine
from grammar_corrector import GrammarCorrector

def verify_stt():
    print("\n--- Verifying STT Engine ---")
    start_load = time.time()
    try:
        stt = STTEngine(model_size="tiny.en", device="cpu", compute_type="int8")
        print(f"STT Load Time: {(time.time() - start_load)*1000:.2f} ms")
        
        # Create dummy audio file if needed, or just check if model loaded
        # For now, just checking load
        return True
    except Exception as e:
        print(f"STT Failed: {e}")
        return False

def verify_grammar():
    print("\n--- Verifying Grammar Corrector ---")
    start_load = time.time()
    try:
        gc = GrammarCorrector()
        print(f"Grammar Load Time: {(time.time() - start_load)*1000:.2f} ms")
        
        sample = "I goes to store."
        res, lat = gc.correct(sample)
        print(f"Correction: '{sample}' -> '{res}'")
        print(f"Latency: {lat:.2f} ms")
        return True
    except Exception as e:
        print(f"Grammar Failed: {e}")
        return False

if __name__ == "__main__":
    stt_ok = verify_stt()
    grammar_ok = verify_grammar()
    
    if stt_ok and grammar_ok:
        print("\nAll models verified successfully.")
    else:
        print("\nModel verification failed.")
