import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId

FAKE_ID = str(ObjectId())

async def test_chat_file_not_found(auth_client):
    with patch("routes.chat.check_rate_limit", new_callable=AsyncMock, return_value=True), \
         patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=None):
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "test"})
        assert res.status_code == 404

async def test_chat_rate_limited(auth_client):
    with patch("routes.chat.check_rate_limit", new_callable=AsyncMock, return_value=False):
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "test"})
        assert res.status_code == 429

async def test_chat_still_processing(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "status": "processing", "transcription": "", "owner_id": FAKE_ID, "segments": []}
    with patch("routes.chat.check_rate_limit", new_callable=AsyncMock, return_value=True), \
         patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file):
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "test"})
        assert res.status_code == 200
        assert "processing" in res.json()["answer"].lower()

async def test_chat_cached_answer(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "status": "completed", "transcription": "text", "owner_id": FAKE_ID, "segments": []}
    with patch("routes.chat.check_rate_limit", new_callable=AsyncMock, return_value=True), \
         patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file), \
         patch("routes.chat.get_cached_answer", new_callable=AsyncMock, return_value="Cached answer"):
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "test?"})
        assert res.status_code == 200
        assert res.json()["answer"] == "Cached answer"

async def test_chat_success(auth_client):
    fake_file = {"_id": ObjectId(FAKE_ID), "status": "completed", "transcription": "AI is great.", "owner_id": FAKE_ID, "segments": []}
    mock_insert = MagicMock(); mock_insert.inserted_id = ObjectId(FAKE_ID)
    with patch("routes.chat.check_rate_limit", new_callable=AsyncMock, return_value=True), \
         patch("database.files_collection.find_one", new_callable=AsyncMock, return_value=fake_file), \
         patch("routes.chat.get_cached_answer", new_callable=AsyncMock, return_value=None), \
         patch("routes.chat.set_cached_answer", new_callable=AsyncMock), \
         patch("routes.chat.search_index", new_callable=AsyncMock, return_value=["context"]), \
         patch("routes.chat.answer_question", new_callable=AsyncMock, return_value="AI is a broad field."), \
         patch("database.chat_collection.insert_one", new_callable=AsyncMock, return_value=mock_insert):
        res = await auth_client.post("/api/chat", json={"file_id": FAKE_ID, "question": "What is AI?"})
        assert res.status_code == 200
        assert "answer" in res.json()
