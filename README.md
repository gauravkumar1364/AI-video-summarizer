# 🎬 AI Video Assistant (Summarizer & Meeting Intelligence)

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenAI Whisper](https://img.shields.io/badge/Whisper-412991?style=for-the-badge&logo=openai&logoColor=white)
![Mistral AI](https://img.shields.io/badge/Mistral_AI-000000?style=for-the-badge)

A powerful, AI-driven Meeting Intelligence Platform and Video Summarizer. Simply provide a YouTube URL or a local audio/video file, and let AI do the heavy lifting!

This app automatically downloads, transcribes, summarizes, and extracts key action items from your videos. It even features a built-in **RAG (Retrieval-Augmented Generation) Chat Engine**, allowing you to ask direct questions about the video's content.

---

## ✨ Features

- **📺 Universal Input**: Paste a YouTube URL or upload a local audio/video file.
- **🗣️ Advanced Transcription**: 
  - English transcription powered by local **OpenAI Whisper**.
  - Hinglish transcription & translation powered by **Sarvam AI**.
- **🧠 AI Summarization & Extraction**: Uses **Mistral AI** to automatically generate:
  - Concise Summaries
  - Action Items
  - Key Decisions
  - Open Questions
- **💬 Chat with Video**: A built-in RAG Engine allows you to chat directly with your transcript to extract precise details.
- **⚡ Real-Time Progress**: A sleek, dark-themed Streamlit UI with real-time dynamic pipeline status updates.

---

## 🚀 Quick Start Guide

### 1️⃣ Prerequisites
- **Python 3.10+** installed on your system.
- **FFmpeg** installed (Required for audio extraction).
  - *Windows*: `choco install ffmpeg`
  - *Mac*: `brew install ffmpeg`
  - *Linux*: `sudo apt install ffmpeg`

### 2️⃣ Installation
Clone the repository and install the dependencies:
```bash
git clone https://github.com/gauravkumar1364/AI-video-summarizer.git
cd AI-video-summarizer

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install required packages
pip install -r Requirements.txt
```

### 3️⃣ Configuration
Copy the example environment file and add your API keys:
```bash
cp .env.example .env
```
Open `.env` and configure:
- `MISTRAL_API_KEY`: Your Mistral AI API key (get it from console.mistral.ai)
- `SARVAM_API_KEY`: Your Sarvam API key (if you want Hinglish translation)

*Note: You can also enter the Mistral API key directly into the Streamlit sidebar when running the app!*

### 4️⃣ Run the App
Launch the Streamlit interface:
```bash
streamlit run app.py
```
The app will automatically open in your browser at `http://localhost:8501`.

---

## 🛠️ Tech Stack
- **Frontend**: Streamlit (with custom premium CSS injection)
- **Transcription**: `whisper`, `sarvam-ai`
- **Audio Processing**: `yt-dlp`, `pydub`, `ffmpeg`
- **LLM / Generation**: Mistral API, LangChain (for RAG)

---

## 💡 How It Works
1. **Audio Extraction**: `yt-dlp` extracts the highest quality audio from YouTube. The file is normalized to 16kHz Mono.
2. **Chunking**: Long audio is chunked intelligently to prevent memory overloads and tensor dimension errors.
3. **Transcription**: The chunks are transcribed sequentially and combined.
4. **Insights Pipeline**: The full transcript is sent to Mistral AI via customized prompts to extract structured insights.
5. **RAG Context**: The transcript is vectorized, allowing you to prompt the LLM directly about the meeting context.