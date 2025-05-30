"""
FastAPI server for Voice Translation Web Interface
"""
import os
import io
import logging
import re

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import openai
from pydantic import BaseModel
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    raise RuntimeError("OPENAI_API_KEY environment variable not set")

app = FastAPI()
# Allow CORS for all origins (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/translate")
async def translate_audio(
    file: UploadFile = File(...),
    target_lang: str = Form(...),
):
    """
    Receive an audio file, transcribe and translate to target language.
    """
    if file.content_type.split('/')[0] != 'audio':
        raise HTTPException(status_code=400, detail="Invalid file type")
    # Read audio data
    audio_bytes = await file.read()
    # Transcription (auto-detect language)
    # Transcribe audio using Whisper
    try:
        # Wrap bytes in BytesIO and give it a filename so the API can detect format
        audio_buffer = io.BytesIO(audio_bytes)
        audio_buffer.name = "recording.webm"
        transcription_resp = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_buffer,
            prompt="Здравствуйте, добро пожаловать на мою лекцию",
        )
        # The response has a .text attribute with the transcript
        transcript = transcription_resp.text
    except Exception as e:
        logger.exception("Failed to transcribe audio")
        raise HTTPException(status_code=500, detail=f"Transcription error: {e}")


    # Translate the transcript to English using GPT-4 mini
    try:
        system_prompt = """You are a highly skilled translator. Your task is to accurately translate user input from Russian to English or English to Russian, depending on the input language.

Your translation must:
- Preserve the original meaning as closely as possible
- Maintain the original tone and intonation
- Accurately convey idiomatic expressions and cultural nuances

Provide only the translated text in your output, without any additional comments, explanations, or clarifications. Respond strictly with the translation."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript},
        ]
        chat_resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
        )
        translation = chat_resp.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("Text translation via GPT-4 mini failed")
        raise HTTPException(status_code=500, detail=f"Translation error: {e}")
    return {"transcription": transcript, "translation": translation}

# Request model for text-only translation
class TextTranslateRequest(BaseModel):
    text: str

@app.post("/api/translate_text")
async def translate_text(request: TextTranslateRequest):
    """
    Translate arbitrary text to English using GPT-4 Mini
    """
    transcript = request.text

    import re
    if not re.search('[a-zA-Zа-яА-Я]', transcript):
        return {"translation": transcript}

    system_prompt = """You are a highly skilled translator. Your task is to accurately translate user input from Russian to English or English to Russian, depending on the input language.

Your translation must:
- Preserve the original meaning as closely as possible
- Maintain the original tone and intonation
- Accurately convey idiomatic expressions and cultural nuances

Provide only the translated text in your output, without any additional comments, explanations, or clarifications. Respond strictly with the translation."""
    try:
        chat_resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript},
            ],
            temperature=0.3,
        )
        translation = chat_resp.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("Text translation via GPT-4 mini failed")
        raise HTTPException(status_code=500, detail=f"Translation error: {e}")
    return {"translation": translation}

# Serve static files (UI)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
