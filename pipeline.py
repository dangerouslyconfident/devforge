import time
from stt_engine import STTEngine
from text_cleaner import TextCleaner
from grammar_corrector import GrammarCorrector
from style_controller import StyleController

class DictationPipeline:
    def __init__(self):
        print("Initializing Pipeline...")
        self.stt = STTEngine()
        self.cleaner = TextCleaner()
        self.grammar = GrammarCorrector()
        self.style = StyleController()
        print("Pipeline Initialized.")

    def process(self, audio_path, style_mode="Neutral"):
        latency_log = {}
        
        # Step 1: STT
        print("Step 1: Transcribing...")
        raw_text, stt_latency = self.stt.transcribe(audio_path)
        latency_log["STT"] = f"{stt_latency:.2f} ms"
        
        if not raw_text:
            return "", "", latency_log, 0

        # Step 2: Cleaning (Disfluency + Repetition)
        print("Step 2: Cleaning...")
        start_clean = time.time()
        cleaned_text = self.cleaner.clean(raw_text)
        clean_latency = (time.time() - start_clean) * 1000
        latency_log["Cleaning"] = f"{clean_latency:.2f} ms"

        # Step 3: Grammar Correction
        print("Step 3: Grammar Correction...")
        grammar_text, grammar_latency = self.grammar.correct(cleaned_text)
        latency_log["Grammar"] = f"{grammar_latency:.2f} ms"

        # Step 4: Style Transfer
        print("Step 4: Style Transfer...")
        start_style = time.time()
        final_text = self.style.apply_style(grammar_text, style_mode)
        style_latency = (time.time() - start_style) * 1000
        latency_log["Style"] = f"{style_latency:.2f} ms"
        
        # Total Latency (excluding STT for the "processing" part, but let's show all)
        total_latency = stt_latency + clean_latency + grammar_latency + style_latency
        latency_log["Total"] = f"{total_latency:.2f} ms"
        
        return raw_text, final_text, latency_log, total_latency

if __name__ == "__main__":
    # Mock run
    pass
