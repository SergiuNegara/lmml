#!/usr/bin/env python3
"""Extract a specific region from audio for targeted transcription"""

from pydub import AudioSegment
import sys

def extract_region(input_file, output_file, start_min, end_min):
    """Extract a region from the audio"""
    print(f"Loading audio file: {input_file}")
    audio = AudioSegment.from_mp3(input_file)

    # Convert to milliseconds
    start_ms = int(start_min * 60 * 1000)
    end_ms = int(end_min * 60 * 1000)

    # Extract region
    region = audio[start_ms:end_ms]
    duration_min = len(region) / 1000 / 60

    # Export
    region.export(output_file, format="mp3")
    print(f"Extracted region from {start_min:.1f} to {end_min:.1f} minutes")
    print(f"Duration: {duration_min:.2f} minutes")
    print(f"Saved to: {output_file}")
    print(f"Estimated transcription cost: ${duration_min * 0.006:.2f}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_region.py <start_min> <end_min> [output_file]")
        print("Example: python extract_region.py 120.5 150.5 region.mp3")
        sys.exit(1)

    start = float(sys.argv[1])
    end = float(sys.argv[2])
    output = sys.argv[3] if len(sys.argv) > 3 else f"region_{start:.0f}_{end:.0f}min.mp3"

    extract_region("audio_task_43.mp3", output, start, end)
