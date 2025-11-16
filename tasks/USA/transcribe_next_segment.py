#!/usr/bin/env python3
"""Continue transcribing to find more keyword letters"""

import whisper
import subprocess
import os
import re

def extract_segment(start_min, duration_min):
    start_sec = start_min * 60
    duration_sec = duration_min * 60
    output = f"segment_{start_min}_{start_min+duration_min}min.mp3"

    if os.path.exists(output):
        print(f"Using existing {output}")
        return output

    print(f"Extracting minutes {start_min}-{start_min+duration_min}...")
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', str(start_sec),
           '-i', 'audio_task_43.mp3', '-t', str(duration_sec),
           '-acodec', 'libmp3lame', '-q:a', '4', output]
    subprocess.run(cmd, check=True)
    return output

print("="*60)
print("Transcribing Next Segments (10-30 minutes)")
print("="*60)

model = whisper.load_model("base")

# Transcribe 10-30 minute range
segment_file = extract_segment(10, 20)

print(f"\nTranscribing {segment_file}...")
result = model.transcribe(segment_file, verbose=True)
transcript = result["text"]

# Save
output_file = "segment_10_30min_transcript.txt"
with open(output_file, "w") as f:
    f.write(transcript)

print(f"\nSaved to {output_file}")

# Search for keyword patterns
pattern = r"[Tt]he\s+(\d+)(?:st|nd|rd|th)\s+letter\s+(?:in|of)\s+(?:the\s+)?keyword\s+is\s+([A-Za-z])[,\s]+([A-Za-z]+)"
matches = re.findall(pattern, transcript)

if matches:
    print(f"\n✓ Found {len(matches)} keyword letters!")
    for pos, letter, phonetic in matches:
        print(f"  Position {pos}: {letter.upper()} ({phonetic})")
else:
    print("\n- No keyword letters found in this segment")

print(f"\nCheck {output_file} for full transcript")
