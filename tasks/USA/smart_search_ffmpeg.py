#!/usr/bin/env python3
"""
Smart search using ffmpeg to extract samples directly without loading entire file
"""

from openai import OpenAI
import os
import subprocess
import tempfile

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

def quick_sample_search(audio_file, api_key, sample_points=10, sample_duration_sec=30):
    """
    Take small samples throughout the audio to find where keywords appear.
    Uses ffmpeg to extract samples directly without loading full file.
    Cost: ~$0.30 for 10 samples of 30 seconds each = 5 minutes total
    """
    client = OpenAI(api_key=api_key)

    print("Getting audio duration...", flush=True)
    total_duration_sec = get_audio_duration(audio_file)
    total_duration_min = total_duration_sec / 60

    print(f"Audio duration: {total_duration_min:.2f} minutes ({total_duration_sec:.1f} seconds)", flush=True)
    print(f"Taking {sample_points} samples of {sample_duration_sec} seconds each", flush=True)
    print(f"Estimated cost: ~${(sample_points * sample_duration_sec / 60) * 0.006:.3f}", flush=True)

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

            print(f"  Transcribing with OpenAI...", flush=True)
            # Transcribe
            with open(temp_path, "rb") as audio_file_obj:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file_obj,
                    response_format="text"
                )

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
                results.append({
                    "sample": i+1,
                    "start_min": start_min,
                    "start_sec": start_sec,
                    "has_keywords": False
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
        print(f"Found keywords in {len(keyword_samples)} sample(s)!", flush=True)
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
            print(f"  Estimated cost: ${region_duration_min * 0.006:.2f}", flush=True)

            print(f"\nExtract command:", flush=True)
            print(f"  ffmpeg -ss {region_start_sec:.0f} -i audio_task_43.mp3 -t {region_duration_sec:.0f} keyword_region.mp3", flush=True)

            return region_start_sec, region_end_sec, keyword_samples
    else:
        print("\nNo keywords found in samples.", flush=True)
        print("Options:", flush=True)
        print("  1. Try more samples: Increase sample_points in the script", flush=True)
        print("  2. Try different sample duration", flush=True)
        print("  3. Keywords might be in a different pattern", flush=True)
        return None, None, []

if __name__ == "__main__":
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Try to read from config
        try:
            with open(os.path.expanduser("~/.config/openai/api_key")) as f:
                api_key = f.read().strip()
        except:
            print("Error: No OpenAI API key found")
            exit(1)

    region_start, region_end, samples = quick_sample_search(
        "audio_task_43.mp3",
        api_key,
        sample_points=10,  # Adjust this
        sample_duration_sec=30
    )

    if region_start is not None:
        print(f"\n{'='*60}", flush=True)
        print(f"SUCCESS! Found keyword location.", flush=True)
        print(f"\nNext step:", flush=True)
        print(f"1. Extract the region using ffmpeg (shown above)", flush=True)
        print(f"2. Transcribe with: python transcribe_audio.py --audio keyword_region.mp3 --method openai", flush=True)
