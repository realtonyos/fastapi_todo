import uuid
import pytest
import asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    # 1. Arrange
    unique_email = f"test{uuid.uuid4()}@example.com"
    user_data = {
        "email": unique_email,
        "password": "testpass123"
    }

    # 2. Act
    response = await client.post('/api/v1/auth/register', json=user_data)

    # 3. Assert
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    # 1. Arrange
    unique_email = f"test{uuid.uuid4()}@example.com"
    user_data = {
        "email": unique_email,
        "password": "testpass123"
    }
    await client.post('/api/v1/auth/register', json=user_data)
    await asyncio.sleep(0.1)

    # 2. Act
    response = await client.post('/api/v1/auth/register', json=user_data)

    # 3. Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
