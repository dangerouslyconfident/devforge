from faster_whisper import WhisperModel
import os
import time

class STTEngine:
    def __init__(self, batch_model_size="base.en", live_model_size="base.en", device="cpu", compute_type="int8"):
        print(f"Loading Batch STT Model: {batch_model_size}...")
        self.batch_model = WhisperModel(batch_model_size, device=device, compute_type=compute_type)
        
        print(f"Loading Live STT Model: {live_model_size}...")
        self.live_model = WhisperModel(live_model_size, device=device, compute_type=compute_type)
        
        print("STT Models Loaded.")

    def transcribe(self, audio_input, initial_prompt=None, model_type="batch", beam_size=5):
        """
        Transcribes audio using the specified model type.
        audio_input can be a file path or numpy array.
        """
        start_time = time.time()
        
        model = self.live_model if model_type == "live" else self.batch_model
        
        # Check if audio_input is a path (string) and verify existence
        if isinstance(audio_input, str) and not os.path.exists(audio_input):
             raise FileNotFoundError(f"Audio file not found: {audio_input}")

        # Tuning parameters
        transcribe_options = {
            "beam_size": beam_size,
            "initial_prompt": initial_prompt
        }
        
        if model_type == "live":
            # Live Mode Optimization
            transcribe_options["condition_on_previous_text"] = False
            transcribe_options["repetition_penalty"] = 1.1
            transcribe_options["temperature"] = 0.0
            transcribe_options["vad_filter"] = True # Skip silence
        else:
            # Batch Mode Optimization for Speed/Long Audio
            transcribe_options["vad_filter"] = True
            transcribe_options["condition_on_previous_text"] = False # Prevent loops
            # Reduce beam size if it was default (5) to improve speed, unless specified otherwise
            if beam_size == 5:
                transcribe_options["beam_size"] = 2 
        
        segments, info = model.transcribe(
            audio_input, 
            **transcribe_options
        )
        
        text = ""
        for segment in segments:
            text += segment.text + " "
        
        end_time = time.time()
        latency = (end_time - start_time) * 1000 # ms
        
        return text.strip(), latency

    def transcribe_generator(self, audio_input, initial_prompt=None, model_type="batch", beam_size=5):
        """
        Yields segments as they are transcribed.
        """
        model = self.live_model if model_type == "live" else self.batch_model
        
        # Check if audio_input is a path (string) and verify existence
        if isinstance(audio_input, str) and not os.path.exists(audio_input):
             raise FileNotFoundError(f"Audio file not found: {audio_input}")

        # Tuning parameters
        transcribe_options = {
            "beam_size": beam_size,
            "initial_prompt": initial_prompt
        }
        
        if model_type == "live":
            transcribe_options["condition_on_previous_text"] = False
            transcribe_options["repetition_penalty"] = 1.1
            transcribe_options["temperature"] = 0.0
            transcribe_options["vad_filter"] = True
        else:
            transcribe_options["vad_filter"] = True
            transcribe_options["condition_on_previous_text"] = False
            if beam_size == 5:
                transcribe_options["beam_size"] = 2 
        
        segments, info = model.transcribe(
            audio_input, 
            **transcribe_options
        )
        
        for segment in segments:
            yield segment.text

if __name__ == "__main__":
    # Simple test
    # Create a dummy file or use an existing one if testing manually
    pass
