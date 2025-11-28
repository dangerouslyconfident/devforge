import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grammar_corrector import GrammarCorrector

def test_large_paragraph():
    print("Initializing GrammarCorrector...")
    gc = GrammarCorrector()
    
    # Create a large paragraph (approx 500 words)
    # Repeating a sentence with some grammar errors
    base_sentence = "I goes to the store yesterday and I buys some milk. "
    large_text = base_sentence * 50
    
    print(f"\nProcessing large text ({len(large_text)} chars)...")
    
    start_time = time.time()
    corrected_text, latency = gc.correct(large_text)
    end_time = time.time()
    
    print(f"Total Processing Time: {(end_time - start_time) * 1000:.2f} ms")
    print(f"Reported Latency: {latency:.2f} ms")
    
    # Verify it didn't crash and returned something reasonable
    if len(corrected_text) > len(large_text) * 0.8:
        print("SUCCESS: Output length is reasonable.")
    else:
        print("FAILURE: Output length is too short (possible truncation).")
        
    # Check if corrections were applied (simple check)
    if "went" in corrected_text:
        print("SUCCESS: Corrections applied (found 'went').")
    else:
        print("FAILURE: Corrections not applied.")

if __name__ == "__main__":
    test_large_paragraph()
