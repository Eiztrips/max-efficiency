from sqlalchemy import Integer, String, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from .base import Base
from .associations import category_users

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    owner: Mapped["User"] = relationship(back_populates="categories_owned")
    users: Mapped[list["User"]] = relationship(secondary=category_users, back_populates="categories_joined", lazy="selectin")
    tasks: Mapped[list["Task"]] = relationship(back_populates="category", cascade="all, delete-orphan")
    tags: Mapped[list["Tag"]] = relationship(back_populates="category", cascade="all, delete-orphan")
