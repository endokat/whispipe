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
    parser.add_argument("-d", "--device", type=str, default="cpu", help="Device to use for Whisper")
    args = parser.parse_args()

    model = whisper.load_model(args.model, device=args.device)
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
            if output and len(output) > 5 and output == last_output:
                sys.stdout.write("\n")
                sys.stdout.flush()
                last_output = None
                recorder.kill()
                break
            else:
                last_output = output
                time.sleep(1)


if __name__ == "__main__":
    main()
