import argparse
import os
import tempfile
import time
import sounddevice as sd
import numpy as np
import whisper

# Default values
timeout = 2  # Default timeout in seconds for silence
model_name = "base"  # Default Whisper model
device = "cpu"  # Default device

def main():
    # Parse command line options
    parser = argparse.ArgumentParser(description="Voice listener using Whisper")
    parser.add_argument("-t", "--timeout", type=int, default=timeout, help="Timeout in seconds for silence")
    parser.add_argument("-m", "--model", type=str, default=model_name, help="Whisper model to use")
    parser.add_argument("-d", "--device", type=str, default=device, help="Device to use for Whisper")
    args = parser.parse_args()

    timeout = args.timeout
    model_name = args.model
    device = args.device

    # Load Whisper model
    model = whisper.load_model(model_name, device=device)

    # Start the transcription loop
    while True:
        # Record audio until silence is detected
        audio_data = record_audio(timeout)

        # Write audio data to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
            temp_audio_path = temp_audio_file.name
            sd.write(temp_audio_path, audio_data, 16000)

        # Transcribe the recorded audio using Whisper
        result = model.transcribe(temp_audio_path)
        output = result["text"].strip()

        # Print the output to stdout
        if output:
            print(output)

        # Emit a newline to indicate end of current transcription
        print("")

        # Clean up temporary file
        os.remove(temp_audio_path)

# Function to record audio until silence is detected
def record_audio(timeout):
    samplerate = 16000  # Sample rate for recording
    duration = 0  # Start with an indefinite duration
    silence_threshold = 0.01  # Silence threshold
    silent_chunks = 0
    max_silent_chunks = int(timeout * samplerate / 1024)

    print("Listening...")
    recorded_audio = []

    def callback(indata, frames, time, status):
        nonlocal silent_chunks, recorded_audio
        volume_norm = np.linalg.norm(indata) * 10
        if volume_norm < silence_threshold:
            silent_chunks += 1
        else:
            silent_chunks = 0

        recorded_audio.append(indata.copy())

        if silent_chunks > max_silent_chunks:
            raise sd.CallbackStop()

    with sd.InputStream(samplerate=samplerate, channels=1, callback=callback, blocksize=1024):
        try:
            sd.sleep(int(1e6))  # Run until silence is detected
        except sd.CallbackStop:
            pass

    return np.concatenate(recorded_audio, axis=0)

