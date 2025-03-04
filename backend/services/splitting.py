import os
import subprocess
from fastapi import HTTPException

async def split_audio(input_path: str):
    output_dir = os.path.join(os.path.dirname(input_path), "output")
    cmd = [
        "spleeter",
        "separate",
        "-p", "spleeter:2stems",
        "-o", output_dir,
        input_path
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    output, error = process.communicate()
    
    if process.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Splitting failed: {error.decode('utf-8')}")
    
    return {"output_dir": output_dir}