from typing import Optional

from sqlalchemy import select, Sequence

from .base import BaseRepository
from ..models import Task, task_tags
from datetime import datetime

from ..schemas import TaskCreate
from ..schemas.task import TaskQuery, TaskUpdate, TaskRead


class TaskRepository(BaseRepository):

    # --------------- GET ----------------

    async def get_by_id(self, id: int) -> Optional[Task]:
        result = await self.session.execute(select(Task)
                                            .where(Task.id == id))
        return result.scalar_one_or_none()

    async def get_tasks(self, payload: TaskQuery) -> Sequence[Task]:

        query = select(Task).where(Task.user_id == payload.user_id)

        if payload.category_id is not None:
            query = query.where(Task.category_id == payload.category_id)

        if payload.tag_id is not None:
            query = query.join(task_tags).where(task_tags.c.tag_id == payload.tag_id)

        if payload.status is not None:
            if payload.status == "done":
                query = query.where(Task.expiration_date < datetime.now())
            elif payload.status == "pending":
                query = query.where(Task.expiration_date >= datetime.now())

        if payload.is_completed is not None:
            query = query.where(Task.is_completed == payload.is_completed)

        if payload.from_date is not None:
            query = query.where(Task.expiration_date >= datetime.fromisoformat(payload.from_date))

        if payload.to_date is not None:
            query = query.where(Task.expiration_date <= datetime.fromisoformat(payload.to_date))

        if payload.search is not None:
            search_pattern = f"%{payload.search}%"
            query = query.where(
                (Task.title.ilike(search_pattern)) | (Task.description.ilike(search_pattern))
            )

        result = await self.session.execute(query)
        return result.scalars().all()

    # --------------- CREATE ----------------

    async def create(self, payload: TaskCreate) -> Task:
        new_task = Task(
            user_id=payload.user_id,
            title=payload.title,
            description=payload.description,
            expiration_date=payload.expiration_date,
            is_completed=payload.is_completed,
            category_id=payload.category_id
        )
        self.session.add(new_task)
        await self.session.commit()
        await self.session.refresh(new_task)
        return new_task

    # --------------- UPDATE ----------------

    async def patch(self, payload: TaskUpdate) -> Optional[Task]:
        task = await self.get_by_id(payload.id)

        if not task:
            return None

        for field, value in payload.dict(exclude_unset=True).items():
            if field != "id":
                setattr(task, field, value)

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