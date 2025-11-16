#!/usr/bin/env python3
"""
Smart search strategy: Sample different parts of the audio to find where keywords are,
then only transcribe that section.
"""

from pydub import AudioSegment
from openai import OpenAI
import os
import tempfile

def quick_sample_search(audio_file, api_key, sample_points=10, sample_duration_sec=30):
    """
    Take small samples throughout the audio to find where keywords appear.
    Cost: ~$0.30 for 10 samples of 30 seconds each = 5 minutes total
    """
    client = OpenAI(api_key=api_key)

    print("Loading audio file...", flush=True)
    audio = AudioSegment.from_mp3(audio_file)
    total_duration_min = len(audio) / 1000 / 60

    print(f"Audio duration: {total_duration_min:.2f} minutes")
    print(f"Taking {sample_points} samples of {sample_duration_sec} seconds each")
    print(f"Estimated cost: ~${(sample_points * sample_duration_sec / 60) * 0.006:.3f}")

    # Take evenly spaced samples
    interval = len(audio) // sample_points
    sample_duration_ms = sample_duration_sec * 1000

    results = []

    for i in range(sample_points):
        start_ms = i * interval
        start_min = start_ms / 1000 / 60

        print(f"\nSample {i+1}/{sample_points} at {start_min:.1f} min...")

        # Extract sample
        sample = audio[start_ms:start_ms + sample_duration_ms]

        # Export to temp file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            sample.export(temp_file.name, format="mp3")
            temp_path = temp_file.name

        try:
            # Transcribe
            with open(temp_path, "rb") as audio_file_obj:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file_obj,
                    response_format="text"
                )

            # Check for keyword pattern
            if "letter in keyword" in transcript.lower():
                print(f"  ✓ FOUND KEYWORD PATTERN!")
                print(f"  Transcript: {transcript[:200]}...")
                results.append({
                    "sample": i+1,
                    "start_min": start_min,
                    "has_keywords": True,
                    "transcript": transcript
                })
            else:
                print(f"  - No keywords found")
                results.append({
                    "sample": i+1,
                    "start_min": start_min,
                    "has_keywords": False
                })

        except Exception as e:
            print(f"  Error: {e}")

        finally:
            os.unlink(temp_path)

    # Find the region with keywords
    keyword_samples = [r for r in results if r.get("has_keywords")]

    if keyword_samples:
        print(f"\n{'='*60}")
        print(f"Found keywords in {len(keyword_samples)} sample(s)!")
        for sample in keyword_samples:
            print(f"  - Sample {sample['sample']} at {sample['start_min']:.1f} min")

        # Estimate the region to transcribe
        if len(keyword_samples) > 0:
            min_start = min(s['start_min'] for s in keyword_samples)
            max_start = max(s['start_min'] for s in keyword_samples)

            # Add buffer (10 minutes before and after)
            region_start = max(0, min_start - 10)
            region_end = min(total_duration_min, max_start + 10)
            region_duration = region_end - region_start

            print(f"\nRecommended region to transcribe:")
            print(f"  Start: {region_start:.1f} min")
            print(f"  End: {region_end:.1f} min")
            print(f"  Duration: {region_duration:.1f} min")
            print(f"  Estimated cost: ${region_duration * 0.006:.2f}")

            return region_start, region_end
    else:
        print("\nNo keywords found in samples. May need to sample more or use full transcription.")
        return None, None

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

    region_start, region_end = quick_sample_search(
        "audio_task_43.mp3",
        api_key,
        sample_points=10,  # Adjust this
        sample_duration_sec=30
    )

    if region_start is not None:
        print(f"\nNext step: Extract and transcribe the region:")
        print(f"  python extract_region.py {region_start} {region_end}")
