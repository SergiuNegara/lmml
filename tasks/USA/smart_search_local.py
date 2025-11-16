#!/usr/bin/env python3
"""
Smart search using LOCAL Whisper (100% FREE!)
No API calls, no costs, runs on your machine
"""

import whisper
import subprocess
import tempfile
import os

def get_audio_duration(audio_file):
    """Get duration of audio file using ffprobe"""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        audio_file
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout.strip())

def extract_sample_ffmpeg(audio_file, start_sec, duration_sec, output_file):
    """Extract a sample using ffmpeg directly"""
    cmd = [
        'ffmpeg', '-y', '-v', 'error',
        '-ss', str(start_sec),
        '-i', audio_file,
        '-t', str(duration_sec),
        '-acodec', 'libmp3lame',
        '-q:a', '4',
        output_file
    ]
    subprocess.run(cmd, check=True)

def quick_sample_search_local(audio_file, sample_points=10, sample_duration_sec=30, model_size="base"):
    """
    Take small samples throughout the audio to find where keywords appear.
    Uses LOCAL Whisper - completely FREE!

    Model sizes:
    - tiny: Fastest, less accurate
    - base: Good balance (recommended)
    - small: More accurate, slower
    - medium: Very accurate, much slower
    """
    print(f"Loading Whisper model '{model_size}'... (first time will download ~150MB)", flush=True)
    model = whisper.load_model(model_size)

    print("Getting audio duration...", flush=True)
    total_duration_sec = get_audio_duration(audio_file)
    total_duration_min = total_duration_sec / 60

    print(f"Audio duration: {total_duration_min:.2f} minutes ({total_duration_sec:.1f} seconds)", flush=True)
    print(f"Taking {sample_points} samples of {sample_duration_sec} seconds each", flush=True)
    print(f"Cost: $0.00 (100% FREE - running locally!)", flush=True)

    # Take evenly spaced samples
    interval_sec = total_duration_sec / sample_points

    results = []

    for i in range(sample_points):
        start_sec = i * interval_sec
        start_min = start_sec / 60

        print(f"\nSample {i+1}/{sample_points} at {start_min:.1f} min ({start_sec:.0f} sec)...", flush=True)

        # Extract sample with ffmpeg
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            print(f"  Extracting sample...", flush=True)
            extract_sample_ffmpeg(audio_file, start_sec, sample_duration_sec, temp_path)

            print(f"  Transcribing with local Whisper...", flush=True)
            # Transcribe with local Whisper
            result = model.transcribe(temp_path)
            transcript = result["text"]

            # Check for keyword pattern
            if "letter in keyword" in transcript.lower() or "letter of the keyword" in transcript.lower():
                print(f"  ✓ FOUND KEYWORD PATTERN!", flush=True)
                print(f"  Transcript snippet: {transcript[:200]}...", flush=True)
                results.append({
                    "sample": i+1,
                    "start_min": start_min,
                    "start_sec": start_sec,
                    "has_keywords": True,
                    "transcript": transcript
                })
            else:
                print(f"  - No keywords found", flush=True)
                print(f"    (snippet: {transcript[:80]}...)", flush=True)
                results.append({
                    "sample": i+1,
                    "start_min": start_min,
                    "start_sec": start_sec,
                    "has_keywords": False,
                    "transcript": transcript
                })

        except Exception as e:
            print(f"  Error: {e}", flush=True)

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    # Find the region with keywords
    keyword_samples = [r for r in results if r.get("has_keywords")]

    print(f"\n{'='*60}", flush=True)
    if keyword_samples:
        print(f"✓ SUCCESS! Found keywords in {len(keyword_samples)} sample(s)!", flush=True)
        for sample in keyword_samples:
            print(f"  - Sample {sample['sample']} at {sample['start_min']:.1f} min ({sample['start_sec']:.0f} sec)", flush=True)

        # Estimate the region to transcribe
        if len(keyword_samples) > 0:
            min_start = min(s['start_sec'] for s in keyword_samples)
            max_start = max(s['start_sec'] for s in keyword_samples)

            # Add buffer (10 minutes = 600 seconds before and after)
            buffer_sec = 600
            region_start_sec = max(0, min_start - buffer_sec)
            region_end_sec = min(total_duration_sec, max_start + buffer_sec + sample_duration_sec)
            region_duration_sec = region_end_sec - region_start_sec
            region_duration_min = region_duration_sec / 60

            print(f"\nRecommended region to transcribe:", flush=True)
            print(f"  Start: {region_start_sec / 60:.1f} min ({region_start_sec:.0f} sec)", flush=True)
            print(f"  End: {region_end_sec / 60:.1f} min ({region_end_sec:.0f} sec)", flush=True)
            print(f"  Duration: {region_duration_min:.1f} min", flush=True)
            print(f"  Cost: $0.00 (FREE!)", flush=True)

            print(f"\nExtract command:", flush=True)
            print(f"  ffmpeg -ss {region_start_sec:.0f} -i audio_task_43.mp3 -t {region_duration_sec:.0f} keyword_region.mp3", flush=True)

            # Save transcripts with keywords
            print(f"\nSaving keyword samples to keyword_samples.txt...", flush=True)
            with open("keyword_samples.txt", "w") as f:
                for sample in keyword_samples:
                    f.write(f"=== Sample {sample['sample']} at {sample['start_min']:.1f} min ===\n")
                    f.write(sample['transcript'] + "\n\n")

            return region_start_sec, region_end_sec, keyword_samples
    else:
        print("\nNo keywords found in samples.", flush=True)
        print("Options:", flush=True)
        print("  1. Try more samples: Increase sample_points", flush=True)
        print("  2. Try different sample duration", flush=True)
        print("  3. Keywords might be in a different pattern", flush=True)

        # Save all transcripts for review
        print(f"\nSaving all transcripts to all_samples.txt for manual review...", flush=True)
        with open("all_samples.txt", "w") as f:
            for sample in results:
                f.write(f"=== Sample {sample['sample']} at {sample['start_min']:.1f} min ===\n")
                f.write(sample.get('transcript', '[ERROR]') + "\n\n")

        return None, None, []

if __name__ == "__main__":
    import sys

    model_size = "base"  # Options: tiny, base, small, medium
    if len(sys.argv) > 1:
        model_size = sys.argv[1]

    print("="*60)
    print("FREE Local Whisper Smart Search")
    print("="*60)
    print(f"Using model: {model_size}")
    print()

    region_start, region_end, samples = quick_sample_search_local(
        "audio_task_43.mp3",
        sample_points=10,
        sample_duration_sec=30,
        model_size=model_size
    )

    if region_start is not None:
        print(f"\n{'='*60}", flush=True)
        print(f"SUCCESS! Found keyword location.", flush=True)
        print(f"\nNext steps:", flush=True)
        print(f"1. Extract region: ffmpeg -ss {region_start:.0f} -i audio_task_43.mp3 -t {region_end - region_start:.0f} keyword_region.mp3", flush=True)
        print(f"2. Transcribe region (FREE): whisper keyword_region.mp3 --model base --output_format txt", flush=True)
        print(f"3. Parse keywords: python transcribe_audio.py --parse-only (after moving transcription)", flush=True)
