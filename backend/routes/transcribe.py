from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
import tempfile
import aiohttp
import os
from ..services.transcription import run_transcription
from ..services.preprocessing import convert_to_wav
from ..services.splitting import split_audio

router = APIRouter()

class TranscriptionRequest(BaseModel):
    model_path: str
    audio_url: Optional[HttpUrl] = None
    language: str = "en"
    translate: bool = False
    timestamps: bool = True
    mixed_music: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "model_path": "/models/ggml-large-v3-turbo.bin",
                "audio_url": "https://example.com/audio.wav",
                "language": "en",
                "translate": False,
                "timestamps": True
            }
        }

@router.post("/file", 
    summary="Transcribe uploaded audio file",
    description="Upload and transcribe an audio file using the specified Whisper model")
async def transcribe_file(
    model_path: str = "/models/ggml-large-v3-turbo.bin",
    file: UploadFile = File(...),
    language: str = "en",
    translate: bool = False,
    timestamps: bool = True,
    mixed_music: bool = False
):
    try:
        # Use original file extension
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file.flush()
            os.fsync(temp_file.fileno())

            try:
                # Convert to WAV 16kHz if needed
                processed_path = await convert_to_wav(temp_file.name)
                
                if mixed_music:
                    separated_path = await split_audio(processed_path)
                    try:
                        return await run_transcription(model_path, separated_path, language, translate, timestamps)
                    finally:
                        if os.path.exists(separated_path) and separated_path != processed_path:
                            os.unlink(separated_path)
                else:
                    return await run_transcription(model_path, processed_path, language, translate, timestamps)

            finally:
                # Only delete processed file if it's different from the input file
                if os.path.exists(processed_path) and processed_path != temp_file.name:
                    os.unlink(processed_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)

@router.post("/url")
async def transcribe_url(request: TranscriptionRequest):
    async with aiohttp.ClientSession() as session:
        async with session.get(str(request.audio_url)) as response:
            if response.status != 200:
                raise HTTPException(status_code=400, detail="Could not download audio file")
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(await response.read())
                temp_file.flush()

                # Preprocess the audio file to WAV 16000Hz
                processed_path = await convert_to_wav(temp_file.name)

                if request.mixed_music:
                    # Separate vocals from music if requested
                    separated_path = await split_audio(processed_path)
                    # Use vocals track for transcription
                    return await run_transcription(request.model_path, separated_path, 
                                                 request.language, request.translate, 
                                                 request.timestamps)
                else:
                    return await run_transcription(request.model_path, processed_path,
                                                 request.language, request.translate,
                                                 request.timestamps)