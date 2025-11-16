#!/usr/bin/env python3
"""
Transcribe the beginning of the audio where hints suggest the keywords are located.
Based on the hint "I-A-S-S" with "One, two, three, four",
all letters might be at the start.
"""

import whisper
import subprocess
import os
import re

def extract_audio_segment(input_file, output_file, start_sec=0, duration_sec=600):
    """Extract audio segment using ffmpeg"""
    print(f"Extracting first {duration_sec/60:.1f} minutes from audio...", flush=True)
    cmd = [
        'ffmpeg', '-y', '-v', 'error',
        '-ss', str(start_sec),
        '-i', input_file,
        '-t', str(duration_sec),
        '-acodec', 'libmp3lame',
        '-q:a', '4',
        output_file
    ]
    subprocess.run(cmd, check=True)
    print(f"Extracted to {output_file}", flush=True)

def transcribe_audio(audio_file, model_size="base"):
    """Transcribe audio with local Whisper"""
    print(f"\nLoading Whisper model '{model_size}'...", flush=True)
    model = whisper.load_model(model_size)

    print(f"Transcribing {audio_file}...", flush=True)
    print("This will take a few minutes...", flush=True)

    result = model.transcribe(audio_file, verbose=True)

    return result["text"]

def find_letter_patterns(text):
    """Find potential keyword letter patterns"""
    print(f"\n{'='*60}")
    print("Analyzing transcription for letter patterns...")
    print(f"{'='*60}\n")

    # Pattern 1: "The Nth letter in keyword is X, [phonetic]"
    pattern1 = r"[Tt]he\s+(\d+)(?:st|nd|rd|th)\s+letter\s+(?:in|of)\s+(?:the\s+)?keyword\s+is\s+([A-Za-z])[,\s]+([A-Za-z]+)"
    matches1 = re.findall(pattern1, text)

    if matches1:
        print("✓ Found standard keyword pattern:")
        keyword_letters = {}
        for pos, letter, phonetic in matches1:
            pos_num = int(pos)
            keyword_letters[pos_num] = letter.upper()
            print(f"  Position {pos_num}: {letter.upper()} ({phonetic})")

        # Build keyword
        if keyword_letters:
            max_pos = max(keyword_letters.keys())
            keyword = ""
            for i in range(1, max_pos + 1):
                keyword += keyword_letters.get(i, "_")
            print(f"\n🚩 KEYWORD: {keyword}")
            return keyword, keyword_letters

    # Pattern 2: Look for spelled-out sequences like "I-A-S-S"
    pattern2 = r'\b([A-Z])[-\s]([A-Z])(?:[-\s]([A-Z]))?(?:[-\s]([A-Z]))?(?:[-\s]([A-Z]))?'
    matches2 = re.findall(pattern2, text)

    if matches2:
        print("\n✓ Found spelled-out letter sequences:")
        for match in matches2[:10]:  # Show first 10
            letters = [l for l in match if l]
            print(f"  {''.join(letters)}")

    # Pattern 3: Look for NATO phonetic alphabet
    nato_alphabet = {
        'Alpha': 'A', 'Bravo': 'B', 'Charlie': 'C', 'Delta': 'D', 'Echo': 'E',
        'Foxtrot': 'F', 'Golf': 'G', 'Hotel': 'H', 'India': 'I', 'Juliet': 'J',
        'Kilo': 'K', 'Lima': 'L', 'Mike': 'M', 'November': 'N', 'Oscar': 'O',
        'Papa': 'P', 'Quebec': 'Q', 'Romeo': 'R', 'Sierra': 'S', 'Tango': 'T',
        'Uniform': 'U', 'Victor': 'V', 'Whiskey': 'W', 'Xray': 'X', 'X-ray': 'X',
        'Yankee': 'Y', 'Zulu': 'Z'
    }

    nato_found = []
    for phonetic, letter in nato_alphabet.items():
        if phonetic.lower() in text.lower():
            nato_found.append((phonetic, letter))

    if nato_found:
        print(f"\n✓ Found {len(nato_found)} NATO phonetic letters:")
        for phonetic, letter in nato_found[:10]:
            print(f"  {phonetic} = {letter}")

    # Pattern 4: Look for number-letter mappings (like "one=I, two=A")
    # Check if "one" appears near letters
    if 'one' in text.lower() and 'two' in text.lower():
        print("\n✓ Found number words (one, two, three, four) - potential number-to-letter mapping")

    return None, {}

def main():
    print("="*60)
    print("Transcribing Beginning of Audio (First 10 Minutes)")
    print("="*60)
    print()

    input_file = "audio_task_43.mp3"
    segment_file = "first_10min.mp3"

    # Extract first 10 minutes
    if not os.path.exists(segment_file):
        extract_audio_segment(input_file, segment_file, start_sec=0, duration_sec=600)
    else:
        print(f"Using existing {segment_file}")

    # Transcribe
    transcript = transcribe_audio(segment_file, model_size="base")

    # Save full transcription
    print(f"\nSaving full transcription to 'first_10min_transcript.txt'...", flush=True)
    with open("first_10min_transcript.txt", "w") as f:
        f.write(transcript)

    print(f"\n{'='*60}")
    print("Full Transcription:")
    print(f"{'='*60}")
    print(transcript)
    print(f"{'='*60}\n")

    # Analyze for patterns
    keyword, letters = find_letter_patterns(transcript)

    # Save results
    if keyword:
        with open("SOLUTION.txt", "w") as f:
            f.write(f"KEYWORD FOUND: {keyword}\n\n")
            f.write("Letter positions:\n")
            for pos, letter in sorted(letters.items()):
                f.write(f"  {pos}: {letter}\n")
            f.write(f"\nFull transcription saved in: first_10min_transcript.txt\n")

        print(f"\n✓ Solution saved to SOLUTION.txt")
        print(f"🚩 FLAG: {keyword}")
    else:
        print("\n⚠ No clear keyword pattern found in standard format.")
        print("Check 'first_10min_transcript.txt' for manual analysis.")
        print("\nThe transcript has been saved - you can search it for patterns!")

if __name__ == "__main__":
    main()
