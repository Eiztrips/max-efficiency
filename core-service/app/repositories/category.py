from typing import Optional

from sqlalchemy import select, Sequence

from .base import BaseRepository
from ..models import Category, User, Tag, Task


class CategoryRepository(BaseRepository):

    # --------------- GET ----------------

    async def get_by_id(self, id: int) -> Optional[Category]:
        result = await self.session.execute(select(Category)
                                            .where(Category.id == id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: int) -> Sequence[Category]:
        result = await self.session.execute(
            select(Category)
            .join(Category.users)
            .where(User.id == user_id)
        )
        return result.scalars().all()

    async def get_all_joined_users_in_category(self, category_id: int) -> Sequence[User]:
        result = await self.session.execute(
            select(User)
            .join(Category.users)
            .where(Category.id == category_id)
        )
        return result.scalars().all()

    async def get_all_tags_in_category(self, category_id: int) -> Sequence[Tag]:
        result = await self.session.execute(
            select(Tag)
            .where(Tag.category_id == category_id)
        )
        return result.scalars().all()

    async def get_all_tasks_in_category(self, category_id: int) -> Sequence[Task]:
        from ..models import Task
        result = await self.session.execute(
            select(Task)
            .where(Task.category_id == category_id)
        )
        return result.scalars().all()

    # --------------- CREATE ----------------

    async def create(self, user_id: int, name: str, description: str = "") -> Optional[Category]:
        category = Category(
            owner_id=user_id,
            name=name,
            description=description
        )
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    # --------------- UPDATE ----------------

    async def patch(self, id: int, data: dict) -> bool:
        category = await self.get_by_id(id)
        if not category:
            return False
        for key, value in data.items():
            setattr(category, key, value)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return True

    async def add_user(self, category_id: int, user_id: int) -> bool:
        category = await self.get_by_id(category_id)
        if not category:
            return False
        user = await self.session.get(User, user_id)
        if not user:
            return False

        category.users.append(user)
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return True

    # --------------- DELETE ----------------

    async def delete(self, id: int) -> bool:
        category = await self.get_by_id(id)
        if not category:
            return False
        await self.session.delete(category)
        await self.session.commit()
        return True

    # --------------- для DEBUG жеск ----------------

    async def get_all_categories(self, offset_: int = 0, limit_: int = 100) -> Sequence[Category]:
        result = await self.session.execute(select(Category).offset(offset_).limit(limit_))
        return result.scalars().all()
