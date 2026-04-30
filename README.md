# 🎯 AI Multimedia Q&A

> Full-stack AI-powered application to upload PDFs, audio, and video files and chat with them using Google Gemini AI.

## ✨ Features

- 📄 Upload PDF, audio (MP3/WAV), video (MP4/MKV) files
- 🤖 AI-powered Q&A using Google Gemini 1.5 Flash + LangChain
- 🔍 Semantic search with FAISS vector embeddings
- 🎙️ Audio/Video transcription with OpenAI Whisper
- ⏱️ Timestamp extraction with clickable media player
- 📋 Auto-generated summaries
- ⚡ Response caching with Redis
- 🔐 JWT-based authentication
- 🚦 Rate limiting (30 requests/min per user)
- 🐳 Dockerized with Docker Compose
- 🔄 CI/CD with GitHub Actions

## 🚀 Quick Start

### Prerequisites
- Python 3.12+, Node.js 20+, MongoDB, Redis

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your GOOGLE_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Docker Compose
```bash
docker compose up --build
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login + get JWT token |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/upload` | Upload file (PDF/audio/video) |
| GET | `/api/files` | List all user files |
| GET | `/api/status/{id}` | Check processing status |
| DELETE | `/api/files/{id}` | Delete a file |
| POST | `/api/chat` | Ask question about file |
| POST | `/api/chat/stream` | Streaming chat response |
| GET | `/api/chat/history/{id}` | Get chat history |
| GET | `/api/media/{id}` | Stream media file |
| GET | `/api/media/{id}/segments` | Get timestamps |
| GET | `/api/files/{id}/summary` | Get file summary |

## 🧪 Running Tests
```bash
cd backend
pytest tests/ -v --cov=. --cov-report=term-missing
```

## 🏗️ Architecture


## 👨‍💻 Author
**Himanshu Tripathi** — [@tripathihimanshu252](https://github.com/tripathihimanshu252)
