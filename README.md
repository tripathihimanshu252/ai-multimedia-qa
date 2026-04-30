# 🎙️ AI Multimedia Q&A Platform

A full-stack AI-powered web application that lets users upload PDFs, audio, and video files — then chat with an AI about the content, get summaries, and jump to relevant timestamps.

## 🚀 Features

- 📄 Upload PDF, audio (MP3/WAV), and video (MP4/MKV) files
- 🤖 AI chatbot powered by Google Gemini via LangChain
- 🎧 Whisper-based audio/video transcription with timestamps
- 🔍 Semantic search using FAISS vector embeddings
- 📝 Automatic content summarization
- ⏱️ Timestamp extraction for topics in audio/video
- ▶️ Play button to jump to relevant media timestamps
- 🔐 JWT authentication (register/login)
- ⚡ Redis-based rate limiting and answer caching
- 🐳 Docker Compose multi-container setup
- 🔄 GitHub Actions CI/CD pipeline

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| AI/LLM | LangChain + Google Gemini 1.5 Flash |
| Transcription | OpenAI Whisper |
| Vector Search | FAISS + sentence-transformers |
| Database | MongoDB (Motor async) |
| Cache | Redis |
| Frontend | React + Vite + TailwindCSS |
| Auth | JWT (python-jose) |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## 📁 Project Structure


## ⚙️ Setup & Running

### Prerequisites
- Python 3.10+, Node.js 18+, Docker, MongoDB, Redis

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Add your API keys
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**With Docker Compose:**
```bash
docker-compose up --build
```

### Environment Variables (`.env`)

## 🔌 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT token |
| GET | `/api/auth/me` | Current user info |

### Files
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/upload` | Upload PDF/audio/video |
| GET | `/api/files` | List user's files |
| GET | `/api/status/{id}` | Processing status |

### Chat
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat` | Ask question about file |

### Media
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/media/{id}/stream` | Stream audio/video |
| GET | `/api/media/{id}/summary` | Get file summary |
| GET | `/api/media/{id}/segments` | Get timestamps |

## 🧪 Testing

```bash
cd backend
pytest tests/ -v --cov=. --cov-report=term-missing
```

Coverage target: **95%+**

## 🐳 Docker

```bash
# Build and run all services
docker-compose up --build

# Services:
# - Backend API: http://localhost:8000
# - Frontend:    http://localhost:5173
# - MongoDB:     localhost:27017
# - Redis:       localhost:6379
```

## 🔄 CI/CD

GitHub Actions automatically runs on every push to `main`:
1. Install dependencies
2. Run pytest with coverage check
3. Build Docker images

See `.github/workflows/ci.yml` for configuration.
