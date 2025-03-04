from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
from ..services.preprocessing import convert_to_wav

router = APIRouter()

@router.post("/convert",
    summary="Convert audio file to WAV format",
    description="Convert any audio format to WAV 16000 Hz using FFmpeg")
async def convert_audio(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()
        os.fsync(temp_file.fileno())  # Ensure file is written to disk
        return await convert_to_wav(temp_file.name)