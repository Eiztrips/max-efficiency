from sqlalchemy import Integer, String, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime

from app.database import Base
from app.models.associations import task_tags


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    tasks: Mapped[list["Task"]] = relationship(secondary=task_tags, back_populates="tags")