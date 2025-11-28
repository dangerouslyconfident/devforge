import requests
import json
import os

# Create a dummy wav file if it doesn't exist
if not os.path.exists("test_audio.wav"):
    import wave
    with wave.open("test_audio.wav", 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        # Write 3 seconds of silence/noise
        wav_file.writeframes(b'\x00\x00' * 16000 * 3)

url = "http://localhost:8000/transcribe_stream"
files = {'file': open('test_audio.wav', 'rb')}
data = {'style': 'Neutral'}

print("Sending request to /transcribe_stream...")
try:
    with requests.post(url, files=files, data=data, stream=True) as response:
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
        else:
            print("Response received. Reading stream...")
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(f"Received: {decoded_line}")
                    if decoded_line.startswith("data: "):
                        data_str = decoded_line.replace("data: ", "")
                        if data_str == "[DONE]":
                            print("Stream finished.")
                            break
                        try:
                            json_data = json.loads(data_str)
                            print(f"Parsed JSON: {json_data}")
                        except:
                            pass
except Exception as e:
    print(f"Request failed: {e}")
finally:
    files['file'].close()
    if os.path.exists("test_audio.wav"):
        os.remove("test_audio.wav")
