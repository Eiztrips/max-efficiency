from typing import Optional

from sqlalchemy import select, update, Sequence

from .base import BaseRepository
from ..models import Task, task_tags
from datetime import datetime


class TaskRepository(BaseRepository):

    # --------------- GET ----------------

    async def get_by_id(self, id: int) -> Optional[Task]:
        result = await self.session.execute(select(Task)
                                            .where(Task.id == id))
        return result.scalar_one_or_none()

    async def get_all_by_user_id(self, user_id: int) -> Sequence[Task]:
        result = await self.session.execute(
            select(Task)
            .where(Task.user_id == user_id)
        )
        return result.scalars().all()

    """
    class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    expiration_date: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))

    category: Mapped["Category"] = relationship(back_populates="tasks")
    tags: Mapped[list["Tag"]] = relationship(secondary=task_tags, back_populates="tasks")
    """

    """
        async def get_tasks(self, user_id: int,
                        category_id: Optional[int] = None,
                        tag_id: Optional[int] = None,
                        status: Optional[str] = None,
                        from_date: Optional[str] = None,
                        to_date: Optional[str] = None,
                        is_completed: Optional[bool] = None,
                        search: Optional[str] = None) -> Sequence[Task]:
        \"""
        Возвращает задачи пользователя с возможностью фильтрации.
        :param user_id: ID пользователя
        :param category_id: (опционально) ID категории
        :param tag_id: (опционально) ID тега
        :param status: (опционально) статус задачи
        :param from_date: (опционально) дата начала диапазона
        :param to_date: (опционально) дата конца диапазона
        :param is_completed: (опционально) флаг завершенности задачи
        :param search: (опционально) поисковый запрос по названию или описанию
        :return: список задач, соответствующих фильтрам
        \"""
        _positive_int_validator(user_id, "ID пользователя")
        if category_id is not None:
            _positive_int_validator(category_id, "ID категории")
        if tag_id is not None:
            _positive_int_validator(tag_id, "ID тега")
        if status is not None:
            _not_empty_str_validator(status, "статус задачи")
        if from_date is not None:
            _not_empty_str_validator(from_date, "дата начала диапазона")
        if to_date is not None:
            _not_empty_str_validator(to_date, "дата конца диапазона")
        if search is not None:
            _not_empty_str_validator(search, "поисковый запрос")

        return await self.task_repo.get_tasks(user_id, category_id, tag_id, status, from_date, to_date, is_completed, search)
    """

    async def get_tasks(self, user_id: int,
                        category_id: Optional[int] = None,
                        tag_id: Optional[int] = None,
                        status: Optional[str] = None,
                        is_completed: Optional[bool] = None,
                        from_date: Optional[str] = None,
                        to_date: Optional[str] = None,
                        search: Optional[str] = None) -> Sequence[Task]:

        query = select(Task).where(Task.user_id == user_id)

        if category_id is not None:
            query = query.where(Task.category_id == category_id)

        if tag_id is not None:
            query = query.join(task_tags).where(task_tags.c.tag_id.eq(tag_id))

        if status is not None:
            if status == "done":
                query = query.where(Task.expiration_date < datetime.now())
            elif status == "pending":
                query = query.where(Task.expiration_date >= datetime.now())

        if is_completed is not None:
            query = query.where(Task.is_completed == is_completed)

        if from_date is not None:
            query = query.where(Task.expiration_date >= datetime.fromisoformat(from_date))

        if to_date is not None:
            query = query.where(Task.expiration_date <= datetime.fromisoformat(to_date))

        if search is not None:
            search_pattern = f"%{search}%"
            query = query.where(
                (Task.title.ilike(search_pattern)) | (Task.description.ilike(search_pattern))
            )

        result = await self.session.execute(query)
        return result.scalars().all()

    # --------------- CREATE ----------------

    async def create(self, user_id: int, title: str, description: str, expiration_date: Optional[datetime],
                     is_completed: bool, category_id: int) -> Task:
        new_task = Task(
            user_id=user_id,
            title=title,
            description=description,
            expiration_date=expiration_date,
            is_completed=is_completed,
            category_id=category_id
        )
        self.session.add(new_task)
        await self.session.commit()
        await self.session.refresh(new_task)
        return new_task

    # --------------- UPDATE ----------------

    async def patch(self, id: int, data: dict) -> Optional[Task]:
        task = await self.get_by_id(id)

        if not task:
            return None

        for k, v in data.items():
            if hasattr(task, k):
                setattr(task, k, v)

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    # --------------- DELETE ----------------

    async def delete(self, id: int) -> bool:
        task = await self.get_by_id(id)

        if not task:
            return False

        await self.session.delete(task)
        await self.session.commit()
        return True

    # --------------- для DEBUG жеск ----------------

    async def get_all_task(self) -> Sequence[Task]:
        result = await self.session.execute(select(Task))
        return result.scalars().all()