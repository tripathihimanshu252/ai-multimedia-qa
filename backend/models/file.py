from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileOut(BaseModel):
    id: str
    filename: str
    type: str
    status: str
    summary: Optional[str] = ""
    upload_date: Optional[datetime] = None

class TimestampItem(BaseModel):
    start: float
    end: float
    text: str
