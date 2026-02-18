import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task_success(client: AsyncClient, test_user):
    response = await client.post(
        '/api/v1/tasks/',
        json={"title": "My test task"},
        headers=test_user["headers"]  # токен автоматически
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["title"] == "My test task"
    assert data["completed"] is False


@pytest.mark.asyncio
async def test_get_tasks_empty(client: AsyncClient, test_user):
    response = await client.get(
        '/api/v1/tasks/',
        headers=test_user["headers"]
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_tasks_with_data(client: AsyncClient, test_user):
    # Создаём задачу
    create_response = await client.post(
        '/api/v1/tasks/',
        json={"title": "My test task"},
        headers=test_user["headers"]
    )
    assert create_response.status_code == 201
    created_task = create_response.json()

    # Получаем список задач
    list_response = await client.get(
        '/api/v1/tasks/',
        headers=test_user["headers"]
    )
    assert list_response.status_code == 200
    tasks = list_response.json()

    # Проверяем, что задача есть в списке
    assert len(tasks) >= 1
    # Находим нашу задачу по ID или title
    task_ids = [t["id"] for t in tasks]
    assert created_task["id"] in task_ids
