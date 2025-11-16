#!/usr/bin/env python3
"""
Transcribe entire 7h50min audio in chunks following the hints.
Hints:
1. Use multilingual audio model (Whisper ✓)
2. Chunk audio by time or silence
3. Transcribe all chunks and search for keywords
"""

import whisper
import subprocess
import os
import re
import json
from pathlib import Path

# Configuration
AUDIO_FILE = "audio_task_43.mp3"
CHUNK_DURATION_MIN = 5  # 5-minute chunks
TOTAL_DURATION_MIN = 470  # 7h50min = 470 minutes
OUTPUT_DIR = "chunks"

def create_chunks():
    """Split audio into time-based chunks"""
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    print("="*70)
    print("Creating Audio Chunks")
    print("="*70)
    print(f"Total duration: {TOTAL_DURATION_MIN} minutes ({TOTAL_DURATION_MIN//60}h {TOTAL_DURATION_MIN%60}min)")
    print(f"Chunk size: {CHUNK_DURATION_MIN} minutes")

    num_chunks = (TOTAL_DURATION_MIN + CHUNK_DURATION_MIN - 1) // CHUNK_DURATION_MIN
    print(f"Number of chunks: {num_chunks}\n")

    chunks = []
    for i in range(num_chunks):
        start_min = i * CHUNK_DURATION_MIN
        start_sec = start_min * 60
        duration_sec = CHUNK_DURATION_MIN * 60

        chunk_file = f"{OUTPUT_DIR}/chunk_{i:03d}_{start_min}min.mp3"

        if os.path.exists(chunk_file):
            print(f"  ✓ Chunk {i+1}/{num_chunks}: {chunk_file} (exists)")
        else:
            print(f"  Creating chunk {i+1}/{num_chunks}: minutes {start_min}-{start_min+CHUNK_DURATION_MIN}...")
            cmd = [
                'ffmpeg', '-y', '-v', 'error',
                '-ss', str(start_sec),
                '-i', AUDIO_FILE,
                '-t', str(duration_sec),
                '-acodec', 'libmp3lame',
                '-q:a', '4',
                chunk_file
            ]
            subprocess.run(cmd, check=True)

        chunks.append({
            'index': i,
            'file': chunk_file,
            'start_min': start_min,
            'end_min': min(start_min + CHUNK_DURATION_MIN, TOTAL_DURATION_MIN)
        })

    return chunks

def transcribe_chunk(model, chunk_info):
    """Transcribe a single chunk"""
    chunk_file = chunk_info['file']
    transcript_file = chunk_file.replace('.mp3', '_transcript.txt')

    # Skip if already transcribed
    if os.path.exists(transcript_file):
        with open(transcript_file, 'r') as f:
            return f.read()

    # Transcribe
    result = model.transcribe(chunk_file, verbose=False)
    transcript = result["text"]

    # Save transcript
    with open(transcript_file, 'w') as f:
        f.write(transcript)

    return transcript

def find_keywords(text):
    """Search for keyword patterns"""
    # Pattern: "The Nth letter in keyword is X, [phonetic]"
    pattern = r"[Tt]he\s+(\d+)(?:st|nd|rd|th)?\s+letter\s+(?:in|of)\s+(?:the\s+)?keyword\s+is\s+([A-Za-z])[,\s]+([A-Za-z]+)"
    matches = re.findall(pattern, text)
    return matches

def main():
    print("="*70)
    print("FULL AUDIO TRANSCRIPTION - Systematic Chunking Approach")
    print("="*70)
    print()

    # Step 1: Create chunks
    chunks = create_chunks()

    # Step 2: Load Whisper model
    print("\n" + "="*70)
    print("Loading Whisper Model (multilingual)")
    print("="*70)
    model = whisper.load_model("base")
    print("✓ Model loaded\n")

    # Step 3: Transcribe all chunks and search
    print("="*70)
    print("Transcribing Chunks and Searching for Keywords")
    print("="*70)
    print(f"This will take approximately {len(chunks) * 3} minutes (~3 min per chunk)")
    print()

    all_keywords = {}
    keyword_locations = {}

    for i, chunk_info in enumerate(chunks):
        print(f"\n[{i+1}/{len(chunks)}] Processing chunk at {chunk_info['start_min']} min...")

        # Transcribe
        transcript = transcribe_chunk(model, chunk_info)

        # Search for keywords
        matches = find_keywords(transcript)

        if matches:
            print(f"  ✓✓✓ FOUND {len(matches)} KEYWORD(S)! ✓✓✓")
            for pos, letter, phonetic in matches:
                pos_num = int(pos)
                print(f"    Position {pos_num}: {letter.upper()} ({phonetic})")
                all_keywords[pos_num] = letter.upper()
                keyword_locations[pos_num] = {
                    'letter': letter.upper(),
                    'phonetic': phonetic,
                    'chunk': i,
                    'time_min': chunk_info['start_min']
                }
        else:
            # Show language/content hint
            snippet = transcript[:80].replace('\n', ' ')
            print(f"  - No keywords (content: {snippet}...)")

        # Save progress every 10 chunks
        if (i + 1) % 10 == 0:
            with open('progress.json', 'w') as f:
                json.dump({
                    'chunks_processed': i + 1,
                    'total_chunks': len(chunks),
                    'keywords_found': all_keywords
                }, f, indent=2)
            print(f"\n  Progress saved: {i+1}/{len(chunks)} chunks processed, {len(all_keywords)} letters found")

    # Step 4: Final summary
    print("\n" + "="*70)
    print("FINAL RESULTS")
    print("="*70)

    if all_keywords:
        print(f"\n✓ Found {len(all_keywords)} keyword letters:\n")

        for pos in sorted(all_keywords.keys()):
            loc = keyword_locations[pos]
            print(f"  Position {pos}: {loc['letter']} ({loc['phonetic']}) - at {loc['time_min']} min (chunk {loc['chunk']})")

        # Build keyword
        max_pos = max(all_keywords.keys())
        keyword = ""
        for i in range(1, max_pos + 1):
            keyword += all_keywords.get(i, "_")

        print(f"\n{'='*70}")
        print(f"🚩 KEYWORD: {keyword}")
        print(f"{'='*70}")

        # Check completeness
        missing = [i for i in range(1, max_pos + 1) if i not in all_keywords]
        if missing:
            print(f"\n⚠ WARNING: Missing positions {missing}")
            print("The keyword may be incomplete!")
        else:
            print(f"\n✓✓✓ COMPLETE KEYWORD FOUND! ✓✓✓")

        # Save results
        with open('SOLUTION.txt', 'w') as f:
            f.write("="*70 + "\n")
            f.write("KEYWORD SOLUTION\n")
            f.write("="*70 + "\n\n")
            f.write(f"KEYWORD: {keyword}\n\n")
            f.write("Letter Positions:\n")
            for pos in sorted(all_keywords.keys()):
                loc = keyword_locations[pos]
                f.write(f"  {pos}: {loc['letter']} ({loc['phonetic']}) at {loc['time_min']} min\n")
            if missing:
                f.write(f"\nMissing positions: {missing}\n")
            f.write(f"\nTotal chunks transcribed: {len(chunks)}\n")

        print(f"\n✓ Solution saved to SOLUTION.txt")
    else:
        print("\n⚠ No keywords found!")

    print(f"\nAll chunk transcripts saved in: {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
