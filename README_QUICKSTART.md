# 🚀 Quick Start Guide

## Get Started in 5 Minutes!

### 1️⃣ Install FFmpeg (if not already installed)
```bash
# Check if FFmpeg is installed
ffmpeg -version

# If not installed, download from: https://ffmpeg.org/download.html
# Or use Chocolatey: choco install ffmpeg
```

### 2️⃣ Set Up API Key
```bash
# Copy the example env file
copy .env.example .env

# Edit .env and add your Mistral API key:
# MISTRAL_API_KEY=your_actual_key_here

# Get your key from: https://console.mistral.ai/
```

### 3️⃣ Run the Application

**Easiest Way (Windows):**
```bash
# Double-click quick_start.bat
# OR run:
quick_start.bat
```

**Manual Way:**
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows CMD)
venv\Scripts\activate.bat

# Install dependencies
pip install -r Requirements.txt

# Run Streamlit app
streamlit run app.py

# OR run CLI version
python main.py
```

### 4️⃣ Use the App
1. Open browser at `http://localhost:8501` (auto-opens)
2. Paste a YouTube URL or local file path
3. Select language (english/hinglish)
4. Click "⚡ Analyse"
5. Wait for processing (can take 2-10 minutes depending on video length)
6. View results and chat with your transcript!

---

## 📁 Project Structure
```
AI-Video-Assistant-/
├── app.py                  # Streamlit web interface ⭐
├── main.py                 # CLI interface
├── Requirements.txt        # Dependencies
├── .env                    # Your API keys (create this!)
├── quick_start.bat         # Windows quick start script
├── SETUP_GUIDE.md         # Detailed setup instructions
├── core/                   # AI processing modules
│   ├── transcriber.py     # Whisper speech-to-text
│   ├── summarizer.py      # LLM summarization
│   ├── extractor.py       # Extract items/decisions
│   └── rag_engine.py      # RAG chat functionality
└── utils/
    └── audio_processor.py # Audio extraction & chunking
```

---

## 🎯 What This App Does

1. **Transcribes** video/audio using OpenAI Whisper
2. **Summarizes** content using Mistral AI
3. **Extracts** action items, decisions, and questions
4. **Enables chat** with your transcript via RAG

---

## ⚡ Quick Tips

- First run downloads Whisper models (~100-400MB)
- Processing time depends on video length (1-10 minutes)
- GPU makes transcription much faster
- Mistral API usage incurs costs - monitor at console.mistral.ai
- Use shorter videos for testing (< 5 minutes)

---

## ❓ Need Help?

See **SETUP_GUIDE.md** for:
- Detailed installation steps
- Troubleshooting guide
- Configuration options
- Advanced usage

---

## 📊 Example Usage

**Try these YouTube videos for testing:**
- Short tech talks (5-10 min)
- Product demos
- Tutorial videos
- Meeting recordings

**Or use local files:**
- Meeting recordings (mp4, mp3)
- Lecture recordings
- Podcast episodes
- Interview recordings

---

## ✅ System Requirements

- **Python:** 3.10 or higher
- **RAM:** 4GB minimum (8GB+ recommended)
- **Disk:** 2GB free space for models
- **Internet:** Required for YouTube downloads and API calls
- **FFmpeg:** Must be installed

---

🎉 **That's it! You're ready to go!**
