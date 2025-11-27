import gradio as gr
from pipeline import DictationPipeline
import os

# Initialize pipeline once
pipeline = DictationPipeline()

def process_audio(audio_path, style):
    if not audio_path:
        return "No audio provided", "", {}, "0 ms"
    
    raw_text, final_text, latency_log, total_latency = pipeline.process(audio_path, style)
    
    return raw_text, final_text, latency_log, f"{total_latency:.2f} ms"

with gr.Blocks(title="Intelligent Speech Dictation Engine") as demo:
    gr.Markdown("# Intelligent Speech Dictation Engine (MVP)")
    gr.Markdown("Real-time, on-device speech-to-text with cleaning, grammar correction, and style transfer.")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Input Speech")
            style_input = gr.Dropdown(choices=["Neutral", "Formal", "Casual", "Concise"], value="Neutral", label="Style Mode")
            process_btn = gr.Button("Process", variant="primary")
        
        with gr.Column():
            raw_output = gr.Textbox(label="Raw Transcription")
            final_output = gr.Textbox(label="Cleaned & Styled Output")
            latency_output = gr.JSON(label="Latency Breakdown")
            total_latency_disp = gr.Textbox(label="Total Processing Time")

    process_btn.click(
        fn=process_audio,
        inputs=[audio_input, style_input],
        outputs=[raw_output, final_output, latency_output, total_latency_disp]
    )

if __name__ == "__main__":
    demo.launch()
