import requests
import time
import sys

def test_transcribe_stream():
    url = "http://localhost:8000/transcribe_stream"
    files = {'file': ('test.wav', open('debug_audio.wav', 'rb'), 'audio/wav')}
    data = {'style': 'Neutral'}
    
    print(f"Sending request to {url}...")
    try:
        with requests.post(url, files=files, data=data, stream=True) as r:
            print(f"Response status: {r.status_code}")
            if r.status_code != 200:
                print(f"Error content: {r.text}")
                return

            for line in r.iter_lines():
                if line:
                    print(f"Received: {line.decode('utf-8')}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Ensure debug_audio.wav exists
    import wave
    with wave.open('debug_audio.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(b'\x00\x00' * 16000)

    # Wait for server to be ready? We'll just try.
    test_transcribe_stream()
