from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(
        from_attributes=True,
    )
