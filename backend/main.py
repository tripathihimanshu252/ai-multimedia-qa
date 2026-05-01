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
allow_origins=[
    "https://ai-multimedia-qa-frontend.vercel.app",
    "https://ai-multimedia-qa-frontend-pdcmcpy8y.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
],
app.include_router(auth.router)
app.include_router(uploads.router)
app.include_router(chat.router)
app.include_router(media.router)

@app.get("/")
async def root():
    return {"message": "AI Multimedia Q&A Backend Running"}
