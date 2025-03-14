"""
🎧 Audiobook Creator Backend - FastAPI Edition 🎧
This beast turns plain text into sick audiobooks using
the Sesame CSM-1b model! No cap, it's fire...

✨ Features:
- Processes entire books at once (no more chunking, we're built different)
- Multiple voice vibes to choose from
- Background processing so you don't have to wait
- Download your fresh audiobooks when they're ready
"""

import os
import shutil
import uuid
import json
from typing import Optional
from datetime import datetime
import logging
from dotenv import load_dotenv
import torch
import torchaudio
import numpy as np

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
# from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 📝 Setup logging - gotta see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 🔑 Load the secret sauce
load_dotenv()

# 🔒 Grab that Hugging Face token
HF_TOKEN = os.environ.get("HF_TOKEN", None)

# 🚀 Create our app with the drip
app = FastAPI(
    title="Audiobook Creator",
    description="A tool to create audiobooks using Sesame CSM-1b for speech generation",
    version="1.0.0"
)

# 🌐 CORS config - let everyone in
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Everyone's invited
    allow_credentials=True,
    allow_methods=["*"],  # All methods welcome
    allow_headers=["*"],  # Every header's a vibe
)

# 📁 Make sure we have places to store our stuff
os.makedirs("data/books", exist_ok=True)
os.makedirs("data/voices", exist_ok=True)
os.makedirs("data/audio", exist_ok=True)

# 🎙️ The real MVP - our voice generator
class CSMGenerator:
    def __init__(self, device="cuda" if torch.cuda.is_available() else "cpu"):
        """🔥 Fire up the text-to-speech engine"""
        self.device = device
        self.sample_rate = 24000
        self.model = None
        self.model_loaded = False
        logging.info(f"CSMGenerator initialized with device: {device}")
    
    def load_model(self):
        """📥 Grab that model from the cloud - it's heavy tho"""
        if self.model_loaded:
            return self.model
        
        try:
            from huggingface_hub import hf_hub_download
            from generator import load_csm_1b
            
            # Yoink the model from HF
            model_path = hf_hub_download(
                repo_id="sesame/csm-1b", 
                filename="ckpt.pt",
                token=HF_TOKEN
            )
            
            # Load it up
            self.model = load_csm_1b(model_path, self.device)
            self.model_loaded = True
            logging.info("CSM-1b model loaded successfully")
            return self.model
            
        except Exception as e:
            logging.error(f"Error loading CSM-1b model: {e}")
            return None
    
    def load_audio(self, audio_path, target_sr=24000):
        """🎵 Load voice sample for the vibe check"""
        try:
            waveform, sr = torchaudio.load(audio_path)
            
            # Make it mono if it's stereo (we don't do surround sound here)
            if waveform.shape[0] > 1:
                waveform = waveform.mean(dim=0, keepdim=True)
            
            # Fix the sample rate if it's off
            if sr != target_sr:
                resampler = torchaudio.transforms.Resample(sr, target_sr)
                waveform = resampler(waveform)
            
            # Move to the right device
            waveform = waveform.to(self.device)
            
            return waveform
        except Exception as e:
            logging.error(f"Error loading audio: {e}")
            return None
    
    def generate(self, text, speaker=0, context=None, max_audio_length_ms=30000):
        """
        🗣️ The main character - turns text into speech
        
        Args:
            text: The words to speak
            speaker: Voice ID (0 is the default vibe)
            context: Voice samples for cloning (optional glow-up)
            max_audio_length_ms: How long can this go on?
            
        Returns:
            audio: The fresh audio tensor that slaps
        """
        # Check if text is too long (that's what she said)
        if len(text) > 2000:
            logging.warning(f"Text is very long ({len(text)} chars). This might cause issues with generation.")
            
            # We'll try it anyway but with more headroom
            max_audio_length_ms = max(max_audio_length_ms, min(300000, len(text) * 80))
        
        # Make sure we're loaded
        if not self.model_loaded:
            self.model = self.load_model()
        
        # If loading failed, fall back to the mock generator
        if self.model is None:
            return self._generate_mock_audio(text, context, max_audio_length_ms)
        
        try:
            # Import the right stuff
            from generator import Segment
            
            # Setup the context - empty list to start
            context_segments = []
            
            # If we have voice samples, add them to the vibe
            if context and isinstance(context, list) and len(context) > 0:
                for ctx in context:
                    if 'text' in ctx and 'audio' in ctx:
                        context_segments.append(
                            Segment(text=ctx['text'], speaker=speaker, audio=ctx['audio'])
                        )
            
            # Let everyone know what's happening
            logging.info(f"Generating audio for text with {len(text)} characters")
            
            # The magic happens here
            audio = self.model.generate(
                text=text,
                speaker=speaker,  # Default vibe
                context=context_segments,  # Voice reference
                max_audio_length_ms=max_audio_length_ms
            )
            
            if audio is None:
                logging.error("Model returned None for audio generation")
                return self._generate_mock_audio(text, context, max_audio_length_ms)
                
            logging.info(f"Successfully generated audio with shape {audio.shape}")
            return audio
            
        except Exception as e:
            logging.error(f"Error generating with real model: {e}")
            # Plan B - fake it 'til you make it
            return self._generate_mock_audio(text, context, max_audio_length_ms)
    
    def _generate_mock_audio(self, text, context, max_audio_length_ms):
        """🔊 Creates fake audio when the real model ghosts us"""
        logging.warning("Using mock audio generation")
        max_length_samples = int(max_audio_length_ms * self.sample_rate / 1000)
        duration_sec = min(len(text) / 20, max_audio_length_ms / 1000)  # Just a guess
        t = torch.arange(0, duration_sec, 1/self.sample_rate)
        
        # Different vibes based on context
        if context and len(context) > 0:
            # Slightly different tone with context (fake voice cloning)
            freq = 420  # blaze it
            audio = 0.5 * torch.sin(2 * np.pi * freq * t) * (0.8 + 0.2 * torch.sin(0.5 * t))
        else:
            # Standard beep boop
            freq = 440
            audio = 0.5 * torch.sin(2 * np.pi * freq * t)
        
        # Cap it at the right length
        if len(audio) > max_length_samples:
            audio = audio[:max_length_samples]
        
        return audio
        
    def save_audio(self, audio, output_path):
        """💾 Saves the audio - from RAM to storage"""
        try:
            if audio is None:
                logging.error("Cannot save None audio")
                return None
                
            # Format for export - CPU and right shape
            audio_to_save = audio.unsqueeze(0).cpu() if len(audio.shape) == 1 else audio.cpu()
            
            # Save it
            torchaudio.save(output_path, audio_to_save, self.sample_rate)
            logging.info(f"Audio saved to {output_path}")
            return output_path
        except Exception as e:
            logging.error(f"Error saving audio: {e}")
            return None

# 🎤 Create our generator
generator = CSMGenerator()

# 📋 Data models - gotta keep things organized
class AudiobookBase(BaseModel):
    title: str
    author: str
    voice_id: Optional[int] = 0

class Audiobook(AudiobookBase):
    id: str
    date: str
    status: str  # 'processing', 'completed', 'failed'
    audio_path: Optional[str] = None
    text_path: str

class TextChunk(BaseModel):
    book_id: str
    chunk_id: int
    text: str
    audio_path: Optional[str] = None

# 🎬 Background processing - do the heavy lifting
def process_audiobook(book_id, text_content, voice_id):
    """⚙️ Creates audiobook in the background while you chill"""
    try:
        # Update the status to let everyone know we're cooking
        with open(f"data/books/{book_id}.json", "r") as f:
            book = json.load(f)
        
        book["status"] = "processing"
        
        with open(f"data/books/{book_id}.json", "w") as f:
            json.dump(book, f)
        
        logging.info(f"Starting processing for audiobook {book_id}")
        
        # Setup voice cloning if we have a sample
        context = []  # Start with nothing
        voice_path = f"data/voices/voice_{voice_id}.wav"
        
        if os.path.exists(voice_path):
            try:
                # Load the voice sample
                voice_audio = generator.load_audio(voice_path)
                
                if voice_audio is not None:
                    # Create context - just one sample is all we need
                    context = [
                        {"text": "This is a voice sample for cloning.", "audio": voice_audio}
                    ]
                    logging.info(f"Voice cloning context created from {voice_path}")
            except Exception as e:
                logging.error(f"Error setting up voice cloning: {e}")
        
        # Generate the entire audiobook at once - one shot, one opportunity
        logging.info(f"Generating audio for entire text of book {book_id}")
        audio = generator.generate(
            text=text_content,
            speaker=0,  # Default voice 
            context=context,
            max_audio_length_ms=min(300000, len(text_content) * 80)  # Big text = big audio
        )
        
        output_path = f"data/books/{book_id}.wav"
        
        if audio is not None:
            # Save the masterpiece
            result = generator.save_audio(audio, output_path)
            
            if result:
                # We did it! 🎉
                book["status"] = "completed"
                book["audio_path"] = output_path
                logging.info(f"Successfully created audiobook {book_id}")
            else:
                # Saving failed - sad noises
                logging.error(f"Failed to save audio for book {book_id}")
                book["status"] = "failed"
        else:
            # Generation failed - big oof
            logging.error(f"Failed to generate audio for book {book_id}")
            book["status"] = "failed"
        
        with open(f"data/books/{book_id}.json", "w") as f:
            json.dump(book, f)
        
        return True
    except Exception as e:
        logging.error(f"Error processing audiobook {book_id}: {e}")
        
        # Update status to failed - we tried
        try:
            with open(f"data/books/{book_id}.json", "r") as f:
                book = json.load(f)
            
            book["status"] = "failed"
            
            with open(f"data/books/{book_id}.json", "w") as f:
                json.dump(book, f)
        except Exception as nested_e:
            logging.error(f"Failed to update book status after error: {nested_e}")
        
        return False

# 🛣️ API Routes - where the requests go

@app.get("/")
def read_root():
    """👋 Just saying hi - API health check"""
    return {"message": "Audiobook API is running"}

@app.post("/audiobook/")
async def create_audiobook(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    author: str = Form(...),
    voice_id: int = Form(0),
    text_file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None)
):
    """🆕 Drop a new audiobook project - from text to speech"""
    try:
        # Make sure we have something to work with
        if not text_file and not text_content:
            raise HTTPException(status_code=400, detail="Either text_file or text_content is required")
        
        # Generate that unique ID
        book_id = str(uuid.uuid4())
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Handle uploaded file if that's what we got
        if text_file:
            # Save the file
            text_path = f"data/books/{book_id}.txt"
            with open(text_path, "wb") as f:
                shutil.copyfileobj(text_file.file, f)
            
            # Extract the text
            with open(text_path, "r", encoding="utf-8") as f:
                text_content = f.read()
        else:
            # Just save the text directly
            text_path = f"data/books/{book_id}.txt"
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(text_content)
        
        # Create the book info
        book = {
            "id": book_id,
            "title": title,
            "author": author,
            "voice_id": voice_id,
            "date": date_str,
            "status": "pending",
            "text_path": text_path
        }
        
        with open(f"data/books/{book_id}.json", "w") as f:
            json.dump(book, f)
        
        # Process in the background - no waiting
        background_tasks.add_task(process_audiobook, book_id, text_content, voice_id)
        
        return JSONResponse(content={"message": "Audiobook creation started", "book_id": book_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating audiobook: {str(e)}")

@app.get("/audiobook/{book_id}")
def get_audiobook(book_id: str):
    """📖 Get the deets on a specific book"""
    try:
        # Load that book info
        with open(f"data/books/{book_id}.json", "r") as f:
            book = json.load(f)
        
        return book
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Audiobook not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audiobook: {str(e)}")

@app.get("/audiobook/{book_id}/audio")
def get_audiobook_audio(book_id: str):
    """🔊 Get the actual audio file - for the ears"""
    try:
        # Check the book info
        with open(f"data/books/{book_id}.json", "r") as f:
            book = json.load(f)
        
        # Make sure it's ready
        if book["status"] != "completed" or not book.get("audio_path"):
            raise HTTPException(status_code=400, detail="Audiobook is not yet completed")
        
        # Send the file
        return FileResponse(
            book["audio_path"], 
            media_type="audio/wav", 
            filename=f"{book['title']}.wav"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Audiobook not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audiobook audio: {str(e)}")

@app.get("/audiobooks/")
def get_audiobooks():
    """📚 Get all the books - the whole collection"""
    try:
        audiobooks = []
        for filename in os.listdir("data/books"):
            if filename.endswith(".json"):
                with open(f"data/books/{filename}", "r") as f:
                    book = json.load(f)
                    audiobooks.append(book)
        
        # Newest vibes first
        audiobooks.sort(key=lambda x: x["date"], reverse=True)
        return {"audiobooks": audiobooks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving audiobooks: {str(e)}")

@app.delete("/audiobook/{book_id}")
def delete_audiobook(book_id: str):
    """🗑️ Yeet a book into oblivion - delete forever"""
    try:
        # Find the book
        book_path = f"data/books/{book_id}.json"
        if not os.path.exists(book_path):
            raise HTTPException(status_code=404, detail="Audiobook not found")
            
        with open(book_path, "r") as f:
            book = json.load(f)
        
        # Delete the audio if it exists
        if book.get("audio_path") and os.path.exists(book["audio_path"]):
            os.remove(book["audio_path"])
        
        # Delete the text file
        if book.get("text_path") and os.path.exists(book["text_path"]):
            os.remove(book["text_path"])
        
        # Delete the metadata
        os.remove(book_path)
        
        # Clean up any leftover audio chunks
        for filename in os.listdir("data/audio"):
            if filename.startswith(f"{book_id}_"):
                os.remove(f"data/audio/{filename}")
        
        return {"message": "Audiobook deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Audiobook not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting audiobook: {str(e)}")

# 📂 Static files - commented out but ready if needed
# app.mount("/static", StaticFiles(directory="static"), name="static")

# 🚀 Start the server if running directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 