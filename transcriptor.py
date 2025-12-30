import os
import sys
from pathlib import Path
from typing import Any
import whisper
from transformers import pipeline
from tqdm import tqdm
import json
from datetime import datetime
import yt_dlp
import shutil
import subprocess


class YouTubeTranscriptor:
    def __init__(self, output_dir="transcripts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Video metadata
        self.video_title = "Unknown"
        self.video_id = "Unknown"
        
        # Check for FFmpeg
        self.ffmpeg_available = self._check_ffmpeg()
        
        # Initialize models
        print("Loading Whisper model...")
        self.whisper_model = whisper.load_model("base")
        
        print("Loading summarization model...")
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
    def _check_ffmpeg(self):
        """Check if FFmpeg is available in system"""
        # Try to find FFmpeg in common installation locations
        if sys.platform == 'win32':
            common_paths = [
                os.path.expandvars(r'%LOCALAPPDATA%\\Microsoft\\WinGet\\Packages'),
                r'C:\\ffmpeg\\bin',
                r'C:\\Program Files\\ffmpeg\\bin',
            ]
            
            # Search for FFmpeg in common paths
            for base_path in common_paths:
                if os.path.exists(base_path):
                    for root, dirs, files in os.walk(base_path):
                        if 'ffmpeg.exe' in files:
                            ffmpeg_dir = root
                            if ffmpeg_dir not in os.environ['PATH']:
                                os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']
                                print(f"✅ Found FFmpeg in: {ffmpeg_dir}")
                            break
        
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, timeout=5)
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
            print("❌ FFmpeg not found in PATH!")
            print("   FFmpeg is REQUIRED for this tool to work.")
            print("   Please install FFmpeg: https://ffmpeg.org/download.html")
            print("   Windows: winget install Gyan.FFmpeg")
            print("   macOS: brew install ffmpeg")
            print("   Linux: sudo apt install ffmpeg")
            sys.exit(1)
        
    def download_audio(self, youtube_url):
        """Download audio from YouTube video"""
        print(f"\n📥 Downloading audio from: {youtube_url}")
        
        try:
            # If FFmpeg is available, download as mp3
            if self.ffmpeg_available:
                ydl_opts: dict[str, Any] = {
                    'format': 'bestaudio[ext=mp3]/bestaudio/best',
                    'outtmpl': str(self.temp_dir / 'audio'),
                    'quiet': False,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': 192,
                    }],
                }
            else:
                # Download as best available audio format (usually webm/opus)
                ydl_opts: dict[str, Any] = {
                    'format': 'bestaudio/best',
                    'outtmpl': str(self.temp_dir / 'audio'),
                    'quiet': False,
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # type: ignore
                info = ydl.extract_info(youtube_url, download=True)
                # Store video metadata
                self.video_title = info.get('title', 'Unknown')
                self.video_id = info.get('id', 'Unknown')
            
            # Find the downloaded file
            audio_files = list(self.temp_dir.glob('audio*'))
            if audio_files:
                audio_path = audio_files[0]
                print(f"✅ Audio downloaded successfully ({audio_path.name})")
                return audio_path
            else:
                print("❌ No audio file found after download")
                sys.exit(1)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error downloading audio: {error_msg}")
            sys.exit(1)
    
    def transcribe_audio(self, audio_path):
        """Transcribe audio using Whisper"""
        print(f"\n🎤 Transcribing audio... (this may take a few minutes)")
        
        try:
            # Convert Path to string and verify file exists
            audio_file = Path(audio_path)
            if not audio_file.exists():
                print(f"❌ Audio file not found: {audio_file}")
                print(f"Looking for audio files in {self.temp_dir}...")
                audio_files = list(self.temp_dir.glob('audio*'))
                if audio_files:
                    audio_file = audio_files[0]
                    print(f"Found: {audio_file}")
                else:
                    print("❌ No audio files found")
                    sys.exit(1)
            
            # Whisper supports many formats: mp3, wav, m4a, opus, webm, etc.
            result = self.whisper_model.transcribe(str(audio_file), verbose=False, language='en')
            transcript = result['text']
            print("✅ Transcription completed")
            return transcript
            
        except Exception as e:
            import traceback
            print(f"❌ Error during transcription: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            sys.exit(1)
    
    def extract_key_points(self, text, num_sentences=5):
        """Extract key points using summarization"""
        print(f"\n🎯 Extracting key points...")
        
        try:
            # Split text into sentences
            sentences = text.replace(".", ".\n").split("\n")
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) < 3:
                return text
            
            # Create summary to identify key points
            max_length = min(150, len(sentences) // 2)
            min_length = min(50, max_length - 10)
            
            summary = self.summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
            key_points = summary[0]['summary_text']
            
            print("✅ Key points extracted")
            return key_points
            
        except Exception as e:
            print(f"⚠️  Could not extract key points: {e}")
            return text[:500] + "..."
    
    def save_results(self, url, transcript, key_points):
        """Save transcript and summary to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create safe filename from video title
        safe_title = self._sanitize_filename(self.video_title)
        base_name = f"{safe_title}_{timestamp}"
        
        # Save JSON file
        json_file = self.output_dir / f"{base_name}.json"
        results = {
            "title": self.video_title,
            "url": url,
            "video_id": self.video_id,
            "timestamp": timestamp,
            "transcript": transcript,
            "key_points": key_points,
            "transcript_length": len(transcript),
            "key_points_length": len(key_points)
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save human-readable text file
        text_file = self.output_dir / f"{base_name}.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"YOUTUBE VIDEO TRANSCRIPT\n")
            f.write(f"{'='*80}\n\n")
            f.write(f"Title: {self.video_title}\n")
            f.write(f"URL: {url}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\n{'='*80}\n")
            f.write(f"KEY POINTS & SUMMARY\n")
            f.write(f"{'='*80}\n\n")
            f.write(key_points)
            f.write(f"\n\n{'='*80}\n")
            f.write(f"FULL TRANSCRIPT\n")
            f.write(f"{'='*80}\n\n")
            f.write(transcript)
        
        print(f"\n💾 Results saved to:")
        print(f"   JSON: {json_file}")
        print(f"   Text: {text_file}")
        return json_file
    
    def _sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        # Limit length and strip whitespace
        filename = filename.strip()[:100]
        return filename
    
    def cleanup(self):
        """Remove temporary files"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def process_video(self, youtube_url):
        """Main processing pipeline"""
        try:
            # Step 1: Download
            audio_path = self.download_audio(youtube_url)
            
            # Step 2: Transcribe
            transcript = self.transcribe_audio(audio_path)
            
            # Step 3: Extract key points
            key_points = self.extract_key_points(transcript)
            
            # Step 4: Save results
            output_file = self.save_results(youtube_url, transcript, key_points)
            
            # Display results
            print("\n" + "="*60)
            print("TRANSCRIPT")
            print("="*60)
            transcript_str = str(transcript)
            print((transcript_str[:1000] + "...") if len(transcript_str) > 1000 else transcript_str)
            
            print("\n" + "="*60)
            print("KEY POINTS & SUMMARY")
            print("="*60)
            print(key_points)
            
            return {
                "success": True,
                "output_file": str(output_file),
                "transcript": transcript,
                "key_points": key_points
            }
            
        finally:
            # Cleanup temp files
            self.cleanup()


def main():
    if len(sys.argv) < 2:
        print("Usage: python transcriptor.py <YouTube_URL>")
        print("\nExample: python transcriptor.py 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'")
        sys.exit(1)
    
    youtube_url = sys.argv[1]
    
    # Validate URL
    if "youtube.com" not in youtube_url and "youtu.be" not in youtube_url:
        print("❌ Please provide a valid YouTube URL")
        sys.exit(1)
    
    # Process video
    transcriptor = YouTubeTranscriptor()
    result = transcriptor.process_video(youtube_url)
    
    if result["success"]:
        print("\n✨ Done! Check the output file for full results.")
    

if __name__ == "__main__":
    main()
