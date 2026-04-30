import pytest
from unittest.mock import AsyncMock, patch
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

async def test_stream_media_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.get(f"/api/media/{FAKE_ID}")
        assert res.status_code == 404

async def test_get_summary_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.get(f"/api/files/{FAKE_ID}/summary")
        assert res.status_code == 404

async def test_get_segments_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.get(f"/api/media/{FAKE_ID}/segments")
        assert res.status_code == 404
