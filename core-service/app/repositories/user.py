from typing import Optional
from sqlalchemy import select, Sequence
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..models import User, Tag, Category, Task
from ..schemas import UserCreate


class UserRepository(BaseRepository):

    # --------------- GET ID BY MAX_ID ----------------

    async def get_id_by_max_user_id(self, max_user_id: int) -> int:
        result = await self.session.execute(
            select(User.id).where(User.max_user_id == max_user_id)
        )
        user_id = result.scalar_one_or_none()
        return user_id

    # --------------- GET BY ID (только в беке юзать) ----------------

    async def get_by_id(self, id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User)
            .options(
                selectinload(User.categories_owned),
                selectinload(User.categories_joined)
            )
            .where(User.id == id)
        )
        return result.scalar_one_or_none()

    # --------------- GET BY MAX_ID ----------------

    # следующее возможно придется переместить в tag/category/task репозитории
    async def get_tags_by_user_id(self, user_id: int) -> Sequence[Tag]:
        result = await self.session.execute(
            select(Tag)
            .options(selectinload(Tag.tasks))
            .join(Category)
            .join(User)
            .where(User.id == user_id)
        )
        return result.scalars().all()

    async def get_categories_by_user_id(self, user_id: int) -> Sequence[Category]:
        result = await self.session.execute(
            select(Category)
            .options(
                selectinload(Category.users),
                selectinload(Category.tags),
                selectinload(Category.tasks)
            )
            .join(User)
            .where(User.id == user_id)
        )
        return result.scalars().all()

    async def get_tasks_by_user_id(self, user_id: int) -> Sequence[Task]:
        user = await self.get_by_id(user_id)
        if not user:
            return []
        result = await self.session.execute(
            select(Task)
            .options(selectinload(Task.tags))
            .where(Task.user_id == user.id)
        )
        return result.scalars().all()

    # --------------- GET BY USERNAME ----------------

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.session.execute(
            select(User)
            .options(
                selectinload(User.categories_owned),
                selectinload(User.categories_joined)
            )
            .where(User.username == username)
        )
        return result.scalar_one_or_none()

    # --------------- CREATE ----------------

    async def create(self, payload: UserCreate) -> User:
        user = User(
            max_user_id=payload.max_user_id, username=payload.username
        )

        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user, ['categories_owned', 'categories_joined'])
        return user

    # --------------- UPDATE ----------------

    """ пока unuse потому что обновлять нечего
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
    """

    # --------------- для DEBUG жеск ----------------

    async def get_all(self, offset_: int = 0, limit_: int = 100) -> Sequence[User]:
        result = await self.session.execute(
            select(User)
            .options(
                selectinload(User.categories_owned),
                selectinload(User.categories_joined)
            )
            .offset(offset_)
            .limit(limit_)
        )
        return result.scalars().all()