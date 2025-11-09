import pytest
from app.repositories.category import CategoryRepository
from app.models import User, Category, Task, Tag


class TestCategoryRepository:

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session):
        """Тест получения категории по ID"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        category = await repo.create(user.id, "Test Category", "Test Description")
        result = await repo.get_by_id(category.id)

        assert result is not None
        assert result.id == category.id
        assert result.name == "Test Category"
        assert result.description == "Test Description"
        assert result.owner_id == user.id

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session):
        """Тест получения несуществующей категории"""
        repo = CategoryRepository(db_session)
        result = await repo.get_by_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_id(self, db_session):
        """Тест получения категорий по user_id"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)

        category1 = Category(name="Category 1", owner_id=user.id)
        category2 = Category(name="Category 2", owner_id=user.id)
        db_session.add(category1)
        db_session.add(category2)
        await db_session.commit()
        await db_session.refresh(category1)
        await db_session.refresh(category2)

        await repo.add_user(category1.id, user.id)
        await repo.add_user(category2.id, user.id)

        result = await repo.get_by_user_id(user.id)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_all_joined_users_in_category(self, db_session):
        """Тест получения всех пользователей категории"""
        user1 = User(max_user_id=123456, username="user1")
        user2 = User(max_user_id=123457, username="user2")
        db_session.add(user1)
        db_session.add(user2)
        await db_session.commit()
        await db_session.refresh(user1)
        await db_session.refresh(user2)

        repo = CategoryRepository(db_session)
        category = await repo.create(user1.id, "Test Category")

        await repo.add_user(category.id, user1.id)
        await repo.add_user(category.id, user2.id)

        users = await repo.get_all_joined_users_in_category(category.id)

        assert len(users) == 2

    @pytest.mark.asyncio
    async def test_get_all_tags_in_category(self, db_session):
        """Тест получения всех тегов категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        category = await repo.create(user.id, "Test Category")

        tag1 = Tag(name="Tag 1", color="red", category_id=category.id)
        tag2 = Tag(name="Tag 2", color="blue", category_id=category.id)
        db_session.add(tag1)
        db_session.add(tag2)
        await db_session.commit()

        tags = await repo.get_all_tags_in_category(category.id)

        assert len(tags) == 2

    @pytest.mark.asyncio
    async def test_get_all_tasks_in_category(self, db_session):
        """Тест получения всех задач категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        category = await repo.create(user.id, "Test Category")

        task1 = Task(user_id=user.id, title="Task 1", category_id=category.id)
        task2 = Task(user_id=user.id, title="Task 2", category_id=category.id)
        db_session.add(task1)
        db_session.add(task2)
        await db_session.commit()

        tasks = await repo.get_all_tasks_in_category(category.id)

        assert len(tasks) == 2

    @pytest.mark.asyncio
    async def test_create(self, db_session):
        """Тест создания категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        category = await repo.create(user.id, "New Category", "Description")

        assert category is not None
        assert category.name == "New Category"
        assert category.description == "Description"
        assert category.owner_id == user.id

    @pytest.mark.asyncio
    async def test_patch(self, db_session):
        """Тест обновления категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        category = await repo.create(user.id, "Old Name", "Old Description")

        assert await repo.patch(category.id, {"name": "New Name"})
        updated = await repo.get_by_id(category.id)

        assert updated is not None
        assert updated.name == "New Name"
        assert updated.description == "Old Description"

    @pytest.mark.asyncio
    async def test_patch_not_found(self, db_session):
        """Тест обновления несуществующей категории"""
        repo = CategoryRepository(db_session)
        result = await repo.patch(999, {"name": "New Name"})

        assert not(result)

    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        """Тест удаления категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        category = await repo.create(user.id, "Test Category")

        result = await repo.delete(category.id)
        assert result is True

        deleted = await repo.get_by_id(category.id)
        assert deleted is None

    @pytest.mark.asyncio
    async def test_delete_not_found(self, db_session):
        """Тест удаления несуществующей категории"""
        repo = CategoryRepository(db_session)
        result = await repo.delete(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_add_user(self, db_session):
        """Тест добавления пользователя в категорию"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        category = await repo.create(user.id, "Test Category")

        result = await repo.add_user(category.id, user.id)
        assert result is True

    @pytest.mark.asyncio
    async def test_add_user_twice(self, db_session):
        """Тест повторного добавления пользователя в категорию"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        category = await repo.create(user.id, "Test Category")
        result = await repo.add_user(category.id, user.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_add_user_not_found(self, db_session):
        """Тест добавления несуществующего пользователя"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        category = await repo.create(user.id, "Test Category")

        result = await repo.add_user(category.id, 999)
        assert result is False