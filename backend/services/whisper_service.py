try:
    import whisper
    _model = None
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠️ Whisper not available - audio transcription disabled")

async def transcribe_audio(file_path: str) -> str:
    if not WHISPER_AVAILABLE:
        return "Audio transcription is not available in this deployment."
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    result = _model.transcribe(file_path)
    return result["text"]
