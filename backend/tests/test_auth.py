import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId

FAKE_ID = str(ObjectId())
FAKE_USER = {"_id": ObjectId(FAKE_ID), "username": "testuser", "email": "test@example.com", "hashed_password": "$2b$12$abc"}

async def test_register_success(client):
    mock_result = MagicMock(); mock_result.inserted_id = ObjectId(FAKE_ID)
    with patch("database.users_collection.find_one", new_callable=AsyncMock, return_value=None), \
         patch("database.users_collection.insert_one", new_callable=AsyncMock, return_value=mock_result), \
         patch("routes.auth.hash_password", return_value="$2b$12$hashedpw"), \
         patch("routes.auth.create_token", return_value="fake.jwt.token"):
        res = await client.post("/api/auth/register", json={"username":"testuser","email":"test@example.com","password":"pass123"})
        assert res.status_code == 201
        assert "access_token" in res.json()

async def test_register_duplicate_email(client):
    with patch("database.users_collection.find_one", new_callable=AsyncMock, return_value=FAKE_USER):
        res = await client.post("/api/auth/register", json={"username":"x","email":"test@example.com","password":"pass"})
        assert res.status_code == 409

async def test_login_success(client):
    with patch("database.users_collection.find_one", new_callable=AsyncMock, return_value=FAKE_USER), \
         patch("routes.auth.verify_password", return_value=True), \
         patch("routes.auth.create_token", return_value="fake.jwt.token"):
        res = await client.post("/api/auth/login", json={"email":"test@example.com","password":"pass123"})
        assert res.status_code == 200
        assert "access_token" in res.json()

async def test_login_invalid_credentials(client):
    with patch("database.users_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await client.post("/api/auth/login", json={"email":"wrong@example.com","password":"wrong"})
        assert res.status_code == 401

async def test_login_wrong_password(client):
    with patch("database.users_collection.find_one", new_callable=AsyncMock, return_value=FAKE_USER), \
         patch("routes.auth.verify_password", return_value=False):
        res = await client.post("/api/auth/login", json={"email":"test@example.com","password":"wrongpass"})
        assert res.status_code == 401

async def test_me_unauthorized(client):
    res = await client.get("/api/auth/me")
    assert res.status_code == 401

async def test_me_authorized(auth_client):
    res = await auth_client.get("/api/auth/me")
    assert res.status_code == 200

async def test_root(client):
    res = await client.get("/")
    assert res.status_code == 200
