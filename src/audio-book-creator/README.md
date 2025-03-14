# 🎧 Audiobook Creator

> Transform any text into natural audiobooks using AI. Built with FastAPI and Sesame CSM-1b. Simple, fast, and production-ready.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

## ✨ Features

* 🎯 **One-Shot Generation**: Process entire books at once
* 🎭 **Voice Cloning**: Multiple voice options with customization
* ⚡ **Async Processing**: Background tasks for large books
* 📱 **Modern UI**: Clean Streamlit interface
* 💾 **Easy Export**: Download audiobooks in WAV format

## 🚀 Quick Start

### Prerequisites

* Python 3.10+
* Hugging Face Account
* CSM-1b Model Access

### Setup in 3 Steps

1. **Clone & Install**
```bash
git clone <your-repo-url>
cd audiobook-creator
pip install -r requirements.txt
```

2. **Configure**
```bash
# Add your HF token to environment
export HF_TOKEN="your_token_here"
```

3. **Launch**
```bash
# Start the API server
python app.py

# In a new terminal, launch UI
streamlit run ui.py
```

Visit `http://localhost:8501` to start creating audiobooks!

## 🎮 Basic Usage

### Create an Audiobook
```python
import requests

# Start a new audiobook
response = requests.post(
    "http://localhost:8000/audiobook/",
    data={
        "title": "My Book",
        "author": "Me",
        "voice_id": 0,
        "text_content": "Once upon a time..."
    }
)

book_id = response.json()["book_id"]
```

### Check Status
```python
status = requests.get(f"http://localhost:8000/audiobook/{book_id}")
print(status.json()["status"])  # 'processing', 'completed', or 'failed'
```

### Download Audio
```python
if status.json()["status"] == "completed":
    audio = requests.get(f"http://localhost:8000/audiobook/{book_id}/audio")
    with open("my_book.wav", "wb") as f:
        f.write(audio.content)
```

## 🎛️ Advanced Configuration

### Voice Customization
```python
# Upload a custom voice sample
with open("voice.wav", "rb") as f:
    requests.post(
        "http://localhost:8000/voice/upload",
        files={"file": f},
        data={"voice_id": 1}
    )
```

## 📈 Resource Usage

The CSM-1b model requires:
* ~2GB GPU memory (inference)
* ~5GB disk space (model weights)
* Processing time: ~1min per 1000 words

## 🤝 Contributing

We welcome:
* Bug reports
* Feature requests
* Pull requests
* Documentation improvements

## 🔮 Roadmap

* 📑 Chapter detection & organization
* 🎵 Background music support
* 🎭 Multi-character voice switching
* 📱 EPUB/PDF parsing
* ⚡ Batch processing

## 📝 License

This project uses the Sesame CSM-1b model under the Apache 2.0 license.

---

Made with ❤️ by [Mahimai Raja]()