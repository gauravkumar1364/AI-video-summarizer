import yt_dlp
from pydub import AudioSegment
import os
import glob

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Minimum chunk duration in milliseconds (1 second).
# Chunks shorter than this are skipped to avoid Whisper tensor errors.
MIN_CHUNK_MS = 1000


def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "restrictfilenames": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # Build the expected filename from the info dict
        base = ydl.prepare_filename(info)
        # The postprocessor changes the extension to .wav
        wav_path = os.path.splitext(base)[0] + ".wav"

    if not os.path.exists(wav_path):
        # Fallback: look for any .wav file in the download directory
        wav_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.wav"))
        if wav_files:
            wav_path = max(wav_files, key=os.path.getmtime)
        else:
            raise FileNotFoundError(
                f"Could not find downloaded WAV file. Expected: {wav_path}"
            )

    # Normalize to 16 kHz mono — Whisper expects this format;
    # yt-dlp may produce stereo / 44.1 kHz audio that causes tensor errors.
    print(f"Normalizing downloaded audio to 16 kHz mono…")
    audio = AudioSegment.from_file(wav_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(wav_path, format="wav")

    print(f"Downloaded audio: {wav_path}")
    return wav_path


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # 16 kHz mono
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    # Ensure source is 16 kHz mono before chunking
    audio = audio.set_channels(1).set_frame_rate(16000)
    
    # Usage Cap: Max 10 minutes (600,000 ms) for the shared demo key
    MAX_DURATION_MS = 10 * 60 * 1000
    if len(audio) > MAX_DURATION_MS:
        raise ValueError(f"Video is too long ({len(audio) // 60000} mins). The shared demo is capped at 10 minutes to prevent abuse. Please clone the repo to process longer videos!")

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]

        # Skip chunks that are too short — they cause Whisper tensor errors
        if len(chunk) < MIN_CHUNK_MS:
            print(f"  Skipping chunk {i} — too short ({len(chunk)}ms)")
            continue

        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
