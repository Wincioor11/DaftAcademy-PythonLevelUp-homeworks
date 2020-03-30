from fastapi.testclient import TestClient
import pytest
from app import app

client = TestClient(app)


def test_hello():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World during the coronavirus pandemic!"}
