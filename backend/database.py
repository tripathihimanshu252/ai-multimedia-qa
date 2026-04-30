import os, asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME", "ai_multimedia_db")

client   = AsyncIOMotorClient(MONGO_URI)
database = client[DB_NAME]

users_collection = database.get_collection("users")
files_collection = database.get_collection("files_data")
chat_collection  = database.get_collection("chat_history")

async def init_db():
    try:
        await client.admin.command("ping")
        await users_collection.create_index("email",    unique=True)
        await users_collection.create_index("username", unique=True)
        await files_collection.create_index("owner_id")
        await chat_collection.create_index("file_id")
        print("✅ MongoDB connected & indexes created")
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())
