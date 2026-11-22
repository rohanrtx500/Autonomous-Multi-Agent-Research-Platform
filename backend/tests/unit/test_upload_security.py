import io
import os
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_upload_valid_text_document():
    content = b"This is a valid research document discussing multi-agent systems and consensus."
    file = io.BytesIO(content)
    response = client.post(
        "/api/v1/upload",
        files={"file": ("valid_notes.txt", file, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["chunks_ingested"] >= 1


def test_upload_path_traversal_attempt():
    content = b"Malicious payload trying to escape upload directory"
    file = io.BytesIO(content)
    # Attempt directory traversal in filename
    response = client.post(
        "/api/v1/upload",
        files={"file": ("../../../../etc/passwd.txt", file, "text/plain")}
    )
    # The endpoint sanitizes the basename or rejects traversal
    # If accepted, file is placed safely within upload dir without escaping
    if response.status_code == 200:
        data = response.json()
        assert not os.path.exists("etc/passwd.txt")
        assert not os.path.exists("../../etc/passwd.txt")
    else:
        assert response.status_code in [400, 422]


def test_upload_disallowed_extension():
    content = b"#!/bin/bash\necho hello"
    file = io.BytesIO(content)
    response = client.post(
        "/api/v1/upload",
        files={"file": ("script.sh", file, "application/x-sh")}
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_upload_corrupted_pdf_header():
    content = b"NOT_A_PDF_HEADER but named as pdf"
    file = io.BytesIO(content)
    response = client.post(
        "/api/v1/upload",
        files={"file": ("corrupted.pdf", file, "application/pdf")}
    )
    assert response.status_code == 400
    assert "Expected valid PDF header" in response.json()["detail"]


def test_upload_oversized_file_limit(monkeypatch):
    # Temporarily set max upload size to 100 bytes for fast testing
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_BYTES", 100)

    oversized_content = b"A" * 200
    file = io.BytesIO(oversized_content)
    response = client.post(
        "/api/v1/upload",
        files={"file": ("oversized.txt", file, "text/plain")}
    )
    assert response.status_code == 413
    assert "exceeds maximum allowed size" in response.json()["detail"]
