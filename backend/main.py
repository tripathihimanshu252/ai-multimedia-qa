from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routes import auth, uploads, chat, media

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="AI Multimedia Q&A", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(chat.router)
app.include_router(media.router)

@app.get("/")
async def root():
    return {"message": "AI Multimedia Q&A Backend Running"}

@app.get("/health")
async def health():
    return {"status": "ok"}
