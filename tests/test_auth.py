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


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user):

    response = await client.post('/api/v1/auth/login', data={
        "username": test_user["email"],
        "password": test_user["password"]
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_with_wrong_pass(client: AsyncClient, test_user):
    login_data = {
        "email": test_user["email"],
        "password": "wrongpass"
    }

    response = await client.post('/api/v1/auth/login', data={
        "username": login_data["email"],
        "password": login_data["password"]
    })

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_login_with_wrong_email(client: AsyncClient, test_user):
    new_email = f"test{uuid.uuid4()}@example.com"
    login_data = {
        "email": new_email,
        "password": test_user["password"]
    }

    response = await client.post('/api/v1/auth/login', data={
        "username": login_data["email"],
        "password": login_data["password"]
    })

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
