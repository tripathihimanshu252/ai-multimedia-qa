import asyncio
import whisper
from typing import Dict

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model

def transcribe_audio_sync(file_path: str) -> Dict:
    model  = _get_model()
    result = model.transcribe(file_path, word_timestamps=False)
    return {
        "text": result.get("text", ""),
        "segments": [
            {"start": s["start"], "end": s["end"], "text": s["text"].strip()}
            for s in result.get("segments", [])
        ],
    }

async def transcribe_audio(file_path: str) -> Dict:
    return await asyncio.to_thread(transcribe_audio_sync, file_path)
