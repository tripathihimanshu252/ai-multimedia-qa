from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatRequest(BaseModel):
    file_id: str
    question: str

class TimestampItem(BaseModel):
    start: float
    end: float
    text: str

class ChatResponse(BaseModel):
    answer: str
    timestamps: List[TimestampItem] = []
    cached: bool = False

class ChatHistoryItem(BaseModel):
    question: str
    answer: str
    created_at: Optional[datetime] = None
