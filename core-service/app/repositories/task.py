from typing import Optional
from sqlalchemy import select, Sequence
from sqlalchemy.orm import selectinload
from datetime import datetime

from .base import BaseRepository
from ..models import Task, task_tags
from ..schemas import TaskCreate, TaskQuery, TaskUpdate


class TaskRepository(BaseRepository):

    # --------------- GET ----------------

    async def get_by_id(self, id: int) -> Optional[Task]:
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.tags))
            .where(Task.id == id)
        )
        return result.scalar_one_or_none()

    async def get_tasks(self, payload: TaskQuery) -> Sequence[Task]:

        query = select(Task).options(selectinload(Task.tags)).where(Task.user_id == payload.user_id)

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
        await self.session.refresh(new_task) # , ['tags']
        return new_task

    # --------------- UPDATE ----------------

    async def patch(self, payload: TaskUpdate) -> Optional[Task]:
        task = await self.get_by_id(payload.id)

        if not task:
            return None

        for field, value in payload.model_dump(exclude_unset=True).items():
            if field != "id":
                setattr(task, field, value)

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task) # , ['tags']
        return task

    # --------------- TAGS ----------------

    async def update_task_tags(self, task_id: int, tag_ids: list[int]) -> Optional[Task]:
        task = await self.get_by_id(task_id)
        if not task:
            return None

        # Загружаем теги
        from ..models import Tag
        result = await self.session.execute(
            select(Tag).where(Tag.id.in_(tag_ids))
        )
        tags = result.scalars().all()

        # Заменяем теги
        task.tags = list(tags)
        await self.session.commit()
        await self.session.refresh(task, ['tags'])
        return task

    async def add_tag_to_task(self, task_id: int, tag_id: int) -> Optional[Task]:
        task = await self.get_by_id(task_id)
        if not task:
            return None

        # Проверяем, что тег еще не добавлен
        if any(tag.id == tag_id for tag in task.tags):
            return task

        # Загружаем тег
        from ..models import Tag
        result = await self.session.execute(
            select(Tag).where(Tag.id == tag_id)
        )
        tag = result.scalar_one_or_none()
        if not tag:
            return None

        # Добавляем тег
        task.tags.append(tag)
        await self.session.commit()
        await self.session.refresh(task, ['tags'])
        return task

    async def remove_tag_from_task(self, task_id: int, tag_id: int) -> Optional[Task]:
        task = await self.get_by_id(task_id)
        if not task:
            return None

        # Удаляем тег
        task.tags = [tag for tag in task.tags if tag.id != tag_id]
        await self.session.commit()
        await self.session.refresh(task, ['tags'])
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
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.tags))
        )
        return result.scalars().all()