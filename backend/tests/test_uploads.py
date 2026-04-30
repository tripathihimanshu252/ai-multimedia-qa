import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId
from jose import jwt
import os

pytestmark = pytest.mark.asyncio
FAKE_ID   = str(ObjectId())
USER_OBJ  = {"_id": ObjectId(FAKE_ID), "username": "u", "email": "u@e.com"}

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

async def test_list_files_empty(auth_client):
    class EmptyAsyncIter:
        def __aiter__(self): return self
        async def __anext__(self): raise StopAsyncIteration
    with patch("database.files_collection.find", return_value=EmptyAsyncIter()):
        res = await auth_client.get("/api/files")
        assert res.status_code == 200

async def test_upload_unsupported_type(auth_client):
    res = await auth_client.post("/api/upload", files={"file": ("test.exe", b"data", "application/octet-stream")})
    assert res.status_code == 400

async def test_status_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.get(f"/api/status/{FAKE_ID}")
        assert res.status_code == 404
