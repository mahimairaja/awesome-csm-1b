# 🎙️ Awesome CSM-1b Applications

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.27.2-FF4B4B.svg)](https://streamlit.io/)
[![Modal](https://img.shields.io/badge/Modal-Cloud-6236FF.svg)](https://modal.com/)
[![CSM-1b](https://img.shields.io/badge/TTS-CSM_1b-FFA726.svg)](https://huggingface.co/sesame/csm-1b)

A collection of powerful applications built with the Sesame CSM-1b text-to-speech model. Generate natural-sounding speech with realistic qualities and voice cloning capabilities.

## 📚 Available Applications

| Application | Description | Key Features | Status |
|-------------|-------------|-------------|--------|
| [Personal Voice Diary](src/personal-voice-diary/) | Convert diary entries into natural-sounding speech | Voice cloning, entry management, playback | 🔜 Planned |
| [Audiobook Creator](src/audio-book-creator/) | Create audiobooks from any text | Text chunking, multiple voices, background processing | ✅ Complete |
| [Voice Message Creator](src/voice-message-creator/) | Generate sharable voice messages | Custom voices, QR codes, expiring messages | 🔜 Planned |
| [Story Narrator for Children](src/story-narrator-for-children/) | Narrate children's stories with character voices | Character voices, sound effects | 🔜 Planned |
| [Emotion-based Voice Generator](src/emotion-based-voice-generator/) | Generate speech with different emotions | Multiple emotion presets, intensity control | 🔜 Planned |
| [Voice Style Transfer](src/voice-style-transfer/) | Transfer voice to different speaking styles | Style presets, voice preservation | 🔜 Planned |
| [Voice-based Social Media Post Creator](src/voice-based-social-media-post-creator/) | Create audio for social media | Background music, platform templates | 🔜 Planned |
| [Multilingual Accent Tool](src/multilingual-accent-tool/) | Generate speech with different accents | Multiple accent options, pronunciation tools | 🔜 Planned |

## ✨ Features

* **Natural Voice Generation**: Create realistic speech with the power of CSM-1b
* **Voice Cloning**: Clone any voice from a short audio sample
* **Independent Applications**: Each app is fully self-contained and ready to use
* **Modern Architecture**: Built with FastAPI backends and Streamlit UIs
* **Cloud Deployment**: Configured for easy deployment with Modal
* **High Performance**: Optimized for both CPU and GPU environments

## 🚀 Getting Started

Getting started with any application is straightforward:

1. Clone the repository  
   ```
   git clone https://github.com/mahimairaja/awesome-csm-1b.git
   cd awesome-csm-1b
   ```

2. Choose an application  
   ```
   cd src/<app-name>
   ```

3. Install dependencies  
   ```
   pip install -r requirements.txt
   ```

4. Set up your Hugging Face token in a `.env` file  
   ```
   HF_TOKEN=your_hugging_face_token
   ```

5. Start the backend  
   ```
   python app.py
   ```

6. In a new terminal, start the UI  
   ```
   streamlit run ui.py
   ```

## 🛠️ Technologies Used

* **FastAPI**: Backend API framework
* **Streamlit**: User interface
* **PyTorch & Torchaudio**: Audio processing
* **Hugging Face**: Model access and management
* **Modal**: Cloud deployment

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Requirements

* Python 3.10 or higher
* Hugging Face account with access to CSM-1b model
* Hugging Face API token
* CUDA-compatible GPU recommended for optimal performance

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ by [Mahimai Raja](https://github.com/mahimairaja)
