from fastapi.testclient import TestClient
from app.main import app
import os

client = TestClient(app)


def test_create_and_retrieve_secret():
    # 1. Create Secret
    payload = {"ciphertext": "test_ciphertext"}
    response = client.post("/api/secret", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    secret_id = data["id"]

    # 2. Retrieve Secret
    response = client.get(f"/api/secret/{secret_id}")
    assert response.status_code == 200
    assert response.json() == {"ciphertext": "test_ciphertext"}

    # 3. Retrieve Again (Should fail)
    response = client.get(f"/api/secret/{secret_id}")
    assert response.status_code == 404
