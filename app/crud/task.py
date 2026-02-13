from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def get_tasks(
    db: AsyncSession,
    owner_id: int,
    skip: int = 0,
    limit: int = 100
) -> list[Task]:
    result = await db.execute(
        select(Task).where(Task.owner_id == owner_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_task(
    db: AsyncSession,
    task_id: int
) -> Task | None:
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def create_task(
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
    return new_task


async def update_task(
    db: AsyncSession,
    task: Task,
    task_in: TaskUpdate
) -> Task:
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(
    db: AsyncSession,
    task_id: int
) -> None:
    task = await get_task(db=db, task_id=task_id)
    if task:
        await db.delete(task)
        await db.commit()
