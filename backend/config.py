import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
)

JWT_SECRET         = os.getenv("JWT_SECRET", "changeme")
JWT_ALGORITHM      = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 1440))

STORAGE_DIR        = "storage"
FAISS_DIR          = "faiss_indexes"
MAX_UPLOAD_BYTES   = int(os.getenv("MAX_UPLOAD_SIZE_MB", 50)) * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".mp3", ".mp4", ".wav", ".mkv", ".m4a", ".ogg"}

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(FAISS_DIR,   exist_ok=True)
