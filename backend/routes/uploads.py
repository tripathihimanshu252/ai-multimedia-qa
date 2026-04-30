import os, asyncio, datetime
import aiofiles
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from bson import ObjectId
from database import files_collection
from services.pdf_service import extract_pdf_text, chunk_text
from services.whisper_service import transcribe_audio
from services.vector_service import build_index
from services.llm_service import summarize
from routes.auth import get_current_user
from config import STORAGE_DIR, MAX_UPLOAD_BYTES, ALLOWED_EXTENSIONS

router = APIRouter(prefix="/api", tags=["uploads"])

async def _run_ai_processing(file_id: str, file_path: str, file_type: str, owner_id: str):
    try:
        text_content = ""
        segments     = []
        if file_type == "pdf":
            text_content = await asyncio.to_thread(extract_pdf_text, file_path)
        elif file_type in {"audio", "video"}:
            result       = await transcribe_audio(file_path)
            text_content = result["text"]
            segments     = result["segments"]
        if not text_content.strip():
            raise ValueError("Could not extract text from file")
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"transcription": text_content, "segments": segments, "status": "generating_summary"}},
        )
        summary = await summarize(text_content)
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"summary": summary, "status": "indexing"}},
        )
        chunks = chunk_text(text_content)
        await build_index(file_id, chunks)
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"status": "completed"}},
        )
        print(f"✅ Processing complete: {file_id}")
    except Exception as e:
        await files_collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": {"status": "error", "error_message": str(e)}},
        )

def _detect_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf": return "pdf"
    if ext in {".mp3", ".wav", ".m4a", ".ogg"}: return "audio"
    if ext in {".mp4", ".mkv"}: return "video"
    return "unknown"

@router.post("/upload")
async def upload_file(background_tasks: BackgroundTasks, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not supported")
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 50 MB)")
    safe_name = f"{ObjectId()}_{file.filename}"
    file_path = os.path.join(STORAGE_DIR, safe_name)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    file_type = _detect_type(file.filename)
    owner_id  = str(current_user["_id"])
    doc = {
        "filename": file.filename, "stored_name": safe_name, "type": file_type,
        "status": "processing", "owner_id": owner_id,
        "upload_date": datetime.datetime.now(datetime.timezone.utc),
        "transcription": "", "segments": [], "summary": "",
    }
    result = await files_collection.insert_one(doc)
    fid    = str(result.inserted_id)
    background_tasks.add_task(_run_ai_processing, fid, file_path, file_type, owner_id)
    return {"id": fid, "filename": file.filename, "status": "processing"}

@router.get("/files")
async def list_files(current_user: dict = Depends(get_current_user)):
    owner_id = str(current_user["_id"])
    cursor   = files_collection.find({"owner_id": owner_id})
    files    = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        doc.pop("transcription", None)
        files.append(doc)
    return files

@router.get("/status/{file_id}")
async def get_status(file_id: str, current_user: dict = Depends(get_current_user)):
    doc = await files_collection.find_one({"_id": ObjectId(file_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    doc.pop("transcription", None)
    return doc

@router.delete("/files/{file_id}", status_code=204)
async def delete_file(file_id: str, current_user: dict = Depends(get_current_user)):
    doc = await files_collection.find_one({"_id": ObjectId(file_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")
    if doc["owner_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not your file")
    stored = os.path.join(STORAGE_DIR, doc.get("stored_name", ""))
    if os.path.exists(stored):
        os.remove(stored)
    await files_collection.delete_one({"_id": ObjectId(file_id)})
