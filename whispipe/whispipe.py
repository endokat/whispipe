import argparse
import sys
import subprocess
import whisper
import os
import io


def main():
    # Parse command line options
    parser = argparse.ArgumentParser(description="Voice listener using Whisper")
    parser.add_argument("-m", "--model", type=str, default="base", help="Whisper model to use")
    parser.add_argument("-d", "--device", type=str, default="cpu", help="Device to use for Whisper")
    args = parser.parse_args()

    # Load Whisper model
    model = whisper.load_model(args.model, device=args.device)

    # Record audio until silence is detected after initial speech
    temp_audio_path = "/tmp/whispipe_tmp.wav"
    while True:
        command = [
            "ffmpeg",
            "-y",
            "-f", "pulse",
            "-i", "default",
            "-af", "silencedetect=n=-50dB:d=1",
            "-ac", "1",
            temp_audio_path
        ]
        try:
          subprocess.run(command, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
          pass

        # Transcribe the recorded audio using Whisper
        result = model.transcribe(temp_audio_path)
        output = result["text"].strip()

        # Print the output to stdout
        if output:
            sys.stdout.write(output)
            sys.stdout.write(" ")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
