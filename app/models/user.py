from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    email: Mapped[str] = mapped_column(
        nullable=False,
        unique=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )
    tasks: Mapped[list["Task"]] = relationship(back_populates="owner")
