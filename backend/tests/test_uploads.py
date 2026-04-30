import pytest
import io
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

async def test_list_files_empty(auth_client):
    class EmptyAsyncIter:
        def __aiter__(self): return self
        async def __anext__(self): raise StopAsyncIteration
    with patch("database.files_collection.find", return_value=EmptyAsyncIter()):
        res = await auth_client.get("/api/files")
        assert res.status_code == 200
        assert res.json() == []

async def test_upload_pdf_success(auth_client):
    mock_result = MagicMock(); mock_result.inserted_id = ObjectId(FAKE_ID)
    with patch("database.files_collection.insert_one", new_callable=AsyncMock, return_value=mock_result), \
         patch("routes.uploads.BackgroundTasks.add_task"), \
         patch("builtins.open", MagicMock()), \
         patch("shutil.copyfileobj"):
        file_content = b"%PDF-1.4 fake pdf content"
        res = await auth_client.post("/api/upload",
            files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")})
        assert res.status_code == 200
        assert "id" in res.json()

async def test_upload_unsupported_type(auth_client):
    res = await auth_client.post("/api/upload",
        files={"file": ("test.exe", io.BytesIO(b"binary"), "application/octet-stream")})
    assert res.status_code == 400

async def test_status_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.get(f"/api/status/{FAKE_ID}")
        assert res.status_code == 404

async def test_status_found(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "filename": "test.pdf", "status": "completed",
                 "owner_id": FAKE_ID, "transcription": "text", "summary": "summary"}
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file):
        res = await auth_client.get(f"/api/status/{FAKE_ID}")
        assert res.status_code == 200

async def test_list_files_with_data(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "filename": "test.pdf", "status": "completed", "owner_id": FAKE_ID}
    class SingleAsyncIter:
        def __init__(self): self.done = False
        def __aiter__(self): return self
        async def __anext__(self):
            if self.done: raise StopAsyncIteration
            self.done = True; return fake_file
    with patch("database.files_collection.find", return_value=SingleAsyncIter()):
        res = await auth_client.get("/api/files")
        assert res.status_code == 200
