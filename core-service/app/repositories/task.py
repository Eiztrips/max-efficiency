from typing import Optional

from sqlalchemy import select, update, Sequence

from .base import BaseRepository
from ..models import Task


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

    # --------------- CREATE ----------------

    async def create(self, user_id: int, title: str, description: str = "", completed: bool = False) -> Optional[Task]:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            is_completed=completed
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

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