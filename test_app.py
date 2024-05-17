"""
Test module for OCR Retrieval Augmented Generation.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_upload_files_success(mock_minio, mock_uuid):
    """Testing mock data upload for upload endpoint."""
    file_content = b"fake file content"
    mock_minio.put_object.return_value = None
    mock_minio.presigned_get_object.return_value = "http://example.com/fake-file-url"
    mock_uuid.return_value = "fake-uuid"

    files = {
        "files": ("test.png", file_content, "image/png"),
    }

    response = client.post("/upload", files=files)

    assert response.status_code == 200
    assert response.json() == [{"file_id": "fake-uuid", "url": "http://example.com/fake-file-url"}]

@pytest.mark.asyncio
async def test_upload_files_invalid_format():
    """Testing wrong file format for file upload."""
    file_content = b"fake file content"
    files = {
        "files": ("test.txt", file_content, "text/plain"),
    }

    response = client.post("/upload", files=files)

    assert response.status_code == 400
    assert response.json() == {"detail": "Unsupported file format: txt"}

@pytest.mark.asyncio
async def test_ocr_and_upload_embeddings(mock_openai, \
                        mock_pinecone, mock_loader, mock_text_splitter):
    """Testing /ocr endpoint with fake data."""
    mock_loader.load.return_value = [{"text": "fake OCR result"}]
    mock_text_splitter.split_documents.return_value = ["chunk1", "chunk2"]
    mock_openai.return_value.embed_documents.return_value = ["embedding1", "embedding2"]
    mock_pinecone.return_value = None

    payload = {"url": "http://example.com/fake-file-url"}

    response = client.post("/ocr", json=payload)

    assert response.status_code == 200
    assert response.json() == "Embeddings uploaded to Pinecone successfully"

@pytest.mark.asyncio
async def test_ocr_and_upload_embeddings_no_url():
    """Testing response with no url."""
    payload = {}

    response = client.post("/ocr", json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "No url provided: 'url'"}

@pytest.mark.asyncio
async def test_create_chat_no_message():
    """Testing /extract endpoint no message returned."""
    payload = {}

    response = client.post("/extract", json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "No message provided: 'message'"}

# Fixture to mock Minio client
@pytest.fixture
def mock_minio(mocker):
    mock_minio_client = mocker.patch("main.minio_client", autospec=True)
    return mock_minio_client

# Fixture to mock uuid generation
@pytest.fixture
def mock_uuid(mocker):
    mock_uuid = mocker.patch("uuid.uuid4", autospec=True)
    return mock_uuid

# Fixture to mock OpenAI embeddings
@pytest.fixture
def mock_openai(mocker):
    mock_openai = mocker.patch("main.OpenAIEmbeddings", autospec=True)
    return mock_openai

# Fixture to mock Pinecone client
@pytest.fixture
def mock_pinecone(mocker):
    mock_pinecone = mocker.patch("main.PC", autospec=True)
    return mock_pinecone

# Fixture to mock JSONLoader
@pytest.fixture
def mock_loader(mocker):
    mock_loader = mocker.patch("main.JSONLoader", autospec=True)
    return mock_loader

# Fixture to mock text splitter
@pytest.fixture
def mock_text_splitter(mocker):
    mock_text_splitter = mocker.patch("main.RecursiveCharacterTextSplitter", autospec=True)
    return mock_text_splitter

# Fixture to mock OpenAI chain
@pytest.fixture
def mock_chain(mocker):
    mock_chain = mocker.patch("main.load_qa_chain", autospec=True)
    return mock_chain
