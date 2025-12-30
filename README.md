# YouTube Video Transcriptor & Summarizer

A command-line tool to extract transcripts from YouTube videos and generate summaries with key points using free, open-source APIs.

## Features

- ✅ Download audio from YouTube videos
- ✅ Transcribe audio to text using OpenAI Whisper
- ✅ Extract key points and create summaries
- ✅ Save results as JSON for easy processing
- ✅ 100% free (no paid API keys required)

## Tech Stack

- **Video Download**: `yt-dlp` - Downloads YouTube videos
- **Transcription**: `OpenAI Whisper` - State-of-the-art speech recognition
- **Summarization**: `Facebook BART` (via HuggingFace) - Extractive summarization
- **Language**: Python 3.8+

## Installation

### 1. Clone/Setup the project
```bash
cd video-transcript
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `yt-dlp` - YouTube downloader
- `openai-whisper` - Transcription model
- `transformers` - NLP models
- `torch` - Deep learning framework
- `numpy` - Numerical computing

**Note**: First run will download ~1GB of model files (Whisper + BART). Subsequent runs are faster.

### 3. Verify installation
```bash
python transcriptor.py
```

Should show usage instructions if working correctly.

## Usage

### Basic Usage
```bash
python transcriptor.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Example
```bash
python transcriptor.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Output

Results are saved in the `transcripts/` folder as JSON files containing:
- Full transcript
- Key points & summary
- Video URL and timestamp
- Transcript length information

## Output Format

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "timestamp": "20251230_143022",
  "transcript": "Full transcribed text...",
  "key_points": "Extracted summary with key points...",
  "transcript_length": 5342,
  "key_points_length": 1240
}
```

## How It Works

1. **Download** - Uses `yt-dlp` to extract MP3 audio from YouTube
2. **Transcribe** - OpenAI Whisper converts audio to text (no internet required after download)
3. **Summarize** - Facebook BART model extracts key points and creates summary
4. **Save** - Results saved as JSON in `transcripts/` folder

## System Requirements

- Python 3.8 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB disk space for models
- Internet connection for downloading videos and models

## Supported Video Types

- Regular YouTube videos
- YouTube Shorts
- Livestream recordings
- Playlist URLs (processes first video)

## Limitations & Notes

- **Model Download**: First run takes time as models (~1GB) are downloaded
- **Processing Time**: Depends on video length (15min video ≈ 2-5 minutes processing)
- **Audio Quality**: Automatically downloads best available MP3 (192kbps)
- **Language**: Works best with English; Whisper supports 99 languages but summarization is English-focused

## Troubleshooting

### "yt-dlp not found"
```bash
pip install --upgrade yt-dlp
```

### "cuda not found" (can be ignored)
The tool works fine on CPU. GPU will make it faster but is optional.

### "Invalid YouTube URL"
Make sure URL is a valid YouTube link:
- ✅ `https://www.youtube.com/watch?v=VIDEO_ID`
- ✅ `https://youtu.be/VIDEO_ID`
- ❌ `youtube.com/watch` (missing video ID)

## Tips for Best Results

1. **Longer videos** (15+ min) produce better summaries
2. **Clear audio** improves transcription accuracy
3. **English videos** work best (though other languages are supported)
4. Run on a machine with idle CPU for faster processing

## Advanced Usage

You can modify the script to:
- Change Whisper model size (`base`, `small`, `medium`, `large`)
- Adjust summary length
- Process multiple videos in batch
- Export to different formats (CSV, TXT, etc.)

## Free Alternatives Comparison

| Feature | This Tool | YouTube Captions | Paid Services |
|---------|-----------|-----------------|---------------|
| Cost | Free | Free* | $$ |
| Works Offline | Yes (after download) | No | No |
| Accuracy | High | Low-Medium | High |
| Summarization | Yes | No | Yes |
| No watermarks | Yes | Yes | Yes |

*YouTube captions may not be available for all videos

## License

This project is open source and free to use.

## Contributing

Feel free to fork and improve!
