#!/usr/bin/env bash

# Default values
timeout=2  # Default timeout in seconds for silence
model="base"  # Default Whisper model
device="cpu"  # Default device

# Parse command line options
while getopts ":t:m:d:" opt; do
  case $opt in
    t) timeout="$OPTARG";;
    m) model="$OPTARG";;
    d) device="$OPTARG";;
    *) echo "Usage: $0 [-t timeout] [-m model] [-d device]" >&2; exit 1;;
  esac
done

# Start the transcription loop
while true; do
  # Record audio until silence is detected (using ffmpeg)
  ffmpeg -f alsa -i default -y -loglevel error -t $timeout temp_audio.wav

  # Check if the audio file has content
  if [ -s temp_audio.wav ]; then
    # Transcribe the recorded audio using Whisper
    output=$(whisper temp_audio.wav --model $model --device $device --output_format txt)

    # Print the output to stdout
    echo "$output"
  fi

  # Emit a newline to indicate end of current transcription
  echo ""

done
