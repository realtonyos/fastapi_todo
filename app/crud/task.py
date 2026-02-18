import json
from datetime import datetime

from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut


def json_serial(obj):
    """Сериализатор для JSON, поддерживающий datetime."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


async def invalidate_user_tasks_cache(redis: Redis, owner_id: int):
    """
    Удаляет все кеши задач для указанного пользователя.
    """
    pattern = f"user:{owner_id}:tasks:*"
    async for key in redis.scan_iter(pattern):
        await redis.delete(key)


async def get_tasks(
    request: Request,
    db: AsyncSession,
    owner_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[Task]:
    redis = request.app.state.redis
    cache_key = f"user:{owner_id}:tasks:skip:{skip}:limit:{limit}"
    cached = await redis.get(cache_key)
    # CACHE HIT
    if cached:
        tasks_data = json.loads(cached)
        return [TaskOut.model_validate(t) for t in tasks_data]
    # CACHE MISS
    result = await db.execute(
        select(Task).where(Task.owner_id == owner_id).offset(skip).limit(limit)
    )
    tasks = result.scalars().all()
    tasks_out = [TaskOut.model_validate(task) for task in tasks]
    # SAVE CACHE (Pydantic → dict → JSON)
    await redis.setex(
        cache_key,
        300,
        json.dumps([t.model_dump() for t in tasks_out], default=json_serial)
    )

    return tasks_out


async def get_task(
    db: AsyncSession,
    task_id: int
) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def create_task(
    redis: Redis,
    db: AsyncSession,
    task_in: TaskCreate,
    owner_id: int
) -> Task:
    new_task = Task(
        title=task_in.title,
        description=task_in.description,
        completed=task_in.completed,
        owner_id=owner_id,
    )
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    await invalidate_user_tasks_cache(redis=redis, owner_id=owner_id)
    return new_task


async def update_task(
    redis: Redis,
    db: AsyncSession,
    task: Task,
    task_in: TaskUpdate
) -> Task:
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    invalidate_user_tasks_cache(redis=redis, owner_id=task.owner_id)
    return task


async def delete_task(
    redis: Redis,
    db: AsyncSession,
    task_id: int
) -> None:
    task = await get_task(db=db, task_id=task_id)
    if task:
        await db.delete(task)
        await db.commit()
        invalidate_user_tasks_cache(redis=redis, owner_id=task.owner_id)
