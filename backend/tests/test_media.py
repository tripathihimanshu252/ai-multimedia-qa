import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId

FAKE_ID = str(ObjectId())

@pytest.fixture
async def auth_client():
    from httpx import AsyncClient, ASGITransport
    fake_user = {"_id": ObjectId(FAKE_ID), "username": "u", "email": "u@e.com", "id": FAKE_ID}
    with patch("database.client.admin.command", new_callable=AsyncMock), \
         patch("database.users_collection.create_index", new_callable=AsyncMock), \
         patch("database.files_collection.create_index", new_callable=AsyncMock), \
         patch("database.chat_collection.create_index", new_callable=AsyncMock), \
         patch("routes.uploads.get_current_user", return_value=fake_user), \
         patch("routes.chat.get_current_user", return_value=fake_user), \
         patch("routes.media.get_current_user", return_value=fake_user):
        from main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac

async def test_stream_media_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.get(f"/api/media/{FAKE_ID}/stream")
        assert res.status_code == 404

async def test_get_summary_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.get(f"/api/media/{FAKE_ID}/summary")
        assert res.status_code == 404

async def test_get_segments_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.get(f"/api/media/{FAKE_ID}/segments")
        assert res.status_code == 404

async def test_get_summary_success(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "summary": "This is a summary.", "owner_id": FAKE_ID}
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file):
        res = await auth_client.get(f"/api/media/{FAKE_ID}/summary")
        assert res.status_code == 200
        assert "summary" in res.json()

async def test_get_segments_success(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "segments": [{"start": 0, "end": 5, "text": "Hello"}], "owner_id": FAKE_ID}
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file):
        res = await auth_client.get(f"/api/media/{FAKE_ID}/segments")
        assert res.status_code == 200

async def test_stream_media_file_missing(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "filename": "test.mp4", "owner_id": FAKE_ID}
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file), \
         patch("os.path.exists", return_value=False):
        res = await auth_client.get(f"/api/media/{FAKE_ID}/stream")
        assert res.status_code == 404
