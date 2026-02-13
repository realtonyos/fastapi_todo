from pydantic import BaseModel
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    completed: bool = False


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


class TaskOut(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    owner_id: int

    class Config:
        from_attributes = True
