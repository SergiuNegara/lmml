# Solution for Mr. Whiskerstein's Lecture Task

## Overview

This solution transcribes the 7h 50min audio lecture and automatically extracts the keyword by finding phrases that follow the pattern:
- "The Nth letter in keyword is X, [NATO phonetic alphabet]"

## Setup

1. **Virtual Environment** (already created):
   ```bash
   source venv/bin/activate
   ```

2. **Dependencies Installed**:
   - `openai` - For OpenAI Whisper API
   - `pydub` - For audio processing
   - `SpeechRecognition` - Alternative transcription method
   - `ffmpeg` - Required by pydub for audio handling

## Usage

### Method 1: OpenAI Whisper API (Recommended - Fast & Accurate)

This is the recommended method for a 7.5-hour audio file.

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Run transcription with OpenAI
source venv/bin/activate
python transcribe_audio.py --method openai
```

**Pros:**
- High accuracy
- Handles long files well
- Relatively fast (~47 chunks of 10 minutes each)

**Cons:**
- Requires OpenAI API key
- Costs money (approximately $0.006/minute, so ~$2.82 for the full audio)

### Method 2: Google Speech Recognition (Free but Slow)

```bash
source venv/bin/activate
python transcribe_audio.py --method google
```

**Pros:**
- Free
- No API key needed

**Cons:**
- Very slow for long files
- Rate limits may apply
- May timeout or fail on very long files

### Using Existing Transcription

If you already have a `transcription.txt` file:

```bash
python transcribe_audio.py --parse-only
```

## How It Works

1. **Audio Splitting**: The script splits the large MP3 file into manageable chunks
   - OpenAI method: 10-minute chunks (API limit is 25MB)
   - Google method: 60-second chunks

2. **Transcription**: Each chunk is sent to the transcription API
   - Progress is saved to `transcription.txt` as it goes
   - Keywords are checked periodically

3. **Keyword Extraction**: The script uses regex to find patterns like:
   ```
   The 1st letter in keyword is A, Alpha.
   The 2nd letter in keyword is B, Bravo.
   ```

4. **Results**:
   - The keyword is printed to console
   - Results are saved to `results.json` with full details

## Output Files

- `transcription.txt` - Full transcription of the audio (created during processing)
- `results.json` - Extracted keyword and letter positions
- Temporary audio chunks (automatically cleaned up)

## Script Options

```bash
python transcribe_audio.py --help
```

Options:
- `--method {openai,google}` - Choose transcription method (default: openai)
- `--audio FILENAME` - Specify audio file (default: audio_task_43.mp3)
- `--use-existing` - Use existing transcription.txt if available
- `--parse-only` - Only parse existing transcription, don't transcribe

## Expected Runtime

- **OpenAI API**: ~15-30 minutes (depending on API response time)
- **Google API**: Several hours (due to rate limits and chunk processing)

## Cost Estimate (OpenAI)

For a 7h 50min (470 minutes) audio file:
- Rate: $0.006 per minute
- Total: 470 × $0.006 = $2.82

## Troubleshooting

### "ffmpeg not found"
Install ffmpeg:
```bash
brew install ffmpeg
```

### "OpenAI API key not found"
Set your API key:
```bash
export OPENAI_API_KEY="your-key"
```

### "Rate limit exceeded"
- For OpenAI: Wait a moment and try again
- For Google: This method may not work for very long files

### Script crashes midway
The script saves progress to `transcription.txt`. You can:
1. Check what was transcribed so far
2. Manually parse it: `python transcribe_audio.py --parse-only`
