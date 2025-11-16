#!/usr/bin/env python3
"""
Sample the entire audio at regular intervals to find keyword letters efficiently.
Total duration: 7h50min = 470 minutes
Strategy: Sample every 50 minutes throughout the audio
"""

import whisper
import subprocess
import os
import re

def extract_segment(start_min, duration_min=2):
    """Extract a short segment from the audio"""
    start_sec = start_min * 60
    duration_sec = duration_min * 60
    output = f"sample_{start_min}min.mp3"

    if os.path.exists(output):
        print(f"  Using existing {output}")
        return output

    print(f"  Extracting {duration_min} min sample at {start_min} min mark...")
    cmd = ['ffmpeg', '-y', '-v', 'error', '-ss', str(start_sec),
           '-i', 'audio_task_43.mp3', '-t', str(duration_sec),
           '-acodec', 'libmp3lame', '-q:a', '4', output]
    subprocess.run(cmd, check=True)
    return output

def find_keywords(text):
    """Search for keyword patterns in text"""
    pattern = r"[Tt]he\s+(\d+)(?:st|nd|rd|th)?\s+letter\s+(?:in|of)\s+(?:the\s+)?keyword\s+is\s+([A-Za-z])[,\s]+([A-Za-z]+)"
    matches = re.findall(pattern, text)
    return matches

def main():
    print("="*70)
    print("Sampling Entire Audio for Keyword Letters")
    print("="*70)
    print("Strategy: Sample 2 minutes at regular intervals throughout 7h50min audio")
    print()

    # Load Whisper model once
    print("Loading Whisper model...")
    model = whisper.load_model("base")

    # Sample points: every 50 minutes from 50 to 450
    sample_points = [50, 100, 150, 200, 250, 300, 350, 400, 450]

    all_keywords = {}

    for sample_min in sample_points:
        print(f"\n{'='*70}")
        print(f"Sample at {sample_min} minutes ({sample_min//60}h {sample_min%60}min)")
        print(f"{'='*70}")

        # Extract segment
        segment_file = extract_segment(sample_min, duration_min=2)

        # Transcribe
        print(f"  Transcribing...")
        result = model.transcribe(segment_file, verbose=False)
        transcript = result["text"]

        # Search for keywords
        matches = find_keywords(transcript)

        if matches:
            print(f"  ✓ FOUND {len(matches)} keyword letter(s)!")
            for pos, letter, phonetic in matches:
                print(f"    Position {pos}: {letter.upper()} ({phonetic})")
                all_keywords[int(pos)] = letter.upper()
        else:
            print(f"  - No keyword letters found at {sample_min} min")
            # Show snippet of what was transcribed
            snippet = transcript[:150] + "..." if len(transcript) > 150 else transcript
            print(f"  Content: {snippet}")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY OF ALL FINDINGS")
    print(f"{'='*70}")

    # Add our known findings
    all_keywords[1] = 'D'  # From first 10 minutes

    if all_keywords:
        print(f"\nFound {len(all_keywords)} keyword letter(s) total:")
        for pos in sorted(all_keywords.keys()):
            print(f"  Position {pos}: {all_keywords[pos]}")

        # Try to build keyword
        max_pos = max(all_keywords.keys())
        keyword = ""
        for i in range(1, max_pos + 1):
            keyword += all_keywords.get(i, "_")

        print(f"\n🚩 KEYWORD SO FAR: {keyword}")
        missing_positions = [i for i in range(1, max_pos + 1) if i not in all_keywords]
        if missing_positions:
            print(f"⚠ Missing positions: {missing_positions}")
            print(f"\nNext step: Need to search more thoroughly around these time ranges")
        else:
            print(f"\n✓ COMPLETE KEYWORD FOUND!")

        # Save results
        with open("keyword_findings.txt", "w") as f:
            f.write("KEYWORD LETTER FINDINGS\n")
            f.write("="*70 + "\n\n")
            for pos in sorted(all_keywords.keys()):
                f.write(f"Position {pos}: {all_keywords[pos]}\n")
            f.write(f"\nKeyword: {keyword}\n")
            if missing_positions:
                f.write(f"Missing: {missing_positions}\n")
        print(f"\n✓ Results saved to keyword_findings.txt")
    else:
        print("\n⚠ No keyword letters found in these samples")
        print("May need to sample more densely or check different time ranges")

if __name__ == "__main__":
    main()
