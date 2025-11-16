#!/usr/bin/env python3
"""
Audio transcription script for finding the keyword in Mr. Whiskerstein's lecture.
"""

import os
import re
import json
from pathlib import Path
import time
import sys
import argparse

def check_dependencies():
    """Check if we have the necessary dependencies"""
    has_openai = False
    has_sr = False

    try:
        import openai
        has_openai = True
    except ImportError:
        pass

    try:
        import speech_recognition as sr
        from pydub import AudioSegment
        has_sr = True
    except ImportError:
        pass

    return has_openai, has_sr

def split_audio(audio_file, chunk_length_ms=60000):
    """Split audio file into chunks for processing"""
    from pydub import AudioSegment

    print(f"Loading audio file: {audio_file}")
    audio = AudioSegment.from_mp3(audio_file)

    print(f"Audio duration: {len(audio) / 1000 / 60:.2f} minutes")

    # Split into chunks
    chunks = []
    for i in range(0, len(audio), chunk_length_ms):
        chunk = audio[i:i + chunk_length_ms]
        chunks.append(chunk)

    print(f"Split into {len(chunks)} chunks of {chunk_length_ms/1000}s each")
    return chunks

def transcribe_with_openai_api(audio_file, output_file="transcription.txt", api_key=None):
    """Transcribe audio using OpenAI's Whisper API"""
    from openai import OpenAI
    from pydub import AudioSegment
    import tempfile

    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            return None

    client = OpenAI(api_key=api_key)

    # OpenAI API has a 25MB file size limit, so we need to split the audio
    # Split into 10-minute chunks (~25MB for mp3)
    print("Splitting audio into chunks for OpenAI API...")
    chunks = split_audio(audio_file, chunk_length_ms=600000)  # 10 minutes

    transcription = []

    with open(output_file, 'w') as f:
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)} with OpenAI API...")

            # Export chunk to temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                chunk.export(temp_file.name, format="mp3")
                temp_path = temp_file.name

            try:
                # Check file size
                file_size = os.path.getsize(temp_path) / 1024 / 1024
                print(f"  Chunk size: {file_size:.2f} MB")

                # Transcribe using OpenAI Whisper API
                with open(temp_path, "rb") as audio_file_obj:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file_obj,
                        response_format="text"
                    )

                transcription.append(transcript)
                f.write(transcript + "\n")
                f.flush()
                print(f"  Transcribed {len(transcript)} characters")

                # Check for keywords periodically
                if i % 5 == 0:
                    full_text = "\n".join(transcription)
                    keyword, _ = parse_keywords(full_text, verbose=False)
                    if keyword and "_" not in keyword:
                        print(f"  *** Found complete keyword: {keyword} ***")

            except Exception as e:
                print(f"  Error transcribing chunk {i+1}: {e}")

            finally:
                # Clean up temp file
                os.unlink(temp_path)

            # Small delay to avoid rate limiting
            time.sleep(1)

    return "\n".join(transcription)

def transcribe_with_google(audio_file, output_file="transcription.txt"):
    """Transcribe audio using Google Speech Recognition (free but limited)"""
    import speech_recognition as sr
    from pydub import AudioSegment
    import tempfile

    recognizer = sr.Recognizer()

    # Split audio into 60-second chunks (Google has limits)
    print("Splitting audio into chunks...")
    chunks = split_audio(audio_file, chunk_length_ms=60000)

    transcription = []

    with open(output_file, 'w') as f:
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...")

            # Export chunk to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                chunk.export(temp_wav.name, format="wav")
                temp_path = temp_wav.name

            try:
                # Transcribe
                with sr.AudioFile(temp_path) as source:
                    audio_data = recognizer.record(source)
                    try:
                        text = recognizer.recognize_google(audio_data)
                        transcription.append(text)
                        f.write(text + "\n")
                        f.flush()
                        print(f"  Transcribed: {text[:100]}...")
                    except sr.UnknownValueError:
                        print(f"  Could not understand audio in chunk {i+1}")
                    except sr.RequestError as e:
                        print(f"  Error with Google API: {e}")

            finally:
                # Clean up temp file
                os.unlink(temp_path)

            # Check if we found any keyword patterns early
            if i % 10 == 0:  # Check every 10 chunks
                parse_keywords("\n".join(transcription), verbose=False)

    return "\n".join(transcription)

def parse_keywords(transcription_text, verbose=True):
    """Parse the transcription to find keyword patterns"""

    # Pattern: "The Nth letter in keyword is X, [NATO phonetic]"
    # Examples: "The 1st letter in keyword is A, Alpha."

    pattern = r"[Tt]he\s+(\d+)(?:st|nd|rd|th)\s+letter\s+in\s+keyword\s+is\s+([A-Za-z])[,\s]+([A-Za-z]+)"

    matches = re.findall(pattern, transcription_text)

    if verbose:
        print(f"\nFound {len(matches)} potential keyword letters:")

    # Sort by position
    keyword_letters = {}
    for position, letter, phonetic in matches:
        pos = int(position)
        keyword_letters[pos] = (letter.upper(), phonetic)
        if verbose:
            print(f"  Position {pos}: {letter.upper()} ({phonetic})")

    # Build the keyword
    if keyword_letters:
        max_pos = max(keyword_letters.keys())
        keyword = ""
        for i in range(1, max_pos + 1):
            if i in keyword_letters:
                keyword += keyword_letters[i][0]
            else:
                keyword += "_"  # Missing letter

        if verbose:
            print(f"\nExtracted keyword: {keyword}")
        return keyword, keyword_letters
    else:
        if verbose:
            print("No keyword patterns found yet.")
        return None, {}

def main():
    parser = argparse.ArgumentParser(description="Transcribe Mr. Whiskerstein's lecture and find the keyword")
    parser.add_argument("--method", choices=["openai", "google"], default="openai",
                        help="Transcription method (default: openai)")
    parser.add_argument("--audio", default="audio_task_43.mp3",
                        help="Audio file to transcribe")
    parser.add_argument("--use-existing", action="store_true",
                        help="Use existing transcription.txt if available")
    parser.add_argument("--parse-only", action="store_true",
                        help="Only parse existing transcription, don't transcribe")

    args = parser.parse_args()
    audio_file = args.audio

    # Check dependencies
    has_openai, has_sr = check_dependencies()

    if not has_openai and not has_sr:
        print("Error: No transcription dependencies found!")
        print("Install either: pip install openai pydub (for OpenAI API)")
        print("           or: pip install SpeechRecognition pydub (for Google API)")
        return

    print("="*60)
    print("Mr. Whiskerstein's Lecture Keyword Extractor")
    print("="*60)
    print(f"Audio file: {audio_file}")
    if os.path.exists(audio_file):
        print(f"File size: {os.path.getsize(audio_file) / 1024 / 1024:.2f} MB")
    else:
        print(f"Error: Audio file not found: {audio_file}")
        return

    # Check if we already have a transcription
    if os.path.exists("transcription.txt") and (args.use_existing or args.parse_only):
        print("\n*** Using existing transcription file ***")
        with open("transcription.txt", 'r') as f:
            transcription = f.read()
        keyword, letters = parse_keywords(transcription)

        # Save results
        if keyword:
            with open("results.json", 'w') as f:
                json.dump({
                    "keyword": keyword,
                    "letters": {k: {"letter": v[0], "phonetic": v[1]} for k, v in letters.items()},
                    "full_transcription_available": True
                }, f, indent=2)
            print("\nResults saved to results.json")
            print(f"\n🚩 FLAG: {keyword}")
        return

    # Validate method
    selected_method = args.method
    if selected_method == "openai" and not has_openai:
        print("Error: OpenAI library not installed!")
        return
    if selected_method == "google" and not has_sr:
        print("Error: SpeechRecognition library not installed!")
        return

    print(f"\nUsing transcription method: {selected_method}")
    print("Starting transcription (this will take a while for a 7h 50min file)...")

    # Transcribe
    if selected_method == "openai":
        transcription = transcribe_with_openai_api(audio_file)
    else:
        transcription = transcribe_with_google(audio_file)

    if not transcription:
        print("Error: Transcription failed!")
        return

    print("\n" + "="*60)
    print("Transcription complete!")
    print("="*60)

    # Parse keywords
    keyword, letters = parse_keywords(transcription)

    # Save results
    if keyword:
        with open("results.json", 'w') as f:
            json.dump({
                "keyword": keyword,
                "letters": {k: {"letter": v[0], "phonetic": v[1]} for k, v in letters.items()},
                "transcription_method": selected_method
            }, f, indent=2)

        print("\nResults saved to results.json")
        print(f"\n🚩 FLAG: {keyword}")
    else:
        print("\nWarning: No keyword found in transcription!")
        print("Check transcription.txt for the full transcription.")

if __name__ == "__main__":
    main()
