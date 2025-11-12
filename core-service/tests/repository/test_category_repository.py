import pytest

from app.repositories.category import CategoryRepository
from app.models import User, Category, Task, Tag
from app.schemas import CategoryCreate
from app.schemas.category import CategoryUsersUpdateV2, CategoryUpdate


class TestCategoryRepository:

    @pytest.mark.asyncio
    async def test_get_by_id(self, db_session):
        """Тест получения категории по ID"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        payload = CategoryCreate(user_id=user.id, name="Test Category", description="Test Description")
        category = await repo.create(payload)
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

        payload = CategoryUsersUpdateV2(id=category1.id, user_id=user.id)
        await repo.add_user(payload)
        payload = CategoryUsersUpdateV2(id=category2.id, user_id=user.id)
        await repo.add_user(payload)

        result = await repo.get_by_user_id(user.id)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_joined_users(self, db_session):
        """Тест получения всех пользователей категории"""
        user1 = User(max_user_id=123456, username="user1")
        user2 = User(max_user_id=123457, username="user2")
        db_session.add(user1)
        db_session.add(user2)
        await db_session.commit()
        await db_session.refresh(user1)
        await db_session.refresh(user2)

        repo = CategoryRepository(db_session)
        payload = CategoryCreate(user_id=user1.id, name="Test Category", description="Test Description")
        category = await repo.create(payload)

        payload = CategoryUsersUpdateV2(id=category.id, user_id=user1.id)
        await repo.add_user(payload)
        payload = CategoryUsersUpdateV2(id=category.id, user_id=user2.id)
        await repo.add_user(payload)

        users = await repo.get_joined_users(category.id)

        assert len(users) == 2

    @pytest.mark.asyncio
    async def test_get_tags(self, db_session):
        """Тест получения всех тегов категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        payload = CategoryCreate(user_id=user.id, name="Test Category")
        category = await repo.create(payload)

        tag1 = Tag(name="Tag 1", color="red", category_id=category.id)
        tag2 = Tag(name="Tag 2", color="blue", category_id=category.id)
        db_session.add(tag1)
        db_session.add(tag2)
        await db_session.commit()

        tags = await repo.get_tags(category.id)

        assert len(tags) == 2

    @pytest.mark.asyncio
    async def test_get_tasks(self, db_session):
        """Тест получения всех задач категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        payload = CategoryCreate(user_id=user.id, name="Test Category")
        payload = CategoryCreate(user_id=user.id, name="Test Category")
        category = await repo.create(payload)

        task1 = Task(user_id=user.id, title="Task 1", category_id=category.id)
        task2 = Task(user_id=user.id, title="Task 2", category_id=category.id)
        db_session.add(task1)
        db_session.add(task2)
        await db_session.commit()

        tasks = await repo.get_tasks(category.id)

        assert len(tasks) == 2

    @pytest.mark.asyncio
    async def test_create(self, db_session):
        """Тест создания категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        payload = CategoryCreate(user_id=user.id, name="New Category", description="Description")
        category = await repo.create(payload)

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

        payload = CategoryCreate(user_id=user.id, name="Old Name", description="Old Description")
        category = await repo.create(payload)

        payload = CategoryUpdate(id=category.id, name="New Name")
        assert await repo.patch(payload)
        updated = await repo.get_by_id(category.id)

        assert updated is not None
        assert updated.name == "New Name"
        assert updated.description == "Old Description"

    @pytest.mark.asyncio
    async def test_patch_not_found(self, db_session):
        """Тест обновления несуществующей категории"""
        repo = CategoryRepository(db_session)
        payload = CategoryUpdate(id=999, name="New Name")
        result = await repo.patch(payload)

        assert not(result)

    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        """Тест удаления категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        payload = CategoryCreate(user_id=user.id, name="Test Category")
        category = await repo.create(payload)

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
        payload = CategoryCreate(user_id=user.id, name="Test Category")
        category = await repo.create(payload)

        payload = CategoryUsersUpdateV2(id=category.id, user_id=user.id)
        result = await repo.add_user(payload)
        assert result is True

    @pytest.mark.asyncio
    async def test_add_user_twice(self, db_session):
        """Тест повторного добавления пользователя в категорию"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        payload = CategoryCreate(user_id=user.id, name="Test Category")
        category = await repo.create(payload)
        payload = CategoryUsersUpdateV2(id=category.id, user_id=user.id)
        result = await repo.add_user(payload)

        assert result is True

    @pytest.mark.asyncio
    async def test_add_user_not_found(self, db_session):
        """Тест добавления несуществующего пользователя"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        payload = CategoryCreate(user_id=user.id, name="Test Category")
        category = await repo.create(payload)

        payload = CategoryUsersUpdateV2(id=category.id, user_id=999)
        result = await repo.add_user(payload)
        assert result is False

    @pytest.mark.asyncio
    async def test_remove_user(self, db_session):
        """Тест удаления пользователя из категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        payload = CategoryCreate(user_id=user.id, name="Test Category")
        category = await repo.create(payload)

        payload = CategoryUsersUpdateV2(id=category.id, user_id=user.id)
        await repo.add_user(payload)

        result = await repo.remove_user(payload)
        assert result is True

    @pytest.mark.asyncio
    async def test_remove_user_not_found(self, db_session):
        """Тест удаления несуществующего пользователя из категории"""
        user = User(max_user_id=123456, username="test_user")
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        repo = CategoryRepository(db_session)
        payload = CategoryCreate(user_id=user.id, name="Test Category")
        category = await repo.create(payload)

        payload = CategoryUsersUpdateV2(id=category.id, user_id=999)
        result = await repo.remove_user(payload)
        assert result is False