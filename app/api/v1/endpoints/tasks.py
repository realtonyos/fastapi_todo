from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate
from app.crud.task import (
    get_tasks,
    get_task,
    create_task,
    update_task,
    delete_task,
)
from app.api.deps import ActiveUserFromToken


router = APIRouter()


@router.get(
    "/",
    response_model=list[TaskOut],
    description="Возвращает все задачи юзера")
async def read_tasks(
    current_user: ActiveUserFromToken,
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
):
    tasks = await get_tasks(
        db=db,
        owner_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return tasks


@router.get(
    "/{task_id}",
    response_model=TaskOut,
    description="Возвращает конкретную задачу с ID")
async def read_task(
    current_user: ActiveUserFromToken,
    task_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await get_task(
        db=db,
        task_id=task_id
    )
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Эта задача вам не доступна"
        )
    return task


@router.post(
    "/",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    description="Создает задачу для конкретного юзера")
async def create_new_task(
    current_user: ActiveUserFromToken,
    task_in: TaskCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await create_task(
        db=db,
        task_in=task_in,
        owner_id=current_user.id
    )
    return task


@router.patch(
    "/{task_id}",
    response_model=TaskOut,
    description="Обновляет данные в задаче")
async def update_current_task(
    current_user: ActiveUserFromToken,
    task_id: int,
    task_in: TaskUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    task = await update_task(db, task, task_in)
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удаляет задачу."
    )
async def delete_current_task(
    current_user: ActiveUserFromToken,
    task_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    task = await get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await delete_task(db, task_id)
    return None
