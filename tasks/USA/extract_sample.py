#!/usr/bin/env python3
"""Extract a sample from the audio file for testing"""

from pydub import AudioSegment
import sys

def extract_sample(input_file, output_file, start_min=0, duration_min=5):
    """Extract a sample from the audio"""
    print(f"Loading audio file: {input_file}")
    audio = AudioSegment.from_mp3(input_file)

    total_duration = len(audio) / 1000 / 60
    print(f"Total duration: {total_duration:.2f} minutes")

    # Convert to milliseconds
    start_ms = start_min * 60 * 1000
    duration_ms = duration_min * 60 * 1000

    # Extract sample
    sample = audio[start_ms:start_ms + duration_ms]

    # Export
    sample.export(output_file, format="mp3")
    print(f"Extracted {duration_min} minutes starting at {start_min} minutes")
    print(f"Saved to: {output_file}")
    print(f"Sample size: {len(sample) / 1000 / 60:.2f} minutes")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_sample.py <start_minute> [duration_minutes]")
        print("Example: python extract_sample.py 0 5  # Extract 5 minutes from start")
        sys.exit(1)

    start = int(sys.argv[1])
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    extract_sample("audio_task_43.mp3", f"sample_{start}min_{duration}min.mp3", start, duration)
