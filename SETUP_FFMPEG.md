# FFmpeg Setup Instructions

Whisper (the transcription tool) requires FFmpeg to be installed **and available in your system PATH**.

## What Happened

FFmpeg was installed by winget, but you need to **restart your terminal** for the PATH changes to take effect.

## Solution

### Option 1: Restart Your Terminal (Recommended)
1. Close this PowerShell terminal completely
2. Open a new PowerShell terminal
3. Navigate back to the project:
   ```bash
   cd C:\Users\Jovanny\Desktop\Projects\video-transcript
   ```
4. Test FFmpeg is working:
   ```bash
   ffmpeg -version
   ```
5. Run the transcriptor again:
   ```bash
   python transcriptor.py "https://www.youtube.com/watch?v=H895ZcG13Hg"
   ```

### Option 2: Add FFmpeg to PATH in Current Session
```powershell
$env:Path += ";C:\ffmpeg\bin"
ffmpeg -version
python transcriptor.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Option 3: Use YouTube's Built-in Captions (If Available)

I can create a simpler version that only downloads videos with existing captions and skips transcription entirely.

## Verify FFmpeg Installation

Run this to check if FFmpeg is installed:
```powershell
where.exe ffmpeg
```

If it shows a path, FFmpeg is installed. If not, run:
```powershell
winget install ffmpeg
```

Then restart your terminal!
