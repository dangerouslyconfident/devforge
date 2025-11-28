from happytransformer import HappyTextToText, TTSettings
import time

class GrammarCorrector:
    def __init__(self, model_name="vennify/t5-base-grammar-correction"):
        print(f"Loading Grammar Model: {model_name}...")
        # Using T5-base for better accuracy, might switch to small if latency is too high
        self.happy_tt = HappyTextToText("T5", model_name)
        self.args = TTSettings(num_beams=1, min_length=1)
        print("Grammar Model Loaded.")

    def correct(self, text):
        if not text or not text.strip():
            return "", 0
            
        start_time = time.time()
        
        # Split text into chunks (sentences) to avoid model token limits
        # Simple split by punctuation for now, can be improved with nltk/spacy if needed
        import re
        # Split by . ? ! followed by space or end of string
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        corrected_sentences = []
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            # Add prefix if the model expects it
            input_text = "grammar: " + sentence
            result = self.happy_tt.generate_text(input_text, args=self.args)
            corrected_sentences.append(result.text)
            
        corrected_text = " ".join(corrected_sentences)
        
        end_time = time.time()
        latency = (end_time - start_time) * 1000
        return corrected_text, latency

if __name__ == "__main__":
    gc = GrammarCorrector()
    sample = "I goes to the store yesterday."
    print(f"Original: {sample}")
    res, lat = gc.correct(sample)
    print(f"Corrected: {res} (Latency: {lat:.2f}ms)")
