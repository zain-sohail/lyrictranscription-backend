import subprocess
import json
import os
from fastapi import HTTPException

async def get_audio_info(input_path: str) -> dict:
    """Get audio file information using ffprobe"""
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            input_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        return info['streams'][0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audio info: {str(e)}")

async def convert_to_wav(input_path: str) -> str:
    """Convert audio to WAV 16kHz mono if needed"""
    try:
        # Get current audio properties
        audio_info = await get_audio_info(input_path)
        sample_rate = int(audio_info.get('sample_rate', 0))
        channels = int(audio_info.get('channels', 0))
        codec_name = audio_info.get('codec_name', '')

        # Check if conversion is needed
        needs_conversion = (
            sample_rate != 16000 or 
            channels != 1 or 
            codec_name != 'pcm_s16le'
        )

        if not needs_conversion:
            return input_path

        # Perform conversion
        output_path = os.path.join(
            os.path.dirname(input_path),
            os.path.splitext(os.path.basename(input_path))[0] + "_converted.wav"
        )

        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            "-y",  # Overwrite output if exists
            output_path
        ]
        process = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return output_path

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {e.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")