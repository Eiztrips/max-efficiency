import pytest
from app.repositories.user import UserRepository
from app.models import User, Category, Task, Tag


class TestUserRepository:

    @pytest.mark.asyncio
    async def test_get_id_by_max_user_id(self, db_session):
        """Тест получения внутреннего user_id по max_user_id"""
        repo = UserRepository(db_session)
        user = await repo.create(max_user_id=123456, username="test_user")
        result = await repo.get_id_by_max_user_id(123456)

        assert result == user.id

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session):
        """Тест получения пользователя по ID"""
        repo = UserRepository(db_session)
        user = await repo.create(max_user_id=123456, username="test_user")
        result = await repo.get_by_id(user.id)

        assert result is not None
        assert result.id == user.id
        assert result.max_user_id == 123456
        assert result.username == "test_user"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session):
        """Тест получения несуществующего пользователя"""
        repo = UserRepository(db_session)
        result = await repo.get_by_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_username(self, db_session):
        """Тест получения пользователя по username"""
        repo = UserRepository(db_session)
        await repo.create(max_user_id=123456, username="test_user")
        result = await repo.get_by_username("test_user")

        assert result is not None
        assert result.username == "test_user"
        assert result.max_user_id == 123456

    @pytest.mark.asyncio
    async def test_get_by_username_not_found(self, db_session):
        """Тест получения несуществующего пользователя по username"""
        repo = UserRepository(db_session)
        result = await repo.get_by_username("nonexistent_user")

        assert result is None

    @pytest.mark.asyncio
    async def test_create(self, db_session):
        """Тест создания пользователя"""
        repo = UserRepository(db_session)
        user = await repo.create(max_user_id=123456, username="new_user")

        assert user.id is not None
        assert user.max_user_id == 123456
        assert user.username == "new_user"
        assert user.created_at is not None
        assert user.updated_at is not None

    @pytest.mark.asyncio
    async def test_patch(self, db_session):
        """Тест обновления пользователя"""
        repo = UserRepository(db_session)
        user = await repo.create(max_user_id=123456, username="old_username")
        updated_user = await repo.patch(user.id, {"username": "new_username"})

        assert updated_user is not None
        assert updated_user.id == user.id
        assert updated_user.username == "new_username"
        assert updated_user.max_user_id == 123456

    @pytest.mark.asyncio
    async def test_patch_not_found(self, db_session):
        """Тест обновления несуществующего пользователя"""
        repo = UserRepository(db_session)
        result = await repo.patch(999, {"username": "new_username"})

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, db_session):
        """Тест получения всех пользователей"""
        repo = UserRepository(db_session)
        await repo.create(max_user_id=111, username="user1")
        await repo.create(max_user_id=222, username="user2")
        await repo.create(max_user_id=333, username="user3")
        users = await repo.get_all()

        assert len(users) == 3
        assert all(isinstance(u, User) for u in users)

    @pytest.mark.asyncio
    async def test_get_all_with_pagination(self, db_session):
        """Тест получения пользователей с пагинацией"""
        repo = UserRepository(db_session)

        for i in range(1, 6):
            await repo.create(max_user_id=i * 100, username=f"user{i}")

        users_page1 = await repo.get_all(offset_=0, limit_=2)
        assert len(users_page1) == 2

        users_page2 = await repo.get_all(offset_=2, limit_=2)
        assert len(users_page2) == 2

        assert users_page1[0].id != users_page2[0].id

    @pytest.mark.asyncio
    async def test_get_categories_by_user_id(self, db_session):
        """Тест получения всех категорий пользователя по max_user_id"""
        repo = UserRepository(db_session)
        user = await repo.create(max_user_id=123456, username="test_user")
        category1 = Category(name="Category 1", description="Desc 1", owner_id=user.id)
        category2 = Category(name="Category 2", description="Desc 2", owner_id=user.id)
        db_session.add(category1)
        db_session.add(category2)
        await db_session.commit()

        categories = await repo.get_categories_by_user_id(user.id)

        assert len(categories) == 2
        assert all(isinstance(c, Category) for c in categories)

    @pytest.mark.asyncio
    async def test_get_tasks_by_user_id(self, db_session):
        """Тест получения всех задач пользователя по max_user_id"""
        repo = UserRepository(db_session)
        user = await repo.create(max_user_id=123456, username="test_user")
        category = Category(name="Category", description="Desc", owner_id=user.id)
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        task1 = Task(user_id=user.id, title="Task 1", category_id=category.id)
        task2 = Task(user_id=user.id, title="Task 2", category_id=category.id)
        db_session.add(task1)
        db_session.add(task2)
        await db_session.commit()

        tasks = await repo.get_tasks_by_user_id(user.id)

        assert len(tasks) == 2
        assert all(isinstance(t, Task) for t in tasks)

    @pytest.mark.asyncio
    async def test_get_tags_by_user_id(self, db_session):
        """Тест получения всех тегов пользователя по max_user_id"""
        repo = UserRepository(db_session)
        user = await repo.create(max_user_id=123456, username="test_user")

        category = Category(name="Category", description="Desc", owner_id=user.id)
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        tag1 = Tag(name="Tag 1", color="red", category_id=category.id)
        tag2 = Tag(name="Tag 2", color="blue", category_id=category.id)
        db_session.add(tag1)
        db_session.add(tag2)
        await db_session.commit()

        tags = await repo.get_tags_by_user_id(user.id)

        assert len(tags) == 2
        assert all(isinstance(t, Tag) for t in tags)

