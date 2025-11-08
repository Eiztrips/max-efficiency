from typing import Optional

from sqlalchemy import select, Sequence

from .base import BaseRepository
from ..models import Category, User

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

    async def patch(self, id: int, data: dict) -> Optional[Category]:
        category = await self.get_by_id(id)

        if not category:
            return None

        for k, v in data.items():
            if hasattr(category, k):
                setattr(category, k, v)

        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def add_user(self, category_id: int, user_id: int) -> bool:
        category = await self.get_by_id(category_id)
        user_result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not category or not user:
            return False

        if user not in category.users:
            category.users.append(user)
            await self.session.commit()
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
