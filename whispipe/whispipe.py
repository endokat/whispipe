import argparse
import time
import sys
import shutil
import subprocess
import whisper
import os
import io


def main():
    parser = argparse.ArgumentParser(description="Voice listener using Whisper")
    parser.add_argument("-m", "--model", type=str, default="base", help="Whisper model to use")
    parser.add_argument("-d", "--device", type=str, default="cuda", help="Device to use for Whisper (falls back to cpu if CUDA unavailable)")
    silence_group = parser.add_mutually_exclusive_group()
    silence_group.add_argument("-n", "--noline", action="store_true", help="Emit no newline on silence")
    silence_group.add_argument("-t", "--timeout", type=float, default=1.0, help="Timeout for silence")
    args = parser.parse_args()

    device = args.device
    if device == "cuda":
        import torch
        if not torch.cuda.is_available():
            device = "cpu"

    model = whisper.load_model(args.model, device=device)
    temp_audio_path = "/tmp/whispipe_tmp.wav"
    while True:
        command = [
            "ffmpeg",
            "-y",
            "-f", "pulse",
            "-i", "default",
            "-ac", "1",
            temp_audio_path
        ]
        try:
          os.remove(temp_audio_path)
        except FileNotFoundError:
          pass
        recorder = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        while not os.path.isfile(temp_audio_path) or os.path.getsize(temp_audio_path) == 0:
          time.sleep(0.1)

        last_output = None
        while True:
            result = model.transcribe(temp_audio_path)
            output = result["text"].strip()

            if last_output is not None:
                for _ in range(len(last_output)):
                    sys.stdout.write("")
                    sys.stdout.flush()
            sys.stdout.write(output)
            sys.stdout.flush()

            if output and output == last_output:
                if not args.noline:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                last_output = None
                recorder.kill()
                break
            else:
                last_output = output
                time.sleep(args.timeout)


if __name__ == "__main__":
    main()
