from typing import Optional, Sequence, cast

from sqlalchemy import select, Sequence

from .base import BaseRepository
from ..models import User, Tag, Category, Task


class UserRepository(BaseRepository):

    # --------------- GET BY ID (только в беке юзать) ----------------

    async def get_by_id(self, id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    # --------------- GET BY MAX_ID ----------------

    async def get_by_max_id(self, max_id: int) -> Optional[User]:
        result = await self.session.execute(select(User)
                                            .where(User.max_id == max_id))
        return result.scalar_one_or_none()

    # следующее возможно придется переместить в tag/category/task репозитории
    async def get_all_tags_by_max_id(self, max_id: int) -> Sequence[Tag]:
        result = await self.session.execute(
            select(Tag).join(Category).join(User).where(User.max_id == max_id)
        )
        return result.scalars().all()

    async def get_all_categories_by_max_id(self, max_id: int) -> Sequence[Category]:
        result = await self.session.execute(
            select(Category).join(User).where(User.max_id == max_id)
        )
        return result.scalars().all()

    async def get_all_tasks_by_max_id(self, max_id: int) -> Sequence[Task]:
        result = await self.session.execute(
            select(Task).join(User).where(User.max_id == max_id)
        )
        return result.scalars().all()

    # --------------- GET BY USERNAME ----------------

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(select(User)
                                            .where(User.username == username))
        return result.scalar_one_or_none()

    # --------------- CREATE ----------------

    async def create(self, max_id: int, username: str) -> User:
        user = User(
            max_id=max_id, username=username
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    # --------------- UPDATE ----------------

    async def patch(self, id: int, data: dict) -> Optional[User]:
        user = await self.get_by_id(id)

        if not user:
            return None

        for k, v in data.items():
            if hasattr(user, k):
                setattr(user, k, v)

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    # --------------- для DEBUG жеск ----------------

    async def get_all(self, offset_: int = 0, limit_: int = 100) -> Sequence[User]:
        result = await self.session.execute(select(User).offset(offset_).limit(limit_))
        return result.scalars().all()