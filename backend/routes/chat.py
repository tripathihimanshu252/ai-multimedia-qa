import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from bson import ObjectId
from database import files_collection, chat_collection
from models.chat import ChatRequest, ChatResponse, TimestampItem
from services.vector_service import search_index
from services.llm_service import answer_question, stream_answer
from services.cache_service import get_cached_answer, set_cached_answer, check_rate_limit
from routes.auth import get_current_user

router = APIRouter(prefix="/api", tags=["chat"])

def _find_relevant_segments(segments: list, answer: str) -> list:
    keywords = set(answer.lower().split())
    results  = []
    for seg in segments:
        words = set(seg["text"].lower().split())
        if len(keywords & words) >= 2:
            results.append(TimestampItem(**seg))
    return results[:5]

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    allowed = await check_rate_limit(str(current_user["_id"]))
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Try again in 1 minute.")
    file_doc = await files_collection.find_one({"_id": ObjectId(req.file_id)})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    if file_doc.get("status") != "completed":
        return ChatResponse(answer="File is still processing - please wait.", timestamps=[])
    cached = await get_cached_answer(req.file_id, req.question)
    if cached:
        segs = _find_relevant_segments(file_doc.get("segments", []), cached)
        return ChatResponse(answer=cached, timestamps=segs, cached=True)
    chunks  = await search_index(req.file_id, req.question, top_k=5)
    if not chunks:
        chunks = [file_doc.get("transcription", "")[:3000]]
    answer  = await answer_question(chunks, req.question)
    await set_cached_answer(req.file_id, req.question, answer)
    await chat_collection.insert_one({
        "file_id": req.file_id, "owner_id": str(current_user["_id"]),
        "question": req.question, "answer": answer,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
    })
    segs = _find_relevant_segments(file_doc.get("segments", []), answer)
    return ChatResponse(answer=answer, timestamps=segs, cached=False)

@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    file_doc = await files_collection.find_one({"_id": ObjectId(req.file_id)})
    if not file_doc or file_doc.get("status") != "completed":
        raise HTTPException(status_code=400, detail="File not ready")
    chunks = await search_index(req.file_id, req.question, top_k=5)
    if not chunks:
        chunks = [file_doc.get("transcription", "")[:3000]]
    async def generator():
        async for token in stream_answer(chunks, req.question):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(generator(), media_type="text/event-stream")

@router.get("/chat/history/{file_id}")
async def chat_history(file_id: str, current_user: dict = Depends(get_current_user)):
    cursor  = chat_collection.find(
        {"file_id": file_id, "owner_id": str(current_user["_id"])},
        sort=[("created_at", -1)], limit=50,
    )
    history = []
    async for doc in cursor:
        history.append({"question": doc["question"], "answer": doc["answer"], "created_at": doc.get("created_at")})
    return history
