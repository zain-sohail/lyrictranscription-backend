from fastapi import FastAPI
from .routes import transcribe, preprocess, split

app = FastAPI(
    title="Whisper Transcription API",
    description="API for transcribing audio files using whisper.cpp",
    version="1.0.0",
    docs_url="/"
)

app.include_router(transcribe.router, prefix="/transcribe", tags=["Transcription"])
app.include_router(preprocess.router, prefix="/preprocess", tags=["Preprocessing"])
app.include_router(split.router, prefix="/split", tags=["Splitting"])