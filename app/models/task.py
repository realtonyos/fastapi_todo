from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None]
    completed: Mapped[bool] = mapped_column(
        default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    owner: Mapped["User"] = relationship(back_populates="tasks")
