from typing import Optional

from sqlalchemy import select, update, Sequence

from .base import BaseRepository
from app.models.user import User

class UserRepository(BaseRepository):

    # --------------- GET ----------------

    async def get_by_id(self, id: int) -> Optional[User]:
        result = await self.session.execute(select(User)
                                            .where(User.id == id))
        return result.scalar_one_or_none()

    async def get_by_max_id(self, max_id: int) -> Optional[User]:
        result = await self.session.execute(select(User)
                                            .where(User.max_id == max_id))
        return result.scalar_one_or_none()

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

    async def update(self, id: int, data: dict) -> Optional[User]:
        result = await self.session.execute(
            update(User)
            .where(User.id == id)
            .values(**data)
            .returning(User)
        )
        await self.session.commit()
        return result.scalar_one_or_none()

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

    async def get_all_users(self, offset_: int = 0, limit_: int = 100) -> Sequence[User]:
        result = await self.session.execute(select(User).offset(offset_).limit(limit_))
        return result.scalars().all()