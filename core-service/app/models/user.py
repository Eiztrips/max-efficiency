from sqlalchemy import Integer, TIMESTAMP
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base
from app.models.associations import category_users


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    max_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    username: Mapped[str] = mapped_column(nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    categories_owned: Mapped[list["Category"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )

    categories_joined: Mapped[list["Category"]] = relationship(
        secondary=category_users, back_populates="users"
    )
