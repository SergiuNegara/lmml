#!/usr/bin/env python3
"""
Search for letter patterns in the entire audio
Since the hint says "use the power of programming" and shows "I-A-S-S",
maybe the letters are spelled out directly throughout the audio
"""

import whisper
import subprocess
import re

def get_audio_duration(audio_file):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
           '-of', 'default=noprint_wrappers=1:nokey=1', audio_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def extract_chunk_ffmpeg(audio_file, start_sec, duration_sec, output_file):
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', str(start_sec),
           '-i', audio_file, '-t', str(duration_sec),
           '-acodec', 'libmp3lame', '-q:a', '4', output_file]
    subprocess.run(cmd, check=True)

def find_letter_sequences(text):
    """Find sequences that look like spelled-out letters"""
    # Pattern 1: Single capital letters separated by dashes or spaces
    pattern1 = r'\b([A-Z])[-\s]([A-Z])[-\s]([A-Z])'

    # Pattern 2: "letter X is Y" or similar
    pattern2 = r'letter[s]?\s+.*?is\s+([A-Z])'

    # Pattern 3: NATO phonetic alphabet
    nato = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot',
            'Golf', 'Hotel', 'India', 'Juliet', 'Kilo', 'Lima', 'Mike',
            'November', 'Oscar', 'Papa', 'Quebec', 'Romeo', 'Sierra',
            'Tango', 'Uniform', 'Victor', 'Whiskey', 'X-ray', 'Yankee', 'Zulu']

    results = []

    # Find dash/space separated letters
    for match in re.finditer(pattern1, text, re.IGNORECASE):
        results.append(('sequence', match.group(0), match.start()))

    # Find NATO phonetics
    for phonetic in nato:
        if phonetic.lower() in text.lower():
            results.append(('nato', phonetic, text.lower().find(phonetic.lower())))

    return results

# Quick scan: transcribe small chunks throughout the audio looking for clear English
print("Quick scanning for letter patterns in the audio...")
print("This will take a while but is FREE!\n")

model = whisper.load_model("base")

audio_file = "audio_task_43.mp3"
duration = get_audio_duration(audio_file)

# Scan more frequently (every minute, 30sec chunks)
scan_interval = 60  # every minute
chunk_duration = 30

letter_findings = []

import tempfile
import os

for start in range(0, int(duration), scan_interval):
    min_mark = start / 60
    print(f"Scanning {min_mark:.1f} min...", end=' ', flush=True)

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        temp_path = f.name

    try:
        extract_chunk_ffmpeg(audio_file, start, chunk_duration, temp_path)
        result = model.transcribe(temp_path)
        text = result["text"]

        # Look for letter patterns
        patterns = find_letter_sequences(text)

        if patterns or any(word in text for word in ['letter', 'keyword', 'Alpha', 'Bravo']):
            print(f"✓ INTERESTING!")
            print(f"  Text: {text[:150]}...")
            letter_findings.append({
                'time': start,
                'text': text,
                'patterns': patterns
            })
        else:
            print("- ")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

print(f"\n{'='*60}")
print(f"Found {len(letter_findings)} interesting segments")

if letter_findings:
    with open("interesting_segments.txt", "w") as f:
        for segment in letter_findings:
            f.write(f"=== {segment['time']/60:.1f} min ({segment['time']}s) ===\n")
            f.write(segment['text'] + "\n\n")
    print("Saved to interesting_segments.txt")
