import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from jose import jwt

pytestmark = pytest.mark.asyncio
FAKE_ID  = str(ObjectId())
USER_OBJ = {"_id": ObjectId(FAKE_ID), "username": "u", "email": "u@e.com"}

def make_token():
    from config import JWT_SECRET, JWT_ALGORITHM
    from datetime import datetime, timedelta, timezone
    return jwt.encode({"sub": FAKE_ID, "exp": datetime.now(timezone.utc)+timedelta(hours=1)}, JWT_SECRET, algorithm=JWT_ALGORITHM)

@pytest.fixture
async def auth_client():
    from httpx import AsyncClient, ASGITransport
    with patch("database.client.admin.command", new_callable=AsyncMock), \
         patch("database.users_collection.create_index", new_callable=AsyncMock), \
         patch("database.files_collection.create_index", new_callable=AsyncMock), \
         patch("database.chat_collection.create_index", new_callable=AsyncMock):
        from main import app
        token = make_token()
        with patch("database.users_collection.find_one", new_callable=AsyncMock, return_value=USER_OBJ):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test",
                                   headers={"Authorization": f"Bearer {token}"}) as ac:
                yield ac

async def test_chat_file_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None), \
         patch("services.cache_service.check_rate_limit", new_callable=AsyncMock, return_value=True):
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "What is this?"})
        assert res.status_code == 404

async def test_chat_still_processing(auth_client):
    file_doc = {"_id": ObjectId(FAKE_ID), "status": "processing", "owner_id": FAKE_ID, "segments": []}
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=file_doc), \
         patch("services.cache_service.check_rate_limit", new_callable=AsyncMock, return_value=True), \
         patch("services.cache_service.get_cached_answer", new_callable=AsyncMock, return_value=None):
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "What is this?"})
        assert res.status_code == 200
        assert "processing" in res.json()["answer"].lower()

async def test_chat_rate_limited(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "transcription": "some text", "owner_id": auth_client.headers.get("owner_id", "x")}
    with patch("routes.chat.check_rate_limit", new_callable=AsyncMock, return_value=False), \
         patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file):
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "test"})
        assert res.status_code == 429
