import asyncio
import sys
import os
import pytest
from main import app
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client(event_loop):
    with TestClient(app) as client:
        yield client

@pytest.mark.asyncio
async def test_get_users(client):
    response = await client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert "users" in users
    assert isinstance(users["users"], list)
    assert len(users["users"]) == 2
    first_user = users["users"][0]
    assert "id" in first_user
    assert "username" in first_user
    assert "skills" in first_user
    assert "interests" in first_user

@pytest.mark.asyncio
async def test_create_users(client):
    data = {
        "username": "test",
        "skills": ["test"],
        "interests": ["test"],
        "email": "user@example.com"
    }
    response = await client.post("/users", json=data)
    assert response.status_code == 200
    created_user = response.json()
    assert created_user["username"] == data["username"]
    assert created_user["email"] == data["email"]
    assert "id" in created_user
    assert "skills" in created_user
    assert "interests" in created_user
