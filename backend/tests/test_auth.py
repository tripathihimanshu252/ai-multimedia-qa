import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId

pytestmark = pytest.mark.asyncio

FAKE_ID  = str(ObjectId())
FAKE_USER = {
    "_id": ObjectId(FAKE_ID),
    "username": "testuser",
    "email": "test@example.com",
    "hashed_password": "$2b$12$KIX6K4v6j3K3K3K3K3K3Ku"
}

@pytest.fixture
async def client():
    from httpx import AsyncClient, ASGITransport
    with patch("database.client.admin.command", new_callable=AsyncMock), \
         patch("database.users_collection.create_index", new_callable=AsyncMock), \
         patch("database.files_collection.create_index", new_callable=AsyncMock), \
         patch("database.chat_collection.create_index", new_callable=AsyncMock):
        from main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac

async def test_register_success(client):
    mock_result = MagicMock(); mock_result.inserted_id = ObjectId(FAKE_ID)
    with patch("database.users_collection.find_one", new_callable=AsyncMock, return_value=None), \
         patch("database.users_collection.insert_one", new_callable=AsyncMock, return_value=mock_result):
        res = await client.post("/api/auth/register", json={"username":"testuser","email":"test@example.com","password":"pass123"})
        assert res.status_code == 201
        assert "access_token" in res.json()

async def test_register_duplicate_email(client):
    with patch("database.users_collection.find_one", new_callable=AsyncMock, return_value=FAKE_USER):
        res = await client.post("/api/auth/register", json={"username":"testuser","email":"test@example.com","password":"pass123"})
        assert res.status_code == 409

async def test_login_invalid_credentials(client):
    with patch("database.users_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await client.post("/api/auth/login", json={"email":"bad@example.com","password":"wrong"})
        assert res.status_code == 401

async def test_me_unauthorized(client):
    res = await client.get("/api/auth/me")
    assert res.status_code == 403

async def test_root(client):
    res = await client.get("/")
    assert res.status_code == 200
    assert "message" in res.json()
