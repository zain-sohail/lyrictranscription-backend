import os
import subprocess
from fastapi import HTTPException

async def run_transcription(model_path: str, audio_path: str, language: str, translate: bool, timestamps: bool):
    if not os.path.exists(model_path):
        raise HTTPException(status_code=400, detail=f"Model not found: {model_path}")
    
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=400, detail=f"Audio file not found: {audio_path}")

    try:
        cmd = [
            "./backend/build_metal/bin/whisper-cli",
            "-m", os.path.abspath(model_path),
            "-f", os.path.abspath(audio_path),
            "-l", language,
            "-oj",  # Output JSON
        ]

        if translate:
            cmd.append("-tr")
        if not timestamps:
            cmd.append("-nt")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        output, error = process.communicate()
        
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Transcription failed: {error.decode('utf-8')}")
        
        decoded_str = output.decode('utf-8').strip()
        processed_str = decoded_str.replace('[BLANK_AUDIO]', '').strip()
        
        return {
            "text": processed_str,
            "language": language,
            "translated": translate
        }

    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)