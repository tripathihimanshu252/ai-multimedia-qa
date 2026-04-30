import pytest
from unittest.mock import AsyncMock, patch
from bson import ObjectId

FAKE_ID = str(ObjectId())

# NOTE: stream = /api/media/{id}, summary = /api/files/{id}/summary, segments = /api/media/{id}/segments

async def test_stream_media_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.get(f"/api/media/{FAKE_ID}")
        assert res.status_code in (403, 404)

async def test_get_summary_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.get(f"/api/files/{FAKE_ID}/summary")
        assert res.status_code == 404

async def test_get_segments_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.get(f"/api/media/{FAKE_ID}/segments")
        assert res.status_code == 404

async def test_get_summary_success(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "summary": "This is a summary.", "owner_id": FAKE_ID, "filename": "test.pdf", "status": "completed"}
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file):
        res = await auth_client.get(f"/api/files/{FAKE_ID}/summary")
        assert res.status_code == 200
        assert "summary" in res.json()

async def test_get_segments_success(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "segments": [{"start": 0.0, "end": 5.0, "text": "Hello"}], "owner_id": FAKE_ID}
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file):
        res = await auth_client.get(f"/api/media/{FAKE_ID}/segments")
        assert res.status_code == 200

async def test_stream_media_file_missing(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "filename": "test.mp4", "owner_id": FAKE_ID, "stored_name": "test.mp4"}
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file), \
         patch("os.path.exists", return_value=False):
        res = await auth_client.get(f"/api/media/{FAKE_ID}")
        assert res.status_code in (403, 404)
