import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from bson import ObjectId
from database import files_collection
from routes.auth import get_current_user
from config import STORAGE_DIR

router = APIRouter(prefix="/api", tags=["media"])

@router.get("/media/{file_id}")
async def stream_media(file_id: str, current_user: dict = Depends(get_current_user)):
    doc = await files_collection.find_one({"_id": ObjectId(file_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")
    if doc["owner_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Access denied")
    file_path = os.path.join(STORAGE_DIR, doc["stored_name"])
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing from storage")
    return FileResponse(file_path, media_type="application/octet-stream", filename=doc["filename"])

@router.get("/media/{file_id}/segments")
async def get_segments(file_id: str, current_user: dict = Depends(get_current_user)):
    doc = await files_collection.find_one({"_id": ObjectId(file_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")
    return {"segments": doc.get("segments", []), "file_id": file_id}

@router.get("/files/{file_id}/summary")
async def get_summary(file_id: str, current_user: dict = Depends(get_current_user)):
    doc = await files_collection.find_one({"_id": ObjectId(file_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")
    return {"file_id": file_id, "filename": doc.get("filename"), "summary": doc.get("summary", ""), "status": doc.get("status")}
