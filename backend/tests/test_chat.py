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

async def test_chat_file_not_found(auth_client):
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "test"})
        assert res.status_code == 404

async def test_chat_still_processing(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "transcription": "", "owner_id": FAKE_ID}
    with patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file), \
         patch("routes.chat.check_rate_limit", new_callable=AsyncMock, return_value=True):
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "test"})
        assert res.status_code == 202

async def test_chat_rate_limited(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "transcription": "some text", "owner_id": FAKE_ID}
    with patch("routes.chat.check_rate_limit", new_callable=AsyncMock, return_value=False), \
         patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file):
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "test"})
        assert res.status_code == 429

async def test_chat_success(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "transcription": "This is a document about AI.", "owner_id": FAKE_ID}
    mock_llm_response = MagicMock(); mock_llm_response.content = "AI is a broad field."
    mock_insert = MagicMock(); mock_insert.inserted_id = ObjectId(FAKE_ID)
    with patch("routes.chat.check_rate_limit", new_callable=AsyncMock, return_value=True), \
         patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file), \
         patch("routes.chat.get_cached_answer", new_callable=AsyncMock, return_value=None), \
         patch("routes.chat.set_cached_answer", new_callable=AsyncMock), \
         patch("routes.chat.search_similar_chunks", return_value="relevant context"), \
         patch("routes.chat.llm") as mock_llm, \
         patch("database.chat_collection.insert_one", new_callable=AsyncMock, return_value=mock_insert):
        mock_llm.ainvoke = AsyncMock(return_value=mock_llm_response)
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "What is AI?"})
        assert res.status_code == 200
        assert "answer" in res.json()

async def test_chat_cached_answer(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "transcription": "some text", "owner_id": FAKE_ID}
    with patch("routes.chat.check_rate_limit", new_callable=AsyncMock, return_value=True), \
         patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file), \
         patch("routes.chat.get_cached_answer", new_callable=AsyncMock, return_value="Cached answer here"):
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "test?"})
        assert res.status_code == 200
        assert res.json()["answer"] == "Cached answer here"
