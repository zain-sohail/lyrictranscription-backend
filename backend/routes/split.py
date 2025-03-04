from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
from ..services.splitting import split_audio

router = APIRouter()

@router.post("/separate",
    summary="Separate audio into stems",
    description="Separate audio into stems using Spleeter")
async def separate_audio(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()
        os.fsync(temp_file.fileno())  # Ensure file is written to disk
        return await split_audio(temp_file.name)