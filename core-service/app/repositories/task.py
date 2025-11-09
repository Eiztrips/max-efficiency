from typing import Optional

from sqlalchemy import select, Sequence

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
            query = query.join(task_tags).where(task_tags.c.tag_id == tag_id)

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